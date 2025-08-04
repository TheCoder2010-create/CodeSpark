# CodeSpark



# Overview

This is an AI-powered code analysis web application built with Flask that provides comprehensive code quality assessment, automated test generation, and improvement suggestions. The application allows users to upload code files and choose from multiple AI providers (OpenAI, Anthropic, Google Gemini, xAI, Perplexity, Cohere, Mistral, HuggingFace, Together AI) to analyze their code using various state-of-the-art language models.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask**: Lightweight Python web framework chosen for rapid development and simplicity
- **Flask-SQLAlchemy**: ORM for database operations with SQLite as the default database
- **Werkzeug ProxyFix**: Handles proxy headers for deployment environments

## Frontend Architecture
- **Bootstrap 5**: Modern CSS framework for responsive UI components
- **Feather Icons**: Lightweight icon library for consistent iconography
- **Prism.js**: Syntax highlighting for code display with dark/light theme support
- **Custom CSS**: Theme system with CSS variables for light/dark mode switching
- **Vanilla JavaScript**: Client-side functionality for file uploads, theme toggling, and UI interactions

## Backend Architecture
- **MVC Pattern**: Routes handle HTTP requests, models define data structure, templates render views
- **File Upload System**: Secure file handling with allowlist of supported file extensions
- **Database Models**: 
  - `CodeAnalysis`: Main analysis records with metadata and results
  - `AnalysisMetrics`: Detailed metrics storage with foreign key relationship
- **Service Layer**: Separated OpenAI integration for maintainable AI operations

## Data Storage
- **SQLite**: Default database for development with PostgreSQL support for production
- **File System**: Uploaded files stored in local uploads directory with timestamp-based naming
- **Session Management**: Flask sessions for user state management

## AI Integration
- **Multi-Provider Support**: 9 different AI providers with 50+ models available
- **Provider Options**: 
  - OpenAI (GPT-4o, GPT-4 Turbo, GPT-3.5 series)
  - Anthropic Claude (Claude 4.0, 3.7, 3.5 Sonnet, Haiku, Opus)
  - Google Gemini (2.5 Pro/Flash, 1.5 Pro/Flash, 1.0 Pro)
  - xAI Grok (Grok 2 Vision, Grok 2, Grok Beta)
  - Perplexity (Llama 3.1 Sonar models, CodeLlama, Mistral)
  - Cohere (Command R+, Command series)
  - Mistral AI (Large, Medium, Small, Codestral)
  - HuggingFace (Llama 2, CodeLlama, CodeBERT, StarCoder)
  - Together AI (Various open-source models, WizardCoder)
- **Secure API Key Management**: Encrypted storage with user-controlled keys
- **Structured Prompts**: JSON-formatted responses for consistent data parsing
- **Multiple Analysis Types**: Code quality assessment, test case generation, and improvement recommendations

## Security Features
- **File Validation**: Strict allowlist of supported file extensions
- **Secure Filenames**: Werkzeug's secure_filename for safe file handling
- **File Size Limits**: 16MB maximum upload size to prevent abuse
- **Environment Variables**: Sensitive configuration stored outside codebase

# External Dependencies

## AI Services
- **OpenAI API**: GPT-4o model for code analysis and natural language processing
- **API Key Management**: Environment-based configuration for secure access

## Frontend Libraries
- **Bootstrap CDN**: CSS framework and components
- **Feather Icons**: SVG icon library
- **Prism.js CDN**: Syntax highlighting library
- **Google Fonts**: JetBrains Mono and Inter font families

## Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **OpenAI**: Official Python client for OpenAI API
- **Werkzeug**: WSGI utilities and security helpers

## Database
- **SQLite**: Default development database
- **PostgreSQL**: Production database option (configurable via DATABASE_URL)

## Deployment
- **Replit Environment**: Optimized for Replit hosting with environment variable support
- **ProxyFix Middleware**: Handles reverse proxy headers for proper request handling
