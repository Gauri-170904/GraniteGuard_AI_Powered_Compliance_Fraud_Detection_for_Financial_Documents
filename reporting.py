import pdfkit
from datetime import datetime
import os
import platform
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    @staticmethod
    def _get_wkhtmltopdf_path():
        """Determine the correct wkhtmltopdf executable path based on OS"""
        if platform.system() == 'Windows':
            # Common Windows installation paths
            paths = [
                r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
            return None  # Return None instead of raising error
        else:
            # Linux/Mac - assumes it's in PATH
            return 'wkhtmltopdf'

    @staticmethod
    def generate_pdf_report(document_name: str, 
                          compliance_results: dict, 
                          fraud_results: dict,
                          output_dir: str = "reports") -> str:
        """
        Generate a PDF report from analysis results
        
        Args:
            document_name: Name of the analyzed document
            compliance_results: Dictionary of compliance findings
            fraud_results: Dictionary of fraud indicators
            output_dir: Output directory path
            
        Returns:
            Path to the generated PDF file or HTML file if PDF generation fails
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate HTML content first
        html_content = ReportGenerator._generate_html_content(document_name, compliance_results, fraud_results)
        
        # Try to generate PDF, fall back to HTML if wkhtmltopdf not available
        wkhtmltopdf_path = ReportGenerator._get_wkhtmltopdf_path()
        
        if wkhtmltopdf_path:
            try:
                pdf_path = os.path.join(output_dir, f"Compliance_Report_{document_name}_{timestamp}.pdf")
                
                # Configure pdfkit
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                
                # PDF generation options
                options = {
                    'encoding': 'UTF-8',
                    'quiet': '',
                    'margin-top': '15mm',
                    'margin-right': '15mm',
                    'margin-bottom': '15mm',
                    'margin-left': '15mm',
                    'footer-center': '[page]/[topage]',
                    'footer-font-size': '8'
                }

                pdfkit.from_string(
                    html_content,
                    pdf_path,
                    configuration=config,
                    options=options
                )
                logger.info(f"PDF report generated successfully: {pdf_path}")
                return pdf_path
                
            except Exception as e:
                logger.warning(f"PDF generation failed, falling back to HTML: {str(e)}")
        
        # Fall back to HTML generation
        html_path = os.path.join(output_dir, f"Compliance_Report_{document_name}_{timestamp}.html")
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML report generated successfully: {html_path}")
            return html_path
        except Exception as e:
            logger.error(f"HTML generation failed: {str(e)}")
            raise RuntimeError(f"Report generation failed: {str(e)}")

    @staticmethod
    def _generate_html_content(document_name: str, compliance_results: dict, fraud_results: dict) -> str:
        """Generate HTML content for the report"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Compliance Report - {document_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                .header {{ text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                .finding {{ margin-bottom: 15px; padding: 10px; border-left: 4px solid #3498db; }}
                .severity-high {{ border-left-color: #e74c3c; background-color: #fadbd8; }}
                .severity-medium {{ border-left-color: #f39c12; background-color: #fdebd0; }}
                .severity-low {{ border-left-color: #2ecc71; background-color: #d5f5e3; }}
                .timestamp {{ color: #7f8c8d; font-size: 0.9em; text-align: right; }}
                .footer {{ font-size: 0.8em; text-align: center; color: #7f8c8d; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>GraniteGuard Compliance Report</h1>
                <p>Document: <strong>{document_name}</strong></p>
                <p class="timestamp">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <h2>Compliance Findings</h2>
            {ReportGenerator._format_findings(compliance_results.get('compliance_issues', []))}
            
            <h2>Fraud Indicators</h2>
            {ReportGenerator._format_findings(fraud_results.get('fraud_indicators', []))}
            
            <div class="footer">
                <p>Confidential - Generated by GraniteGuard AI | IBM TechXchange Hackathon</p>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def _format_findings(findings: list) -> str:
        """Format findings list into HTML"""
        if not findings:
            return "<p>No issues detected.</p>"
        
        formatted = []
        for finding in findings:
            # Determine severity class
            severity_class = "severity-medium"
            if isinstance(finding, str):
                if "high" in finding.lower():
                    severity_class = "severity-high"
                elif "low" in finding.lower():
                    severity_class = "severity-low"
            
            formatted.append(f"""
            <div class="finding {severity_class}">
                {finding.replace(chr(10), '<br>') if isinstance(finding, str) else str(finding)}
            </div>
            """)
        
        return "\n".join(formatted)