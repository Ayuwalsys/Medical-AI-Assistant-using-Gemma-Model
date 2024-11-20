from google.cloud import aiplatform
from google.oauth2 import service_account
from config import Config
import logging
import os
from google.auth import default


def initialize_vertex_ai():
    """Initialize Vertex AI connection"""
    try:
        # Get credentials
        credentials, project = default()
        
        # Initialize Vertex AI
        aiplatform.init(
            project="angelic-goods-438016-f6",  # Your project ID
            location="us-central1"              # Your location
        )
        
        # Create endpoint
        endpoint = aiplatform.Endpoint(
            endpoint_name="projects/angelic-goods-438016-f6/locations/us-central1/endpoints/5936642609874206720"
        )
        
        # Test connection
        test_response = endpoint.predict(
            instances=[{"prompt": "Test connection"}],
            parameters={
                "temperature": 0.1,
                "max_output_tokens": 256,
                "candidate_count": 1
            }
        )
        
        if test_response:
            logging.info("Successfully connected to Vertex AI")
            return endpoint
            
    except Exception as e:
        logging.error(f"Failed to initialize Vertex AI: {str(e)}")
        raise

