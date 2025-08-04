import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

# Import AI client libraries
import requests

# Import AI clients with error handling
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    from google import genai
except ImportError:
    genai = None

# Available AI Providers and Models
AI_PROVIDERS = {
    'openai': {
        'name': 'OpenAI',
        'models': {
            'gpt-4o': 'GPT-4o (Latest)',
            'gpt-4o-mini': 'GPT-4o Mini',
            'gpt-4-turbo': 'GPT-4 Turbo',
            'gpt-4-turbo-preview': 'GPT-4 Turbo Preview',
            'gpt-4': 'GPT-4',
            'gpt-4-0613': 'GPT-4 (June 2023)',
            'gpt-3.5-turbo': 'GPT-3.5 Turbo',
            'gpt-3.5-turbo-16k': 'GPT-3.5 Turbo 16K',
            'gpt-3.5-turbo-1106': 'GPT-3.5 Turbo (Nov 2023)'
        },
        'api_key_env': 'OPENAI_API_KEY',
        'requires': ['openai']
    },
    'anthropic': {
        'name': 'Anthropic Claude',
        'models': {
            'claude-sonnet-4-20250514': 'Claude 4.0 Sonnet (Latest)',
            'claude-3-7-sonnet-20250219': 'Claude 3.7 Sonnet',
            'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet',
            'claude-3-5-haiku-20241022': 'Claude 3.5 Haiku',
            'claude-3-opus-20240229': 'Claude 3 Opus',
            'claude-3-sonnet-20240229': 'Claude 3 Sonnet',
            'claude-3-haiku-20240307': 'Claude 3 Haiku',
            'claude-2.1': 'Claude 2.1',
            'claude-2.0': 'Claude 2.0',
            'claude-instant-1.2': 'Claude Instant 1.2'
        },
        'api_key_env': 'ANTHROPIC_API_KEY',
        'requires': ['anthropic']
    },
    'gemini': {
        'name': 'Google Gemini',
        'models': {
            'gemini-2.5-pro': 'Gemini 2.5 Pro (Latest)',
            'gemini-2.5-flash': 'Gemini 2.5 Flash',
            'gemini-1.5-pro': 'Gemini 1.5 Pro',
            'gemini-1.5-flash': 'Gemini 1.5 Flash',
            'gemini-1.0-pro': 'Gemini 1.0 Pro',
            'gemini-pro': 'Gemini Pro',
            'gemini-pro-vision': 'Gemini Pro Vision'
        },
        'api_key_env': 'GEMINI_API_KEY',
        'requires': ['google-genai']
    },
    'xai': {
        'name': 'xAI Grok',
        'models': {
            'grok-2-vision-1212': 'Grok 2 Vision (Latest)',
            'grok-2-1212': 'Grok 2',
            'grok-vision-beta': 'Grok Vision Beta',
            'grok-beta': 'Grok Beta',
            'grok-1': 'Grok 1'
        },
        'api_key_env': 'XAI_API_KEY',
        'requires': ['openai']  # Uses OpenAI-compatible API
    },
    'perplexity': {
        'name': 'Perplexity',
        'models': {
            'llama-3.1-sonar-huge-128k-online': 'Llama 3.1 Sonar Huge (Online)',
            'llama-3.1-sonar-large-128k-online': 'Llama 3.1 Sonar Large (Online)',
            'llama-3.1-sonar-small-128k-online': 'Llama 3.1 Sonar Small (Online)',
            'llama-3.1-sonar-large-128k-chat': 'Llama 3.1 Sonar Large (Chat)',
            'llama-3.1-sonar-small-128k-chat': 'Llama 3.1 Sonar Small (Chat)',
            'llama-3.1-8b-instruct': 'Llama 3.1 8B Instruct',
            'llama-3.1-70b-instruct': 'Llama 3.1 70B Instruct',
            'codellama-34b-instruct': 'CodeLlama 34B Instruct',
            'codellama-70b-instruct': 'CodeLlama 70B Instruct',
            'mistral-7b-instruct': 'Mistral 7B Instruct',
            'mixtral-8x7b-instruct': 'Mixtral 8x7B Instruct'
        },
        'api_key_env': 'PERPLEXITY_API_KEY',
        'requires': ['requests']
    },
    'cohere': {
        'name': 'Cohere',
        'models': {
            'command-r-plus': 'Command R+ (Latest)',
            'command-r': 'Command R',
            'command': 'Command',
            'command-nightly': 'Command Nightly',
            'command-light': 'Command Light',
            'command-light-nightly': 'Command Light Nightly'
        },
        'api_key_env': 'COHERE_API_KEY',
        'requires': ['requests']
    },
    'mistral': {
        'name': 'Mistral AI',
        'models': {
            'mistral-large-latest': 'Mistral Large (Latest)',
            'mistral-medium-latest': 'Mistral Medium',
            'mistral-small-latest': 'Mistral Small',
            'open-mistral-7b': 'Open Mistral 7B',
            'open-mixtral-8x7b': 'Open Mixtral 8x7B',
            'open-mixtral-8x22b': 'Open Mixtral 8x22B',
            'codestral-latest': 'Codestral (Code)',
            'mistral-embed': 'Mistral Embed'
        },
        'api_key_env': 'MISTRAL_API_KEY',
        'requires': ['requests']
    },
    'huggingface': {
        'name': 'HuggingFace',
        'models': {
            'meta-llama/Llama-2-70b-chat-hf': 'Llama 2 70B Chat',
            'meta-llama/Llama-2-13b-chat-hf': 'Llama 2 13B Chat',
            'meta-llama/Llama-2-7b-chat-hf': 'Llama 2 7B Chat',
            'codellama/CodeLlama-34b-Instruct-hf': 'CodeLlama 34B Instruct',
            'microsoft/DialoGPT-large': 'DialoGPT Large',
            'microsoft/CodeBERT-base': 'CodeBERT Base',
            'Salesforce/codegen-16B-mono': 'CodeGen 16B',
            'bigcode/starcoder': 'StarCoder'
        },
        'api_key_env': 'HUGGINGFACE_API_KEY',
        'requires': ['requests']
    },
    'together': {
        'name': 'Together AI',
        'models': {
            'meta-llama/Llama-2-70b-chat-hf': 'Llama 2 70B Chat',
            'meta-llama/Llama-2-13b-chat-hf': 'Llama 2 13B Chat',
            'meta-llama/Llama-2-7b-chat-hf': 'Llama 2 7B Chat',
            'codellama/CodeLlama-34b-Instruct-hf': 'CodeLlama 34B Instruct',
            'codellama/CodeLlama-13b-Instruct-hf': 'CodeLlama 13B Instruct',
            'codellama/CodeLlama-7b-Instruct-hf': 'CodeLlama 7B Instruct',
            'WizardLM/WizardCoder-Python-34B-V1.0': 'WizardCoder Python 34B',
            'Phind/Phind-CodeLlama-34B-v2': 'Phind CodeLlama 34B v2'
        },
        'api_key_env': 'TOGETHER_API_KEY',
        'requires': ['requests']
    }
}

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the AI client"""
        pass
    
    @abstractmethod
    def analyze_code_quality(self, code_content: str, language: str) -> Dict[str, Any]:
        """Analyze code quality"""
        pass
    
    @abstractmethod
    def generate_test_cases(self, code_content: str, language: str) -> Dict[str, Any]:
        """Generate test cases"""
        pass
    
    @abstractmethod
    def get_code_suggestions(self, code_content: str, language: str) -> Dict[str, Any]:
        """Get code improvement suggestions"""
        pass

class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    def _initialize_client(self):
        return OpenAI(api_key=self.api_key)
    
    def analyze_code_quality(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_quality_prompt(code_content, language)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer and static analysis tool. Provide detailed, actionable feedback on code quality, security, and best practices."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    def generate_test_cases(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_test_prompt(code_content, language)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert test engineer. Generate comprehensive, practical test cases that follow testing best practices and cover edge cases."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        
        return json.loads(response.choices[0].message.content)
    
    def get_code_suggestions(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_suggestions_prompt(code_content, language)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a senior software architect and code mentor. Provide actionable, specific suggestions for code improvement."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _build_quality_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Analyze the following {language} code for quality, best practices, and potential issues.
        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "quality_score": <number between 0-100>,
            "issues": [
                {{
                    "type": "error|warning|suggestion",
                    "severity": "high|medium|low",
                    "line": <line_number_or_null>,
                    "message": "description of the issue",
                    "suggestion": "how to fix it"
                }}
            ],
            "metrics": {{
                "complexity": "low|medium|high",
                "maintainability": <number between 0-100>,
                "readability": <number between 0-100>,
                "security": <number between 0-100>
            }},
            "summary": "Overall summary of code quality",
            "recommendations": [
                "list of general recommendations for improvement"
            ]
        }}

        Code to analyze:
        {code_content}
        """
    
    def _build_test_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Generate comprehensive test cases for the following {language} code.
        Provide the response in JSON format with the following structure:
        {{
            "test_framework": "recommended testing framework for {language}",
            "test_cases": [
                {{
                    "name": "test case name",
                    "description": "what this test validates",
                    "type": "unit|integration|edge_case",
                    "priority": "high|medium|low",
                    "test_code": "actual test code implementation"
                }}
            ],
            "coverage_suggestions": [
                "areas that need more test coverage"
            ],
            "mocking_suggestions": [
                "components that should be mocked and why"
            ]
        }}

        Code to generate tests for:
        {code_content}
        """
    
    def _build_suggestions_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Provide specific code improvement suggestions for the following {language} code.
        Focus on performance, security, maintainability, and best practices.
        Respond in JSON format:
        {{
            "refactoring_suggestions": [
                {{
                    "category": "performance|security|maintainability|style",
                    "description": "what to improve",
                    "before_code": "current problematic code snippet",
                    "after_code": "improved code snippet",
                    "explanation": "why this improvement matters"
                }}
            ],
            "architecture_suggestions": [
                "high-level architectural improvements"
            ],
            "dependency_suggestions": [
                "library or framework recommendations"
            ]
        }}

        Code to improve:
        {code_content}
        """

