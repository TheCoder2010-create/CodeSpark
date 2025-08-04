from app import db
from datetime import datetime

class CodeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    language = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    analysis_result = db.Column(db.Text)
    test_suggestions = db.Column(db.Text)
    quality_score = db.Column(db.Float)
    issues_count = db.Column(db.Integer, default=0)
    suggestions_count = db.Column(db.Integer, default=0)
    ai_model = db.Column(db.String(100))  # Track which AI model was used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CodeAnalysis {self.filename}>'

class AnalysisMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('code_analysis.id'), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.String(255))
    metric_type = db.Column(db.String(50))  # 'quality', 'complexity', 'security', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    analysis = db.relationship('CodeAnalysis', backref=db.backref('metrics', lazy=True))

    def __repr__(self):
        return f'<AnalysisMetrics {self.metric_name}>'

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False, unique=True)
    ai_provider = db.Column(db.String(50), default='openai')  # openai, anthropic, gemini, perplexity, xai
    ai_model = db.Column(db.String(100))  # specific model name
    api_keys = db.Column(db.Text)  # JSON string storing encrypted API keys
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserSettings {self.session_id}>'
