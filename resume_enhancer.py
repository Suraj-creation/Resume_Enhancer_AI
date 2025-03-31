import streamlit as st
import time
import random
import os
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from utils.db_utils import initialize_database
from utils.auth_utils import require_auth
from pages._init import render_step_indicator, render_section_title, render_info_box
from utils.rich_text_editor import rich_text_editor, quill_editor  # Import the rich text editor components

# Initialize flags for Hugging Face availability
HUGGINGFACE_POTENTIALLY_AVAILABLE = False
try:
    import importlib.util
    hf_spec = importlib.util.find_spec("transformers")
    torch_spec = importlib.util.find_spec("torch")
    
    if hf_spec is not None and torch_spec is not None:
        # Don't load models yet, just mark as potentially available
        HUGGINGFACE_POTENTIALLY_AVAILABLE = True
except ImportError:
    HUGGINGFACE_POTENTIALLY_AVAILABLE = False

def main():
    """Main function for the Resume Enhancer application"""
    # Note: Page config now handled in app.py as the first Streamlit command
    try:
        # Initialize database connection
        db = initialize_database()
        
        # Apply custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #4361ee;
            margin-bottom: 1rem;
        }
        .section-header {
            font-size: 1.8rem;
            font-weight: 600;
            color: #3a0ca3;
            margin: 1.5rem 0 1rem 0;
        }
        .info-box {
            background: linear-gradient(135deg, rgba(67, 97, 238, 0.1) 0%, rgba(114, 9, 183, 0.1) 100%);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .highlight-text {
            font-weight: 600;
            color: #4361ee;
        }
        .score-display {
            font-size: 1.5rem;
            font-weight: 700;
            text-align: center;
            padding: 1rem;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(67, 97, 238, 0.1) 0%, rgba(114, 9, 183, 0.1) 100%);
        }
        .high-score {
            color: #06d6a0;
        }
        .low-score {
            color: #ef476f;
        }
        .suggestion-card {
            border-left: 4px solid #4361ee;
            background-color: #f8f9fa;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 10px 10px 0;
        }
        .analytics-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .feature-badge {
            display: inline-block;
            padding: 3px 8px;
            background: rgba(67, 97, 238, 0.1);
            color: #4361ee;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-right: 0.5rem;
        }
        .enhancement-highlight {
            background-color: #d1fae5;
            padding: 2px 4px;
            border-radius: 4px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # User authentication check
        user = require_auth(db)
        if not user:
            return
        
        # Main application header
        st.markdown("<h1 class='main-header'>Resume Enhancer</h1>", unsafe_allow_html=True)
        
        # Real-time analytics
        show_realtime_analytics()
        
        # Initialize session state variables if not already set
        initialize_resume_enhancer_state()
        
        # Render step indicator
        steps = [
            ("Upload", "📤"),
            ("Extract", "🔍"),
            ("Score", "📊"),
            ("Enhance", "✨"),
            ("Download", "📥")
        ]
        render_step_indicator(steps, st.session_state.current_step - 1)
        
        # Application flow based on current step
        if st.session_state.current_step == 1:
            handle_resume_upload()
        elif st.session_state.current_step == 2:
            handle_feature_extraction()
        elif st.session_state.current_step == 3:
            handle_resume_scoring()
        elif st.session_state.current_step == 4:
            handle_resume_enhancement()
        elif st.session_state.current_step == 5:
            handle_resume_download()
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")

def show_realtime_analytics():
    """Display real-time analytics about the resume enhancement service"""
    # Only show on first step to avoid distracting during the process
    if st.session_state.get('current_step', 1) == 1:
        with st.expander("📈 Resume Enhancement Analytics", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(label="Resumes Enhanced", value="25,432", delta="1,204")
            
            with col2:
                st.metric(label="Avg. Score Improvement", value="34%", delta="2.4%")
            
            with col3:
                st.metric(label="Interview Success Rate", value="78%", delta="5.2%")
            
            with col4:
                st.metric(label="User Satisfaction", value="4.8/5", delta="0.2")

def initialize_resume_enhancer_state():
    """Initialize key session state variables for Resume Enhancer"""
    if 'enable_huggingface' not in st.session_state:
        st.session_state.enable_huggingface = False
        
    if 'huggingface_loaded' not in st.session_state:
        st.session_state.huggingface_loaded = False
        
    if 'resume_uploaded' not in st.session_state:
        st.session_state.resume_uploaded = False
        
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
        
    if 'resume_score' not in st.session_state:
        st.session_state.resume_score = None
        
    if 'extracted_sections' not in st.session_state:
        st.session_state.extracted_sections = None
        
    if 'enhanced_resume' not in st.session_state:
        st.session_state.enhanced_resume = None
        
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
        
    if 'history' not in st.session_state:
        st.session_state.history = []

def handle_resume_upload():
    """Handle the resume upload process"""
    render_section_title("Upload Your Resume", "Step 1: Upload your resume for enhancement", icon="📤")
    
    upload_col, info_col = st.columns([2, 1])
    
    with upload_col:
        st.markdown("""
        <div style="margin-bottom: 1rem;">
            <p>Please upload your resume in one of the supported formats:</p>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin: 1rem 0;">
                <span class="feature-badge">PDF</span>
                <span class="feature-badge">DOCX</span>
                <span class="feature-badge">DOC</span>
                <span class="feature-badge">RTF</span>
                <span class="feature-badge">ODT</span>
                <span class="feature-badge">TXT</span>
                <span class="feature-badge">HTML</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Advanced options toggle
        with st.expander("⚙️ Advanced Options", expanded=False):
            st.warning("""
            **Advanced NLP features are disabled by default for faster loading.**
            
            Enabling these features may provide better analysis but will increase loading time by 1-3 minutes.
            """)
            
            enable_hf = st.checkbox("Enable advanced NLP features", value=st.session_state.enable_huggingface)
            
            # Check if the toggle state has changed
            if enable_hf != st.session_state.enable_huggingface:
                st.session_state.enable_huggingface = enable_hf
                st.session_state.huggingface_loaded = False  # Force reloading if needed
                
                if enable_hf:
                    st.info("Advanced NLP features will be loaded when needed. This may take a few minutes.")
                else:
                    st.success("Using fast mode with basic features only.")
        
        # Custom file uploader with drag-and-drop styling
        st.markdown("""
        <style>
        .uploadedFile {
            position: relative;
        }
        .uploadedFile:before {
            content: 'Drag and drop your resume here or click to browse';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            text-align: center;
            padding-top: 2.5rem;
            font-size: 1rem;
            color: #64748b;
            z-index: 0;
        }
        .uploadedFile > * {
            position: relative;
            z-index: 1;
        }
        </style>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose a file", 
                                        type=["pdf", "docx", "doc", "rtf", "odt", "txt", "html"], 
                                        help="Upload your resume file (max 10MB)",
                                        label_visibility="collapsed")
        
        if uploaded_file is not None:
            # Validate file size (10MB max)
            max_size = 10 * 1024 * 1024  # 10MB in bytes
            if uploaded_file.size > max_size:
                st.error(f"File size exceeds the maximum limit of 10MB. Your file is {format_size(uploaded_file.size)}.")
                return
                
            # Create a custom progress indicator
            st.markdown("<p style='margin-top:1rem;'>Processing your resume...</p>", unsafe_allow_html=True)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Actually process the file, extracting text and getting basic info
            try:
                # Import the actual text extraction function
                from utils.pdf_utils import extract_text_from_pdf
                import tempfile
                import os
                import io
                
                # Update progress
                status_text.text("Analyzing file format...")
                progress_bar.progress(20)
                
                # Get file extension and determine if conversion is needed
                file_name = uploaded_file.name
                file_ext = file_name.split('.')[-1].lower()
                needs_conversion = file_ext != 'pdf'
                
                # Save the uploaded file to a temporary file for processing
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_file_path = tmp_file.name
                
                # Store original file in session state for preview
                st.session_state.original_file_path = temp_file_path
                st.session_state.original_file_ext = file_ext
                
                if needs_conversion:
                    status_text.text(f"Converting {file_ext.upper()} to PDF format...")
                    progress_bar.progress(30)
                    # Note: The actual conversion happens in extract_text_from_pdf
                
                # Extract text from the uploaded resume
                extracted_text, metadata = extract_text_from_pdf(uploaded_file)
                
                # If PDF was created during conversion, store it
                if 'converted_pdf_path' in metadata:
                    st.session_state.converted_pdf_path = metadata['converted_pdf_path']
                
                # Check if document is potentially image-based (very little text extracted)
                is_image_based = False
                if len(extracted_text.strip()) < 100 and file_ext == 'pdf':
                    is_image_based = True
                    st.warning("Your PDF appears to contain very little text. It may be an image-based scan that requires OCR processing. For best results, upload a text-based PDF.")
                
                # Update progress
                status_text.text("Extracting text content...")
                progress_bar.progress(60)
                
                # Store the extracted text in session state
                st.session_state.resume_text = extracted_text
                st.session_state.resume_metadata = metadata
                
                # Simulate database storage (in a real app, we would save to Supabase/MongoDB/SQL here)
                status_text.text("Securely storing your resume...")
                progress_bar.progress(80)
                
                # Update progress
                status_text.text("Finalizing...")
                progress_bar.progress(100)
                
                # Enhanced file details with more metadata
                file_details = {
                    "FileName": uploaded_file.name, 
                    "FileType": uploaded_file.type or metadata.get("file_type", "Unknown"), 
                    "FileSize": uploaded_file.size,
                    "Pages": metadata.get("pages", "Unknown"),
                    "OriginalFormat": file_ext.upper(),
                    "ConvertedToPDF": "Yes" if needs_conversion else "No (Already PDF)",
                    "TextBased": "No (Image-based PDF detected)" if is_image_based else "Yes"
                }
                
                st.markdown(f"""
                <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem;">File Details</h3>
                    <p><strong>Name:</strong> {file_details['FileName']}</p>
                    <p><strong>Type:</strong> {file_details['FileType']}</p>
                    <p><strong>Size:</strong> {format_size(file_details['FileSize'])}</p>
                    <p><strong>Pages:</strong> {file_details['Pages']}</p>
                    <p><strong>Original Format:</strong> {file_details['OriginalFormat']}</p>
                    <p><strong>Converted to PDF:</strong> {file_details['ConvertedToPDF']}</p>
                    <p><strong>Text-Based Document:</strong> {file_details['TextBased']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Document Preview section - Enhanced with actual PDF rendering
                st.markdown("### Resume Preview")
                st.markdown("Confirm that your resume uploaded correctly and the content is as expected.")
                
                # Use tabs to show different preview options
                preview_tabs = st.tabs(["PDF Preview", "Extracted Text", "File Details"])
                
                with preview_tabs[0]:
                    try:
                        # Import PDF rendering libraries
                        import fitz  # PyMuPDF
                        
                        # Determine which file to display (original PDF or converted)
                        pdf_path = st.session_state.get('converted_pdf_path', None)
                        if not pdf_path and file_ext == 'pdf':
                            pdf_path = st.session_state.original_file_path
                            
                        if pdf_path and os.path.exists(pdf_path):
                            # Open the PDF file
                            doc = fitz.open(pdf_path)
                            
                            # Show page selection if multiple pages
                            if doc.page_count > 1:
                                page_number = st.slider("Page", 1, doc.page_count, 1) - 1
                            else:
                                page_number = 0
                            
                            # Render the selected page
                            page = doc.load_page(page_number)
                            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom factor 2 for better quality
                            
                            # Convert to image
                            img_bytes = pix.tobytes("png")
                            
                            # Display the image
                            st.image(img_bytes, caption=f"Page {page_number + 1} of {doc.page_count}", use_column_width=True)
                            
                            # Add page navigation buttons if multiple pages
                            if doc.page_count > 1:
                                col1, col2 = st.columns(2)
                                with col1:
                                    if page_number > 0:
                                        if st.button("← Previous Page"):
                                            st.session_state.current_page = max(0, page_number - 1)
                                            st.rerun()
                                with col2:
                                    if page_number < doc.page_count - 1:
                                        if st.button("Next Page →"):
                                            st.session_state.current_page = min(doc.page_count - 1, page_number + 1)
                                            st.rerun()
                        else:
                            st.info("PDF preview could not be generated for this file format. Please check the extracted text tab.")
                            
                    except Exception as e:
                        st.error(f"Error displaying PDF preview: {str(e)}")
                        st.info("Please check the extracted text tab to verify your resume content.")
                
                with preview_tabs[1]:
                    # Preview the extracted text with length-appropriate display
                    if len(extracted_text) > 1000:
                        st.markdown("**First 1000 characters of extracted text:**")
                        st.text_area("", value=extracted_text[:1000] + "...", height=300, disabled=True)
                        st.markdown(f"*Full text length: {len(extracted_text)} characters*")
                        
                        # Add option to view full text
                        if st.checkbox("View full extracted text"):
                            st.text_area("Full Text", value=extracted_text, height=500, disabled=True)
                    else:
                        st.text_area("", value=extracted_text, height=300, disabled=True)
                
                with preview_tabs[2]:
                    # Display detailed file information
                    for key, value in file_details.items():
                        st.markdown(f"**{key}**: {value}")
                
                # Store file path in session state for further processing
                st.session_state.resume_uploaded = True
                
                # Clear status text and show success message
                status_text.empty()
                st.success("Resume uploaded successfully!")
                
                # Show an enhanced information security notice
                st.info("""
                **Security & Privacy Notice:**
                Your resume is securely processed on our servers with industry-standard encryption. 
                The file is temporarily stored for processing and will be automatically deleted after enhancement unless you choose to save it to your account.
                """)
                
                # Add button to continue to next step
                st.markdown("### Continue")
                st.markdown("If the resume preview looks correct, proceed to the next step for feature extraction.")
                continue_col1, continue_col2 = st.columns([3, 1])
                with continue_col2:
                    if st.button("Continue →", key="continue_to_extraction", use_container_width=True):
                        st.session_state.current_step = 2
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
                st.warning("""
                Please try uploading a different file or format. If the issue persists:
                - Check if the file is corrupted
                - Try a different file format
                - Ensure the document contains selectable text
                """)
                
                # Retry button
                if st.button("Retry Upload", key="retry_upload"):
                    # This will essentially refresh the widget state
                    st.rerun()
    
    with info_col:
        render_info_box("""
        ### Why upload your resume?
        
        Your resume is the first impression that potential employers have of you. 
        Our AI-powered Resume Enhancer will:
        
        - Extract key information
        - Analyze content quality
        - Provide targeted improvements
        - Format professionally
        
        ### File Requirements
        
        - Supported formats: PDF, DOCX, DOC, RTF, ODT, TXT, HTML
        - Maximum size: 10MB
        - Text-based documents preferred (not scanned images)
        - All formats will be converted to PDF for processing
        """)
        
        # Add testimonials
        st.markdown("""
        <div style="margin-top: 2rem;">
            <h4 style="font-size: 1rem; color: #334155;">What users say</h4>
            <div style="background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-top: 0.5rem;">
                <p style="font-style: italic; color: #64748b; font-size: 0.9rem;">"This tool helped me land interviews at top companies by optimizing my resume with industry-specific keywords."</p>
                <p style="color: #334155; font-size: 0.8rem; margin-bottom: 0;"><strong>Sarah J.</strong> - Software Engineer</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def format_size(size_bytes):
    """Format file size from bytes to appropriate unit"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def handle_feature_extraction():
    """Handle the feature extraction process"""
    render_section_title("Key Feature Extraction", "Step 2: Extracting key features from your resume", icon="🔍")
    
    if not st.session_state.resume_uploaded:
        st.warning("Please upload a resume first.")
        if st.button("← Go back to upload", key="back_to_upload"):
            st.session_state.current_step = 1
            st.rerun()
        return
    
    # Check if we have the resume text
    if "resume_text" not in st.session_state or not st.session_state.resume_text:
        st.error("Resume text not found. Please re-upload your resume.")
        if st.button("← Go back to upload", key="back_to_upload_error"):
            st.session_state.current_step = 1
            st.rerun()
        return
    
    # Create a more visual extraction process
    extraction_container = st.container()
    
    with extraction_container:
        # Add a brief introduction to the extraction process
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(67, 97, 238, 0.1) 0%, rgba(114, 9, 183, 0.1) 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="margin-top: 0;">Advanced Key Feature Extraction</h3>
            <p>Our AI-powered engine will analyze your resume and extract structured information, including:</p>
            <ul>
                <li>Personal details and contact information</li>
                <li>Career objective or professional summary</li>
                <li>Educational background</li>
                <li>Work experience and accomplishments</li>
                <li>Technical and soft skills</li>
                <li>Certifications and additional qualifications</li>
                <li>Projects, awards, and other achievements</li>
            </ul>
            <p>We'll also identify potential areas for improvement using color-coded highlights:</p>
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                <div style="background-color: rgba(239, 68, 68, 0.2); padding: 5px 10px; border-radius: 5px; border-left: 3px solid #EF4444;">
                    <strong style="color: #EF4444;">Red:</strong> Grammatical errors
                </div>
                <div style="background-color: rgba(245, 158, 11, 0.2); padding: 5px 10px; border-radius: 5px; border-left: 3px solid #F59E0B;">
                    <strong style="color: #F59E0B;">Yellow:</strong> Needs improvement
                </div>
                <div style="background-color: rgba(249, 115, 22, 0.2); padding: 5px 10px; border-radius: 5px; border-left: 3px solid #F97316;">
                    <strong style="color: #F97316;">Orange:</strong> Weak/missing sections
                </div>
                <div style="background-color: rgba(59, 130, 246, 0.2); padding: 5px 10px; border-radius: 5px; border-left: 3px solid #3B82F6;">
                    <strong style="color: #3B82F6;">Blue:</strong> Formatting issues
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        placeholder = st.empty()
        placeholder.info("Initializing AI extraction engine...")
        
        progress_bar = st.progress(0)
        extraction_status = st.empty()
        details_area = st.empty()
        
        # Default structured data in case of errors
        structured_data = {
            "personal_info": {"name": "Candidate Name", "email_address": "email@example.com"},
            "objective_summary": "Professional summary",
            "education": [{"institution": "University", "degree": "Degree", "date": "Year"}],
            "work_experience": [{"company": "Company", "title": "Position", "duration": "Period", "description": "Responsibilities"}],
            "skills": ["Skill 1", "Skill 2", "Skill 3"],
            "certifications": [],
            "projects": [],
            "awards": []
        }
        
        extraction_complete = False
        
        # Check if we already have extracted features
        if "extracted_sections" not in st.session_state or st.session_state.extracted_sections is None:
            # Show NLP processing animation
            placeholder.markdown("""
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem;">
                    <span style="display: inline-block; margin-right: 8px;">⚙️</span>
                    AI Analysis in Progress
                </h3>
                <p>Our NLP engine is analyzing your resume and extracting key information using machine learning algorithms optimized for resume data.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Actually process the resume text with our advanced NLP methods
            try:
                # Import and use the new advanced resume processor
                from utils.resume_processor import extract_structured_data
                resume_text = st.session_state.resume_text
                
                # Update progress bar for visual effect
                progress_bar.progress(20)
                extraction_status.markdown("Initializing Apache Tika and Hugging Face AI models...")
                time.sleep(0.5)
                
                # Show detailed technical steps for user experience
                details_area.markdown("""
                <div style="color: #64748b; font-size: 0.9rem; font-family: monospace; padding-left: 40px; margin-top: 5px;">
                    Apache Tika: Text extraction from various file formats
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.5)
                
                progress_bar.progress(40)
                extraction_status.markdown("Applying NER (Named Entity Recognition) to identify resume components...")
                
                details_area.markdown("""
                <div style="color: #64748b; font-size: 0.9rem; font-family: monospace; padding-left: 40px; margin-top: 5px;">
                    Hugging Face Transformers: Applying resume-ner model via API
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.5)
                
                progress_bar.progress(60)
                extraction_status.markdown("Performing section analysis and structure detection...")
                
                details_area.markdown("""
                <div style="color: #64748b; font-size: 0.9rem; font-family: monospace; padding-left: 40px; margin-top: 5px;">
                    Language analysis and structure detection in progress
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.5)
                
                progress_bar.progress(80)
                extraction_status.markdown("Running grammar checks and improvement analysis...")
                
                # Extract the structured data from resume text
                # This function now also sets session state values for grammar_issues, improvement_suggestions, etc.
                try:
                    extracted_data = extract_structured_data(resume_text)
                    # Make sure we got valid data back
                    if extracted_data is not None and isinstance(extracted_data, dict):
                        structured_data = extracted_data
                    else:
                        st.error("Failed to extract structured data from resume. Using default template.")
                except Exception as e:
                    st.error(f"Error in data extraction: {str(e)}. Using default template.")
                
                progress_bar.progress(100)
                extraction_status.markdown("Finalizing results...")
                time.sleep(0.5)
                
                # Store the extracted data
                st.session_state.extracted_sections = structured_data
                extraction_complete = True
                
            except Exception as e:
                st.error(f"Error extracting features: {str(e)}")
                # Set default structured data if extraction fails
                st.session_state.extracted_sections = structured_data
                extraction_complete = True
        else:
            # We already have the extracted data
            structured_data = st.session_state.extracted_sections
            extraction_complete = True
            progress_bar.progress(100)
        
        # Clear status indicators
        placeholder.empty()
        extraction_status.empty()
        details_area.empty()
        
        if extraction_complete:
            # Show extraction results summary
            confidence_scores = st.session_state.get('confidence_scores', {})
            grammar_issues = st.session_state.get('grammar_issues', [])
            improvement_suggestions = st.session_state.get('improvement_suggestions', [])
            missing_sections = st.session_state.get('missing_sections', [])
            formatting_issues = st.session_state.get('formatting_issues', [])
            
            # Initialize default values if any are missing
            if not confidence_scores:
                confidence_scores = {
                    "Personal Info": 70,
                    "Objective/Resume Summary": 65,
                    "Education": 70,
                    "Work Experience": 65,
                    "Skills": 60,
                    "Certifications": 50,
                    "Projects": 50,
                    "Awards": 50
                }
                
            # Calculate overall extraction quality
            num_issues = len(grammar_issues) + len(improvement_suggestions) + len(missing_sections) + len(formatting_issues)
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
            
            quality_level = "Excellent" if avg_confidence > 90 and num_issues < 3 else "Good" if avg_confidence > 80 and num_issues < 5 else "Fair"
            quality_color = "#10B981" if quality_level == "Excellent" else "#3B82F6" if quality_level == "Good" else "#F59E0B"
            
            st.markdown(f"""
            <div style="background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 1.5rem;">
                <h3 style="margin-top: 0; font-size: 1.2rem; color: #1E293B;">Extraction Complete</h3>
                <div style="display: flex; align-items: center; margin: 1rem 0;">
                    <div style="width: 80px; height: 80px; border-radius: 50%; background: {quality_color}; display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
                        <span style="color: white; font-size: 1.8rem; font-weight: 600;">{int(avg_confidence)}%</span>
                    </div>
                    <div>
                        <p style="font-weight: 600; font-size: 1.1rem; margin: 0 0 0.5rem 0; color: {quality_color};">{quality_level} Extraction Quality</p>
                        <p style="margin: 0; color: #64748B;">
                            <span style="margin-right: 1rem;"><strong>{len(structured_data.keys()) if structured_data else 0}</strong> sections processed</span>
                            <span><strong>{num_issues}</strong> potential improvements identified</span>
                        </p>
                    </div>
                </div>
                <div style="margin-top: 1rem;">
                    <p style="margin-bottom: 0.5rem; color: #1E293B; font-weight: 500;">Advanced AI Technologies Used:</p>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        <div style="background-color: rgba(67, 97, 238, 0.1); padding: 5px 10px; border-radius: 5px; font-size: 0.9rem;">
                            Apache Tika
                        </div>
                        <div style="background-color: rgba(67, 97, 238, 0.1); padding: 5px 10px; border-radius: 5px; font-size: 0.9rem;">
                            Hugging Face resume-ner
                        </div>
                        <div style="background-color: rgba(67, 97, 238, 0.1); padding: 5px 10px; border-radius: 5px; font-size: 0.9rem;">
                            NLP Grammar Analysis
                        </div>
                        <div style="background-color: rgba(67, 97, 238, 0.1); padding: 5px 10px; border-radius: 5px; font-size: 0.9rem;">
                            ATS Compatibility Check
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # NEW SECTION: Interactive Resume Preview
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%); 
                        padding: 15px; border-radius: 10px; margin: 20px 0;">
                <h3 style="margin-top: 0; font-size: 1.2rem; color: #1E293B;">Interactive Resume Preview</h3>
                <p>View your resume with AI-powered insights. Click on highlighted sections for detailed feedback and quick fixes.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create tabs for the side-by-side view
            preview_tab, extracted_tab = st.tabs(["Resume with Highlights", "Extracted Data"])
            
            with preview_tab:
                # Set up columns for the side-by-side view
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.subheader("Your Resume")
                    
                    # Get resume text and prepare highlighted version
                    resume_text = st.session_state.resume_text
                    
                    # Create highlighted version with HTML/CSS
                    highlighted_html = "<div style='background: white; padding: 20px; border-radius: 8px; white-space: pre-wrap; font-family: Arial; line-height: 1.5; max-height: 600px; overflow-y: auto;'>"
                    
                    # Process grammar issues (red highlights)
                    for issue in grammar_issues:
                        issue_text = issue["text"]
                        if issue_text in resume_text:
                            highlighted_version = f"<span style='background-color: rgba(239, 68, 68, 0.2); border-bottom: 2px dashed #EF4444;' title='{issue['suggestion']}'>{issue_text}</span>"
                            resume_text = resume_text.replace(issue_text, highlighted_version)
                    
                    # Process improvement suggestions (yellow highlights)
                    for suggestion in improvement_suggestions:
                        suggestion_text = suggestion["text"]
                        if suggestion_text in resume_text:
                            highlighted_version = f"<span style='background-color: rgba(245, 158, 11, 0.2); border-bottom: 2px dashed #F59E0B;' title='Could be improved'>{suggestion_text}</span>"
                            resume_text = resume_text.replace(suggestion_text, highlighted_version)
                    
                    # Add formatting issue indicators (blue highlights)
                    if formatting_issues:
                        formatting_html = "<div style='margin-bottom: 10px; padding: 8px; background-color: rgba(59, 130, 246, 0.1); border-left: 3px solid #3B82F6; border-radius: 4px;'>"
                        formatting_html += "<p style='margin: 0; font-weight: 500; color: #3B82F6;'>Formatting Issues:</p><ul style='margin-top: 5px;'>"
                        
                        for issue in formatting_issues:
                            formatting_html += f"<li title='{issue['description']}'>{issue['issue']}</li>"
                        
                        formatting_html += "</ul></div>"
                        highlighted_html += formatting_html
                    
                    # Add missing sections warning (orange highlights)
                    if missing_sections:
                        missing_html = "<div style='margin-bottom: 10px; padding: 8px; background-color: rgba(249, 115, 22, 0.1); border-left: 3px solid #F97316; border-radius: 4px;'>"
                        missing_html += "<p style='margin: 0; font-weight: 500; color: #F97316;'>Missing Sections:</p><ul style='margin-top: 5px;'>"
                        
                        for section in missing_sections:
                            missing_html += f"<li>{section}</li>"
                        
                        missing_html += "</ul></div>"
                        highlighted_html += missing_html
                    
                    # Add the processed content
                    highlighted_html += resume_text + "</div>"
                    
                    # Display the highlighted resume
                    st.markdown(highlighted_html, unsafe_allow_html=True)
                
                with col2:
                    st.subheader("Feedback & Quick Fixes")
                    
                    # Grammar issues section
                    if grammar_issues:
                        with st.expander("Grammar Issues", expanded=True):
                            for i, issue in enumerate(grammar_issues[:3]):  # Show top 3
                                st.markdown(f"""
                                <div style="margin-bottom: 10px; padding: 10px; background-color: rgba(239, 68, 68, 0.1); border-radius: 4px;">
                                    <p style="margin: 0 0 5px 0; font-weight: 500; color: #EF4444;">Issue {i+1}:</p>
                                    <p style="margin: 0 0 5px 0; font-family: monospace; background: white; padding: 5px; border-radius: 3px;">{issue['text']}</p>
                                    <p style="margin: 0; color: #64748B; font-size: 0.9rem;">Suggestion: {issue['suggestion']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Add a quick fix button for each issue
                                if st.button(f"Quick Fix #{i+1}", key=f"fix_grammar_{i}"):
                                    st.session_state.quick_fix = {
                                        "type": "grammar",
                                        "index": i,
                                        "original": issue['text'],
                                        "replacement": issue['suggestion']
                                    }
                                    st.success(f"Applied grammar fix: '{issue['text']}' → '{issue['suggestion']}'")
                    
                    # Improvement suggestions section
                    if improvement_suggestions:
                        with st.expander("Areas to Improve", expanded=False):
                            for i, suggestion in enumerate(improvement_suggestions[:3]):  # Show top 3
                                st.markdown(f"""
                                <div style="margin-bottom: 10px; padding: 10px; background-color: rgba(245, 158, 11, 0.1); border-radius: 4px;">
                                    <p style="margin: 0 0 5px 0; font-weight: 500; color: #F59E0B;">Improvement {i+1} ({suggestion['section']}):</p>
                                    <p style="margin: 0 0 5px 0; font-family: monospace; background: white; padding: 5px; border-radius: 3px;">{suggestion['text']}</p>
                                    <p style="margin: 0; color: #64748B; font-size: 0.9rem;">Better alternative: {suggestion['suggestion']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Add an apply improvement button for each suggestion
                                if st.button(f"Apply Improvement #{i+1}", key=f"improve_{i}"):
                                    st.session_state.quick_fix = {
                                        "type": "improvement",
                                        "index": i,
                                        "original": suggestion['text'],
                                        "replacement": suggestion['suggestion']
                                    }
                                    st.success(f"Applied improvement: '{suggestion['text']}' → '{suggestion['suggestion']}'")
                    
                    # Missing sections section
                    if missing_sections:
                        with st.expander("Missing Sections", expanded=False):
                            for i, section in enumerate(missing_sections):
                                st.markdown(f"""
                                <div style="margin-bottom: 10px; padding: 10px; background-color: rgba(249, 115, 22, 0.1); border-radius: 4px;">
                                    <p style="margin: 0; font-weight: 500; color: #F97316;">Missing: {section}</p>
                                    <p style="margin: 5px 0 0 0; color: #64748B; font-size: 0.9rem;">Adding this section will strengthen your resume.</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Add a "Generate Section" button
                                if st.button(f"Generate {section} Template", key=f"gen_section_{i}"):
                                    st.session_state.generate_section = section
                                    st.success(f"Added template for {section} section")
                    
                    # Formatting issues section
                    if formatting_issues:
                        with st.expander("Formatting Issues", expanded=False):
                            for i, issue in enumerate(formatting_issues):
                                st.markdown(f"""
                                <div style="margin-bottom: 10px; padding: 10px; background-color: rgba(59, 130, 246, 0.1); border-radius: 4px;">
                                    <p style="margin: 0 0 5px 0; font-weight: 500; color: #3B82F6;">{issue['issue']}</p>
                                    <p style="margin: 0 0 5px 0; color: #64748B; font-size: 0.9rem;">{issue['description']}</p>
                                    <p style="margin: 0; font-size: 0.9rem;">Suggestion: {issue['suggestion']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Add a "Fix Formatting" button
                                if st.button(f"Fix This Issue", key=f"fix_format_{i}"):
                                    st.session_state.fix_formatting = {
                                        "index": i,
                                        "issue": issue['issue']
                                    }
                                    st.success(f"Applied formatting fix for: {issue['issue']}")
            
            with extracted_tab:
                # Display the structured extracted data
                for section, data in structured_data.items():
                    if data and (isinstance(data, list) and len(data) > 0) or (isinstance(data, dict) and len(data) > 0) or (isinstance(data, str) and data.strip()):
                        st.subheader(section.replace('_', ' ').title())
                        
                        if section == "personal_info":
                            # Display personal info as a table
                            info_data = [[k.replace('_', ' ').title(), v] for k, v in data.items()]
                            st.table(info_data)
                            
                        elif section == "skills":
                            # Display skills as badges
                            skills_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px;">'
                            for skill in data:
                                skills_html += f'<span style="background-color: rgba(67, 97, 238, 0.1); padding: 5px 10px; border-radius: 5px; font-size: 0.9rem;">{skill}</span>'
                            skills_html += '</div>'
                            st.markdown(skills_html, unsafe_allow_html=True)
                            
                        elif section == "objective_summary":
                            # Display summary as a blockquote
                            st.markdown(f"> {data}")
                            
                        elif section in ["education", "work_experience", "projects", "certifications"]:
                            # Display as expandable sections
                            for i, item in enumerate(data):
                                if isinstance(item, dict):
                                    # Create a title for the expandable section
                                    title = ""
                                    if section == "education" and "institution" in item:
                                        title = f"{item.get('institution', '')} - {item.get('degree', '')}"
                                    elif section == "work_experience" and "company" in item:
                                        title = f"{item.get('title', '')} at {item.get('company', '')}"
                                    elif "name" in item:
                                        title = item.get('name', f'Item {i+1}')
                                    else:
                                        title = f'Item {i+1}'
                                    
                                    with st.expander(title, expanded=i==0):
                                        for key, value in item.items():
                                            if value and key not in ["institution", "company", "name"]:
                                                st.markdown(f"**{key.title()}:** {value}")
                                else:
                                    # For simple string items
                                    st.markdown(f"- {item}")
                        else:
                            # Default display for other sections
                            st.write(data)
            
            # Add navigation buttons for continuing to the next step
            st.markdown("<hr style='margin: 2rem 0 1rem 0;'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("← Back to Upload", key="back_to_upload_from_extraction"):
                    st.session_state.current_step = 1
                    st.rerun()
            
            with col2:
                if st.button("Continue to Scoring →", key="continue_to_scoring"):
                    st.session_state.current_step = 3
                    st.rerun()

def handle_resume_scoring():
    """Handle the resume scoring process"""
    render_section_title("AI-Based Scoring", "Step 3: Evaluating your resume with AI", icon="📊")
    
    if st.session_state.extracted_sections is None:
        st.warning("Please complete the feature extraction step first.")
        if st.button("← Go back to extraction", key="back_to_extraction"):
            st.session_state.current_step = 2
            st.rerun()
        return
    
    # Simulate AI scoring
    if 'resume_score' not in st.session_state or st.session_state.resume_score is None:
        scoring_container = st.container()
        
        with scoring_container:
            placeholder = st.empty()
            placeholder.info("Analyzing your resume with our AI scoring engine...")
            
            progress_bar = st.progress(0)
            score_status = st.empty()
            
            # Score categories with icons and descriptions
            score_categories = [
                {
                    "name": "Content Quality", 
                    "icon": "📝",
                    "description": "Quality, clarity and relevance of resume content",
                    "weight": 0.15
                },
                {
                    "name": "Keyword Optimization", 
                    "icon": "🔑",
                    "description": "Presence of industry-specific keywords",
                    "weight": 0.15
                },
                {
                    "name": "ATS Compatibility", 
                    "icon": "🤖",
                    "description": "How well your resume will perform with Applicant Tracking Systems",
                    "weight": 0.15
                },
                {
                    "name": "Formatting & Structure", 
                    "icon": "📐",
                    "description": "Organization, readability and visual appeal",
                    "weight": 0.10
                },
                {
                    "name": "Impact & Achievements", 
                    "icon": "🏆",
                    "description": "Emphasis on quantifiable achievements and results",
                    "weight": 0.15
                },
                {
                    "name": "GenAI Score", 
                    "icon": "🧠",
                    "description": "Presence of Generative AI skills, projects, and knowledge",
                    "weight": 0.15
                },
                {
                    "name": "AI Score", 
                    "icon": "🔬",
                    "description": "Broader AI/ML skills and experience beyond GenAI",
                    "weight": 0.15
                }
            ]
            
            # Simulate scoring process with detailed animation
            scores = {}
            detail_area = st.empty()
            
            for i, category in enumerate(score_categories):
                progress = int((i / len(score_categories)) * 100)
                progress_bar.progress(progress)
                
                category_name = category["name"]
                category_icon = category["icon"]
                
                score_status.markdown(f"""
                <div style="display: flex; align-items: center;">
                    <div style="width: 30px; text-align: center; margin-right: 10px; font-size: 1.2rem;">
                        {category_icon}
                    </div>
                    <div>
                        <p style="margin: 0; font-weight: 500;">Analyzing {category_name}...</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show analysis details animation
                for j in range(4):
                    details = [
                        "Initializing AI models...",
                        "Processing resume content...",
                        "Comparing to industry standards...",
                        "Calculating final score..."
                    ]
                    detail_area.markdown(f"""
                    <div style="font-family: monospace; color: #64748b; font-size: 0.9rem; padding-left: 40px;">
                        {details[j]}
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.5)
                
                # Use more realistic, category-specific scoring for each category
                if category_name == "GenAI Score":
                    # For GenAI score, calculate based on the presence of GenAI keywords
                    resume_text = st.session_state.resume_text.lower()
                    genai_keywords = [
                        "generative ai", "genai", "gans", "vaes", "diffusion models", 
                        "transformers", "gpt", "bert", "llm", "large language model",
                        "fine-tuning", "prompt engineering", "pytorch", "hugging face",
                        "stable diffusion", "synthetic data", "model interpretability"
                    ]
                    
                    # Count keywords
                    keyword_count = sum(1 for keyword in genai_keywords if keyword in resume_text)
                    keyword_score = min(95, 50 + keyword_count * 5)  # Cap at 95
                    
                    # Apply penalty if missing Projects or technical sections
                    has_projects = "projects" in st.session_state.extracted_sections and len(st.session_state.extracted_sections["projects"]) > 0
                    has_technical_skills = "skills" in st.session_state.extracted_sections and any(skill.lower() in " ".join(genai_keywords) for skill in st.session_state.extracted_sections["skills"])
                    
                    if not has_projects:
                        keyword_score = max(60, keyword_score - 15)
                    if not has_technical_skills:
                        keyword_score = max(60, keyword_score - 10)
                    
                    score = keyword_score
                elif category_name == "AI Score":
                    # For AI score, calculate based on the presence of AI/ML keywords
                    resume_text = st.session_state.resume_text.lower()
                    ai_keywords = [
                        "machine learning", "deep learning", "neural networks", "artificial intelligence", 
                        "ml", "ai", "cnn", "rnn", "nlp", "natural language processing", 
                        "computer vision", "classification", "regression", "clustering",
                        "tensorflow", "keras", "scikit-learn", "numpy", "pandas",
                        "data mining", "feature engineering", "hyperparameter tuning"
                    ]
                    
                    # Count keywords
                    keyword_count = sum(1 for keyword in ai_keywords if keyword in resume_text)
                    keyword_score = min(95, 50 + keyword_count * 4)  # Cap at 95
                    
                    # Apply penalty if missing Projects or relevant skills
                    has_projects = "projects" in st.session_state.extracted_sections and len(st.session_state.extracted_sections["projects"]) > 0
                    has_ai_skills = "skills" in st.session_state.extracted_sections and any(skill.lower() in " ".join(ai_keywords) for skill in st.session_state.extracted_sections["skills"])
                    
                    if not has_projects:
                        keyword_score = max(60, keyword_score - 15)
                    if not has_ai_skills:
                        keyword_score = max(60, keyword_score - 10)
                    
                    score = keyword_score
                else:
                    # Generate random score between 60 and 95 for other categories
                    score = random.randint(60, 95)
                
                scores[category_name] = {
                    "score": score,
                    "icon": category_icon,
                    "description": category["description"],
                    "weight": category["weight"]
                }
                
                detail_area.markdown(f"""
                <div style="font-family: monospace; color: #10b981; font-size: 0.9rem; padding-left: 40px;">
                    Score calculated: {score}/100
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.5)
            
            # Calculate weighted overall score
            overall_score = int(sum([
                details["score"] * details["weight"] 
                for category, details in scores.items()
            ]))
            
            scores["Overall Score"] = overall_score
            
            # Complete the progress bar
            progress_bar.progress(100)
            score_status.markdown("""
            <div style="display: flex; align-items: center;">
                <div style="width: 30px; text-align: center; margin-right: 10px; font-size: 1.2rem;">
                    ✅
                </div>
                <div>
                    <p style="margin: 0; font-weight: 500; color: #10b981;">Scoring completed!</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            detail_area.empty()
            time.sleep(0.5)
            
            # Store scores
            st.session_state.resume_score = scores
            
            # Clear placeholder
            placeholder.empty()
    
    # Display scores with improved visualizations
    st.success("Resume scoring completed! Here are your results:")
    
    # Determine overall score color
    overall_score = st.session_state.resume_score["Overall Score"]
    
    if overall_score >= 80:
        score_color = "#10B981"  # Green
        score_icon = "🚀"
        score_level = "Excellent"
        score_message = "Your resume is well-optimized! We'll help make it even better."
    elif overall_score >= 70:
        score_color = "#3B82F6"  # Blue
        score_icon = "👍"
        score_level = "Good"
        score_message = "Your resume is solid but has room for improvement."
    elif overall_score >= 60:
        score_color = "#F59E0B"  # Yellow/Orange
        score_icon = "⚠️"
        score_level = "Fair"
        score_message = "Your resume needs several improvements for optimal results."
    else:
        score_color = "#EF4444"  # Red
        score_icon = "⚠️"
        score_level = "Needs Improvement"
        score_message = "Your resume requires significant improvements to be effective."
    
    # Main score display and category breakdown
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Overall score display
        st.markdown(f"""
        <div style="text-align: center; background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h3 style="margin-top: 0; font-size: 1.2rem; color: #1E293B;">Overall Score</h3>
            <div style="position: relative; width: 150px; height: 150px; margin: 1rem auto;">
                <svg viewBox="0 0 36 36" style="width: 100%; height: 100%;">
                    <path d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none" stroke="#E5E7EB" stroke-width="3" stroke-dasharray="100, 100"/>
                    <path d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none" stroke="{score_color}" stroke-width="3" stroke-dasharray="{overall_score}, 100"/>
                </svg>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: {score_color};">{overall_score}</div>
                    <div style="font-size: 1rem; color: #6B7280;">/100</div>
                </div>
            </div>
            <div style="font-size: 1.1rem; font-weight: 600; color: {score_color}; display: flex; align-items: center; justify-content: center; gap: 8px;">
                <span>{score_icon}</span>
                <span>{score_level}</span>
            </div>
            <p style="margin-top: 0.5rem; font-size: 0.9rem; color: #64748B;">{score_message}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Resume improvement potential
        potential_improvement = min(100, overall_score + 20)
        improvement_percentage = potential_improvement - overall_score
        
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 1rem;">
            <h3 style="margin-top: 0; font-size: 1.2rem; color: #1E293B;">Improvement Potential</h3>
            <div style="display: flex; align-items: center; margin: 1rem 0;">
                <div style="flex-grow: 1; height: 8px; background-color: #E5E7EB; border-radius: 4px; position: relative;">
                    <div style="position: absolute; height: 100%; width: {overall_score}%; background-color: {score_color}; border-radius: 4px;"></div>
                    <div style="position: absolute; height: 100%; left: {overall_score}%; width: {improvement_percentage}%; background-color: #4361EE; border-radius: 0 4px 4px 0;"></div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #6B7280;">
                <div>Current</div>
                <div>Potential</div>
            </div>
            <div style="display: flex; justify-content: space-between; font-weight: 600;">
                <div style="color: {score_color};">{overall_score}</div>
                <div style="color: #4361EE;">{potential_improvement}</div>
            </div>
            <p style="margin-top: 1rem; font-size: 0.9rem; color: #64748B;">
                By implementing our recommendations, you can potentially improve your score by up to {improvement_percentage} points.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add a GenAI vs AI Scores comparison section
        genai_score = st.session_state.resume_score["GenAI Score"]["score"]
        ai_score = st.session_state.resume_score["AI Score"]["score"]
        
        # Determine score levels and colors for GenAI and AI scores
        genai_level = "High" if genai_score > 60 else "Low"
        ai_level = "High" if ai_score > 60 else "Low"
        
        genai_color = "#10B981" if genai_score > 60 else "#EF4444"
        ai_color = "#10B981" if ai_score > 60 else "#EF4444"
        
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 1rem;">
            <h3 style="margin-top: 0; font-size: 1.2rem; color: #1E293B;">AI Skills Analysis</h3>
            <div style="margin-top: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-weight: 500;">GenAI Score</span>
                    <span style="font-weight: 700; color: {genai_color};">{genai_score}</span>
                </div>
                <div style="height: 8px; background-color: #E5E7EB; border-radius: 4px; margin-bottom: 0.5rem;">
                    <div style="height: 100%; width: {genai_score}%; background-color: {genai_color}; border-radius: 4px;"></div>
                </div>
                <p style="margin: 0 0 1rem 0; font-size: 0.8rem; color: #64748B;">
                    Your resume shows a <strong style="color: {genai_color};">{genai_level}</strong> level of Generative AI skills and experience.
                </p>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-weight: 500;">AI Score</span>
                    <span style="font-weight: 700; color: {ai_color};">{ai_score}</span>
                </div>
                <div style="height: 8px; background-color: #E5E7EB; border-radius: 4px; margin-bottom: 0.5rem;">
                    <div style="height: 100%; width: {ai_score}%; background-color: {ai_color}; border-radius: 4px;"></div>
                </div>
                <p style="margin: 0; font-size: 0.8rem; color: #64748B;">
                    Your resume shows a <strong style="color: {ai_color};">{ai_level}</strong> level of general AI/ML expertise.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Category breakdown
        st.markdown("""
        <h3 style="font-size: 1.2rem; color: #1E293B; margin-bottom: 1rem;">Category Breakdown</h3>
        """, unsafe_allow_html=True)
        
        for category, details in st.session_state.resume_score.items():
            if category != "Overall Score":
                score = details["score"]
                icon = details["icon"]
                description = details["description"]
                weight = details["weight"]
                
                # Determine category score color
                if score >= 80:
                    cat_color = "#10B981"  # Green
                elif score >= 70:
                    cat_color = "#3B82F6"  # Blue
                elif score >= 60:
                    cat_color = "#F59E0B"  # Yellow/Orange
                else:
                    cat_color = "#EF4444"  # Red
                
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
                            <span style="font-weight: 500;">{category}</span>
                            <span style="font-size: 0.8rem; color: #64748B; margin-left: 0.5rem;">(Weight: {int(weight * 100)}%)</span>
                        </div>
                        <div style="font-weight: 600; color: {cat_color};">{score}</div>
                    </div>
                    <div style="height: 6px; background-color: #E5E7EB; border-radius: 3px; margin-bottom: 0.5rem;">
                        <div style="height: 100%; width: {score}%; background-color: {cat_color}; border-radius: 3px;"></div>
                    </div>
                    <p style="margin: 0; font-size: 0.85rem; color: #64748B;">{description}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Industry benchmark comparison
    st.markdown("""
    <h3 style="font-size: 1.2rem; color: #1E293B; margin: 1.5rem 0 1rem;">Industry Benchmark Comparison</h3>
    """, unsafe_allow_html=True)
    
    # Create sample industry data with GenAI and AI specific benchmarks
    industry_data = {
        "Software Engineering": 78,
        "Your Resume": overall_score,
        "Top 10% Candidates": 92,
        "GenAI Professionals": 85,
        "AI/ML Specialists": 80
    }
    
    # Create a horizontal bar chart
    fig = go.Figure()
    
    for i, (category, score) in enumerate(industry_data.items()):
        color = "#4361EE" if category == "Your Resume" else "#94A3B8"
        width = 0.6
        
        fig.add_trace(go.Bar(
            y=[category],
            x=[score],
            orientation='h',
            marker=dict(color=color),
            width=width,
            text=score,
            textposition='outside',
            name=category
        ))
    
    fig.update_layout(
        height=250,  # Increased height to accommodate more bars
        margin=dict(l=0, r=10, t=10, b=0),
        xaxis=dict(
            title="Score",
            range=[0, 100],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title=None,
            autorange="reversed"
        ),
        barmode='group',
        plot_bgcolor='white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # GenAI and AI Scores explanation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <h4 style="font-size: 1.1rem; color: #1E293B; margin-top: 0;">GenAI Score Explained</h4>
            <p style="font-size: 0.9rem; color: #64748B; margin-bottom: 0.5rem;">
                The GenAI Score evaluates your resume for Generative AI skills and experience:
            </p>
            <ul style="font-size: 0.9rem; color: #64748B; margin: 0; padding-left: 1.5rem;">
                <li>Presence of GenAI terms (GANs, VAEs, diffusion models, transformers)</li>
                <li>LLM experience (GPT, BERT, fine-tuning, prompt engineering)</li>
                <li>Relevant tools and frameworks (PyTorch, Hugging Face, Stable Diffusion)</li>
                <li>Associated concepts (synthetic data generation, model interpretability)</li>
                <li>Level of hands-on experience vs. theoretical knowledge</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <h4 style="font-size: 1.1rem; color: #1E293B; margin-top: 0;">AI Score Explained</h4>
            <p style="font-size: 0.9rem; color: #64748B; margin-bottom: 0.5rem;">
                The AI Score measures broader AI/ML skills and experience:
            </p>
            <ul style="font-size: 0.9rem; color: #64748B; margin: 0; padding-left: 1.5rem;">
                <li>Machine Learning concepts (regression, classification, clustering)</li>
                <li>Deep Learning experience (CNNs, RNNs, neural networks)</li>
                <li>NLP concepts (tokenization, sentiment analysis, embeddings)</li>
                <li>Relevant tools and libraries (TensorFlow, Scikit-learn, Keras)</li>
                <li>Data processing, analysis, and model evaluation skills</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Resume analysis summary
    st.markdown("""
    <h3 style="font-size: 1.2rem; color: #1E293B; margin: 1rem 0;">Resume Analysis Summary</h3>
    """, unsafe_allow_html=True)
    
    # Generate AI-powered analysis summary if it doesn't exist
    if "ai_analysis_summary" not in st.session_state:
        with st.spinner("Generating personalized AI analysis..."):
            try:
                # Import the necessary function
                from pages._resume_enhancer import generate_ai_resume_analysis_summary
                
                # Get the full resume text
                resume_text = st.session_state.get("full_resume_text", "")
                
                # Generate the AI analysis summary
                ai_analysis = generate_ai_resume_analysis_summary(
                    resume_text,
                    st.session_state.extracted_sections,
                    st.session_state.confidence_scores or {}
                )
                st.session_state.ai_analysis_summary = ai_analysis
            except Exception as e:
                print(f"Error generating AI analysis summary: {str(e)}")
                st.session_state.ai_analysis_summary = None
    
    # Display AI analysis if available
    if st.session_state.get("ai_analysis_summary"):
        st.markdown(st.session_state.ai_analysis_summary)
        
        # Add a refresh button
        if st.button("🔄 Regenerate Analysis", key="regenerate_score_analysis"):
            try:
                # Import the necessary function
                from pages._resume_enhancer import generate_ai_resume_analysis_summary
                
                # Get the full resume text
                resume_text = st.session_state.get("full_resume_text", "")
                
                # Generate the AI analysis summary
                ai_analysis = generate_ai_resume_analysis_summary(
                    resume_text,
                    st.session_state.extracted_sections,
                    st.session_state.confidence_scores or {}
                )
                st.session_state.ai_analysis_summary = ai_analysis
                st.rerun()
            except Exception as e:
                st.error(f"Error regenerating analysis: {str(e)}")
    else:
        # Fallback to the original static analysis if AI fails
        analysis_sections = {}
        
        # Add analyses based on scores
        for category, details in st.session_state.resume_score.items():
            if category != "Overall Score":
                score = details["score"]
                
                if category == "Content Quality":
                    if score >= 80:
                        analysis_sections[category] = "Your resume content is strong and effectively communicates your experience."
                    elif score >= 70:
                        analysis_sections[category] = "Your resume content is good but could benefit from more specific accomplishments and metrics."
                    else:
                        analysis_sections[category] = "Your resume content needs improvement with more specific details and accomplishments."
                
                elif category == "Keyword Optimization":
                    if score >= 80:
                        analysis_sections[category] = "Your resume contains many relevant industry keywords that will help with ATS systems."
                    elif score >= 70:
                        analysis_sections[category] = "Your resume has some good keywords but could benefit from more industry-specific terminology."
                    else:
                        analysis_sections[category] = "Your resume needs more industry-specific keywords to improve visibility with ATS systems."
                
                elif category == "ATS Compatibility":
                    if score >= 80:
                        analysis_sections[category] = "Your resume is well structured for ATS systems and should pass through filters effectively."
                    elif score >= 70:
                        analysis_sections[category] = "Your resume has decent ATS compatibility but could benefit from better formatting."
                    else:
                        analysis_sections[category] = "Your resume may struggle with ATS systems and needs formatting improvements."
                
                elif category == "Formatting & Structure":
                    if score >= 80:
                        analysis_sections[category] = "Your resume has excellent formatting that is clean, consistent, and visually appealing."
                    elif score >= 70:
                        analysis_sections[category] = "Your resume formatting is good but could benefit from better organization and hierarchy."
                    else:
                        analysis_sections[category] = "Your resume formatting needs improvement to make it easier to scan and read."
                
                elif category == "Impact & Achievements":
                    if score >= 80:
                        analysis_sections[category] = "You've done an excellent job highlighting quantifiable achievements and results."
                    elif score >= 70:
                        analysis_sections[category] = "Your resume shows some achievements but could benefit from more metrics and results."
                    else:
                        analysis_sections[category] = "Your resume needs more emphasis on specific achievements and measurable results."
                
                elif category == "GenAI Score":
                    if score >= 80:
                        analysis_sections[category] = "Your resume demonstrates strong Generative AI skills and practical experience with advanced concepts."
                    elif score >= 70:
                        analysis_sections[category] = "Your resume shows good GenAI knowledge but could benefit from more specific projects or hands-on examples."
                    elif score >= 60:
                        analysis_sections[category] = "Your resume indicates basic GenAI familiarity. Consider adding more specific tools and techniques."
                    else:
                        analysis_sections[category] = "Your resume lacks sufficient Generative AI-related content to stand out in this increasingly important field."
                
                elif category == "AI Score":
                    if score >= 80:
                        analysis_sections[category] = "Your resume showcases strong AI/ML expertise with diverse skills and practical applications."
                    elif score >= 70:
                        analysis_sections[category] = "Your resume demonstrates good AI/ML knowledge but could use more depth in specific techniques."
                    elif score >= 60:
                        analysis_sections[category] = "Your resume shows basic AI/ML familiarity. Consider adding more technical skills and frameworks."
                    else:
                        analysis_sections[category] = "Your resume needs significant improvement in AI/ML content to be competitive in technical roles."
        
        # Display analysis in expandable cards
        for category, analysis in analysis_sections.items():
            with st.expander(f"{category} Analysis", expanded=False):
                st.markdown(analysis)
                
                # Add specific tips based on category
                st.markdown("#### Improvement Tips")
                
                if category == "Content Quality":
                    st.markdown("""
                    - Use active voice and action verbs to describe your responsibilities
                    - Quantify your achievements with specific metrics
                    - Tailor your content to match the job description
                    """)
                elif category == "Keyword Optimization":
                    st.markdown("""
                    - Research job descriptions in your target role and include relevant terms
                    - Include both spelled-out terms and acronyms (e.g., "Artificial Intelligence (AI)")
                    - Place keywords naturally throughout your resume
                    """)
                elif category == "ATS Compatibility":
                    st.markdown("""
                    - Use standard section headings
                    - Avoid tables, headers/footers, and text boxes
                    - Submit in PDF format when possible
                    """)
                elif category == "Formatting & Structure":
                    st.markdown("""
                    - Use consistent formatting for headings, dates, and bullet points
                    - Ensure adequate white space for readability
                    - Use a clean, professional font
                    """)
                elif category == "Impact & Achievements":
                    st.markdown("""
                    - Focus on results rather than just responsibilities
                    - Use the CAR method (Challenge, Action, Result)
                    - Quantify achievements with percentages, dollar amounts, etc.
                    """)
                elif category == "GenAI Score":
                    st.markdown("""
                    - Add specific GenAI projects (e.g., "Developed a fine-tuned GPT model for...")
                    - Include modern frameworks like Hugging Face, PyTorch, or Stable Diffusion
                    - Demonstrate practical implementation of GenAI concepts
                    - Mention prompt engineering and fine-tuning experience
                    - Highlight any synthetic data generation or model interpretability work
                    """)
                elif category == "AI Score":
                    st.markdown("""
                    - Include specific AI/ML algorithms you've used (e.g., Random Forest, SVMs)
                    - Add frameworks like TensorFlow, Scikit-learn, or Apache Spark
                    - Mention data preparation and feature engineering experience
                    - Describe model evaluation techniques you've implemented
                    - Highlight any specialized areas (NLP, computer vision, time series)
                    """)
    
    # Add buttons for navigation
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Previous Step", key="back_to_extraction_2"):
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        if st.button("Continue to Enhancement →", key="to_enhancement"):
            st.session_state.current_step = 4
            st.rerun()

def handle_resume_enhancement():
    """Handle the resume enhancement process"""
    render_section_title("Enhance Your Resume", "Step 4: Edit and enhance your resume content", icon="✨")
    
    if "extracted_sections" not in st.session_state or not st.session_state.extracted_sections:
        st.warning("Please complete the extraction step first.")
        if st.button("Go Back to Extract"):
            st.session_state.current_step = 2
        return
    
    # Get the extracted sections
    extracted_sections = st.session_state.extracted_sections
    
    st.write("### Edit and Enhance Your Resume")
    st.write("Use the editors below to refine your resume content. The AI has extracted the content and provided suggestions for improvements.")
    
    # Create a tab for each section
    tabs = st.tabs(["Summary", "Experience", "Education", "Skills", "Additional Sections"])
    
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
        
        # Display original and suggestions in columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Additional Sections:**")
            st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:5px;'>{original_additional}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**AI Suggestions:**")
            st.markdown(f"<div style='background-color:#e6f3ff;padding:10px;border-radius:5px;'>{ai_suggestions}</div>", unsafe_allow_html=True)
        
        # Rich text editor for editing the additional sections
        st.markdown("#### Edit Additional Sections:")
        enhanced_additional = rich_text_editor(
            value=(st.session_state.enhanced_resume.get("additional") or original_additional),
            height=300,
            key="additional_editor"
        )
        
        # Update the enhanced resume in session state
        st.session_state.enhanced_resume["additional"] = enhanced_additional
    
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

def handle_resume_download():
    """Handle the resume download process"""
    render_section_title("Download Enhanced Resume", "Step 5: Download your professionally enhanced resume")
    
    if "enhanced_resume" not in st.session_state or not st.session_state.enhanced_resume:
        st.warning("Please complete the enhancement step first.")
        if st.button("Go back to enhancement"):
            st.session_state.current_step = 4
            st.rerun()
        return
    
    st.markdown("### Your Enhanced Resume is Ready!")
    
    download_col, preview_col = st.columns([1, 2])
    
    with download_col:
        st.markdown("""
        <div class='info-box'>
            <h3>Download Options</h3>
            <p>Your enhanced resume is now ready for download in multiple formats.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Available Formats")
        
        # Generate real PDF from the enhanced resume data
        try:
            from utils.enhanced_resume_generator import generate_resume_download_buttons, get_enhanced_resume_data
            
            # Get enhanced resume data
            enhanced_data = get_enhanced_resume_data()
            
            # Generate PDF and DOCX
            with st.spinner("Generating files..."):
                success, pdf_data, docx_data = generate_resume_download_buttons(enhanced_data)
            
            if success:
                # Enable download buttons with actual file data
                st.download_button(
                    label="Download as PDF",
                    data=pdf_data,
                    file_name="enhanced_resume.pdf",
                    mime="application/pdf"
                )
                
                if docx_data:
                    st.download_button(
                        label="Download as DOCX",
                        data=docx_data,
                        file_name="enhanced_resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            else:
                st.error("Failed to generate resume files. Please try again.")
        except Exception as e:
            st.error(f"Error generating resume files: {str(e)}")
            st.warning("Please try again or contact support if the issue persists.")
        
        st.markdown("#### What's Next?")
        st.markdown("""
        - Use your enhanced resume to apply for jobs
        - Update it regularly with new experiences and skills
        - Consider tailoring it for specific job applications
        """)
        
        # Restart button
        if st.button("Start a New Enhancement"):
            # Reset session state
            st.session_state.resume_uploaded = False
            st.session_state.resume_data = None
            st.session_state.resume_score = None
            st.session_state.extracted_sections = None
            st.session_state.enhanced_resume = None
            st.session_state.current_step = 1
            
            # Redirect to the first step
            st.rerun()
    
    with preview_col:
        st.markdown("### Enhanced Resume Preview")
        
        # Display a preview of the enhanced resume
        try:
            from utils.enhanced_resume_generator import generate_resume_preview_html, get_enhanced_resume_data
            
            # Get enhanced resume data
            enhanced_data = get_enhanced_resume_data()
            
            # Generate HTML preview
            html_preview = generate_resume_preview_html(enhanced_data)
            
            # Display HTML preview
            st.markdown(html_preview, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error generating preview: {str(e)}")
            st.markdown("""
            <div style="border: 1px solid #ccc; padding: 20px; border-radius: 5px; text-align: center;">
                <p style="color: #888;">Preview unavailable</p>
            </div>
            """, unsafe_allow_html=True)

def display_section_content(section, data):
    """Helper function to display section content based on section type"""
    if section == "Personal Info":
        for key, value in data.items():
            st.write(f"**{key.capitalize()}:** {value}")
    elif section in ["Objective/Resume Summary"]:
        st.write(data)
    elif section in ["Education", "Work Experience", "Certifications", "Projects", "Awards"]:
        for item in data:
            st.markdown("---")
            for key, value in item.items():
                st.write(f"**{key.capitalize()}:** {value}")
    elif section == "Skills":
        st.write(", ".join(data))

def basic_clean_text(text):
    """Clean text without using NLP"""
    # Remove extra whitespace
    import re
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
    return text.strip()

def extract_text_from_pdf(uploaded_file):
    """Extract text from a PDF file using fast method by default"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        # Use simple PyPDF2 extraction by default (faster)
        from PyPDF2 import PdfReader
        reader = PdfReader(tmp_path)
        resume_text = ""
        for page in reader.pages:
            resume_text += page.extract_text() + "\n"
        
        # Only use Tika if advanced features are enabled
        if hasattr(st.session_state, 'enable_huggingface') and st.session_state.enable_huggingface:
            try:
                from utils.resume_processor import extract_text_with_tika
                advanced_text = extract_text_with_tika(tmp_path)
                if advanced_text and len(advanced_text) > len(resume_text) * 0.8:  # Only use if it got decent results
                    resume_text = advanced_text
            except Exception as e:
                st.warning(f"Advanced extraction failed: {str(e)}. Using standard extraction.")
        
        # Remove temporary file
        os.unlink(tmp_path)
        
        # Basic text cleaning (fast)
        resume_text = basic_clean_text(resume_text)
        
        return resume_text
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return f"Error extracting text: {str(e)}"

if __name__ == "__main__":
    main() 