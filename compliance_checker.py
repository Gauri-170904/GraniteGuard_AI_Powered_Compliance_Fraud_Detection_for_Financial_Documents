from ibm_watson_machine_learning.foundation_models import Model
import yaml
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ComplianceChecker:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize IBM Granite-powered compliance checker"""
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
            
            logger.info(f"Compliance checker initialized with IBM Granite model: {self.config['model']['model_id']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize compliance checker: {e}")
            raise

    def check_compliance(self, document_text: str) -> dict:
        """
        Analyze financial documents for compliance violations using IBM Granite
        
        Args:
            document_text: Text content of the document to analyze
            
        Returns:
            Dictionary containing compliance analysis results
        """
        try:
            # Improved prompt for IBM Granite model
            prompt = f"""
You are a financial compliance expert. Carefully review the following document for any compliance or regulatory violations (such as SOX, GDPR, CCPA, etc.).

If you find any issues, list each violation with:
- The regulation or law potentially violated
- The specific text or data from the document that is problematic
- A brief explanation of why it is a violation

If the document is fully compliant and you find no issues, reply exactly with: NO COMPLIANCE ISSUES FOUND.

Do NOT copy large sections of the document. Only summarize findings or state 'NO COMPLIANCE ISSUES FOUND'.

Document:
{document_text[:4000]}
"""
            response = self.model.generate_text(prompt)
            logger.info(f"Raw Granite model output: {repr(response)}")
            # If response is empty, very short, or just section headers, show a warning
            if not response or not response.strip():
                response = "No substantive analysis returned by the model. Try a simpler document or a different model."
            elif response.strip().upper() == "NO COMPLIANCE ISSUES FOUND":
                response = "✅ No compliance issues found in this document."
            return {
                "compliance_issues": [response],
                "model_used": self.config['model']['model_id'],
                "analysis_type": "IBM Granite Compliance Check",
                "timestamp": str(datetime.now())
            }
            
        except Exception as e:
            logger.error(f"Error during compliance analysis: {e}")
            return {
                "compliance_issues": [f"Error during analysis: {str(e)}"],
                "error": True,
                "model_used": self.config['model']['model_id']
            }