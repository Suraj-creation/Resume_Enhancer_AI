"""
Content Enhancer Service - Provides AI-powered text enhancement capabilities
"""

import logging
import streamlit as st
from typing import Dict, List, Any, Optional, Union
import re

from utils.ai_services.service_manager import AIServiceManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentEnhancerService:
    """Service for enhancing text content using AI"""
    
    def __init__(self, api_key=None):
        """
        Initialize the Content Enhancer service
        
        Args:
            api_key (str, optional): Not used directly, but kept for API compatibility
        """
        # Get the service manager
        self.service_manager = AIServiceManager()
        
        # Try to get AI services
        self.gemini = self.service_manager.get_service("gemini")
        self.huggingface = self.service_manager.get_service("huggingface")
        self.openai = self.service_manager.get_service("openai")
        
        # Set availability flags
        self.gemini_available = self.gemini is not None
        self.huggingface_available = self.huggingface is not None
        self.openai_available = self.openai is not None
        
    def improve_grammar(self, text):
        """
        Check and correct grammar issues in text
        
        Args:
            text (str): Text to check and correct
            
        Returns:
            dict: Results including corrected text and list of issues
        """
        # If Gemini is available, use it
        if self.gemini_available:
            try:
                issues = self.gemini.check_grammar(text)
                
                # If we have issues, fix them
                if issues:
                    # Sort issues by position (reversed so we can edit from end to beginning)
                    sorted_issues = sorted(issues, key=lambda x: x.get("start", 0), reverse=True)
                    
                    # Apply corrections
                    corrected_text = text
                    for issue in sorted_issues:
                        if "text" in issue and "correction" in issue:
                            problematic_text = issue["text"]
                            correction = issue["correction"]
                            corrected_text = corrected_text.replace(problematic_text, correction)
                            
                    return {
                        "corrected_text": corrected_text,
                        "issues": issues,
                        "improved": len(issues) > 0
                    }
                
                # No issues found
                return {
                    "corrected_text": text,
                    "issues": [],
                    "improved": False
                }
                
            except Exception as e:
                logger.error(f"Error checking grammar with Gemini: {str(e)}")
                # Fall back to other services
                
        # If no issues or service failed, return original text
        return {
            "corrected_text": text,
            "issues": [],
            "improved": False
        }
        
    def enhance_text_style(self, text, style=None):
        """
        Enhance the style of text
        
        Args:
            text (str): Text to enhance
            style (str, optional): Desired style (professional, concise, engaging, etc.)
            
        Returns:
            str: Enhanced text
        """
        if not text:
            return text
            
        # Use default style if none specified
        style = style or "professional"
        
        # If Gemini is available, use it
        if self.gemini_available:
            try:
                prompt = f"""
                Enhance the following text to make it more {style}.
                
                ORIGINAL TEXT:
                ```
                {text}
                ```
                
                Guidelines for {style} style:
                """
                
                # Add style-specific guidelines
                if style.lower() == "professional":
                    prompt += """
                    - Use clear, direct language
                    - Maintain a formal tone
                    - Use industry-specific terminology appropriately
                    - Emphasize expertise and credibility
                    - Be concise and avoid unnecessary words
                    """
                elif style.lower() == "concise":
                    prompt += """
                    - Eliminate unnecessary words and phrases
                    - Use direct language and active voice
                    - Combine sentences where possible
                    - Maintain key information while reducing length
                    - Focus on essential points only
                    """
                elif style.lower() == "engaging":
                    prompt += """
                    - Use more dynamic language and varied sentence structure
                    - Add rhetorical questions or hooks where appropriate
                    - Incorporate storytelling elements if relevant
                    - Create a conversational but professional tone
                    - Use vivid descriptions and examples
                    """
                else:
                    # Default guidelines
                    prompt += """
                    - Improve clarity and readability
                    - Use correct grammar and punctuation
                    - Maintain the original meaning and key points
                    - Improve sentence structure where needed
                    - Enhance overall flow and coherence
                    """
                    
                prompt += """
                
                Please provide ONLY the enhanced text with no additional explanation.
                """
                
                # Generate enhanced text
                enhanced_text = self.gemini.generate_text(prompt, temperature=0.3)
                
                # Clean up any markdown code blocks or unnecessary text
                enhanced_text = re.sub(r'```.*?\n', '', enhanced_text)
                enhanced_text = re.sub(r'```', '', enhanced_text)
                
                return enhanced_text.strip()
                
            except Exception as e:
                logger.error(f"Error enhancing text style with Gemini: {str(e)}")
                # Fall back to original text
                return text
                
        # If Gemini is not available or failed, return original text
        return text
        
    def summarize_text(self, text, max_length=150):
        """
        Summarize text to a shorter length
        
        Args:
            text (str): Text to summarize
            max_length (int): Approximate target length in words
            
        Returns:
            str: Summarized text
        """
        if not text:
            return text
            
        # If text is already shorter than max_length, return as is
        if len(text.split()) <= max_length:
            return text
            
        # If HuggingFace is available, use it
        if self.huggingface_available:
            try:
                return self.huggingface.summarize_text(text, max_length=max_length)
            except Exception as e:
                logger.error(f"Error summarizing with HuggingFace: {str(e)}")
                # Fall back to Gemini
                
        # If Gemini is available, use it
        if self.gemini_available:
            try:
                prompt = f"""
                Summarize the following text to approximately {max_length} words while preserving the key information.
                
                TEXT TO SUMMARIZE:
                ```
                {text}
                ```
                
                Please provide ONLY the summary with no additional explanation.
                """
                
                # Generate summary
                summary = self.gemini.generate_text(prompt, temperature=0.3)
                
                # Clean up any markdown code blocks or unnecessary text
                summary = re.sub(r'```.*?\n', '', summary)
                summary = re.sub(r'```', '', summary)
                
                return summary.strip()
                
            except Exception as e:
                logger.error(f"Error summarizing with Gemini: {str(e)}")
                # Fall back to basic summarization
                
        # Basic fallback: just take first few sentences
        sentences = text.split('.')
        summary_sentences = []
        word_count = 0
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            sentence_words = len(sentence.split())
            if word_count + sentence_words <= max_length:
                summary_sentences.append(sentence.strip())
                word_count += sentence_words
            else:
                break
                
        if not summary_sentences:
            # If we couldn't extract any sentences, just take the first part
            return ' '.join(text.split()[:max_length])
            
        return '. '.join(summary_sentences) + '.'
        
    def expand_text(self, text, target_length=None, additional_points=None):
        """
        Expand text to add more detail or length
        
        Args:
            text (str): Text to expand
            target_length (int, optional): Target length in words
            additional_points (list, optional): Specific points to include
            
        Returns:
            str: Expanded text
        """
        if not text:
            return text
            
        # If Gemini is available, use it
        if self.gemini_available:
            try:
                prompt = f"""
                Expand the following text to provide more detail and depth.
                
                ORIGINAL TEXT:
                ```
                {text}
                ```
                """
                
                # Add target length if specified
                if target_length:
                    prompt += f"\nExpand to approximately {target_length} words."
                    
                # Add specific points to include if provided
                if additional_points:
                    prompt += "\nInclude the following points in the expanded text:"
                    for point in additional_points:
                        prompt += f"\n- {point}"
                        
                prompt += """
                
                Guidelines for expansion:
                - Maintain the original tone and style
                - Add relevant details, examples, or context
                - Ensure logical flow and coherence
                - Do not contradict the original content
                - Elaborate on key points with supporting information
                
                Please provide ONLY the expanded text with no additional explanation.
                """
                
                # Generate expanded text
                expanded_text = self.gemini.generate_text(prompt, temperature=0.4)
                
                # Clean up any markdown code blocks or unnecessary text
                expanded_text = re.sub(r'```.*?\n', '', expanded_text)
                expanded_text = re.sub(r'```', '', expanded_text)
                
                return expanded_text.strip()
                
            except Exception as e:
                logger.error(f"Error expanding text with Gemini: {str(e)}")
                # Fall back to original text
                return text
                
        # If Gemini is not available or failed, return original text
        return text
        
    def highlight_keywords(self, text, keywords):
        """
        Highlight keywords in text
        
        Args:
            text (str): Text to process
            keywords (list): Keywords to highlight
            
        Returns:
            dict: Results including HTML version with highlights
        """
        if not text or not keywords:
            return {
                "html": text,
                "matches": {}
            }
            
        # Count keyword occurrences
        matches = {}
        for keyword in keywords:
            # Create regex pattern for whole word match
            pattern = r'\b' + re.escape(keyword) + r'\b'
            count = len(re.findall(pattern, text, re.IGNORECASE))
            if count > 0:
                matches[keyword] = count
                
        # Create HTML with highlighted keywords
        html = text
        for keyword in keywords:
            pattern = r'\b(' + re.escape(keyword) + r')\b'
            replacement = r'<span style="background-color: #FFFF00; font-weight: bold;">\1</span>'
            html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
            
        return {
            "html": html,
            "matches": matches
        }
        
    def generate_bullets(self, text):
        """
        Transform paragraph text into bulleted list items
        
        Args:
            text (str): Text to transform
            
        Returns:
            str: Bulleted list version of the text
        """
        if not text:
            return text
            
        # If Gemini is available, use it
        if self.gemini_available:
            try:
                prompt = f"""
                Transform the following paragraph text into a clear, concise bulleted list.
                Extract key points and create separate bullet points.
                
                PARAGRAPH TEXT:
                ```
                {text}
                ```
                
                Guidelines:
                - Start each bullet with a strong action verb or key concept
                - Keep each bullet to 1-2 sentences
                - Ensure bullets are parallel in structure
                - Focus on the most important information
                - Organize bullets in a logical sequence
                - Use the "•" character for bullet points
                
                Please provide ONLY the bulleted list with no additional explanation.
                """
                
                # Generate bulleted list
                bullet_list = self.gemini.generate_text(prompt, temperature=0.3)
                
                # Clean up any markdown code blocks or unnecessary text
                bullet_list = re.sub(r'```.*?\n', '', bullet_list)
                bullet_list = re.sub(r'```', '', bullet_list)
                
                return bullet_list.strip()
                
            except Exception as e:
                logger.error(f"Error generating bullets with Gemini: {str(e)}")
                # Fall back to basic bullet generation
                
        # Basic fallback: split into sentences and make each a bullet
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        bullets = ['• ' + s + '.' for s in sentences]
        return '\n'.join(bullets)
        
    def transform_to_paragraphs(self, bullet_text):
        """
        Transform bulleted list into cohesive paragraphs
        
        Args:
            bullet_text (str): Bulleted list text
            
        Returns:
            str: Paragraph version of the text
        """
        if not bullet_text:
            return bullet_text
            
        # If Gemini is available, use it
        if self.gemini_available:
            try:
                prompt = f"""
                Transform the following bulleted list into cohesive paragraphs.
                
                BULLETED LIST:
                ```
                {bullet_text}
                ```
                
                Guidelines:
                - Combine related bullets into logical paragraphs
                - Add transitions between ideas
                - Ensure logical flow and coherence
                - Maintain all the key information from the bullets
                - Create a professional writing style
                
                Please provide ONLY the paragraph text with no additional explanation.
                """
                
                # Generate paragraph text
                paragraph_text = self.gemini.generate_text(prompt, temperature=0.3)
                
                # Clean up any markdown code blocks or unnecessary text
                paragraph_text = re.sub(r'```.*?\n', '', paragraph_text)
                paragraph_text = re.sub(r'```', '', paragraph_text)
                
                return paragraph_text.strip()
                
            except Exception as e:
                logger.error(f"Error generating paragraphs with Gemini: {str(e)}")
                # Fall back to basic paragraph generation
                
        # Basic fallback: strip bullet points and join text
        # Extract bullet items
        bullet_items = re.findall(r'[•\-*]\s*([^\n]+)', bullet_text)
        if not bullet_items:
            # If no bullet pattern found, split by lines
            bullet_items = [line.strip() for line in bullet_text.split('\n') if line.strip()]
            
        # Join items into a paragraph
        paragraph = ' '.join(bullet_items)
        return paragraph
        
    def rephrase_text(self, text, tone=None):
        """
        Rephrase text while maintaining meaning
        
        Args:
            text (str): Text to rephrase
            tone (str, optional): Desired tone (formal, casual, persuasive, etc.)
            
        Returns:
            str: Rephrased text
        """
        if not text:
            return text
            
        # Use default tone if none specified
        tone = tone or "neutral"
            
        # If Gemini is available, use it
        if self.gemini_available:
            try:
                prompt = f"""
                Rephrase the following text in a {tone} tone, while maintaining the original meaning.
                
                ORIGINAL TEXT:
                ```
                {text}
                ```
                
                Guidelines for {tone} tone:
                """
                
                # Add tone-specific guidelines
                if tone.lower() == "formal":
                    prompt += """
                    - Use sophisticated vocabulary
                    - Avoid contractions and slang
                    - Use complex sentence structures
                    - Maintain professional distance
                    - Use third-person perspective
                    """
                elif tone.lower() == "casual":
                    prompt += """
                    - Use conversational language
                    - Use contractions (e.g., don't, can't)
                    - Include some colloquial expressions
                    - Use simpler, more direct sentences
                    - Be friendly and approachable
                    """
                elif tone.lower() == "persuasive":
                    prompt += """
                    - Use compelling, confident language
                    - Include rhetorical questions
                    - Use strong, decisive words
                    - Appeal to emotion and logic
                    - Include calls to action
                    """
                else:
                    # Default neutral tone
                    prompt += """
                    - Use balanced, straightforward language
                    - Avoid extreme expressions or emotion
                    - Present information objectively
                    - Use a mix of sentence structures
                    - Focus on clarity and precision
                    """
                    
                prompt += """
                
                Please provide ONLY the rephrased text with no additional explanation.
                """
                
                # Generate rephrased text
                rephrased_text = self.gemini.generate_text(prompt, temperature=0.4)
                
                # Clean up any markdown code blocks or unnecessary text
                rephrased_text = re.sub(r'```.*?\n', '', rephrased_text)
                rephrased_text = re.sub(r'```', '', rephrased_text)
                
                return rephrased_text.strip()
                
            except Exception as e:
                logger.error(f"Error rephrasing text with Gemini: {str(e)}")
                # Fall back to original text
                return text
                
        # If Gemini is not available or failed, return original text
        return text 