import re
import os
from typing import List, Dict, Any, Optional
import random

def check_grammar(text: str) -> List[Dict[str, Any]]:
    """
    Check for grammar issues in the text
    
    Args:
        text: The text to check
        
    Returns:
        List[Dict]: List of grammar issues with text, suggestion, and position
    """
    # This is a simplified version - in production, use a proper grammar checker like language_tool_python
    issues = []
    
    # Common grammar issues
    grammar_patterns = [
        {"pattern": r"\b(i|we|they|he|she|it)\s+(is|are|was|were|have|has|do|does)\b", 
         "fix": lambda m: m.group(1).capitalize() + " " + m.group(2),
         "reason": "Capitalize the first word of sentences"},
        
        {"pattern": r"\b(team leaded|team headed)\b", 
         "fix": "team led",
         "reason": "Correct verb form"},
        
        {"pattern": r"\bresponsable\b", 
         "fix": "responsible",
         "reason": "Correct spelling"},
        
        {"pattern": r"\b(their|they're|there)\b", 
         "fix": None,  # Need context to determine correct form
         "reason": "Check usage of their/they're/there"},
        
        {"pattern": r"\b(your|you're)\b", 
         "fix": None,  # Need context to determine correct form
         "reason": "Check usage of your/you're"},
        
        {"pattern": r"\b(its|it's)\b", 
         "fix": None,  # Need context to determine correct form
         "reason": "Check usage of its/it's"},
        
        {"pattern": r"\ba\s+[aeiou]", 
         "fix": lambda m: "an" + m.group(0)[1:],
         "reason": "Use 'an' before words starting with vowels"},
        
        {"pattern": r"\b(i|we|they|he|she|it)\s+have\s+been\b", 
         "fix": lambda m: m.group(1).capitalize() + " have been",
         "reason": "Capitalize the start of sentences"},
        
        {"pattern": r",\s*and\s+", 
         "fix": " and ",
         "reason": "No comma needed before 'and'"},
        
        {"pattern": r"\s+,\s*", 
         "fix": ", ",
         "reason": "No space before comma"},
    ]
    
    # Check each pattern
    for grammar_rule in grammar_patterns:
        for match in re.finditer(grammar_rule["pattern"], text, re.IGNORECASE):
            # Get the matched text
            matched_text = match.group(0)
            
            # Determine suggestion
            if callable(grammar_rule.get("fix")):
                suggestion = grammar_rule["fix"](match)
            else:
                suggestion = grammar_rule.get("fix", matched_text)
                
            # Add to issues if we have a fix
            if suggestion and suggestion != matched_text:
                issues.append({
                    "text": matched_text,
                    "suggestion": suggestion,
                    "reason": grammar_rule["reason"],
                    "start": match.start(),
                    "end": match.end()
                })
            elif grammar_rule.get("reason"):
                # Add even if we don't have a specific fix but have a reason
                issues.append({
                    "text": matched_text,
                    "suggestion": grammar_rule["reason"],
                    "reason": grammar_rule["reason"],
                    "start": match.start(),
                    "end": match.end()
                })
    
    # Additional random grammar issues for demo purposes
    if len(issues) < 3:
        # Add some sample issues if not enough were found
        sample_issues = [
            {"text": "Im", "suggestion": "I'm", "reason": "Use apostrophe for contractions"},
            {"text": "dont", "suggestion": "don't", "reason": "Use apostrophe for contractions"},
            {"text": "theyre", "suggestion": "they're", "reason": "Use apostrophe for contractions"},
            {"text": "a lot", "suggestion": "a lot", "reason": "'A lot' is two words"},
            {"text": "i worked", "suggestion": "I worked", "reason": "Capitalize 'I'"}
        ]
        
        for issue in sample_issues:
            if issue["text"].lower() in text.lower() and len(issues) < 4:
                # Find the position
                pos = text.lower().find(issue["text"].lower())
                if pos != -1:
                    issues.append({
                        "text": text[pos:pos+len(issue["text"])],
                        "suggestion": issue["suggestion"],
                        "reason": issue["reason"],
                        "start": pos,
                        "end": pos + len(issue["text"])
                    })
    
    return issues