class AnthropicProvider(AIProvider):
    """Anthropic provider implementation"""
    
    def _initialize_client(self):
        return anthropic.Anthropic(api_key=self.api_key)
    
    def analyze_code_quality(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_quality_prompt(code_content, language)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system="You are an expert code reviewer and static analysis tool. Provide detailed, actionable feedback on code quality, security, and best practices. Always respond with valid JSON."
        )
        
        return json.loads(response.content[0].text)
    
    def generate_test_cases(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_test_prompt(code_content, language)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system="You are an expert test engineer. Generate comprehensive, practical test cases that follow testing best practices and cover edge cases. Always respond with valid JSON."
        )
        
        return json.loads(response.content[0].text)
    
    def get_code_suggestions(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_suggestions_prompt(code_content, language)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system="You are a senior software architect and code mentor. Provide actionable, specific suggestions for code improvement. Always respond with valid JSON."
        )
        
        return json.loads(response.content[0].text)
    
    def _build_quality_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Analyze the following {language} code for quality, best practices, and potential issues.
        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "quality_score": <number between 0-100>,
            "issues": [
                {{
                    "type": "error|warning|suggestion",
                    "severity": "high|medium|low",
                    "line": <line_number_or_null>,
                    "message": "description of the issue",
                    "suggestion": "how to fix it"
                }}
            ],
            "metrics": {{
                "complexity": "low|medium|high",
                "maintainability": <number between 0-100>,
                "readability": <number between 0-100>,
                "security": <number between 0-100>
            }},
            "summary": "Overall summary of code quality",
            "recommendations": [
                "list of general recommendations for improvement"
            ]
        }}

        Code to analyze:
        {code_content}
        """
    
    def _build_test_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Generate comprehensive test cases for the following {language} code.
        Provide the response in JSON format with the following structure:
        {{
            "test_framework": "recommended testing framework for {language}",
            "test_cases": [
                {{
                    "name": "test case name",
                    "description": "what this test validates",
                    "type": "unit|integration|edge_case",
                    "priority": "high|medium|low",
                    "test_code": "actual test code implementation"
                }}
            ],
            "coverage_suggestions": [
                "areas that need more test coverage"
            ],
            "mocking_suggestions": [
                "components that should be mocked and why"
            ]
        }}

        Code to generate tests for:
        {code_content}
        """
    
    def _build_suggestions_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Provide specific code improvement suggestions for the following {language} code.
        Focus on performance, security, maintainability, and best practices.
        Respond in JSON format:
        {{
            "refactoring_suggestions": [
                {{
                    "category": "performance|security|maintainability|style",
                    "description": "what to improve",
                    "before_code": "current problematic code snippet",
                    "after_code": "improved code snippet",
                    "explanation": "why this improvement matters"
                }}
            ],
            "architecture_suggestions": [
                "high-level architectural improvements"
            ],
            "dependency_suggestions": [
                "library or framework recommendations"
            ]
        }}

        Code to improve:
        {code_content}
        """

class GeminiProvider(AIProvider):
    """Google Gemini provider implementation"""
    
    def _initialize_client(self):
        return genai.Client(api_key=self.api_key)
    
    def analyze_code_quality(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_quality_prompt(code_content, language)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        
        return json.loads(response.text)
    
    def generate_test_cases(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_test_prompt(code_content, language)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4
            )
        )
        
        return json.loads(response.text)
    
    def get_code_suggestions(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_suggestions_prompt(code_content, language)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        
        return json.loads(response.text)
    
    def _build_quality_prompt(self, code_content: str, language: str) -> str:
        return f"""
        You are an expert code reviewer and static analysis tool. Analyze the following {language} code for quality, best practices, and potential issues.
        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "quality_score": <number between 0-100>,
            "issues": [
                {{
                    "type": "error|warning|suggestion",
                    "severity": "high|medium|low",
                    "line": <line_number_or_null>,
                    "message": "description of the issue",
                    "suggestion": "how to fix it"
                }}
            ],
            "metrics": {{
                "complexity": "low|medium|high",
                "maintainability": <number between 0-100>,
                "readability": <number between 0-100>,
                "security": <number between 0-100>
            }},
            "summary": "Overall summary of code quality",
            "recommendations": [
                "list of general recommendations for improvement"
            ]
        }}

        Code to analyze:
        {code_content}
        """
    
    def _build_test_prompt(self, code_content: str, language: str) -> str:
        return f"""
        You are an expert test engineer. Generate comprehensive test cases for the following {language} code.
        Provide the response in JSON format with the following structure:
        {{
            "test_framework": "recommended testing framework for {language}",
            "test_cases": [
                {{
                    "name": "test case name",
                    "description": "what this test validates",
                    "type": "unit|integration|edge_case",
                    "priority": "high|medium|low",
                    "test_code": "actual test code implementation"
                }}
            ],
            "coverage_suggestions": [
                "areas that need more test coverage"
            ],
            "mocking_suggestions": [
                "components that should be mocked and why"
            ]
        }}

        Code to generate tests for:
        {code_content}
        """
    
    def _build_suggestions_prompt(self, code_content: str, language: str) -> str:
        return f"""
        You are a senior software architect and code mentor. Provide specific code improvement suggestions for the following {language} code.
        Focus on performance, security, maintainability, and best practices.
        Respond in JSON format:
        {{
            "refactoring_suggestions": [
                {{
                    "category": "performance|security|maintainability|style",
                    "description": "what to improve",
                    "before_code": "current problematic code snippet",
                    "after_code": "improved code snippet",
                    "explanation": "why this improvement matters"
                }}
            ],
            "architecture_suggestions": [
                "high-level architectural improvements"
            ],
            "dependency_suggestions": [
                "library or framework recommendations"
            ]
        }}

        Code to improve:
        {code_content}
        """

class PerplexityProvider(AIProvider):
    """Perplexity provider implementation"""
    
    def _initialize_client(self):
        return None  # Uses requests directly
    
    def analyze_code_quality(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_quality_prompt(code_content, language)
        return self._make_request(prompt, "You are an expert code reviewer and static analysis tool. Provide detailed, actionable feedback on code quality, security, and best practices. Always respond with valid JSON.")
    
    def generate_test_cases(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_test_prompt(code_content, language)
        return self._make_request(prompt, "You are an expert test engineer. Generate comprehensive, practical test cases that follow testing best practices and cover edge cases. Always respond with valid JSON.")
    
    def get_code_suggestions(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_suggestions_prompt(code_content, language)
        return self._make_request(prompt, "You are a senior software architect and code mentor. Provide actionable, specific suggestions for code improvement. Always respond with valid JSON.")
    
    def _make_request(self, prompt: str, system_message: str) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'stream': False
        }
        
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.loads(result['choices'][0]['message']['content'])
        else:
            raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
    
    def _build_quality_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Analyze the following {language} code for quality, best practices, and potential issues.
        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "quality_score": <number between 0-100>,
            "issues": [
                {{
                    "type": "error|warning|suggestion",
                    "severity": "high|medium|low",
                    "line": <line_number_or_null>,
                    "message": "description of the issue",
                    "suggestion": "how to fix it"
                }}
            ],
            "metrics": {{
                "complexity": "low|medium|high",
                "maintainability": <number between 0-100>,
                "readability": <number between 0-100>,
                "security": <number between 0-100>
            }},
            "summary": "Overall summary of code quality",
            "recommendations": [
                "list of general recommendations for improvement"
            ]
        }}

        Code to analyze:
        {code_content}
        """
    
    def _build_test_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Generate comprehensive test cases for the following {language} code.
        Provide the response in JSON format with the following structure:
        {{
            "test_framework": "recommended testing framework for {language}",
            "test_cases": [
                {{
                    "name": "test case name",
                    "description": "what this test validates",
                    "type": "unit|integration|edge_case",
                    "priority": "high|medium|low",
                    "test_code": "actual test code implementation"
                }}
            ],
            "coverage_suggestions": [
                "areas that need more test coverage"
            ],
            "mocking_suggestions": [
                "components that should be mocked and why"
            ]
        }}

        Code to generate tests for:
        {code_content}
        """
    
    def _build_suggestions_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Provide specific code improvement suggestions for the following {language} code.
        Focus on performance, security, maintainability, and best practices.
        Respond in JSON format:
        {{
            "refactoring_suggestions": [
                {{
                    "category": "performance|security|maintainability|style",
                    "description": "what to improve",
                    "before_code": "current problematic code snippet",
                    "after_code": "improved code snippet",
                    "explanation": "why this improvement matters"
                }}
            ],
            "architecture_suggestions": [
                "high-level architectural improvements"
            ],
            "dependency_suggestions": [
                "library or framework recommendations"
            ]
        }}

        Code to improve:
        {code_content}
        """

