import streamlit as st
import sys
import os
from utils.rich_text_editor import rich_text_editor, quill_editor
from utils.highlight_utils import highlight_keywords, highlight_with_feedback, extract_keywords_from_text, find_improvement_suggestions, pdf_annotator

# Add the parent directory to the path for module imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# Import the main function from _resume_enhancer.py
from pages._resume_enhancer import main as resume_enhancer_main

# Import the main logic from parent module but enhance with rich text editing
from resume_enhancer import main as base_main

def main():
    """
    Enhanced version of the resume enhancer that uses rich text editing
    capabilities for a better user experience.
    """
    # Check if we're in the enhancement step
    if "current_step" in st.session_state and st.session_state.current_step == 4:
        # Override the enhancement step with rich text editing
        handle_resume_enhancement_with_rich_text()
    else:
        # Use the base implementation for other steps
        base_main()

def handle_resume_enhancement_with_rich_text():
    """Handle the resume enhancement process with rich text editing capabilities"""
    st.markdown("<h1 class='main-header'>Enhance Your Resume</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Step 4: Edit and improve your resume with our rich text editor</p>", unsafe_allow_html=True)
    
    if "extracted_sections" not in st.session_state or not st.session_state.extracted_sections:
        st.warning("Please complete the extraction step first.")
        if st.button("Go Back to Extract"):
            st.session_state.current_step = 2
        return
    
    # Get the extracted sections
    extracted_sections = st.session_state.extracted_sections
    
    st.write("### Edit and Enhance Your Resume")
    st.write("Use the editors below to refine your resume content. The AI has extracted the content and provided suggestions for improvements.")
    
    # Add job description field for keyword targeting (optional)
    with st.expander("Add Job Description for Targeted Enhancement"):
        job_description = st.text_area("Enter Job Description (Optional)",
                        "Paste a job description here to get targeted keywords and suggestions",
                        height=150)
        
        if job_description and job_description != "Paste a job description here to get targeted keywords and suggestions":
            # Extract keywords from job description
            job_keywords = extract_keywords_from_text(job_description, 15)
            st.write(f"**Detected Keywords:** {', '.join(job_keywords)}")
            st.session_state.job_keywords = job_keywords
            st.session_state.job_description = job_description
        else:
            st.session_state.job_keywords = []
            st.session_state.job_description = ""
    
    # Create a tab for each section, including a new PDF Annotations tab
    tabs = st.tabs(["Summary", "Experience", "Education", "Skills", "Additional Sections", "PDF Annotations"])
    
    # If enhanced resume doesn't exist in session state, initialize it
    if "enhanced_resume" not in st.session_state or st.session_state.enhanced_resume is None:
        st.session_state.enhanced_resume = {
            "summary": extracted_sections.get("summary", ""),
            "experience": extracted_sections.get("experience", ""),
            "education": extracted_sections.get("education", ""),
            "skills": extracted_sections.get("skills", ""),
            "additional": ""
        }
    
    # Summary tab
    with tabs[0]:
        st.markdown("#### Professional Summary")
        st.info("A strong summary highlights your most relevant skills and experience in 3-5 sentences.")
        
        # Get the original summary
        original_summary = extracted_sections.get("summary", "")
        
        # Get AI suggestions
        ai_suggestions = get_ai_suggestions("summary", original_summary)
        
        # Get keywords to highlight
        keywords = st.session_state.get("job_keywords", [])
        
        # Find improvement suggestions
        improvement_suggestions = find_improvement_suggestions(
            original_summary, 
            st.session_state.get("job_description", "")
        )
        
        # Display the interactive highlighted content first
        if keywords or improvement_suggestions:
            st.markdown("**Interactive Analysis:**")
            highlight_with_feedback(
                original_summary, 
                keywords, 
                improvement_suggestions,
                height=200,
                key="summary_highlight"
            )
        
        # Display original and suggestions in columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Summary:**")
            st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:5px;'>{original_summary}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**AI Suggestions:**")
            st.markdown(f"<div style='background-color:#e6f3ff;padding:10px;border-radius:5px;'>{ai_suggestions}</div>", unsafe_allow_html=True)
        
        # Rich text editor for editing the summary
        st.markdown("#### Edit Your Summary:")
        enhanced_summary = rich_text_editor(
            value=(st.session_state.enhanced_resume.get("summary") or original_summary),
            height=200,
            key="summary_editor"
        )
        
        # Update the enhanced resume in session state
        st.session_state.enhanced_resume["summary"] = enhanced_summary
    
    # Experience tab
    with tabs[1]:
        st.markdown("#### Professional Experience")
        st.info("Highlight accomplishments using action verbs and quantify results where possible.")
        
        # Get the original experience
        original_experience = extracted_sections.get("experience", "")
        
        # Get AI suggestions
        ai_suggestions = get_ai_suggestions("experience", original_experience)
        
        # Get keywords to highlight
        keywords = st.session_state.get("job_keywords", [])
        
        # Find improvement suggestions
        improvement_suggestions = find_improvement_suggestions(
            original_experience, 
            st.session_state.get("job_description", "")
        )
        
        # Display the interactive highlighted content first
        if keywords or improvement_suggestions:
            st.markdown("**Interactive Analysis:**")
            highlight_with_feedback(
                original_experience, 
                keywords, 
                improvement_suggestions,
                height=250,
                key="experience_highlight"
            )
        
        # Display original and suggestions in columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Experience:**")
            st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:5px;'>{original_experience}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**AI Suggestions:**")
            st.markdown(f"<div style='background-color:#e6f3ff;padding:10px;border-radius:5px;'>{ai_suggestions}</div>", unsafe_allow_html=True)
        
        # Rich text editor for editing the experience
        st.markdown("#### Edit Your Experience:")
        enhanced_experience = rich_text_editor(
            value=(st.session_state.enhanced_resume.get("experience") or original_experience),
            height=300,
            key="experience_editor"
        )
        
        # Update the enhanced resume in session state
        st.session_state.enhanced_resume["experience"] = enhanced_experience
    
    # Education tab
    with tabs[2]:
        st.markdown("#### Education")
        st.info("List your degrees in reverse chronological order with relevant coursework and achievements.")
        
        # Get the original education
        original_education = extracted_sections.get("education", "")
        
        # Get AI suggestions
        ai_suggestions = get_ai_suggestions("education", original_education)
        
        # Get keywords to highlight
        keywords = st.session_state.get("job_keywords", [])
        
        # Find improvement suggestions
        improvement_suggestions = find_improvement_suggestions(
            original_education, 
            st.session_state.get("job_description", "")
        )
        
        # Display the interactive highlighted content first
        if keywords or improvement_suggestions:
            st.markdown("**Interactive Analysis:**")
            highlight_with_feedback(
                original_education, 
                keywords, 
                improvement_suggestions,
                height=200,
                key="education_highlight"
            )
        
        # Display original and suggestions in columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Education:**")
            st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:5px;'>{original_education}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**AI Suggestions:**")
            st.markdown(f"<div style='background-color:#e6f3ff;padding:10px;border-radius:5px;'>{ai_suggestions}</div>", unsafe_allow_html=True)
        
        # Rich text editor for editing the education
        st.markdown("#### Edit Your Education:")
        enhanced_education = rich_text_editor(
            value=(st.session_state.enhanced_resume.get("education") or original_education),
            height=200,
            key="education_editor"
        )
        
        # Update the enhanced resume in session state
        st.session_state.enhanced_resume["education"] = enhanced_education
    
    # Skills tab
    with tabs[3]:
        st.markdown("#### Skills")
        st.info("Organize skills by category and include proficiency levels for technical skills.")
        
        # Get the original skills
        original_skills = extracted_sections.get("skills", "")
        
        # Get AI suggestions
        ai_suggestions = get_ai_suggestions("skills", original_skills)
        
        # Get keywords to highlight
        keywords = st.session_state.get("job_keywords", [])
        
        # Find improvement suggestions
        improvement_suggestions = find_improvement_suggestions(
            original_skills, 
            st.session_state.get("job_description", "")
        )
        
        # Display the interactive highlighted content first
        if keywords or improvement_suggestions:
            st.markdown("**Interactive Analysis:**")
            highlight_with_feedback(
                original_skills, 
                keywords, 
                improvement_suggestions,
                height=200,
                key="skills_highlight"
            )
        
        # Display original and suggestions in columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Skills:**")
            st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:5px;'>{original_skills}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**AI Suggestions:**")
            st.markdown(f"<div style='background-color:#e6f3ff;padding:10px;border-radius:5px;'>{ai_suggestions}</div>", unsafe_allow_html=True)
        
        # Rich text editor for editing the skills
        st.markdown("#### Edit Your Skills:")
        enhanced_skills = rich_text_editor(
            value=(st.session_state.enhanced_resume.get("skills") or original_skills),
            height=200,
            key="skills_editor"
        )
        
        # Update the enhanced resume in session state
        st.session_state.enhanced_resume["skills"] = enhanced_skills
    
    # Additional Sections tab
    with tabs[4]:
        st.markdown("#### Additional Sections")
        st.info("Include other relevant sections like Projects, Certifications, Languages, or Volunteer Work.")
        
        # Get the original additional sections
        original_additional = ""
        for section_name in ["projects", "certifications", "publications", "languages"]:
            section_content = extracted_sections.get(section_name, "")
            if section_content:
                original_additional += f"**{section_name.title()}:**\n{section_content}\n\n"
        
        # Get AI suggestions
        ai_suggestions = get_ai_suggestions("additional", original_additional)
        
        # Get keywords to highlight
        keywords = st.session_state.get("job_keywords", [])
        
        # Find improvement suggestions
        improvement_suggestions = find_improvement_suggestions(
            original_additional, 
            st.session_state.get("job_description", "")
        )
        
        # Display the interactive highlighted content first
        if keywords or improvement_suggestions:
            st.markdown("**Interactive Analysis:**")
            highlight_with_feedback(
                original_additional, 
                keywords, 
                improvement_suggestions,
                height=200,
                key="additional_highlight"
            )
        
        # Display original and suggestions in columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Additional Sections:**")
            st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:5px;'>{original_additional}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**AI Suggestions:**")
            st.markdown(f"<div style='background-color:#e6f3ff;padding:10px;border-radius:5px;'>{ai_suggestions}</div>", unsafe_allow_html=True)
        
        # Rich text editor for editing the additional sections
        st.markdown("#### Edit Your Additional Sections:")
        enhanced_additional = rich_text_editor(
            value=(st.session_state.enhanced_resume.get("additional") or original_additional),
            height=200,
            key="additional_editor"
        )
        
        # Update the enhanced resume in session state
        st.session_state.enhanced_resume["additional"] = enhanced_additional
    
    # PDF Annotations tab
    with tabs[5]:
        st.markdown("#### Annotate Original PDF Resume")
        st.info("Use this tool to highlight important parts of your original resume or add notes for future editing.")
        
        # Check if original PDF exists in session state
        if "uploaded_file" in st.session_state and st.session_state.uploaded_file:
            try:
                # Get the original PDF content
                pdf_content = st.session_state.uploaded_file.getvalue()
                
                # Get any existing annotations
                annotations = st.session_state.get("pdf_annotations", [])
                
                st.markdown("**Instructions:**")
                st.markdown("""
                1. Use the **Highlight** button to highlight important sections (click and drag)
                2. Use the **Add Note** button to add comments or suggestions
                3. Click **Save** to preserve your annotations
                """)
                
                # Display PDF annotator
                new_annotations = pdf_annotator(
                    pdf_content,
                    annotations=annotations,
                    height=600,
                    key="resume_pdf_annotator"
                )
                
                # Save annotations to session state
                st.session_state.pdf_annotations = new_annotations
                
                # Show annotation summary if there are any
                if new_annotations and len(new_annotations) > 0:
                    with st.expander("View Annotation Summary"):
                        st.markdown("#### Annotation Summary")
                        st.markdown(f"Total annotations: {len(new_annotations)}")
                        
                        for i, anno in enumerate(new_annotations):
                            if anno["type"] == "highlight":
                                st.markdown(f"**Highlight {i+1}:** At position ({anno['x']:.0f}, {anno['y']:.0f})")
                            elif anno["type"] == "note":
                                st.markdown(f"**Note {i+1}:** {anno['text']} - At position ({anno['x']:.0f}, {anno['y']:.0f})")
                
            except Exception as e:
                st.error(f"Error displaying PDF annotator: {str(e)}")
                st.info("Try re-uploading your resume in the upload step, or contact support if the issue persists.")
        else:
            st.warning("No PDF resume found. Please upload your resume in the upload step.")
            if st.button("Go to Upload Step"):
                st.session_state.current_step = 1
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Scoring"):
            st.session_state.current_step = 3
    
    with col3:
        if st.button("Proceed to Download →"):
            # Save the enhanced resume to session state
            st.session_state.current_step = 5

