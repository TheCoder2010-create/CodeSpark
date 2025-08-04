import os
import json
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import secrets
from app import app, db
from models import CodeAnalysis, AnalysisMetrics, UserSettings
from ai_service import create_ai_provider, get_available_providers, validate_api_key, detect_language

ALLOWED_EXTENSIONS = {
    'py', 'js', 'ts', 'java', 'cpp', 'c', 'cs', 'php', 'rb', 'go', 'rs', 
    'swift', 'kt', 'scala', 'sh', 'sql', 'html', 'css', 'json', 'xml', 
    'yaml', 'yml', 'txt', 'md'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_or_create_session_id():
    """Get or create session ID for user settings"""
    if 'session_id' not in session:
        session['session_id'] = secrets.token_urlsafe(32)
    return session['session_id']

def get_user_settings():
    """Get user settings from database"""
    session_id = get_or_create_session_id()
    settings = UserSettings.query.filter_by(session_id=session_id).first()
    if not settings:
        settings = UserSettings(
            session_id=session_id,
            ai_provider='openai',
            ai_model='gpt-4o'
        )
        db.session.add(settings)
        db.session.commit()
    return settings

def encrypt_api_keys(api_keys_dict):
    """Encrypt API keys for storage"""
    if not api_keys_dict:
        return None
    key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
    f = Fernet(key)
    return f.encrypt(json.dumps(api_keys_dict).encode()).decode()

def decrypt_api_keys(encrypted_keys):
    """Decrypt API keys from storage"""
    if not encrypted_keys:
        return {}
    try:
        key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        f = Fernet(key)
        return json.loads(f.decrypt(encrypted_keys.encode()).decode())
    except:
        return {}

@app.route('/')
def index():
    """Home page with recent analyses."""
    recent_analyses = CodeAnalysis.query.order_by(CodeAnalysis.created_at.desc()).limit(5).all()
    return render_template('index.html', recent_analyses=recent_analyses)

@app.route('/upload')
def upload_page():
    """Code upload page."""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and initiate analysis."""
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to prevent filename conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            unique_filename = timestamp + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            file.save(file_path)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code_content = f.read()
            
            # Detect language
            language = detect_language(filename, code_content)
            
            # Create analysis record
            analysis = CodeAnalysis(
                filename=unique_filename,
                original_filename=filename,
                file_path=file_path,
                language=language,
                file_size=len(code_content)
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            flash('File uploaded successfully! Starting analysis...', 'success')
            return redirect(url_for('analyze_file', analysis_id=analysis.id))
        else:
            flash('Invalid file type. Please upload a supported code file.', 'error')
            return redirect(request.url)
            
    except Exception as e:
        flash(f'Error uploading file: {str(e)}', 'error')
        return redirect(url_for('upload_page'))

@app.route('/analyze/<int:analysis_id>')
def analyze_file(analysis_id):
    """Perform AI analysis on uploaded file."""
    try:
        analysis = CodeAnalysis.query.get_or_404(analysis_id)
        
        # Get user settings
        settings = get_user_settings()
        api_keys = decrypt_api_keys(settings.api_keys)
        
        # Check if user has configured API key for selected provider
        required_key = get_available_providers()[settings.ai_provider]['api_key_env']
        api_key = api_keys.get(required_key) or os.environ.get(required_key)
        
        if not api_key:
            flash(f'Please configure your {settings.ai_provider.upper()} API key in settings.', 'error')
            return redirect(url_for('settings_page'))
        
        # Read file content
        with open(analysis.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code_content = f.read()
        
        # Create AI provider instance
        ai_provider = create_ai_provider(settings.ai_provider, api_key, settings.ai_model)
        
        # Perform AI analysis
        quality_analysis = ai_provider.analyze_code_quality(code_content, analysis.language)
        test_suggestions = ai_provider.generate_test_cases(code_content, analysis.language)
        code_suggestions = ai_provider.get_code_suggestions(code_content, analysis.language)
        
        # Store results
        analysis.analysis_result = json.dumps({
            'quality_analysis': quality_analysis,
            'code_suggestions': code_suggestions
        })
        analysis.test_suggestions = json.dumps(test_suggestions)
        analysis.quality_score = quality_analysis.get('quality_score', 0)
        analysis.issues_count = len(quality_analysis.get('issues', []))
        analysis.suggestions_count = len(code_suggestions.get('refactoring_suggestions', []))
        analysis.ai_model = f"{settings.ai_provider}:{settings.ai_model}"
        
        # Store metrics
        metrics = quality_analysis.get('metrics', {})
        for metric_name, metric_value in metrics.items():
            metric = AnalysisMetrics(
                analysis_id=analysis.id,
                metric_name=metric_name,
                metric_value=str(metric_value),
                metric_type='quality'
            )
            db.session.add(metric)
        
        db.session.commit()
        
        flash('Analysis completed successfully!', 'success')
        return redirect(url_for('view_analysis', analysis_id=analysis.id))
        
    except Exception as e:
        flash(f'Error during analysis: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/analysis/<int:analysis_id>')
def view_analysis(analysis_id):
    """View detailed analysis results."""
    analysis = CodeAnalysis.query.get_or_404(analysis_id)
    
    # Read file content for display
    try:
        with open(analysis.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code_content = f.read()
    except:
        code_content = "File content could not be loaded."
    
    # Parse JSON results
    analysis_result = {}
    test_suggestions = {}
    
    if analysis.analysis_result:
        try:
            analysis_result = json.loads(analysis.analysis_result)
        except:
            pass
    
    if analysis.test_suggestions:
        try:
            test_suggestions = json.loads(analysis.test_suggestions)
        except:
            pass
    
    return render_template('analysis.html', 
                         analysis=analysis, 
                         code_content=code_content,
                         analysis_result=analysis_result,
                         test_suggestions=test_suggestions)

@app.route('/dashboard')
def dashboard():
    """Dashboard with overview of all analyses."""
    analyses = CodeAnalysis.query.order_by(CodeAnalysis.created_at.desc()).all()
    
    # Calculate summary statistics
    total_analyses = len(analyses)
    avg_quality_score = sum(a.quality_score or 0 for a in analyses) / max(total_analyses, 1)
    total_issues = sum(a.issues_count or 0 for a in analyses)
    
    # Language distribution
    language_stats = {}
    for analysis in analyses:
        lang = analysis.language or 'unknown'
        language_stats[lang] = language_stats.get(lang, 0) + 1
    
    return render_template('dashboard.html', 
                         analyses=analyses,
                         total_analyses=total_analyses,
                         avg_quality_score=round(avg_quality_score, 1),
                         total_issues=total_issues,
                         language_stats=language_stats)

@app.route('/delete/<int:analysis_id>', methods=['POST'])
def delete_analysis(analysis_id):
    """Delete an analysis and its associated file."""
    try:
        analysis = CodeAnalysis.query.get_or_404(analysis_id)
        
        # Delete file if it exists
        if os.path.exists(analysis.file_path):
            os.remove(analysis.file_path)
        
        # Delete metrics
        AnalysisMetrics.query.filter_by(analysis_id=analysis.id).delete()
        
        # Delete analysis
        db.session.delete(analysis)
        db.session.commit()
        
        flash('Analysis deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting analysis: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/export/<int:analysis_id>')
def export_analysis(analysis_id):
    """Export analysis results as JSON."""
    analysis = CodeAnalysis.query.get_or_404(analysis_id)
    
    export_data = {
        'filename': analysis.original_filename,
        'language': analysis.language,
        'quality_score': analysis.quality_score,
        'issues_count': analysis.issues_count,
        'suggestions_count': analysis.suggestions_count,
        'created_at': analysis.created_at.isoformat(),
        'analysis_result': json.loads(analysis.analysis_result) if analysis.analysis_result else {},
        'test_suggestions': json.loads(analysis.test_suggestions) if analysis.test_suggestions else {},
        'metrics': [
            {
                'name': m.metric_name,
                'value': m.metric_value,
                'type': m.metric_type
            }
            for m in analysis.metrics
        ]
    }
    
    return jsonify(export_data)

@app.route('/providers')
def providers_page():
    """AI providers and models information page."""
    providers = get_available_providers()
    return render_template('providers.html', providers=providers)

@app.route('/settings')
def settings_page():
    """Settings page for AI provider configuration."""
    settings = get_user_settings()
    api_keys = decrypt_api_keys(settings.api_keys)
    providers = get_available_providers()
    
    # Pre-select provider if specified in query params
    selected_provider = request.args.get('provider')
    if selected_provider and selected_provider in providers:
        settings.ai_provider = selected_provider
        # Set default model for the provider
        default_model = list(providers[selected_provider]['models'].keys())[0]
        settings.ai_model = default_model
    
    return render_template('settings.html', 
                         settings=settings,
                         api_keys=api_keys,
                         providers=providers)

@app.route('/settings', methods=['POST'])
def update_settings():
    """Update user settings."""
    try:
        settings = get_user_settings()
        
        # Update AI provider and model
        settings.ai_provider = request.form.get('ai_provider', 'openai')
        settings.ai_model = request.form.get('ai_model', 'gpt-4o')
        
        # Update API keys
        api_keys = decrypt_api_keys(settings.api_keys) or {}
        
        # Get all potential API keys from form
        for provider, provider_info in get_available_providers().items():
            api_key_field = provider_info['api_key_env']
            api_key_value = request.form.get(api_key_field)
            if api_key_value and api_key_value.strip():
                api_keys[api_key_field] = api_key_value.strip()
        
        # Encrypt and store API keys
        settings.api_keys = encrypt_api_keys(api_keys)
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')
    
    return redirect(url_for('settings_page'))

@app.route('/validate_api_key', methods=['POST'])
def validate_api_key_route():
    """Validate API key for a provider."""
    try:
        data = request.get_json()
        provider = data.get('provider')
        api_key = data.get('api_key')
        
        if not provider or not api_key:
            return jsonify({'valid': False, 'error': 'Missing provider or API key'})
        
        is_valid = validate_api_key(provider, api_key)
        return jsonify({'valid': is_valid})
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