def check_formatting_issues(text: str, file_path: str) -> List[Dict[str, Any]]:
    """
    Check for formatting issues in the resume
    
    Args:
        text: The text content of the resume
        file_path: Path to the resume file
        
    Returns:
        List[Dict]: List of formatting issues with text, suggestion, and position
    """
    issues = []
    
    # Check for extremely long paragraphs
    paragraphs = text.split('\n\n')
    for i, para in enumerate(paragraphs):
        if len(para.split()) > 100:
            # Find the position in the original text
            pos = 0
            for j in range(i):
                pos += len(paragraphs[j]) + 2  # +2 for the \n\n
                
            issues.append({
                "text": "Extremely long paragraph",
                "suggestion": "Break this into smaller paragraphs for better readability",
                "start": pos,
                "end": pos + len(para),
                "paragraph_index": i
            })
    
    # Check for inconsistent spacing
    space_matches = list(re.finditer(r'([^\n])\n([^\n])', text))
    for match in space_matches:
        issues.append({
            "text": match.group(0),
            "suggestion": "Use consistent spacing (double line breaks between sections)",
            "start": match.start(),
            "end": match.end()
        })
    
    # Check for excessive bullet points
    bullet_count = len(re.findall(r'•|\*|\-|\+', text))
    if bullet_count > 30:
        issues.append({
            "text": "Excessive bullet points",
            "suggestion": f"Reduce the number of bullet points ({bullet_count} found) for better focus",
            "start": 0,
            "end": 10
        })
    
    # Check for font inconsistency (for PDFs)
    if file_path.lower().endswith('.pdf'):
        # In a real implementation, use a PDF library to check fonts
        # For this example, we'll simulate it
        issues.append({
            "text": "Potential font inconsistency",
            "suggestion": "Use consistent fonts throughout your resume (1-2 fonts maximum)",
            "start": 0,
            "end": 10
        })
    
    # Check for ATS-unfriendly elements
    if file_path.lower().endswith('.pdf'):
        # In a real implementation, check for tables, images, etc.
        issues.append({
            "text": "Possible ATS-unfriendly elements",
            "suggestion": "Avoid tables, columns, headers/footers, and images for ATS compatibility",
            "start": 0,
            "end": 10
        })
    
    return issues

def apply_grammar_fixes(text: str, grammar_issues: List[Dict[str, Any]]) -> str:
    """
    Apply automatic grammar fixes to the text
    
    Args:
        text: The original text
        grammar_issues: List of grammar issues to fix
        
    Returns:
        str: The text with grammar issues fixed
    """
    fixed_text = text
    
    # Sort issues by position (end to beginning to maintain indices)
    sorted_issues = sorted(grammar_issues, key=lambda x: x.get('start', 0), reverse=True)
    
    # Apply fixes from end to beginning to maintain correct indices
    for issue in sorted_issues:
        if 'start' in issue and 'end' in issue and 'suggestion' in issue:
            before = fixed_text[:issue['start']]
            after = fixed_text[issue['end']:]
            fixed_text = before + issue['suggestion'] + after
        else:
            # For issues without position, try simple replacement
            fixed_text = fixed_text.replace(issue['text'], issue['suggestion'])
    
    return fixed_text

def strengthen_weak_phrases(text: str, suggestions: List[Dict[str, Any]]) -> str:
    """
    Strengthen weak phrases in the text
    
    Args:
        text: The original text
        suggestions: List of improvement suggestions
        
    Returns:
        str: The text with strengthened phrases
    """
    strengthened_text = text
    
    # Dictionary of common weak phrases and their stronger alternatives
    replacements = {
        "responsible for": "managed",
        "worked on": "developed",
        "worked with": "collaborated with",
        "helped": "facilitated",
        "assisted": "supported",
        "duties include": "achievements include",
        "duties included": "key contributions included",
        "good communication": "effective communication",
        "excellent communication": "outstanding communication",
        "team player": "collaborative professional",
        "hard working": "dedicated",
        "hard-working": "committed",
        "various": "specific",
        "different": "diverse",
        "etc": ""
    }
    
    # Apply replacements
    for weak, strong in replacements.items():
        strengthened_text = re.sub(r'\b' + re.escape(weak) + r'\b', strong, strengthened_text, flags=re.IGNORECASE)
    
    return strengthened_text