def get_ai_suggestions(section_type, original_content):
    """Generate AI suggestions for resume content improvement
    
    Args:
        section_type: Type of resume section
        original_content: Original content from the resume
        
    Returns:
        str: AI suggestions for improving the content
    """
    # In a real application, this would call an AI service
    # For demonstration, we'll return mock suggestions
    
    suggestions = {
        "summary": "Consider highlighting your key achievements and quantifying results. Use action verbs and focus on your most relevant skills for your target role. Keep it concise at 3-5 sentences.",
        
        "experience": "• Use strong action verbs to start each bullet point<br>• Quantify achievements with numbers/percentages<br>• Focus on accomplishments rather than responsibilities<br>• Include relevant technologies and methodologies<br>• Ensure chronological order with clear date formatting",
        
        "education": "• List degrees in reverse chronological order<br>• Include relevant coursework and academic achievements<br>• Add GPA if it's 3.5+ or relevant<br>• Mention scholarships, honors, or awards<br>• Include study abroad experiences if applicable",
        
        "skills": "• Group skills by category (Technical, Software, Soft Skills)<br>• List most important skills first<br>• Include proficiency levels for technical skills<br>• Remove outdated or irrelevant skills<br>• Add skills mentioned in your target job descriptions",
        
        "additional": "• Projects: Highlight relevant projects with technologies used and outcomes<br>• Certifications: Include name, issuing organization, and date<br>• Languages: List with proficiency levels<br>• Volunteer Work: Include if relevant to your target role"
    }
    
    return suggestions.get(section_type, "Consider formatting this section for better readability and highlighting key information.")

if __name__ == "__main__":
    main() 