class XAIProvider(AIProvider):
    """xAI (Grok) provider implementation using OpenAI-compatible API"""
    
    def _initialize_client(self):
        return OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
    
    def analyze_code_quality(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_quality_prompt(code_content, language)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer and static analysis tool. Provide detailed, actionable feedback on code quality, security, and best practices."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    def generate_test_cases(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_test_prompt(code_content, language)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert test engineer. Generate comprehensive, practical test cases that follow testing best practices and cover edge cases."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        
        return json.loads(response.choices[0].message.content)
    
    def get_code_suggestions(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_suggestions_prompt(code_content, language)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a senior software architect and code mentor. Provide actionable, specific suggestions for code improvement."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _build_quality_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Analyze the following {language} code for quality, best practices, and potential issues.
        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "quality_score": <number between 0-100>,
            "issues": [
                {{
                    "type": "error|warning|suggestion",
                    "severity": "high|medium|low",
                    "line": <line_number_or_null>,
                    "message": "description of the issue",
                    "suggestion": "how to fix it"
                }}
            ],
            "metrics": {{
                "complexity": "low|medium|high",
                "maintainability": <number between 0-100>,
                "readability": <number between 0-100>,
                "security": <number between 0-100>
            }},
            "summary": "Overall summary of code quality",
            "recommendations": [
                "list of general recommendations for improvement"
            ]
        }}

        Code to analyze:
        {code_content}
        """
    
    def _build_test_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Generate comprehensive test cases for the following {language} code.
        Provide the response in JSON format with the following structure:
        {{
            "test_framework": "recommended testing framework for {language}",
            "test_cases": [
                {{
                    "name": "test case name",
                    "description": "what this test validates",
                    "type": "unit|integration|edge_case",
                    "priority": "high|medium|low",
                    "test_code": "actual test code implementation"
                }}
            ],
            "coverage_suggestions": [
                "areas that need more test coverage"
            ],
            "mocking_suggestions": [
                "components that should be mocked and why"
            ]
        }}

        Code to generate tests for:
        {code_content}
        """
    
    def _build_suggestions_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Provide specific code improvement suggestions for the following {language} code.
        Focus on performance, security, maintainability, and best practices.
        Respond in JSON format:
        {{
            "refactoring_suggestions": [
                {{
                    "category": "performance|security|maintainability|style",
                    "description": "what to improve",
                    "before_code": "current problematic code snippet",
                    "after_code": "improved code snippet",
                    "explanation": "why this improvement matters"
                }}
            ],
            "architecture_suggestions": [
                "high-level architectural improvements"
            ],
            "dependency_suggestions": [
                "library or framework recommendations"
            ]
        }}

        Code to improve:
        {code_content}
        """

class HTTPProvider(AIProvider):
    """Generic HTTP provider for APIs that use standard HTTP requests"""
    
    def __init__(self, api_key: str, model: str, base_url: str, headers: Dict[str, str] = None):
        self.base_url = base_url
        self.headers = headers or {}
        super().__init__(api_key, model)
    
    def _initialize_client(self):
        return None  # Uses requests directly
    
    def analyze_code_quality(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_quality_prompt(code_content, language)
        return self._make_request(prompt, "You are an expert code reviewer. Analyze the code and provide detailed feedback in JSON format.")
    
    def generate_test_cases(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_test_prompt(code_content, language)
        return self._make_request(prompt, "You are a test engineer. Generate comprehensive test cases in JSON format.")
    
    def get_code_suggestions(self, code_content: str, language: str) -> Dict[str, Any]:
        prompt = self._build_suggestions_prompt(code_content, language)
        return self._make_request(prompt, "You are a senior developer. Provide code improvement suggestions in JSON format.")
    
    def _make_request(self, prompt: str, system_message: str) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            **self.headers
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 4000
        }
        
        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback for non-JSON responses
                return {"error": "Invalid JSON response", "content": content}
        else:
            raise Exception(f"API error: {response.status_code} - {response.text}")
    
    def _build_quality_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Analyze the following {language} code for quality, best practices, and potential issues.
        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "quality_score": <number between 0-100>,
            "issues": [
                {{
                    "type": "error|warning|suggestion",
                    "severity": "high|medium|low",
                    "line": <line_number_or_null>,
                    "message": "description of the issue",
                    "suggestion": "how to fix it"
                }}
            ],
            "metrics": {{
                "complexity": "low|medium|high",
                "maintainability": <number between 0-100>,
                "readability": <number between 0-100>,
                "security": <number between 0-100>
            }},
            "summary": "Overall summary of code quality",
            "recommendations": [
                "list of general recommendations for improvement"
            ]
        }}

        Code to analyze:
        {code_content}
        """
    
    def _build_test_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Generate comprehensive test cases for the following {language} code.
        Provide the response in JSON format with the following structure:
        {{
            "test_framework": "recommended testing framework for {language}",
            "test_cases": [
                {{
                    "name": "test case name",
                    "description": "what this test validates",
                    "type": "unit|integration|edge_case",
                    "priority": "high|medium|low",
                    "test_code": "actual test code implementation"
                }}
            ],
            "coverage_suggestions": [
                "areas that need more test coverage"
            ],
            "mocking_suggestions": [
                "components that should be mocked and why"
            ]
        }}

        Code to generate tests for:
        {code_content}
        """
    
    def _build_suggestions_prompt(self, code_content: str, language: str) -> str:
        return f"""
        Provide specific code improvement suggestions for the following {language} code.
        Focus on performance, security, maintainability, and best practices.
        Respond in JSON format:
        {{
            "refactoring_suggestions": [
                {{
                    "category": "performance|security|maintainability|style",
                    "description": "what to improve",
                    "before_code": "current problematic code snippet",
                    "after_code": "improved code snippet",
                    "explanation": "why this improvement matters"
                }}
            ],
            "architecture_suggestions": [
                "high-level architectural improvements"
            ],
            "dependency_suggestions": [
                "library or framework recommendations"
            ]
        }}

        Code to improve:
        {code_content}
        """

# Factory function to create AI providers
def create_ai_provider(provider_name: str, api_key: str, model: str) -> AIProvider:
    """Factory function to create AI provider instances"""
    
    if provider_name == 'openai':
        return OpenAIProvider(api_key, model)
    elif provider_name == 'anthropic':
        return AnthropicProvider(api_key, model)
    elif provider_name == 'gemini':
        return GeminiProvider(api_key, model)
    elif provider_name == 'perplexity':
        return PerplexityProvider(api_key, model)
    elif provider_name == 'xai':
        return XAIProvider(api_key, model)
    elif provider_name == 'cohere':
        return HTTPProvider(api_key, model, "https://api.cohere.ai/v1")
    elif provider_name == 'mistral':
        return HTTPProvider(api_key, model, "https://api.mistral.ai/v1")
    elif provider_name == 'huggingface':
        return HTTPProvider(api_key, model, "https://api-inference.huggingface.co/models")
    elif provider_name == 'together':
        return HTTPProvider(api_key, model, "https://api.together.xyz/v1")
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")

def get_available_providers() -> Dict[str, Dict]:
    """Get list of available AI providers and their models"""
    return AI_PROVIDERS

def validate_api_key(provider: str, api_key: str) -> bool:
    """Validate API key for a given provider"""
    try:
        if provider == 'openai':
            client = OpenAI(api_key=api_key)
            client.models.list()
        elif provider == 'anthropic':
            client = anthropic.Anthropic(api_key=api_key)
            client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}]
            )
        elif provider == 'gemini':
            client = genai.Client(api_key=api_key)
            client.models.generate_content(
                model="gemini-1.5-flash",
                contents="Test"
            )
        elif provider == 'perplexity':
            headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            data = {
                'model': 'llama-3.1-sonar-small-128k-online',
                'messages': [{'role': 'user', 'content': 'Test'}],
                'max_tokens': 1
            }
            response = requests.post('https://api.perplexity.ai/chat/completions', headers=headers, json=data)
            response.raise_for_status()
        elif provider == 'xai':
            client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
            client.models.list()
        elif provider == 'cohere':
            headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            data = {
                'model': 'command',
                'message': 'Test',
                'max_tokens': 1
            }
            response = requests.post('https://api.cohere.ai/v1/generate', headers=headers, json=data)
            response.raise_for_status()
        elif provider == 'mistral':
            headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            data = {
                'model': 'mistral-small-latest',
                'messages': [{'role': 'user', 'content': 'Test'}],
                'max_tokens': 1
            }
            response = requests.post('https://api.mistral.ai/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
        elif provider == 'huggingface':
            headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            data = {'inputs': 'Test'}
            response = requests.post('https://api-inference.huggingface.co/models/microsoft/DialoGPT-large', 
                                   headers=headers, json=data)
            response.raise_for_status()
        elif provider == 'together':
            headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            data = {
                'model': 'meta-llama/Llama-2-7b-chat-hf',
                'messages': [{'role': 'user', 'content': 'Test'}],
                'max_tokens': 1
            }
            response = requests.post('https://api.together.xyz/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
        else:
            return False
        
        return True
    except Exception:
        return False

def detect_language(filename: str, code_content: str) -> str:
    """Detect programming language from filename and content"""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.sh': 'bash',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml'
    }

    # Get extension from filename
    ext = os.path.splitext(filename.lower())[1]
    detected_language = extension_map.get(ext, 'text')

    # If we can't detect from extension, try to detect from content
    if detected_language == 'text' and code_content:
        # Simple heuristics for common languages
        if 'def ' in code_content and 'import ' in code_content:
            detected_language = 'python'
        elif 'function ' in code_content and ('var ' in code_content or 'let ' in code_content):
            detected_language = 'javascript'
        elif 'public class ' in code_content and 'public static void main' in code_content:
            detected_language = 'java'

    return detected_language