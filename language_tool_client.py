import requests
import json
import streamlit as st
from utils.api_config import API_CONFIG

class LanguageToolClient:
    def __init__(self):
        self.config = API_CONFIG["language_tool"]
        self.host = self.config["host"]
        self.api_key = self.config["api_key"]
        self.initialized = self.api_key is not None and self.host is not None
        
    def check_text(self, text, language="en-US"):
        """
        Check text for grammar and style issues
        
        Args:
            text: Text to check
            language: Language code (e.g., en-US, de-DE)
            
        Returns:
            list: List of issues found
        """
        if not self.initialized:
            return self._get_mock_issues(text)
            
        try:
            # API endpoint
            endpoint = f"{self.host}/v2/check"
            
            # Prepare parameters
            params = {
                "text": text,
                "language": language,
                "enabledOnly": "false",
                "level": "picky"  # More strict checking
            }
            
            # Add API key if available
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Make API request
            response = requests.post(endpoint, data=params, headers=headers)
            
            if response.status_code == 200:
                issues = response.json().get("matches", [])
                return issues
            
            # Fall back to mock issues if API fails
            st.warning(f"LanguageTool API error (status {response.status_code})")
            return self._get_mock_issues(text)
            
        except Exception as e:
            st.warning(f"LanguageTool API error: {str(e)}")
            return self._get_mock_issues(text)
    
    def _get_mock_issues(self, text):
        """
        Generate mock grammar issues when API is unavailable
        
        Args:
            text: Original text
            
        Returns:
            list: Mock list of issues
        """
        # Simple pattern matching for common issues
        issues = []
        
        # Check for passive voice (simplified)
        passive_patterns = ["is being", "was being", "were being", "are being", 
                          "has been", "have been", "had been",
                          "will be", "will have been"]
                          
        for pattern in passive_patterns:
            if pattern in text.lower():
                start_index = text.lower().find(pattern)
                end_index = start_index + len(pattern)
                
                # Find the full containing sentence (simplified)
                sentence_start = max(0, text.rfind(".", 0, start_index) + 1)
                sentence_end = text.find(".", end_index)
                if sentence_end == -1:
                    sentence_end = len(text)
                
                context = text[sentence_start:sentence_end].strip()
                
                issues.append({
                    "message": "Consider using active voice instead of passive voice",
                    "replacements": [{"value": "actively did"}],  # Simplified suggestion
                    "offset": start_index,
                    "length": len(pattern),
                    "context": {
                        "text": context,
                        "offset": start_index - sentence_start
                    },
                    "rule": {
                        "id": "PASSIVE_VOICE",
                        "description": "Use of passive voice",
                        "issueType": "style"
                    }
                })
        
        # Check for weak words (simplified)
        weak_words = [
            {"word": "very", "replacement": "extremely", "message": "Consider a stronger alternative to 'very'"},
            {"word": "really", "replacement": "genuinely", "message": "Consider a stronger alternative to 'really'"},
            {"word": "good", "replacement": "excellent", "message": "Consider a more specific or stronger alternative to 'good'"},
            {"word": "nice", "replacement": "outstanding", "message": "Consider a more impactful alternative to 'nice'"},
            {"word": "great", "replacement": "exceptional", "message": "Consider a more specific alternative to 'great'"},
            {"word": "a lot", "replacement": "significantly", "message": "Consider a more precise alternative to 'a lot'"}
        ]
        
        for weak in weak_words:
            word = weak["word"]
            if word in text.lower():
                start_index = text.lower().find(word)
                end_index = start_index + len(word)
                
                # Find the full containing sentence (simplified)
                sentence_start = max(0, text.rfind(".", 0, start_index) + 1)
                sentence_end = text.find(".", end_index)
                if sentence_end == -1:
                    sentence_end = len(text)
                
                context = text[sentence_start:sentence_end].strip()
                
                issues.append({
                    "message": weak["message"],
                    "replacements": [{"value": weak["replacement"]}],
                    "offset": start_index,
                    "length": len(word),
                    "context": {
                        "text": context,
                        "offset": start_index - sentence_start
                    },
                    "rule": {
                        "id": "WEAK_WORD",
                        "description": "Use of weak or vague words",
                        "issueType": "style"
                    }
                })
        
        return issues
    
    def apply_corrections(self, text, issues=None):
        """
        Apply corrections to text based on issues
        
        Args:
            text: Original text
            issues: Issues to correct (if None, will check text)
            
        Returns:
            str: Corrected text
        """
        if issues is None:
            issues = self.check_text(text)
        
        # No issues to correct
        if not issues:
            return text
        
        # Sort issues by offset in reverse order to avoid changing offsets
        sorted_issues = sorted(issues, key=lambda x: x.get("offset", 0), reverse=True)
        
        # Apply corrections
        corrected_text = text
        for issue in sorted_issues:
            offset = issue.get("offset", 0)
            length = issue.get("length", 0)
            replacements = issue.get("replacements", [])
            
            if replacements:
                # Use the first replacement
                replacement = replacements[0].get("value", "")
                
                # Replace the text
                corrected_text = corrected_text[:offset] + replacement + corrected_text[offset + length:]
        
        return corrected_text
    
    def get_style_suggestions(self, text, section_type=None):
        """
        Get style improvement suggestions for resume text
        
        Args:
            text: Text to analyze
            section_type: Type of resume section (e.g., "summary", "experience")
            
        Returns:
            list: Style improvement suggestions
        """
        # First get grammar issues
        issues = self.check_text(text)
        
        # Additional resume-specific style suggestions
        suggestions = []
        
        # Add grammar issues as suggestions
        for issue in issues:
            if issue.get("rule", {}).get("issueType") == "style":
                message = issue.get("message", "")
                context = issue.get("context", {}).get("text", "")
                
                suggestions.append({
                    "type": "grammar",
                    "message": message,
                    "context": context,
                    "replacements": issue.get("replacements", [])
                })
        
        # Resume-specific style suggestions
        if section_type == "summary" or section_type is None:
            if "responsible for" in text.lower():
                suggestions.append({
                    "type": "resume_style",
                    "message": "Avoid 'responsible for' in resume. Use action verbs instead.",
                    "context": text[:100] + "...",
                    "replacements": [{"value": "managed", "example": "Managed team of 5 engineers"}]
                })
            
            if "worked on" in text.lower() or "worked with" in text.lower():
                suggestions.append({
                    "type": "resume_style",
                    "message": "Avoid 'worked on/with' in resume. Use stronger action verbs.",
                    "context": text[:100] + "...",
                    "replacements": [
                        {"value": "developed", "example": "Developed ML models that..."},
                        {"value": "implemented", "example": "Implemented solutions for..."}
                    ]
                })
        
        if section_type == "experience" or section_type is None:
            if "team player" in text.lower():
                suggestions.append({
                    "type": "resume_style",
                    "message": "Avoid cliché phrases like 'team player'. Provide specific examples of collaboration.",
                    "context": text[:100] + "...",
                    "replacements": [
                        {"value": "Collaborated with cross-functional teams to deliver...", "example": "Collaborated with cross-functional teams to deliver project 2 weeks ahead of schedule"}
                    ]
                })
        
        return suggestions

# Initialize LanguageTool client
language_tool_client = LanguageToolClient() 