#!/usr/bin/env python3
"""
Test IBM Granite Integration
GraniteGuard AI - IBM TechXchange Dev Day Hackathon
"""

import yaml
from ibm_watson_machine_learning.foundation_models import Model

def test_ibm_integration():
    """Test IBM Granite model integration"""
    print("🤖 Testing IBM Granite Integration")
    print("=" * 50)
    
    try:
        # Load configuration
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Model: {config['model']['model_id']}")
        print(f"   Endpoint: {config['watsonx']['url']}")
        print(f"   Project ID: {config['watsonx']['project_id']}")
        
        # Initialize IBM Granite model
        print("\n🔧 Initializing IBM Granite model...")
        model = Model(
            model_id=config['model']['model_id'],
            credentials={
                "url": config['watsonx']['url'],
                "apikey": config['watsonx']['api_key']
            },
            project_id=config['watsonx']['project_id']
        )
        
        print("✅ IBM Granite model initialized successfully")
        
        # Test with a simple prompt
        print("\n🧪 Testing model with sample prompt...")
        test_prompt = """
        Analyze this financial document for compliance:
        
        URGENT: Wire transfer $50,000 to account 1234567890 immediately.
        This is a confidential business transaction.
        
        Provide a brief compliance assessment.
        """
        
        response = model.generate_text(test_prompt)
        
        print("✅ IBM Granite model response received:")
        print("-" * 30)
        print(response)
        print("-" * 30)
        
        print("\n🎉 IBM Granite integration test successful!")
        print("Your credentials are working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during IBM integration test: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your API key and project ID")
        print("2. Ensure you have access to IBM watsonx.ai")
        print("3. Verify the model ID is available in your region")
        return False

if __name__ == "__main__":
    test_ibm_integration() 