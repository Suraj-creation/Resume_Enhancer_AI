"""
Highlighting and Annotation Utilities

This module provides functions for interactive highlighting and annotation
of resume content using mark.js and other tools.
"""

import streamlit as st
import streamlit.components.v1 as components
import random
import string
import re
from typing import List, Dict, Any, Optional

def generate_random_id(length=10):
    """Generate a random ID for unique element IDs"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def highlight_keywords(text: str, keywords: List[str], height: int = 300, key: Optional[str] = None) -> str:
    """
    Highlight keywords in text content using mark.js
    
    Args:
        text: The text content to highlight
        keywords: List of keywords to highlight
        height: Height of the component in pixels
        key: Unique key for the component
        
    Returns:
        str: The original text (highlighting is visual only)
    """
    if key is None:
        key = generate_random_id()
        
    # Sanitize keywords for JavaScript
    sanitized_keywords = [k.replace("'", "\\'").replace('"', '\\"') for k in keywords]
    
    # Create HTML with mark.js to highlight keywords
    html = f"""
    <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/8.11.1/mark.min.js"></script>
            <style>
                .highlight-container {{
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    height: {height}px;
                    overflow-y: auto;
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    line-height: 1.5;
                    background-color: white;
                }}
                mark {{
                    background-color: #ffe082;
                    padding: 2px 0;
                    border-radius: 2px;
                }}
                .keyword-match {{
                    background-color: #bbdefb;
                }}
                .improvement {{
                    background-color: #ffcdd2;
                }}
                .keyword-count {{
                    margin-bottom: 10px;
                    font-size: 12px;
                    color: #555;
                }}
            </style>
        </head>
        <body>
            <div class="keyword-count" id="count-{key}"></div>
            <div class="highlight-container" id="content-{key}">
                {text}
            </div>
            
            <script>
                // Initialize mark.js
                var markInstance = new Mark(document.getElementById("content-{key}"));
                
                // Keywords to highlight
                var keywords = {sanitized_keywords};
                
                // Highlight all keywords
                markInstance.mark(keywords, {{
                    accuracy: "partially",
                    separateWordSearch: true,
                    className: "keyword-match",
                    done: function(counter) {{
                        document.getElementById("count-{key}").textContent = 
                            "Found " + counter + " matches for " + keywords.length + " keywords";
                    }}
                }});
            </script>
        </body>
    </html>
    """
    
    # Render the HTML component
    components.html(html, height=height+50)
    
    return text

def highlight_with_feedback(text: str, extracted_features: Dict[str, Any], 
                          show_grammar: bool = True, show_improvements: bool = True,
                          show_missing: bool = True, show_formatting: bool = True,
                          height: int = 500, key: Optional[str] = None) -> str:
    """
    Highlight resume content with color-coded feedback for different types of issues
    
    Args:
        text: The text content to highlight
        extracted_features: Dictionary containing extracted resume features
        show_grammar: Whether to show grammar issues
        show_improvements: Whether to show improvement suggestions
        show_missing: Whether to show missing sections
        show_formatting: Whether to show formatting issues
        height: Height of the component in pixels
        key: Unique key for the component
        
    Returns:
        str: HTML with highlighted content
    """
    if key is None:
        key = generate_random_id()
    
    # Create HTML with enhanced styling and highlighting
    html = f"""
    <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/8.11.1/mark.min.js"></script>
            <style>
                .resume-container {{
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    height: {height}px;
                    overflow-y: auto;
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    line-height: 1.5;
                    background-color: white;
                    position: relative;
                }}
                .highlight-controls {{
                    margin-bottom: 15px;
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                }}
                .highlight-toggle {{
                    display: flex;
                    align-items: center;
                    gap: 5px;
                    padding: 5px 10px;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    cursor: pointer;
                    transition: all 0.2s;
                }}
                .highlight-toggle.active {{
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }}
                .highlight-toggle input[type="checkbox"] {{
                    margin: 0;
                }}
                .highlight-toggle label {{
                    margin: 0;
                    font-size: 12px;
                    cursor: pointer;
                }}
                /* Grammar Issues (Red) */
                .grammar-issue {{
                    background-color: #ffebee;
                    border-bottom: 2px solid #ef5350;
                    position: relative;
                    cursor: help;
                }}
                .grammar-issue:hover::after {{
                    content: attr(data-suggestion);
                    position: absolute;
                    bottom: 100%;
                    left: 0;
                    background-color: #ef5350;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    white-space: nowrap;
                    z-index: 100;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }}
                /* Improvement Areas (Yellow) */
                .improvement-area {{
                    background-color: #fff3e0;
                    border-bottom: 2px solid #ffa726;
                    position: relative;
                    cursor: help;
                }}
                .improvement-area:hover::after {{
                    content: attr(data-suggestion);
                    position: absolute;
                    bottom: 100%;
                    left: 0;
                    background-color: #ffa726;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    white-space: nowrap;
                    z-index: 100;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }}
                /* Missing Sections (Orange) */
                .missing-section {{
                    background-color: #fff8e1;
                    border-bottom: 2px solid #ffb74d;
                    position: relative;
                    cursor: help;
                }}
                .missing-section:hover::after {{
                    content: attr(data-suggestion);
                    position: absolute;
                    bottom: 100%;
                    left: 0;
                    background-color: #ffb74d;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    white-space: nowrap;
                    z-index: 100;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }}
                /* Formatting Issues (Blue) */
                .formatting-issue {{
                    background-color: #e3f2fd;
                    border-bottom: 2px solid #2196f3;
                    position: relative;
                    cursor: help;
                }}
                .formatting-issue:hover::after {{
                    content: attr(data-suggestion);
                    position: absolute;
                    bottom: 100%;
                    left: 0;
                    background-color: #2196f3;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    white-space: nowrap;
                    z-index: 100;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }}
                /* Legend */
                .highlight-legend {{
                    margin-top: 15px;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border-radius: 4px;
                    font-size: 12px;
                }}
                .legend-item {{
                    display: inline-flex;
                    align-items: center;
                    margin-right: 15px;
                }}
                .legend-color {{
                    width: 12px;
                    height: 12px;
                    border-radius: 2px;
                    margin-right: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="highlight-controls">
                <div class="highlight-toggle" id="grammar-toggle-{key}">
                    <input type="checkbox" id="show-grammar-{key}" {'checked' if show_grammar else ''}>
                    <label for="show-grammar-{key}">Grammar Issues</label>
                </div>
                <div class="highlight-toggle" id="improvements-toggle-{key}">
                    <input type="checkbox" id="show-improvements-{key}" {'checked' if show_improvements else ''}>
                    <label for="show-improvements-{key}">Improvement Areas</label>
                </div>
                <div class="highlight-toggle" id="missing-toggle-{key}">
                    <input type="checkbox" id="show-missing-{key}" {'checked' if show_missing else ''}>
                    <label for="show-missing-{key}">Missing Sections</label>
                </div>
                <div class="highlight-toggle" id="formatting-toggle-{key}">
                    <input type="checkbox" id="show-formatting-{key}" {'checked' if show_formatting else ''}>
                    <label for="show-formatting-{key}">Formatting Issues</label>
                </div>
            </div>
            
            <div class="resume-container" id="content-{key}">
                {text}
            </div>
            
            <div class="highlight-legend">
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #ffebee; border-bottom: 2px solid #ef5350;"></div>
                    <span>Grammar Issues</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #fff3e0; border-bottom: 2px solid #ffa726;"></div>
                    <span>Improvement Areas</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #fff8e1; border-bottom: 2px solid #ffb74d;"></div>
                    <span>Missing Sections</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #e3f2fd; border-bottom: 2px solid #2196f3;"></div>
                    <span>Formatting Issues</span>
                </div>
            </div>
            
            <script>
                // Initialize mark.js
                var markInstance = new Mark(document.getElementById("content-{key}"));
                
                // Function to update highlighting based on toggles
                function updateHighlighting() {{
                    // Clear all existing highlights
                    markInstance.unmark();
                    
                    const showGrammar = document.getElementById("show-grammar-{key}").checked;
                    const showImprovements = document.getElementById("show-improvements-{key}").checked;
                    const showMissing = document.getElementById("show-missing-{key}").checked;
                    const showFormatting = document.getElementById("show-formatting-{key}").checked;
                    
                    // Get the extracted features
                    const features = {extracted_features};
                    
                    // Highlight grammar issues (red)
                    if (showGrammar && features.grammar_issues) {{
                        features.grammar_issues.forEach(function(issue) {{
                            markInstance.mark(issue.text, {{
                                className: "grammar-issue",
                                accuracy: "exactly",
                                separateWordSearch: false,
                                acrossElements: true,
                                done: function() {{
                                    // Add data-suggestion attribute to highlighted elements
                                    document.querySelectorAll('.grammar-issue').forEach(function(elem) {{
                                        if (elem.textContent === issue.text) {{
                                            elem.setAttribute('data-suggestion', issue.suggestion || issue.reason);
                                        }}
                                    }});
                                }}
                            }});
                        }});
                    }}
                    
                    // Highlight improvement areas (yellow)
                    if (showImprovements && features.improvement_suggestions) {{
                        features.improvement_suggestions.forEach(function(suggestion) {{
                            markInstance.mark(suggestion.text, {{
                                className: "improvement-area",
                                accuracy: "exactly",
                                separateWordSearch: false,
                                acrossElements: true,
                                done: function() {{
                                    // Add data-suggestion attribute to highlighted elements
                                    document.querySelectorAll('.improvement-area').forEach(function(elem) {{
                                        if (elem.textContent === suggestion.text) {{
                                            elem.setAttribute('data-suggestion', suggestion.suggestion || suggestion.reason);
                                        }}
                                    }});
                                }}
                            }});
                        }});
                    }}
                    
                    // Highlight missing sections (orange)
                    if (showMissing && features.missing_sections) {{
                        features.missing_sections.forEach(function(section) {{
                            const sectionText = section.name;
                            markInstance.mark(sectionText, {{
                                className: "missing-section",
                                accuracy: "exactly",
                                separateWordSearch: false,
                                acrossElements: true,
                                done: function() {{
                                    // Add data-suggestion attribute to highlighted elements
                                    document.querySelectorAll('.missing-section').forEach(function(elem) {{
                                        if (elem.textContent === sectionText) {{
                                            elem.setAttribute('data-suggestion', section.suggestion);
                                        }}
                                    }});
                                }}
                            }});
                        }});
                    }}
                    
                    // Highlight formatting issues (blue)
                    if (showFormatting && features.formatting_issues) {{
                        features.formatting_issues.forEach(function(issue) {{
                            markInstance.mark(issue.text, {{
                                className: "formatting-issue",
                                accuracy: "exactly",
                                separateWordSearch: false,
                                acrossElements: true,
                                done: function() {{
                                    // Add data-suggestion attribute to highlighted elements
                                    document.querySelectorAll('.formatting-issue').forEach(function(elem) {{
                                        if (elem.textContent === issue.text) {{
                                            elem.setAttribute('data-suggestion', issue.suggestion);
                                        }}
                                    }});
                                }}
                            }});
                        }});
                    }}
                }}
                
                // Add event listeners to toggles
                document.getElementById("show-grammar-{key}").addEventListener('change', updateHighlighting);
                document.getElementById("show-improvements-{key}").addEventListener('change', updateHighlighting);
                document.getElementById("show-missing-{key}").addEventListener('change', updateHighlighting);
                document.getElementById("show-formatting-{key}").addEventListener('change', updateHighlighting);
                
                // Initial highlighting
                updateHighlighting();
            </script>
        </body>
    </html>
    """
    
    # Render the HTML component
    components.html(html, height=height+100)
    
    return text

def pdf_annotator(pdf_content, annotations=None, height=600, key=None):
    """
    Render a PDF with annotation capabilities using pdf-annotate.js
    
    Args:
        pdf_content: The PDF file content as bytes
        annotations: Optional list of pre-defined annotations
        height: Height of the component in pixels
        key: Unique key for the component
        
    Returns:
        List[Dict]: Any new or updated annotations
    """
    if key is None:
        key = generate_random_id()
    
    # Convert PDF content to base64 for embedding in HTML
    import base64
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    # Format annotations for JS if provided
    annotations_js = "[]"
    if annotations:
        import json
        try:
            annotations_js = json.dumps(annotations)
        except:
            annotations_js = "[]"
    
    # Create HTML with PDF.js and pdf-annotate.js
    html = f"""
    <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.min.js"></script>
            <script src="https://unpkg.com/pdf-annotate.js@1.2.0/dist/pdf-annotate.min.js"></script>
            <style>
                .pdf-container {{
                    width: 100%;
                    height: {height}px;
                    border: 1px solid #ddd;
                    overflow: auto;
                    position: relative;
                }}
                #pdf-canvas-{key} {{
                    position: absolute;
                }}
                #annotations-{key} {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    pointer-events: none;
                }}
                .toolbar {{
                    display: flex;
                    gap: 10px;
                    margin-bottom: 10px;
                }}
                .annotation-btn {{
                    padding: 5px 10px;
                    background: #f1f1f1;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                .annotation-btn.active {{
                    background: #4361EE;
                    color: white;
                }}
            </style>
        </head>
        <body>
            <div class="toolbar">
                <button id="highlight-btn-{key}" class="annotation-btn">Highlight</button>
                <button id="note-btn-{key}" class="annotation-btn">Add Note</button>
                <button id="clear-btn-{key}" class="annotation-btn">Clear</button>
                <button id="save-btn-{key}" class="annotation-btn">Save</button>
            </div>
            
            <div class="pdf-container" id="pdf-container-{key}">
                <canvas id="pdf-canvas-{key}"></canvas>
                <svg id="annotations-{key}"></svg>
            </div>
            
            <script>
                // Initialize PDF.js and pdf-annotate.js
                const pdfjsLib = window['pdfjs-dist/build/pdf'];
                const PDFAnnotate = window.PDFAnnotate;
                
                // Configure PDF.js
                pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.worker.min.js';
                
                // Initialize variables
                let currentAnnotationType = null;
                let currentPage = 1;
                let pdfDocument = null;
                let existingAnnotations = {annotations_js};
                
                // Load the PDF from base64
                const loadPDF = async () => {{
                    const pdfData = atob('{pdf_base64}');
                    const loadingTask = pdfjsLib.getDocument({{ data: pdfData }});
                    pdfDocument = await loadingTask.promise;
                    
                    // Render first page
                    renderPage(currentPage);
                    
                    // Set up annotation functionality
                    setupAnnotations();
                    
                    // Load existing annotations if any
                    if (existingAnnotations.length > 0) {{
                        renderAnnotations();
                    }}
                }};
                
                // Render a specific page
                const renderPage = async (pageNumber) => {{
                    const page = await pdfDocument.getPage(pageNumber);
                    const canvas = document.getElementById('pdf-canvas-{key}');
                    const context = canvas.getContext('2d');
                    
                    // Calculate scale to fit container width
                    const container = document.getElementById('pdf-container-{key}');
                    const containerWidth = container.clientWidth;
                    const viewport = page.getViewport({{ scale: 1 }});
                    const scale = containerWidth / viewport.width;
                    const scaledViewport = page.getViewport({{ scale }});
                    
                    // Set canvas size to match scaled page
                    canvas.width = scaledViewport.width;
                    canvas.height = scaledViewport.height;
                    
                    // Render PDF page
                    await page.render({{
                        canvasContext: context,
                        viewport: scaledViewport
                    }}).promise;
                    
                    // Setup annotations layer
                    const annotationLayer = document.getElementById('annotations-{key}');
                    annotationLayer.setAttribute('width', scaledViewport.width);
                    annotationLayer.setAttribute('height', scaledViewport.height);
                }};
                
                // Set up annotation functionality
                const setupAnnotations = () => {{
                    // Highlight button
                    document.getElementById('highlight-btn-{key}').addEventListener('click', () => {{
                        setAnnotationType('highlight');
                    }});
                    
                    // Note button
                    document.getElementById('note-btn-{key}').addEventListener('click', () => {{
                        setAnnotationType('note');
                    }});
                    
                    // Clear button
                    document.getElementById('clear-btn-{key}').addEventListener('click', () => {{
                        clearAnnotations();
                    }});
                    
                    // Save button
                    document.getElementById('save-btn-{key}').addEventListener('click', () => {{
                        saveAnnotations();
                    }});
                    
                    // Setup annotation drawing on canvas
                    const canvas = document.getElementById('pdf-canvas-{key}');
                    canvas.addEventListener('mousedown', startAnnotation);
                    canvas.addEventListener('mousemove', moveAnnotation);
                    canvas.addEventListener('mouseup', endAnnotation);
                }};
                
                // Set the current annotation type
                const setAnnotationType = (type) => {{
                    // Reset active states
                    document.querySelectorAll('.annotation-btn').forEach(btn => {{
                        btn.classList.remove('active');
                    }});
                    
                    if (type === currentAnnotationType) {{
                        // Toggle off
                        currentAnnotationType = null;
                    }} else {{
                        // Set new type
                        currentAnnotationType = type;
                        document.getElementById(`${{type}}-btn-{key}`).classList.add('active');
                    }}
                }};
                
                // Start drawing annotation
                const startAnnotation = (e) => {{
                    if (!currentAnnotationType) return;
                    
                    // Get position relative to canvas
                    const canvas = document.getElementById('pdf-canvas-{key}');
                    const rect = canvas.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    if (currentAnnotationType === 'highlight') {{
                        // Create highlight rectangle
                        const svg = document.getElementById('annotations-{key}');
                        const highlight = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                        highlight.setAttribute('x', x);
                        highlight.setAttribute('y', y);
                        highlight.setAttribute('width', '0');
                        highlight.setAttribute('height', '0');
                        highlight.setAttribute('fill', 'rgba(255, 255, 0, 0.3)');
                        highlight.setAttribute('data-type', 'highlight');
                        highlight.id = 'current-annotation';
                        svg.appendChild(highlight);
                    }} else if (currentAnnotationType === 'note') {{
                        // Create note icon
                        const svg = document.getElementById('annotations-{key}');
                        const note = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                        note.setAttribute('x', x);
                        note.setAttribute('y', y);
                        note.setAttribute('font-family', 'Arial');
                        note.setAttribute('font-size', '16');
                        note.setAttribute('fill', 'blue');
                        note.setAttribute('data-type', 'note');
                        note.id = 'current-annotation';
                        note.textContent = '📝';
                        svg.appendChild(note);
                        
                        // Prompt for note text
                        const noteText = prompt('Enter note:');
                        if (noteText) {{
                            note.setAttribute('data-text', noteText);
                            
                            // Add tooltip behavior
                            note.addEventListener('mouseover', (e) => {{
                                const tooltip = document.createElement('div');
                                tooltip.textContent = noteText;
                                tooltip.style.position = 'absolute';
                                tooltip.style.background = '#fff8e1';
                                tooltip.style.padding = '5px';
                                tooltip.style.border = '1px solid #ddd';
                                tooltip.style.borderRadius = '4px';
                                tooltip.style.left = (e.pageX + 10) + 'px';
                                tooltip.style.top = (e.pageY + 10) + 'px';
                                tooltip.style.zIndex = '1000';
                                tooltip.id = 'tooltip';
                                document.body.appendChild(tooltip);
                            }});
                            
                            note.addEventListener('mouseout', () => {{
                                const tooltip = document.getElementById('tooltip');
                                if (tooltip) tooltip.remove();
                            }});
                        }} else {{
                            // Remove if cancelled
                            note.remove();
                        }}
                        
                        // No need to track mouse movement for notes
                        currentAnnotationType = null;
                        document.querySelectorAll('.annotation-btn').forEach(btn => {{
                            btn.classList.remove('active');
                        }});
                    }}
                }};
                
                // Update annotation while dragging
                const moveAnnotation = (e) => {{
                    if (currentAnnotationType !== 'highlight') return;
                    
                    const annotation = document.getElementById('current-annotation');
                    if (!annotation) return;
                    
                    // Get position relative to canvas
                    const canvas = document.getElementById('pdf-canvas-{key}');
                    const rect = canvas.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    // Update highlight size
                    const startX = parseFloat(annotation.getAttribute('x'));
                    const startY = parseFloat(annotation.getAttribute('y'));
                    const width = x - startX;
                    const height = y - startY;
                    
                    annotation.setAttribute('width', width);
                    annotation.setAttribute('height', height);
                }};
                
                // Finish annotation
                const endAnnotation = () => {{
                    if (currentAnnotationType !== 'highlight') return;
                    
                    const annotation = document.getElementById('current-annotation');
                    if (annotation) {{
                        annotation.id = 'annotation-' + Date.now();
                        
                        // Reset state
                        currentAnnotationType = null;
                        document.querySelectorAll('.annotation-btn').forEach(btn => {{
                            btn.classList.remove('active');
                        }});
                    }}
                }};
                
                // Clear all annotations
                const clearAnnotations = () => {{
                    const svg = document.getElementById('annotations-{key}');
                    svg.innerHTML = '';
                    existingAnnotations = [];
                }};
                
                // Save annotations to send back to Streamlit
                const saveAnnotations = () => {{
                    const svg = document.getElementById('annotations-{key}');
                    const annotationElements = svg.querySelectorAll('[data-type]');
                    
                    const savedAnnotations = [];
                    annotationElements.forEach(el => {{
                        if (el.getAttribute('data-type') === 'highlight') {{
                            savedAnnotations.push({{
                                type: 'highlight',
                                x: parseFloat(el.getAttribute('x')),
                                y: parseFloat(el.getAttribute('y')),
                                width: parseFloat(el.getAttribute('width')),
                                height: parseFloat(el.getAttribute('height')),
                                page: currentPage
                            }});
                        }} else if (el.getAttribute('data-type') === 'note') {{
                            savedAnnotations.push({{
                                type: 'note',
                                x: parseFloat(el.getAttribute('x')),
                                y: parseFloat(el.getAttribute('y')),
                                text: el.getAttribute('data-text') || '',
                                page: currentPage
                            }});
                        }}
                    }});
                    
                    // Send annotations to Streamlit
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: JSON.stringify(savedAnnotations),
                    }}, '*');
                    
                    alert('Annotations saved!');
                }};
                
                // Render existing annotations
                const renderAnnotations = () => {{
                    const svg = document.getElementById('annotations-{key}');
                    
                    existingAnnotations.forEach((anno, index) => {{
                        if (anno.page !== currentPage) return;
                        
                        if (anno.type === 'highlight') {{
                            const highlight = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                            highlight.setAttribute('x', anno.x);
                            highlight.setAttribute('y', anno.y);
                            highlight.setAttribute('width', anno.width);
                            highlight.setAttribute('height', anno.height);
                            highlight.setAttribute('fill', 'rgba(255, 255, 0, 0.3)');
                            highlight.setAttribute('data-type', 'highlight');
                            highlight.id = 'annotation-' + index;
                            svg.appendChild(highlight);
                        }} else if (anno.type === 'note') {{
                            const note = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                            note.setAttribute('x', anno.x);
                            note.setAttribute('y', anno.y);
                            note.setAttribute('font-family', 'Arial');
                            note.setAttribute('font-size', '16');
                            note.setAttribute('fill', 'blue');
                            note.setAttribute('data-type', 'note');
                            note.setAttribute('data-text', anno.text);
                            note.id = 'annotation-' + index;
                            note.textContent = '📝';
                            svg.appendChild(note);
                            
                            // Add tooltip behavior
                            note.addEventListener('mouseover', (e) => {{
                                const tooltip = document.createElement('div');
                                tooltip.textContent = anno.text;
                                tooltip.style.position = 'absolute';
                                tooltip.style.background = '#fff8e1';
                                tooltip.style.padding = '5px';
                                tooltip.style.border = '1px solid #ddd';
                                tooltip.style.borderRadius = '4px';
                                tooltip.style.left = (e.pageX + 10) + 'px';
                                tooltip.style.top = (e.pageY + 10) + 'px';
                                tooltip.style.zIndex = '1000';
                                tooltip.id = 'tooltip';
                                document.body.appendChild(tooltip);
                            }});
                            
                            note.addEventListener('mouseout', () => {{
                                const tooltip = document.getElementById('tooltip');
                                if (tooltip) tooltip.remove();
                            }});
                        }}
                    }});
                }};
                
                // Load PDF when component is ready
                loadPDF();
            </script>
        </body>
    </html>
    """
    
    # Initialize saved annotations in session state if not already there
    if f"annotations_{key}" not in st.session_state:
        st.session_state[f"annotations_{key}"] = annotations or []
    
    # Render the component and get the returned annotations
    component_value = components.html(html, height=height+60, key=f"pdf_annotator_{key}")
    
    # Update and return saved annotations if component returns a value
    if component_value:
        import json
        try:
            new_annotations = json.loads(component_value)
            st.session_state[f"annotations_{key}"] = new_annotations
            return new_annotations
        except:
            pass
    
    return st.session_state[f"annotations_{key}"]

def extract_keywords_from_text(text: str, count: int = 15) -> List[str]:
    """
    Extract important keywords from text using simple frequency analysis
    
    Args:
        text: The text to analyze
        count: Maximum number of keywords to extract
        
    Returns:
        List[str]: The extracted keywords
    """
    # Stop words to exclude
    stop_words = set([
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", 
        "any", "are", "as", "at", "be", "because", "been", "before", "being", "below", 
        "between", "both", "but", "by", "can", "did", "do", "does", "doing", "don", 
        "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", 
        "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", 
        "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", 
        "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", 
        "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", 
        "same", "she", "should", "so", "some", "such", "t", "than", "that", "the", 
        "their", "theirs", "them", "themselves", "then", "there", "these", "they", 
        "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", 
        "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", 
        "will", "with", "you", "your", "yours", "yourself", "yourselves"
    ])
    
    # Clean and tokenize text
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
    words = text.split()
    
    # Remove stop words and short words
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_freq = {}
    for word in words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda item: item[1], reverse=True)
    
    # Return top keywords
    keywords = [word for word, freq in sorted_words[:count]]
    return keywords

def find_improvement_suggestions(text: str, job_description: str = None) -> List[Dict[str, Any]]:
    """
    Find areas for improvement in the resume text
    
    Args:
        text: The resume text
        job_description: Optional job description for targeted suggestions
        
    Returns:
        List[Dict]: Suggestions with text, reason, and positions
    """
    suggestions = []
    
    # Check for common weak phrases
    weak_phrases = [
        {"pattern": r"\b(responsible for)\b", "reason": "Use action verbs instead of 'responsible for'"},
        {"pattern": r"\b(worked on|worked with)\b", "reason": "Replace with more specific action verbs like 'implemented' or 'developed'"},
        {"pattern": r"\b(helped|assisted)\b", "reason": "Use stronger action verbs that show your direct contribution"},
        {"pattern": r"\bdutie?s include[d]?\b", "reason": "Focus on achievements rather than duties"},
        {"pattern": r"\b(good|excellent) (communication|skills)\b", "reason": "Too generic - provide specific examples of your skills"},
        {"pattern": r"\bteam player\b", "reason": "Generic term - describe specific collaborative achievements"},
        {"pattern": r"\bhard[ -]working\b", "reason": "Demonstrate your work ethic through specific achievements"},
        {"pattern": r"\b(etc|different|various)\b", "reason": "Be specific instead of using vague terms"},
        {"pattern": r"\bi (think|believe|feel)\b", "reason": "Avoid subjective phrases, focus on facts and achievements"}
    ]
    
    # Check for phrases without metrics
    metric_patterns = [
        {"pattern": r"\b(improved|increased|decreased|reduced|enhanced|boosted)\b", 
         "reason": "Add specific metrics, such as percentages or numbers, to quantify this achievement"}
    ]
    
    # Check for weak phrases
    for phrase in weak_phrases:
        for match in re.finditer(phrase["pattern"], text, re.IGNORECASE):
            suggestions.append({
                "text": match.group(0),
                "reason": phrase["reason"],
                "start": match.start(),
                "end": match.end()
            })
    
    # Check for metrics
    for pattern in metric_patterns:
        for match in re.finditer(pattern["pattern"], text, re.IGNORECASE):
            # Check if there's a number within 6 words after the match
            after_text = text[match.end():match.end() + 50]
            words_after = re.split(r'\s+', after_text)[:6]
            has_metric = any(re.search(r'\d+%?', word) for word in words_after)
            
            if not has_metric:
                suggestions.append({
                    "text": match.group(0),
                    "reason": pattern["reason"],
                    "start": match.start(),
                    "end": match.end()
                })
    
    # If job description is provided, check for keyword matches
    if job_description:
        job_keywords = extract_keywords_from_text(job_description, 10)
        for keyword in job_keywords:
            if keyword not in text.lower():
                # Find a good place to insert this keyword
                suggestions.append({
                    "text": "Consider adding: " + keyword,
                    "reason": f"The job description mentions '{keyword}', but it's not in your resume",
                    "start": 0,
                    "end": 0
                })
    
    return suggestions 