def add_missing_section_templates(text: str, missing_sections: List[str]) -> str:
    """
    Add templates for missing sections
    
    Args:
        text: The original text
        missing_sections: List of missing section names
        
    Returns:
        str: The text with added section templates
    """
    enhanced_text = text
    
    # Templates for common sections
    section_templates = {
        "summary": "\n\nPROFESSIONAL SUMMARY\n" +
                  "Experienced professional with expertise in [key skill] and [key skill]. " +
                  "Proven track record of [achievement] and [achievement]. " +
                  "Seeking to leverage my skills in [area] to contribute to [target role/company].",
        
        "experience": "\n\nPROFESSIONAL EXPERIENCE\n" +
                     "[Company Name], [Location] — [Job Title]\n" +
                     "[Start Date] - [End Date]\n" +
                     "• Achieved [specific result] by implementing [action/strategy]\n" +
                     "• Led [project/initiative] resulting in [measurable outcome]\n" +
                     "• Collaborated with [stakeholders] to deliver [result]",
        
        "education": "\n\nEDUCATION\n" +
                    "[University Name], [Location] — [Degree]\n" +
                    "[Graduation Date]\n" +
                    "• GPA: [GPA] / 4.0\n" +
                    "• Relevant Coursework: [Course 1], [Course 2], [Course 3]",
        
        "skills": "\n\nSKILLS\n" +
                 "• Technical Skills: [Skill 1], [Skill 2], [Skill 3]\n" +
                 "• Software: [Software 1], [Software 2], [Software 3]\n" +
                 "• Soft Skills: [Skill 1], [Skill 2], [Skill 3]",
        
        "projects": "\n\nPROJECTS\n" +
                   "[Project Name]\n" +
                   "• Developed [what you built] using [technologies/tools]\n" +
                   "• Implemented [feature/functionality] to solve [problem]\n" +
                   "• Resulted in [outcome/impact]",
        
        "certifications": "\n\nCERTIFICATIONS\n" +
                         "• [Certification Name], [Issuing Organization], [Date]\n" +
                         "• [Certification Name], [Issuing Organization], [Date]",
        
        "languages": "\n\nLANGUAGES\n" +
                    "• English (Native/Fluent)\n" +
                    "• [Language 2] (Proficiency Level)\n",
        
        "interests": "\n\nINTERESTS\n" +
                    "• [Interest 1], [Interest 2], [Interest 3]"
    }
    
    # Add each missing section template
    for section in missing_sections:
        if section in section_templates:
            enhanced_text += section_templates[section]
    
    return enhanced_text

def fix_formatting_issues(text: str, formatting_issues: List[Dict[str, Any]]) -> str:
    """
    Fix formatting issues in the text
    
    Args:
        text: The original text
        formatting_issues: List of formatting issues
        
    Returns:
        str: The text with formatting issues fixed
    """
    fixed_text = text
    
    # Replace inconsistent spacing
    fixed_text = re.sub(r'([^\n])\n([^\n])', r'\1\n\n\2', fixed_text)
    
    # Break long paragraphs
    paragraphs = fixed_text.split('\n\n')
    for i, para in enumerate(paragraphs):
        if len(para.split()) > 100:
            # Split paragraph after approximately 50 words
            words = para.split()
            mid_point = len(words) // 2
            # Try to find a period or comma near the midpoint for better splitting
            split_point = mid_point
            for j in range(mid_point - 10, mid_point + 10):
                if j < len(words) and j >= 0 and (words[j].endswith('.') or words[j].endswith(',')):
                    split_point = j + 1
                    break
            
            first_half = ' '.join(words[:split_point])
            second_half = ' '.join(words[split_point:])
            paragraphs[i] = first_half + '\n\n' + second_half
    
    fixed_text = '\n\n'.join(paragraphs)
    
    return fixed_text

def optimize_for_ats(text: str) -> str:
    """
    Optimize the resume for ATS systems
    
    Args:
        text: The original text
        
    Returns:
        str: The text optimized for ATS
    """
    optimized_text = text
    
    # Convert to plain text format
    optimized_text = re.sub(r'[^\w\s.,():;/\\-]', '', optimized_text)
    
    # Ensure consistent section headers (all caps, followed by line break)
    section_headers = ["SUMMARY", "EXPERIENCE", "EDUCATION", "SKILLS", "PROJECTS", 
                      "CERTIFICATIONS", "LANGUAGES", "INTERESTS"]
    
    # Standardize common section headers
    for header in section_headers:
        # Find variations of the header (case-insensitive, possibly with other characters)
        pattern = r'(?i)([^\n]*\b' + re.escape(header) + r'\b[^\n]*)'
        
        # Replace with standardized version
        replacements = re.findall(pattern, optimized_text)
        for replacement in replacements:
            optimized_text = optimized_text.replace(replacement, "\n\n" + header + "\n")
    
    # Remove multiple consecutive line breaks
    optimized_text = re.sub(r'\n{3,}', '\n\n', optimized_text)
    
    # Ensure consistent bullet points (use standard bullet character)
    bullet_variations = ['-', '•', '*', '+', '>', '→']
    for bullet in bullet_variations:
        optimized_text = optimized_text.replace(bullet + ' ', '• ')
    
    return optimized_text 