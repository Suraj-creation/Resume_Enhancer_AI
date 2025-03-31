"""
Gemini Feedback Utilities

This module provides functions for generating personalized feedback and quick fixes
using Gemini AI for resume enhancement and job matching.
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Union

def generate_gemini_feedback_for_resume(resume_text: str, resume_sections: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Generate structured feedback for resume using Gemini AI
    
    Args:
        resume_text: The full resume text
        resume_sections: Dictionary of resume sections (optional)
    
    Returns:
        Dictionary containing overall and section-specific feedback
    """
    print(f"Generating Gemini feedback for resume: {len(resume_text)} chars")
    try:
        # Import the service manager
        from utils.ai_services.service_manager import AIServiceManager
        
        # Get the Gemini service
        service_manager = AIServiceManager()
        gemini_service = service_manager.get_service("gemini")
        
        if not gemini_service:
            print("Gemini service not available")
            return {
                "overall": {
                    "overall_assessment": "AI-powered feedback unavailable. Please check your Gemini API configuration."
                }
            }
        
        # Create feedback structure
        feedback = {
            "overall": {},
            "sections": {}
        }
        
        # Check resume grammar
        print("Checking resume grammar...")
        grammar_feedback = gemini_service.check_grammar(resume_text)
        if grammar_feedback:
            feedback["overall"] = grammar_feedback
        
        # If we have sections, analyze each one
        if resume_sections:
            print(f"Analyzing {len(resume_sections)} resume sections...")
            
            # Process only these standard sections
            standard_sections = ["summary", "experience", "education", "skills", "projects"]
            
            for section_name, section_content in resume_sections.items():
                # Skip the full_text section and empty sections
                if section_name == "full_text" or not section_content.strip():
                    continue
                
                # Process only standard sections
                if section_name.lower() not in standard_sections:
                    continue
                
                print(f"Analyzing section: {section_name}")
                
                try:
                    # Get quality analysis for this section
                    section_analysis = gemini_service.analyze_section_quality(
                        section_name=section_name,
                        section_content=section_content
                    )
                    
                    # Store the analysis
                    feedback["sections"][section_name] = section_analysis
                    print(f"Completed analysis for {section_name}")
                except Exception as e:
                    print(f"Error analyzing section {section_name}: {str(e)}")
                    feedback["sections"][section_name] = {
                        "strengths": "Error analyzing this section.",
                        "weaknesses": "Unable to provide detailed feedback.",
                        "suggestions": "Try again or check your Gemini API configuration."
                    }
        else:
            print("No resume sections provided for detailed analysis")
            
        print("Feedback generation complete")
        return feedback
    
    except Exception as e:
        import traceback
        print(f"Error in generate_gemini_feedback_for_resume: {str(e)}")
        print(traceback.format_exc())
        
        return {
            "overall": {
                "overall_assessment": f"Error generating feedback: {str(e)}. Please check your API configuration."
            }
        }

