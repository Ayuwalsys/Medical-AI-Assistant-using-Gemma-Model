from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
from google.cloud import aiplatform
from typing import Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ModelConfig
from models.retrieval_models import MedicalKnowledgeBase

class Chain(ABC):
    @abstractmethod
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pass


# Add the missing RetrievalChain class
class RetrievalChain(Chain):
    def __init__(self):
        self.knowledge_base = MedicalKnowledgeBase()

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Get relevant information from the knowledge base
        retrieved_info = self.knowledge_base.retrieve_information(inputs["Patient"])
        inputs["retrieved_info"] = retrieved_info
        return inputs
    
class InputValidationChain(Chain):
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ["Patient", "Description"]
        for field in required_fields:
            if field not in inputs or not inputs[field].strip():
                raise ValueError(f"Missing or empty {field}")
        return inputs

class ContextEnhancementChain(Chain):
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        symptoms = inputs["Patient"].lower()
        enhanced_context = ""
        
        # Enhanced symptom contexts with more detailed medical information
        symptom_contexts = {
            "fever": " Assessment includes temperature monitoring, hydration status, and potential underlying causes.",
            "headache": " Evaluation considers type, location, duration, and associated neurological symptoms.",
            "cough": " Analysis includes duration, character (productive/dry), and associated respiratory symptoms.",
            "blood pressure": " Cardiovascular assessment including BP readings, lifestyle factors, and medication review.",
            "chest pain": " Urgent evaluation required - characteristics, radiation, associated symptoms crucial.",
            "diabetes": " Blood glucose monitoring, medication compliance, and complications screening needed.",
            "pain": " Detailed pain assessment using PQRST method (Provocation/Palliation, Quality, Region, Severity, Timing).",
            "breathing": " Respiratory evaluation including rate, effort, oxygen saturation, and associated symptoms.",
            "dizzy": " Assessment of vertigo vs lightheadedness, postural changes, and cardiovascular status.",
            "nausea": " Evaluation of gastrointestinal symptoms, hydration status, and potential underlying causes."
        }
        
        # Add relevant context based on symptoms
        for symptom, context in symptom_contexts.items():
            if symptom in symptoms:
                enhanced_context += context
        
        # Check for urgent symptoms
        urgent_symptoms = ["chest pain", "breathing", "severe", "emergency"]
        if any(symptom in symptoms for symptom in urgent_symptoms):
            enhanced_context += "\nURGENT: This condition may require immediate medical attention."
        
        # Use enhanced context if available, otherwise use original symptoms
        inputs["Description"] = enhanced_context if enhanced_context else symptoms
        return inputs

class ResponseGenerationChain(Chain):
    def __init__(self, endpoint: aiplatform.Endpoint, config: ModelConfig):
        self.endpoint = endpoint
        self.config = config
        self.severity_levels = {
            "HIGH": "🚨 URGENT - Immediate medical attention recommended",
            "MEDIUM": "⚠️ MODERATE - Medical consultation recommended",
            "LOW": "ℹ️ MILD - Can be monitored at home with precautions"
        }

    def assess_severity(self, symptoms: str) -> str:
        # Add cancer-related terms to urgent symptoms
        urgent_symptoms = ["chest pain", "breathing", "severe", "emergency", "heart", "stroke", 
                         "unconscious", "bleeding heavily", "head injury", "cancer", "tumor", "malignant"]
        moderate_symptoms = ["fever", "persistent", "chronic", "diabetes", "infection", 
                           "vomiting", "dizziness", "pain"]
        
        symptoms_lower = symptoms.lower()
        if any(symptom in symptoms_lower for symptom in urgent_symptoms):
            return self.severity_levels["HIGH"]
        elif any(symptom in symptoms_lower for symptom in moderate_symptoms):
            return self.severity_levels["MEDIUM"]
        return self.severity_levels["LOW"]

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            severity = self.assess_severity(inputs["Patient"])
            
            # Include retrieved information in the prompt
            system_prompt = f"""You are a medical AI assistant. Use the following retrieved medical information to provide a comprehensive response:

Retrieved Information:
{inputs.get('retrieved_info', 'No specific information retrieved.')}

Please provide a response in the following format:


1. ACKNOWLEDGMENT: Brief empathetic acknowledgment
2. ASSESSMENT: Initial assessment based on symptoms and retrieved information
3. RECOMMENDATIONS: Specific actionable recommendations
4. WARNINGS: Important warning signs to watch for
5. FOLLOW-UP: When to seek medical attention

Keep each section concise but informative."""

            formatted_prompt = f"""System: {system_prompt}

Patient's Concern: {inputs['Patient']}

Medical Context: {inputs['Description']}

Please provide your response following the format above:"""

            instance = {
                "prompt": formatted_prompt,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                "raw_response": self.config.raw_response,
            }
            
            try:
                response = self.endpoint.predict([instance])
                response_text = response.predictions[0]
                
                # Validate response length and format
                if len(response_text.split()) < 20:
                    response_text = self.generate_structured_response(inputs, severity)
                
                inputs["Response"] = response_text
                inputs["Severity"] = severity
                return inputs
                
            except Exception as e:
                print(f"Error in AI response generation: {str(e)}")
                inputs["Response"] = self.generate_structured_response(inputs, severity)
                inputs["Severity"] = severity
                return inputs
                
        except Exception as e:
            print(f"Error in response chain: {str(e)}")
            inputs["Response"] = self.generate_fallback_response()
            inputs["Severity"] = self.severity_levels["MEDIUM"]
            return inputs

    def generate_structured_response(self, inputs: Dict[str, Any], severity: str) -> str:
        symptoms = inputs["Patient"]
        retrieved_info = inputs.get('retrieved_info', '')
        
        return f"""1. ACKNOWLEDGMENT:
I understand your concern about experiencing {symptoms}. It's important to take your symptoms seriously.

2. ASSESSMENT:
Based on your symptoms and the available medical information:
{retrieved_info[:200] + '...' if len(retrieved_info) > 200 else retrieved_info}
This could indicate several conditions that require proper evaluation.

3. RECOMMENDATIONS:
- Rest and monitor your symptoms carefully
- Stay well-hydrated
- Take over-the-counter medications as appropriate for symptom relief
- Document any changes in symptoms
- Maintain good hygiene and preventive measures

4. WARNINGS:
Seek immediate medical attention if you experience:
- Severe or worsening symptoms
- Development of new concerning symptoms
- Difficulty breathing
- Severe pain
- Changes in consciousness or mental state

5. FOLLOW-UP:
{self._generate_followup_advice(severity)}"""

    def _generate_followup_advice(self, severity: str) -> str:
        if "URGENT" in severity:
            return "Please seek immediate medical attention or visit the nearest emergency room."
        elif "MODERATE" in severity:
            return "Schedule an appointment with your healthcare provider within the next 24-48 hours."
        else:
            return "Monitor your symptoms and consult with a healthcare provider if they persist or worsen."

    def generate_fallback_response(self) -> str:
        return """1. ACKNOWLEDGMENT:
I apologize, but I'm having trouble processing your request properly.

2. ASSESSMENT:
Without being able to properly analyze your symptoms, I cannot provide a specific assessment.

3. RECOMMENDATIONS:
- Document your symptoms in detail
- Monitor any changes
- Consider consulting with a healthcare provider

4. WARNINGS:
If you're experiencing any severe symptoms or are concerned about your health:
- Seek immediate medical attention
- Call emergency services if you feel it's urgent
- Don't wait if you feel your condition is serious

5. FOLLOW-UP:
Please consult with a qualified healthcare provider for proper evaluation and treatment advice."""
class ResponseFormattingChain(Chain):
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        severity_level = inputs.get("Severity", "⚠️ Severity level not determined")
        
        formatted_output = (
            #"\n" + "="*80 + "\n"
            f"🏥 MEDICAL CONSULTATION REPORT\n"
            f"{'-'*30}\n\n"
            f"Severity Assessment:\n{severity_level}\n\n"
            f"📋 Patient's Concern:\n{inputs['Patient']}\n\n"
            f"🔍 Medical Context:\n{inputs['Description']}\n\n"
            f"👨‍⚕️ Medical Response:\n{inputs['Response']}\n\n"
            # f"⚕️ IMPORTANT DISCLAIMERS:\n"
            # f"1. This is an AI-generated response for informational purposes only.\n"
            # f"2. This is not a substitute for professional medical advice.\n"
            # f"3. If in doubt, always consult with a healthcare provider.\n"
            # f"4. For emergencies, call your local emergency services immediately.\n"
            # + "="*80 + "\n"
        )
        inputs["FormattedOutput"] = formatted_output
        return inputs

