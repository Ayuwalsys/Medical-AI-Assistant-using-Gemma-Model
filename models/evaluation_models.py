from typing import Dict, Any, List
from dataclasses import dataclass
from google.cloud import aiplatform

@dataclass
class EvaluationCriterion:
    name: str
    description: str
    weight: float = 1.0

class ResponseEvaluator:
    def __init__(self):
        self.criteria = {
            "medical_accuracy": EvaluationCriterion(
                name="Medical Accuracy",
                description="Evaluates adherence to medical guidelines, factual correctness, and appropriate medical terminology",
                weight=1.5
            ),
            "completeness": EvaluationCriterion(
                name="Completeness",
                description="Assesses if all required sections (Acknowledgment, Assessment, Recommendations, Warnings, Follow-up) are present and adequately addressed",
                weight=1.0
            ),
            "empathy": EvaluationCriterion(
                name="Empathy",
                description="Measures the level of empathy, compassion, and appropriate bedside manner in the response",
                weight=1.0
            ),
            "clarity": EvaluationCriterion(
                name="Clarity",
                description="Evaluates clarity, readability, and understandability for a general audience",
                weight=1.0
            ),
            "safety": EvaluationCriterion(
                name="Safety",
                description="Assesses the inclusion and appropriateness of safety warnings, precautions, and emergency guidance",
                weight=1.5
            )
        }

    def generate_evaluation_prompt(self, patient_concern: str, response: str) -> str:
        criteria_text = "\n".join([
            f"{criterion.name} ({criterion.weight}x weight):\n"
            f"- {criterion.description}\n"
            for criterion in self.criteria.values()
        ])

        return f"""You are an expert medical response evaluator. Evaluate the following medical AI response based on specific criteria.

PATIENT CONCERN:
{patient_concern}

AI RESPONSE:
{response}

EVALUATION CRITERIA:
{criteria_text}

For each criterion, provide:
1. A score from 1-10 (1 being poorest, 10 being excellent)
2. A brief justification for the score
3. Specific suggestions for improvement if score is below 8

Format your response exactly as follows for each criterion:
[CRITERION_NAME]
Score: [1-10]
Justification: [Your justification]
Improvements: [Suggestions if needed, or "None needed" if score >= 8]
"""

    def parse_evaluation_response(self, eval_text: str) -> Dict[str, Any]:
        results = {}
        current_criterion = None
        current_data = {}

        for line in eval_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check if line is a criterion header
            if line.upper() in [c.name.upper() for c in self.criteria.values()]:
                if current_criterion:
                    results[current_criterion.lower().replace(' ', '_')] = current_data
                current_criterion = line
                current_data = {}
            elif line.startswith('Score:'):
                current_data['score'] = int(line.split(':')[1].strip())
            elif line.startswith('Justification:'):
                current_data['justification'] = line.split(':')[1].strip()
            elif line.startswith('Improvements:'):
                current_data['improvements'] = line.split(':')[1].strip()

        # Add the last criterion
        if current_criterion:
            results[current_criterion.lower().replace(' ', '_')] = current_data

        return results

    def calculate_weighted_score(self, evaluation_results: Dict[str, Any]) -> float:
        total_weight = sum(criterion.weight for criterion in self.criteria.values())
        weighted_sum = 0

        for criterion_key, criterion_obj in self.criteria.items():
            if criterion_key in evaluation_results:
                score = evaluation_results[criterion_key].get('score', 0)
                weighted_sum += score * criterion_obj.weight

        return round(weighted_sum / total_weight, 2)

    def evaluate(self, endpoint: aiplatform.Endpoint, patient_concern: str, response: str) -> Dict[str, Any]:
        try:
            # Generate the evaluation prompt
            eval_prompt = self.generate_evaluation_prompt(patient_concern, response)

            # Call the LLM endpoint
            instance = {
                "prompt": eval_prompt,
                "max_tokens": 1000,
                "temperature": 0.2,
            }
            
            eval_response = endpoint.predict([instance])
            eval_text = eval_response.predictions[0]

            # Parse the evaluation results
            evaluation_results = self.parse_evaluation_response(eval_text)
            
            # Calculate the weighted score
            weighted_score = self.calculate_weighted_score(evaluation_results)

            return {
                "criteria_scores": evaluation_results,
                "weighted_score": weighted_score,
                "raw_evaluation": eval_text
            }

        except Exception as e:
            return {
                "error": f"Evaluation failed: {str(e)}",
                "criteria_scores": {},
                "weighted_score": 0,
                "raw_evaluation": ""
            }