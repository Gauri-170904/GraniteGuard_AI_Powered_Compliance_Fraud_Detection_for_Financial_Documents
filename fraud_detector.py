from ibm_watson_machine_learning.foundation_models import Model
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FraudDetector:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize IBM Granite-powered fraud detector"""
        try:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
            
            # Initialize IBM Granite model
            self.model = Model(
                model_id=self.config['model']['model_id'],
                credentials={
                    "url": self.config['watsonx']['url'],
                    "apikey": self.config['watsonx']['api_key']
                },
                project_id=self.config['watsonx']['project_id']
            )
            
            logger.info(f"Fraud detector initialized with IBM Granite model: {self.config['model']['model_id']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize fraud detector: {e}")
            raise

    def detect_fraud_indicators(self, document_text: str) -> dict:
        """
        Detect fraud indicators in financial documents using IBM Granite
        
        Args:
            document_text: Text content of the document to analyze
            
        Returns:
            Dictionary containing fraud detection results
        """
        try:
            # Simple, direct prompt for IBM Granite model
            prompt = f"Analyze the following financial document for signs of fraud or suspicious activity. Summarize any findings.\n\nDocument:\n{document_text[:4000]}"
            response = self.model.generate_text(prompt)
            logger.info(f"Raw Granite model output: {repr(response)}")
            # If response is empty, very short, or just section headers, show a warning
            if not response or not response.strip() or response.strip().lower() in ["no fraud indicators detected.", "no issues detected."] or len(response.strip()) < 40:
                response = "No substantive analysis returned by the model. Try a simpler document or a different model."
            return {
                "fraud_indicators": [response],
                "model_used": self.config['model']['model_id'],
                "analysis_type": "IBM Granite Fraud Detection",
                "timestamp": str(datetime.now())
            }
            
        except Exception as e:
            logger.error(f"Error during fraud detection: {e}")
            return {
                "fraud_indicators": [f"Error during analysis: {str(e)}"],
                "error": True,
                "model_used": self.config['model']['model_id']
            }