from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MedicalKnowledgeBase:
    def __init__(self):
        # Sample medical knowledge base - in production, this could be loaded from a database
        self.knowledge_base = {
            "headache": """
                Common types of headaches include tension headaches, migraines, and cluster headaches.
                Key considerations:
                - Duration and frequency of headaches
                - Location and type of pain
                - Associated symptoms
                - Triggers and relieving factors
                Treatment approaches may include:
                - Over-the-counter pain relievers
                - Stress management
                - Proper hydration
                - Regular sleep schedule
            """,
            "fever": """
                Fever is a temporary increase in body temperature, often due to infection.
                Important aspects:
                - Normal body temperature is 98.6°F (37°C)
                - Fever threshold is generally considered 100.4°F (38°C)
                - Can be a sign of infection or inflammation
                Management includes:
                - Rest and hydration
                - Temperature monitoring
                - Appropriate use of fever reducers
                - Watching for warning signs
            """,
            "chest_pain": """
                Chest pain requires immediate medical attention as it may indicate serious conditions.
                Potential causes:
                - Heart attack
                - Angina
                - Pulmonary embolism
                - Pneumonia
                Warning signs:
                - Pressure or squeezing sensation
                - Pain radiating to arm or jaw
                - Shortness of breath
                - Sweating
                IMMEDIATE MEDICAL ATTENTION REQUIRED
            """,
            # Add more medical knowledge entries
        }
        
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.vectors = self.vectorizer.fit_transform(list(self.knowledge_base.values()))
    
    def retrieve_information(self, query: str) -> str:  # Changed from retrieve_relevant_information
        """
        Retrieve information based on the query
        """
        relevant_info = self.retrieve_relevant_information(query)
        if relevant_info:
            return "\n".join(relevant_info)
        return "No relevant information found."

    def retrieve_relevant_information(self, query: str, top_k: int = 3) -> List[str]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectors).flatten()
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_info = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Similarity threshold
                relevant_info.append(list(self.knowledge_base.values())[idx])
        
        return relevant_info
