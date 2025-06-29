#!/usr/bin/env python3
"""
GraniteGuard AI - Demo Script
IBM TechXchange Dev Day Hackathon Project

This script provides a demo mode for testing the application functionality
without requiring IBM watsonx.ai credentials.
"""

import os
import yaml
import json
from datetime import datetime
from src.document_processing import DocumentProcessor
from src.reporting import ReportGenerator

class DemoComplianceChecker:
    """Demo compliance checker that simulates IBM Granite model responses"""
    
    def check_compliance(self, document_text: str) -> dict:
        """Simulate compliance analysis with realistic responses"""
        
        # Sample compliance issues based on common patterns
        compliance_issues = []
        
        # Check for common compliance keywords
        text_lower = document_text.lower()
        
        if 'confidential' in text_lower and 'public' in text_lower:
            compliance_issues.append(
                "⚠️ MEDIUM RISK: Potential disclosure of confidential information in public context. "
                "Review document for proper classification and access controls."
            )
        
        if 'financial' in text_lower and 'unauthorized' in text_lower:
            compliance_issues.append(
                "🚨 HIGH RISK: Unauthorized financial transactions detected. "
                "Immediate review required for SOX compliance and fraud prevention."
            )
        
        if 'personal data' in text_lower or 'pii' in text_lower:
            compliance_issues.append(
                "🔒 HIGH RISK: Personal Identifiable Information (PII) found. "
                "Ensure GDPR/CCPA compliance and proper data handling procedures."
            )
        
        if 'contract' in text_lower and 'amendment' in text_lower:
            compliance_issues.append(
                "📋 MEDIUM RISK: Contract amendment detected. "
                "Verify proper approval workflow and legal review processes."
            )
        
        if not compliance_issues:
            compliance_issues.append(
                "✅ LOW RISK: No significant compliance violations detected. "
                "Document appears to follow standard business practices."
            )
        
        return {"compliance_issues": compliance_issues}

class DemoFraudDetector:
    """Demo fraud detector that simulates IBM Granite model responses"""
    
    def detect_fraud_indicators(self, document_text: str) -> dict:
        """Simulate fraud detection with realistic responses"""
        
        # Sample fraud indicators based on common patterns
        fraud_indicators = []
        
        # Check for common fraud keywords
        text_lower = document_text.lower()
        
        if 'urgent' in text_lower and 'payment' in text_lower:
            fraud_indicators.append(
                "🚨 HIGH RISK: Urgent payment request detected. "
                "Verify authenticity and follow proper verification procedures."
            )
        
        if 'wire transfer' in text_lower and 'immediate' in text_lower:
            fraud_indicators.append(
                "⚠️ MEDIUM RISK: Immediate wire transfer request. "
                "Review for potential business email compromise (BEC) fraud."
            )
        
        if 'account number' in text_lower and 'routing' in text_lower:
            fraud_indicators.append(
                "🔍 MEDIUM RISK: Banking information in document. "
                "Ensure proper security controls and access restrictions."
            )
        
        if 'invoice' in text_lower and 'duplicate' in text_lower:
            fraud_indicators.append(
                "📊 LOW RISK: Potential duplicate invoice detected. "
                "Review for billing accuracy and prevent overpayment."
            )
        
        if not fraud_indicators:
            fraud_indicators.append(
                "✅ LOW RISK: No significant fraud indicators detected. "
                "Document appears to follow standard business practices."
            )
        
        return {"fraud_indicators": fraud_indicators}

def create_sample_document():
    """Create a sample document for testing"""
    sample_text = """
    CONFIDENTIAL BUSINESS DOCUMENT
    
    Financial Report - Q4 2024
    
    This document contains sensitive financial information including:
    - Revenue projections
    - Cost analysis
    - Strategic planning data
    
    URGENT: Payment Processing
    
    We require immediate wire transfer to account number 1234567890
    Routing number: 987654321
    Amount: $50,000
    
    This is a confidential business transaction that requires urgent attention.
    Please process this payment immediately to avoid delays.
    
    Personal Data Notice:
    This document may contain personal identifiable information (PII)
    of employees and customers. Handle with appropriate care.
    
    Contract Amendment:
    The existing service agreement is hereby amended to include
    additional terms and conditions as outlined below.
    
    This is a duplicate invoice for services rendered.
    Please review and process accordingly.
    
    End of Document
    """
    
    # Create sample file
    os.makedirs('uploads', exist_ok=True)
    sample_file = 'uploads/sample_document.txt'
    
    with open(sample_file, 'w') as f:
        f.write(sample_text)
    
    return sample_file

def run_demo():
    """Run the demo analysis"""
    print("🤖 GraniteGuard AI - Demo Mode")
    print("=" * 50)
    print("IBM TechXchange Dev Day Hackathon 2025")
    print()
    
    # Create sample document
    print("📄 Creating sample document...")
    sample_file = create_sample_document()
    
    # Initialize components
    print("🔧 Initializing demo components...")
    processor = DocumentProcessor()
    compliance_checker = DemoComplianceChecker()
    fraud_detector = DemoFraudDetector()
    
    # Process document
    print("📖 Extracting text from document...")
    try:
        document_text = processor.extract_text(sample_file)
        print(f"✅ Extracted {len(document_text)} characters")
    except Exception as e:
        # Fallback to reading text file
        with open(sample_file, 'r') as f:
            document_text = f.read()
        print(f"✅ Read {len(document_text)} characters from text file")
    
    # Perform analysis
    print("\n🔍 Running compliance analysis...")
    compliance_results = compliance_checker.check_compliance(document_text)
    
    print("🚨 Running fraud detection...")
    fraud_results = fraud_detector.detect_fraud_indicators(document_text)
    
    # Generate report
    print("\n📊 Generating PDF report...")
    try:
        report_path = ReportGenerator.generate_pdf_report(
            document_name="Sample_Document_Demo",
            compliance_results=compliance_results,
            fraud_results=fraud_results,
            output_dir="reports"
        )
        print(f"✅ Report generated: {report_path}")
    except Exception as e:
        print(f"⚠️ PDF generation failed: {e}")
        print("Displaying results in console instead...")
    
    # Display results
    print("\n" + "=" * 50)
    print("📋 ANALYSIS RESULTS")
    print("=" * 50)
    
    print("\n🔍 COMPLIANCE FINDINGS:")
    for issue in compliance_results.get('compliance_issues', []):
        print(f"  • {issue}")
    
    print("\n🚨 FRAUD INDICATORS:")
    for indicator in fraud_results.get('fraud_indicators', []):
        print(f"  • {indicator}")
    
    print("\n" + "=" * 50)
    print("🎯 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("\nThis demo shows how GraniteGuard AI would analyze documents")
    print("using IBM Granite models on watsonx.ai platform.")
    print("\nTo use the full application:")
    print("1. Get IBM Cloud account: https://www.ibm.com/account/reg/us-en/signup?formid=urx-53809")
    print("2. Configure config/config.yaml with your credentials")
    print("3. Run: python app.py")
    print("4. Access: http://localhost:5000")
    
    # Cleanup
    try:
        os.remove(sample_file)
        print(f"\n🧹 Cleaned up sample file: {sample_file}")
    except:
        pass

if __name__ == "__main__":
    run_demo() 