class MedicalChain:
    def __init__(self, endpoint: aiplatform.Endpoint):
        self._endpoint = endpoint  # Store the endpoint privately
        self.config = ModelConfig()
        self.chains = [
            InputValidationChain(),
            RetrievalChain(),
            ContextEnhancementChain(),
            ResponseGenerationChain(endpoint, self.config),
            ResponseFormattingChain()
        ]
        self.response_history = []
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0
        }

    @property
    def endpoint(self):
        return self._endpoint

    def process(self, example: Dict[str, str]) -> Dict[str, Any]:
        try:
            self._stats["total_requests"] += 1
            
            # Process through chain
            result = example
            for chain in self.chains:
                result = chain.run(result)
        
            # Record history with timestamp
            self.response_history.append({
                "concern": example["Patient"],
                "timestamp": datetime.now(),
                "response": result["Response"],
                "severity": result.get("Severity", "Unknown"),
                "description": example.get("Description", ""),
                "retrieved_info": result.get("retrieved_info", "")
            })
        
            self._stats["successful_requests"] += 1
            return result
            
        except Exception as e:
            self._stats["failed_requests"] += 1
            raise Exception(f"Error in chain processing: {str(e)}")

    def get_statistics(self):
        base_stats = {
            "total_requests": self._stats["total_requests"],
            "successful_requests": self._stats["successful_requests"],
            "failed_requests": self._stats["failed_requests"]
        }
        
        if not self.response_history:
            return {
                **base_stats,
                "total_responses": 0,
                "unique_concerns": 0,
                "average_response_length": 0,
                "severity_distribution": {
                    "HIGH": 0,
                    "MEDIUM": 0,
                    "LOW": 0
                }
            }
            
        return {
            **base_stats,
            "total_responses": len(self.response_history),
            "unique_concerns": len(set(r["concern"] for r in self.response_history)),
            "average_response_length": sum(len(r["response"].split()) for r in self.response_history) / len(self.response_history),
            "severity_distribution": {
                "HIGH": sum(1 for r in self.response_history if "URGENT" in r["severity"]),
                "MEDIUM": sum(1 for r in self.response_history if "MODERATE" in r["severity"]),
                "LOW": sum(1 for r in self.response_history if "MILD" in r["severity"])
            }
        }

    def test_connection(self) -> Tuple[bool, str]:
        """Test the endpoint connection with a simple prompt"""
        try:
            test_prompt = "Say 'Hello' if you can hear me."
            response = self._endpoint.predict(
                instances=[{"prompt": test_prompt}],
                parameters={
                    "temperature": 0.1,
                    "max_output_tokens": 256,
                    "candidate_count": 1
                }
            )
            return True, response.predictions[0] if response.predictions else "No response"
        except Exception as e:
            return False, str(e)