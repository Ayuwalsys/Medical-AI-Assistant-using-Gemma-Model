import json
from typing import List, Dict, Any

class MedicalDocumentLoader:
    @staticmethod
    def load_medical_guidelines() -> List[Dict[str, Any]]:
        # In production, this could load from a database or file system
        return [
            {
                "content": """
                Headache Assessment Guidelines:
                1. Evaluate pain characteristics
                2. Check for associated symptoms
                3. Review medical history
                4. Consider red flags
                """,
                "metadata": {
                    "type": "guideline",
                    "category": "headache",
                    "source": "medical_guidelines"
                }
            },
            # Add more medical documents
        ]

    @staticmethod
    def load_medical_research() -> List[Dict[str, Any]]:
        # Could load recent medical research papers or summaries
        return [
            {
                "content": """
                Recent research on migraine treatment shows...
                """,
                "metadata": {
                    "type": "research",
                    "category": "headache",
                    "source": "medical_journal"
                }
            },
            # Add more research documents
        ]