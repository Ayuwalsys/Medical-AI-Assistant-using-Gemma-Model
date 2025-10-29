
# Medical AI Assistant
An intelligent medical consultation system powered by Gemma 7B LLM, providing preliminary health guidance and severity assessment through an interactive interface.


🛠️ Tech Stack
Base Model: Gemma 7B
Fine-tuning: LoRA (rank 32)
Framework: LangChain
Frontend: Streamlit
Deployment: Google Cloud Vertex AI


Implementation Details
Model Architecture:
# LoRA Configuration
lora_config = LoraConfig(
    r=32,                     # Rank for adaptation
    target_modules=["q", "v"], # Attention layers
    lora_alpha=16,            
    lora_dropout=0.1,         
    task_type="CAUSAL_LM"     
)


Key Features
Medical context enhancement
Severity assessment
Real-time response generation
Interactive consultation interface
Statistical tracking


Dataset
250,000+ medical dialogues
Patient-Doctor conversations
Structured format:
Patient queries
Medical context
Professional responses


Setup & Installation

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export VERTEX_AI_ENDPOINT="your-endpoint"

# Run application
streamlit run app.py


## Usage
1. Enter medical concern in the text area
2. Click "Get Medical Advice"
3. Receive structured medical response with:
   - Severity assessment
   - Medical context
   - Professional guidance

## Important Notes
- For informational purposes only
- Not a replacement for professional medical advice
- Consult healthcare providers for medical decisions
- Emergency cases should seek immediate medical attention

## 🔄 Project Structure


![image](https://github.com/user-attachments/assets/3043fa20-e9aa-4925-b2ed-309e3e4e93d6)



## Contributing
Contributions welcome! Please read our contributing guidelines before submitting PRs.

## License
This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments
- Medical dataset providers
- Google Cloud Platform
- Open-source community

## Contact
- Project Link: [https://github.com/ayuwal12/medical-ai-assistant](https://github.com/ayuwal12/medical-ai-assistant)
- Waliu Ayuba - [@twitter profile link](https://twitter.com/ayuwal12)

## Future Improvements
- Multi-modal capabilities
- Enhanced medical knowledge base
- Automated testing implementation
- Advanced caching mechanisms

---
Developed with focus on medical accuracy and user safety