def generate_gemini_feedback_for_job_match(resume_text: str, job_description: str, resume_sections: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Generate job-specific feedback for a resume using Gemini AI
    
    Args:
        resume_text: The full text of the resume
        job_description: The job description to match against
        resume_sections: Optional dictionary of resume sections
        
    Returns:
        Dict: Feedback data structure with overall match assessment and section-specific feedback
    """
    try:
        # Import gemini service
        from utils.ai_services.service_manager import AIServiceManager
        service_manager = AIServiceManager()
        gemini_service = service_manager.get_service("gemini")
        
        if not gemini_service:
            print("Gemini service not available")
            return None
        
        # If sections not provided, extract them
        if not resume_sections:
            resume_sections = gemini_service.extract_resume_sections(resume_text)
        
        # Generate job-specific feedback
        gemini_job_feedback = {
            "sections": {},
            "overall": {}
        }
        
        # Get overall resume-to-job match feedback
        match_result = gemini_service.match_resume_to_job(resume_sections, job_description)
        gemini_job_feedback["overall"] = {
            "match_percentage": match_result.get("match_percentage", 0),
            "matching_skills": match_result.get("matching_skills", []),
            "missing_skills": match_result.get("missing_skills", []),
            "recommendations": match_result.get("recommendations", "")
        }
        
        # Process each section for job-specific feedback
        for section_name, section_content in resume_sections.items():
            if section_name in ["summary", "experience", "education", "skills", "projects"] and section_content and section_content != "Missing":
                # Generate enhanced version tailored to the job
                section_analysis = gemini_service.enhance_resume_section(
                    section_name, 
                    section_content,
                    job_description
                )
                gemini_job_feedback["sections"][section_name] = section_analysis
        
        return gemini_job_feedback
    
    except Exception as e:
        print(f"Error generating Gemini job feedback: {str(e)}")
        return None

def display_gemini_feedback(gemini_feedback: Dict[str, Any], section_content: Dict[str, str] = None) -> None:
    """
    Display Gemini-powered feedback in Streamlit UI
    
    Args:
        gemini_feedback: The feedback data structure
        section_content: Optional dictionary of original section content
    """
    if not gemini_feedback:
        st.info("AI-powered personalized feedback is not available. Using basic feedback.")
        return
    
    # Display overall assessment
    if "overall" in gemini_feedback:
        overall = gemini_feedback["overall"]
        
        st.markdown("### 🔍 Overall Assessment")
        
        if "overall_assessment" in overall:
            st.markdown(f"""
            <div style="padding: 15px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 15px;">
                {overall["overall_assessment"]}
            </div>
            """, unsafe_allow_html=True)
        
        # Display issues if available
        if "issues" in overall and overall["issues"]:
            st.markdown("#### Grammar & Style Issues")
            for i, issue in enumerate(overall["issues"]):
                if isinstance(issue, dict) and "text" in issue and "correction" in issue:
                    st.markdown(f"""
                    <div style="margin-bottom: 10px; padding: 10px; border-left: 4px solid #ef5350; background-color: #ffebee;">
                        <strong>Issue {i+1}:</strong> "{issue['text']}"<br>
                        <strong>Correction:</strong> {issue['correction']}<br>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Quick fix button for all grammar issues
            if st.button("🔍 Fix All Grammar Issues with AI", key="gemini_fix_grammar"):
                try:
                    # Import gemini service
                    from utils.ai_services.service_manager import AIServiceManager
                    service_manager = AIServiceManager()
                    gemini_service = service_manager.get_service("gemini")
                    
                    if gemini_service:
                        # Create a prompt to fix all grammar issues
                        fixed_text = gemini_service.generate_text(
                            f"""
                            Fix all grammar, spelling, and style issues in the following resume text:
                            
                            ```
                            {section_content.get('full_text', '')}
                            ```
                            
                            Return ONLY the corrected text with no explanations or additional information.
                            """
                        )
                        st.session_state.fixed_text = fixed_text
                        st.success("All grammar issues fixed with AI!")
                    else:
                        st.error("Gemini service not available. Unable to fix grammar issues.")
                except Exception as e:
                    st.error(f"Error fixing grammar issues: {str(e)}")
    
    # Section-specific feedback
    if "sections" in gemini_feedback and gemini_feedback["sections"]:
        st.markdown("### 📝 Section-by-Section Feedback")
        
        # Create tabs for each section's feedback
        section_names = list(gemini_feedback["sections"].keys())
        if section_names:
            section_tabs = st.tabs([s.title() for s in section_names])
            
            # Set up the AI service for quick fixes
            try:
                from utils.ai_services.service_manager import AIServiceManager
                service_manager = AIServiceManager()
                gemini_service = service_manager.get_service("gemini")
            except Exception as e:
                gemini_service = None
                print(f"Error setting up Gemini service: {str(e)}")
            
            # Display each section's feedback in its tab
            for i, section_name in enumerate(section_names):
                section_data = gemini_feedback["sections"][section_name]
                original_content = section_content.get(section_name, "") if section_content else ""
                
                with section_tabs[i]:
                    # Create columns for original content and feedback
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("##### 📋 Original Content")
                        if original_content:
                            st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:5px;'>{original_content}</div>", unsafe_allow_html=True)
                        else:
                            st.info(f"No content available for {section_name} section")
                    
                    with col2:
                        st.markdown("##### 💡 AI Feedback")
                        
                        # Display strengths if available
                        if isinstance(section_data, dict) and "strengths" in section_data:
                            with st.expander("💪 Strengths", expanded=True):
                                st.markdown(section_data["strengths"])
                        
                        # Display weaknesses if available
                        if isinstance(section_data, dict) and "weaknesses" in section_data:
                            with st.expander("🔧 Areas for Improvement", expanded=True):
                                st.markdown(section_data["weaknesses"])
                        
                        # Display suggestions if available
                        if isinstance(section_data, dict) and "suggestions" in section_data:
                            with st.expander("💡 Specific Suggestions", expanded=True):
                                st.markdown(section_data["suggestions"])
                        # If it's not a dict or doesn't have these keys, just display the data
                        elif not isinstance(section_data, dict):
                            st.markdown(section_data)
                    
                    # Quick fix button for this section
                    if gemini_service and original_content:
                        if st.button(f"✨ Enhance {section_name.title()} with AI", key=f"enhance_{section_name}"):
                            try:
                                # Get improved section from Gemini
                                enhanced_section = apply_gemini_quick_fix(section_name, original_content)
                                
                                # Store the enhanced section in session state
                                if "enhanced_sections" not in st.session_state:
                                    st.session_state.enhanced_sections = {}
                                    
                                st.session_state.enhanced_sections[section_name] = enhanced_section
                                
                                # Display the enhanced version
                                st.markdown("##### ✅ Enhanced Version")
                                if isinstance(enhanced_section, dict) and "enhanced_content" in enhanced_section:
                                    st.markdown(f"""
                                    <div style='padding:15px;background-color:#e6f4ea;border-radius:5px;border-left:4px solid #34a853;'>
                                        {enhanced_section["enhanced_content"]}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if "suggestions" in enhanced_section:
                                        st.markdown("**Improvements Made:**")
                                        st.markdown(enhanced_section["suggestions"])
                                else:
                                    st.markdown(f"""
                                    <div style='padding:15px;background-color:#e6f4ea;border-radius:5px;border-left:4px solid #34a853;'>
                                        {enhanced_section}
                                    </div>
                                    """, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error enhancing section: {str(e)}")
            
            # Add a button to apply all enhancements
            if st.button("Apply All Section Enhancements", key="apply_all_enhancements"):
                if "enhanced_sections" in st.session_state and st.session_state.enhanced_sections:
                    # Combine all enhanced sections into a single document
                    all_sections = {}
                    for s_name, s_content in section_content.items():
                        if s_name in st.session_state.enhanced_sections:
                            enhanced = st.session_state.enhanced_sections[s_name]
                            if isinstance(enhanced, dict) and "enhanced_content" in enhanced:
                                all_sections[s_name] = enhanced["enhanced_content"]
                            else:
                                all_sections[s_name] = enhanced
                        else:
                            all_sections[s_name] = s_content
                    
                    # Convert to text and store
                    enhanced_text = "\n\n".join([
                        f"# {s_name.upper()}\n{s_content}" 
                        for s_name, s_content in all_sections.items()
                        if s_content and s_name not in ["full_text"]
                    ])
                    
                    st.session_state.fixed_text = enhanced_text
                    st.success("All enhancements applied!")
                else:
                    st.warning("No sections have been enhanced yet. Use the 'Enhance' buttons to improve sections first.")

def apply_gemini_quick_fix(section_name: str, section_content: str, job_description: str = None) -> Union[str, Dict[str, str]]:
    """
    Apply a quick fix to a resume section using Gemini AI
    
    Args:
        section_name: Name of the section (summary, experience, etc.)
        section_content: The content of the section
        job_description: Optional job description for tailoring
    
    Returns:
        Either enhanced content as string or dictionary with enhanced_content and suggestions
    """
    try:
        # Import the service manager
        from utils.ai_services.service_manager import AIServiceManager
        
        # Get the Gemini service
        service_manager = AIServiceManager()
        gemini_service = service_manager.get_service("gemini")
        
        if not gemini_service:
            return f"Error: Gemini service not available. Unable to enhance {section_name}."
        
        # Use the enhance_resume_section method which returns enhanced content and suggestions
        result = gemini_service.enhance_resume_section(section_name, section_content, job_description)
        
        # If result is a dict with enhanced_content, return it directly
        if isinstance(result, dict) and "enhanced_content" in result:
            return result
        
        # If it's just a string, wrap it in a dict
        if isinstance(result, str):
            return {
                "enhanced_content": result,
                "suggestions": "Content has been professionally enhanced to highlight your qualifications."
            }
            
        return result
    except Exception as e:
        import traceback
        print(f"Error in apply_gemini_quick_fix: {str(e)}")
        print(traceback.format_exc())
        return f"Error enhancing {section_name}: {str(e)}"

def display_gemini_job_feedback(gemini_job_feedback: Dict[str, Any], resume_sections: Dict[str, str]) -> None:
    """
    Display Gemini-powered job match feedback in Streamlit UI
    
    Args:
        gemini_job_feedback: The job feedback data structure
        resume_sections: Dictionary of original resume sections
    """
    if not gemini_job_feedback:
        st.info("AI-powered job match feedback is not available. Using basic match analysis.")
        return
    
    # Overall job match assessment
    if "overall" in gemini_job_feedback:
        overall = gemini_job_feedback["overall"]
        
        # Display overall assessment
        st.markdown("#### 🎯 Overall Job Match Assessment")
        
        match_percentage = overall.get("match_percentage", 0)
        if isinstance(match_percentage, str):
            try:
                match_percentage = int(match_percentage.strip("%"))
            except:
                match_percentage = 0
        
        # Create progress bar for match percentage
        st.progress(match_percentage / 100)
        st.markdown(f"**Match score: {match_percentage}%**")
        
        # Display matching skills
        if "matching_skills" in overall and overall["matching_skills"]:
            st.markdown("**✅ Matching Skills:**")
            for skill in overall["matching_skills"]:
                st.markdown(f"- {skill}")
        
        # Display missing skills
        if "missing_skills" in overall and overall["missing_skills"]:
            st.markdown("**❌ Missing Skills:**")
            for skill in overall["missing_skills"]:
                st.markdown(f"- {skill}")
        
        # Display overall recommendations
        if "recommendations" in overall and overall["recommendations"]:
            st.markdown("**💡 Overall Recommendations:**")
            st.markdown(overall["recommendations"])
    
    # Section-specific feedback
    if "sections" in gemini_job_feedback and gemini_job_feedback["sections"]:
        st.markdown("#### 📝 Section-by-Section Job Match Feedback")
        
        # Create tabs for each section's feedback
        section_names = list(gemini_job_feedback["sections"].keys())
        if section_names:
            section_tabs = st.tabs([s.title() for s in section_names])
            
            # Set up the AI service for quick fixes
            try:
                from utils.ai_services.service_manager import AIServiceManager
                service_manager = AIServiceManager()
                gemini_service = service_manager.get_service("gemini")
            except Exception as e:
                gemini_service = None
                print(f"Error setting up Gemini service: {str(e)}")
            
            # Display each section's feedback in its tab
            for i, section_name in enumerate(section_names):
                section_data = gemini_job_feedback["sections"][section_name]
                section_content = resume_sections.get(section_name, "")
                
                with section_tabs[i]:
                    # Display section feedback
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("##### 📋 Original Content")
                        st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:5px;'>{section_content}</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("##### 💡 Job-Tailored Suggestions")
                        if isinstance(section_data, dict):
                            if "suggestions" in section_data:
                                st.markdown(section_data["suggestions"])
                        else:
                            st.markdown(section_data)
                    
                    # Quick fix button for this section
                    if gemini_service and section_content:
                        if st.button(f"✨ Auto-Tailor {section_name.title()} to Job", key=f"tailor_{section_name}"):
                            try:
                                # Get job-tailored section from Gemini
                                enhanced_section = gemini_service.generate_text(
                                    f"""
                                    As an expert resume writer, rewrite the following {section_name} section to perfectly match this job description.
                                    Add relevant keywords from the job, use appropriate terminology, and highlight relevant experiences.
                                    Keep the same factual information, but optimize the wording, structure, and emphasis.
                                    
                                    SECTION CONTENT:
                                    {section_content}
                                    
                                    JOB DESCRIPTION:
                                    {st.session_state.job_description}
                                    
                                    Return ONLY the improved section with no explanations.
                                    """
                                )
                                
                                # Store the enhanced section in session state
                                if "job_enhanced_sections" not in st.session_state:
                                    st.session_state.job_enhanced_sections = {}
                                    
                                st.session_state.job_enhanced_sections[section_name] = enhanced_section
                                
                                # Display the enhanced version
                                st.markdown("##### ✅ Job-Tailored Version")
                                st.markdown(f"""
                                <div style='padding:15px;background-color:#e6f4ea;border-radius:5px;border-left:4px solid #34a853;'>
                                    {enhanced_section}
                                </div>
                                """, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error tailoring section: {str(e)}") 