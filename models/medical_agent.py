from enum import Enum
from typing import List, Dict, Any
from google.cloud import aiplatform

from models.chain_models import MedicalChain
class MedicalAction(Enum):
    BASIC_RESPONSE = "basic_response"
    EMERGENCY_RESPONSE = "emergency_response"
    SPECIALIST_REFERRAL = "specialist_referral"
    FOLLOWUP_SCHEDULING = "followup_scheduling"
    FEVER_RESPONSE = "fever_response"  # New action

def analyze_input(self, text: str) -> List[MedicalAction]:
    """Determine which actions to take based on input text."""
    actions = []
    text_lower = text.lower()
    
    # Emergency keywords
    if any(word in text_lower for word in ["emergency", "severe", "chest pain", "breathing"]):
        actions.append(MedicalAction.EMERGENCY_RESPONSE)
    
    # Fever/headache keywords
    if any(word in text_lower for word in ["fever", "headache", "temperature"]):
        actions.append(MedicalAction.FEVER_RESPONSE)
    
    # Specialist keywords
    if any(word in text_lower for word in ["chronic", "specialist", "recurring"]):
        actions.append(MedicalAction.SPECIALIST_REFERRAL)
    
    # Always include basic response if no other actions
    if not actions:
        actions.append(MedicalAction.BASIC_RESPONSE)
        
    return actions

def execute_actions(self, actions: List[MedicalAction], inputs: Dict[str, str]) -> Dict[str, Any]:
    """Execute the determined actions in sequence."""
    result = self.medical_chain.process(inputs)
    
    for action in actions:
        if action == MedicalAction.EMERGENCY_RESPONSE:
            result["FormattedOutput"] = "🚨 EMERGENCY ALERT:\n" + result["FormattedOutput"]
            result["FormattedOutput"] += "\n\nIMMEDIATE ACTION REQUIRED: Please call emergency services or visit the nearest emergency room."
            
        elif action == MedicalAction.SPECIALIST_REFERRAL:
            result["FormattedOutput"] += "\n\n👨‍⚕️ SPECIALIST REFERRAL:\nBased on your symptoms, consulting with a specialist is recommended."
            
        elif action == MedicalAction.FEVER_RESPONSE:
            result["FormattedOutput"] += "\n\n🌡️ FEVER MONITORING:\n"
            result["FormattedOutput"] += "• Monitor your temperature every 4-6 hours\n"
            result["FormattedOutput"] += "• Take over-the-counter fever reducers as directed\n"
            result["FormattedOutput"] += "• Stay hydrated and rest\n"
            result["FormattedOutput"] += "• Seek immediate medical attention if temperature exceeds 103°F (39.4°C)"
    
    return result