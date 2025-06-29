#!/usr/bin/env python3
"""
GraniteGuard AI - Main Flask Application
IBM TechXchange Dev Day Hackathon Project

This application provides a web interface for AI-powered compliance checking
and fraud detection using IBM Granite models on watsonx.ai platform.
"""

import os
import yaml
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Import our custom modules
from src.document_processing import DocumentProcessor
from src.compliance_checker import ComplianceChecker
from src.fraud_detector import FraudDetector
from src.reporting import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'graniteguard-hackathon-2025')

# Load configuration
def load_config():
    """Load configuration from YAML file"""
    try:
        with open('config/config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error("Configuration file not found. Please create config/config.yaml")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration: {e}")
        return None

config = load_config()

if config:
    # Configure Flask app from config
    app.config['MAX_CONTENT_LENGTH'] = config['app']['max_file_size'] * 1024 * 1024  # Convert MB to bytes
    app.config['UPLOAD_FOLDER'] = config['app']['upload_folder']
    app.config['REPORT_FOLDER'] = config['app']['report_folder']
    
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

# Initialize AI components
document_processor = DocumentProcessor()
compliance_checker = None
fraud_detector = None

def initialize_ai_components():
    """Initialize AI components with IBM watsonx.ai credentials"""
    global compliance_checker, fraud_detector
    
    if not config:
        logger.error("Configuration not loaded. Cannot initialize AI components.")
        return False
    
    try:
        # Check if credentials are configured
        if (config['watsonx']['api_key'] == 'your_api_key_here' or 
            config['watsonx']['project_id'] == 'your_project_id_here'):
            logger.warning("IBM watsonx.ai credentials not configured. Please update config/config.yaml")
            return False
        
        compliance_checker = ComplianceChecker()
        fraud_detector = FraudDetector()
        logger.info("AI components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize AI components: {e}")
        return False

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    if not config:
        return False
    
    allowed_extensions = config['app']['allowed_extensions']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in [ext.replace('.', '') for ext in allowed_extensions]

@app.route('/')
def index():
    """Main page with file upload interface"""
    ai_ready = compliance_checker is not None and fraud_detector is not None
    
    return render_template('index.html', 
                         ai_ready=ai_ready,
                         config=config,
                         allowed_extensions=config['app']['allowed_extensions'] if config else [])

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    if not allowed_file(file.filename):
        flash('File type not allowed. Please upload PDF, DOCX, XLSX, XLS, or CSV files.', 'error')
        return redirect(request.url)
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {safe_filename}")
        
        # Check if AI components are ready
        if not compliance_checker or not fraud_detector:
            flash('AI components not initialized. Please check your IBM watsonx.ai configuration.', 'error')
            return redirect(url_for('index'))
        
        # Process document
        try:
            document_text = document_processor.extract_text(filepath)
            logger.info(f"Document text extracted: {len(document_text)} characters")
            
            # Perform AI analysis
            compliance_results = compliance_checker.check_compliance(document_text)
            fraud_results = fraud_detector.detect_fraud_indicators(document_text)
            
            logger.info("AI analysis completed successfully")
            
            # Generate PDF report
            try:
                report_path = ReportGenerator.generate_pdf_report(
                    document_name=filename,
                    compliance_results=compliance_results,
                    fraud_results=fraud_results,
                    output_dir=app.config['REPORT_FOLDER']
                )
                
                # Clean up uploaded file
                os.remove(filepath)
                
                flash('Document analyzed successfully!', 'success')
                return jsonify({
                    'success': True,
                    'message': 'Analysis completed successfully',
                    'report_path': os.path.basename(report_path),
                    'report_type': 'PDF' if report_path.endswith('.pdf') else 'HTML',
                    'compliance_results': compliance_results,
                    'fraud_results': fraud_results
                })
                
            except Exception as report_error:
                logger.error(f"Error during report generation: {report_error}")
                # Still return analysis results even if report generation fails
                flash('Analysis completed but report generation failed. Results displayed below.', 'warning')
                return jsonify({
                    'success': True,
                    'message': 'Analysis completed successfully (report generation failed)',
                    'report_error': str(report_error),
                    'compliance_results': compliance_results,
                    'fraud_results': fraud_results
                })
            
        except Exception as e:
            logger.error(f"Error during document analysis: {e}")
            flash(f'Error during analysis: {str(e)}', 'error')
            return jsonify({'success': False, 'error': str(e)})
            
    except RequestEntityTooLarge:
        flash('File too large. Please upload a smaller file.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error handling file upload: {e}")
        flash(f'Error uploading file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_report(filename):
    """Download generated PDF report"""
    try:
        return send_file(
            os.path.join(app.config['REPORT_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except FileNotFoundError:
        flash('Report file not found', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_ready': compliance_checker is not None and fraud_detector is not None,
        'config_loaded': config is not None
    })

@app.route('/config-status')
def config_status():
    """Check configuration status"""
    if not config:
        return jsonify({
            'status': 'error',
            'message': 'Configuration file not found or invalid'
        })
    
    # Check if credentials are configured
    credentials_configured = (
        config['watsonx']['api_key'] != 'your_api_key_here' and
        config['watsonx']['project_id'] != 'your_project_id_here'
    )
    
    return jsonify({
        'status': 'ok' if credentials_configured else 'warning',
        'credentials_configured': credentials_configured,
        'model_id': config['model']['model_id'],
        'endpoint_url': config['watsonx']['url']
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File too large. Please upload a smaller file.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {e}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize AI components
    ai_ready = initialize_ai_components()
    
    if not ai_ready:
        logger.warning("AI components not initialized. The application will run but AI features will be disabled.")
    
    # Start Flask application
    host = config['app']['host'] if config else '0.0.0.0'
    port = config['app']['port'] if config else 5000
    debug = config['app']['debug'] if config else True
    
    logger.info(f"Starting GraniteGuard AI application on {host}:{port}")
    logger.info("Access the application at: http://localhost:5000")
    
    app.run(host=host, port=port, debug=debug)
