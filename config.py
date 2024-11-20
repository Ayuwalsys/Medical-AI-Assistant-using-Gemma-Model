from dataclasses import dataclass
from typing import List
from google.cloud import aiplatform
from google.auth import default
import subprocess
import os

@dataclass
class ModelConfig:
    max_tokens: int = 1024
    temperature: float = 0.3
    top_p: float = 0.9
    top_k: int = 40
    raw_response: bool = True
    stop_sequences: List[str] = None

    def __post_init__(self):
        self.stop_sequences = ["\n\n", "Human:", "Assistant:"]

class Config:
    PROJECT_ID = "angelic-goods-438016-f6"
    LOCATION = "us-central1"
    ENDPOINT_ID = "5936642609874206720"
    SERVICE_ACCOUNT = "gemma-vertexai@angelic-goods-438016-f6.iam.gserviceaccount.com"

    @classmethod
    def initialize_google_auth(cls):
        try:
            # Try to get default credentials
            credentials, project = default()
            
            # If no credentials, attempt to authenticate
            if not credentials:
                subprocess.run(["gcloud", "auth", "application-default", "login"], check=True)
                subprocess.run(["gcloud", "config", "set", "project", cls.PROJECT_ID], check=True)
                subprocess.run(["gcloud", "auth", "application-default", "set-quota-project", cls.PROJECT_ID], check=True)
                credentials, project = default()  # Get credentials again after authentication
                
            # Initialize Vertex AI with the project configuration and credentials
            aiplatform.init(
                project=cls.PROJECT_ID,
                location=cls.LOCATION,
                credentials=credentials
            )
            
            # Get the endpoint with full path and credentials
            endpoint_path = f"projects/{cls.PROJECT_ID}/locations/{cls.LOCATION}/endpoints/{cls.ENDPOINT_ID}"
            endpoint = aiplatform.Endpoint(
                endpoint_name=endpoint_path,
                credentials=credentials
            )
            return endpoint
            
        except Exception as e:
            print(f"Error initializing Google Cloud authentication: {str(e)}")
            raise

    @classmethod
    def get_endpoint(cls):
        """Get or create authenticated endpoint connection"""
        try:
            return cls.initialize_google_auth()
        except Exception as e:
            print(f"Failed to connect to endpoint: {str(e)}")
            raise