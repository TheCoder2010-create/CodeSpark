import json
import os
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-openai-api-key")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_code_quality(code_content, language):
    """Analyze code quality using OpenAI and return structured results."""
    try:
        prompt = f"""
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

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert code reviewer and static analysis tool. Provide detailed, actionable feedback on code quality, security, and best practices."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        raise Exception(f"Failed to analyze code quality: {str(e)}")

def generate_test_cases(code_content, language):
    """Generate test cases for the provided code."""
    try:
        prompt = f"""
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

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert test engineer. Generate comprehensive, practical test cases that follow testing best practices and cover edge cases."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        raise Exception(f"Failed to generate test cases: {str(e)}")

def get_code_suggestions(code_content, language):
    """Get code improvement suggestions."""
    try:
        prompt = f"""
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

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software architect and code mentor. Provide actionable, specific suggestions for code improvement."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        raise Exception(f"Failed to get code suggestions: {str(e)}")

def detect_language(filename, code_content):
    """Detect programming language from filename and content."""
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
