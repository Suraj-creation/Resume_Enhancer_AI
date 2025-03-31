import streamlit as st
import streamlit.components.v1 as components
import random
import string
import json

def generate_random_id(length=10):
    """Generate a random ID for unique element IDs"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def rich_text_editor(value="", height=400, key=None):
    """
    Create a TinyMCE rich text editor embedded in Streamlit
    
    Args:
        value (str): Initial HTML content
        height (int): Height of the editor in pixels
        key (str): Unique key for the component
    
    Returns:
        str: The edited HTML content
    """
    # Generate unique keys for this instance
    if key is None:
        key = generate_random_id()
    
    editor_id = f"tinymce_{key}"
    result_id = f"result_{key}"
    
    # Store initial value in session state
    if f"content_{key}" not in st.session_state:
        st.session_state[f"content_{key}"] = value
        
    # Create the TinyMCE editor using HTML component
    tinymce_html = f"""
    <html>
        <head>
            <script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js" referrerpolicy="origin"></script>
            <script>
                function setupTinyMCE() {{
                    tinymce.init({{
                        selector: '#{editor_id}',
                        height: {height},
                        plugins: 'anchor autolink charmap codesample emoticons image link lists media searchreplace table visualblocks wordcount checklist mediaembed casechange export formatpainter pageembed linkchecker permanentpen powerpaste advtable advcode tableofcontents',
                        toolbar: 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
                        setup: function(editor) {{
                            editor.on('change', function() {{
                                document.getElementById('{result_id}').value = editor.getContent();
                                // Send update to Streamlit
                                setTimeout(function() {{
                                    const event = new CustomEvent('updateContent', {{ detail: editor.getContent() }});
                                    window.dispatchEvent(event);
                                }}, 100);
                            }});
                        }},
                        content_style: 'body {{ font-family:Arial,Helvetica,sans-serif; font-size:16px }}'
                    }});
                }}
                
                // Setup on load
                window.addEventListener('load', setupTinyMCE);
                
                // Handle content updates from Streamlit
                window.addEventListener('message', function(e) {{
                    if (e.data.type === 'streamlitUpdateValue') {{
                        try {{
                            const data = JSON.parse(e.data.value);
                            if (data.key === '{key}' && tinymce.get('{editor_id}')) {{
                                tinymce.get('{editor_id}').setContent(data.value || '');
                            }}
                        }} catch (err) {{
                            console.error('Error updating TinyMCE content:', err);
                        }}
                    }}
                }});
                
                // Send content to Streamlit on update
                window.addEventListener('updateContent', function(e) {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: JSON.stringify({{ key: '{key}', value: e.detail }}),
                    }}, '*');
                }});
            </script>
        </head>
        <body>
            <div class="tinymce-wrapper">
                <textarea id="{editor_id}">{value}</textarea>
                <input type="hidden" id="{result_id}" name="content">
            </div>
        </body>
    </html>
    """
    
    # Use an HTML component with specified height to display the editor
    components.html(tinymce_html, height=height+50)
    
    # Create a callback for receiving content updates from the editor
    if f"content_{key}" in st.session_state and st.session_state[f"content_{key}"] != value:
        # Only update if the value has changed
        update_script = f"""
        <script>
            window.parent.postMessage({{
                type: 'streamlit:updateValue',
                value: JSON.stringify({{ key: '{key}', value: '{st.session_state[f"content_{key}"]}' }}),
            }}, '*');
        </script>
        """
        components.html(update_script, height=0, width=0)
    
    # Return the current content value
    return st.session_state.get(f"content_{key}", value)

def quill_editor(value="", height=400, key=None):
    """
    Create a Quill.js rich text editor embedded in Streamlit
    
    Args:
        value (str): Initial HTML content
        height (int): Height of the editor in pixels
        key (str): Unique key for the component
    
    Returns:
        str: The edited HTML content
    """
    # Generate unique keys for this instance
    if key is None:
        key = generate_random_id()
    
    editor_id = f"quill_{key}"
    result_id = f"result_{key}"
    
    # Store initial value in session state
    if f"content_{key}" not in st.session_state:
        st.session_state[f"content_{key}"] = value
    
    # Create the Quill editor using HTML component
    quill_html = f"""
    <html>
        <head>
            <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
            <script src="https://cdn.quilljs.com/1.3.6/quill.min.js"></script>
            <style>
                .quill-wrapper {{
                    height: {height}px;
                }}
                #editor-container {{
                    height: {height-50}px;
                }}
            </style>
        </head>
        <body>
            <div class="quill-wrapper">
                <div id="editor-container">{value}</div>
                <input type="hidden" id="{result_id}" name="content">
            </div>
            
            <script>
                var quill = new Quill('#editor-container', {{
                    modules: {{
                        toolbar: [
                            [{{ 'header': [1, 2, 3, false] }}],
                            ['bold', 'italic', 'underline', 'strike'],
                            ['blockquote', 'code-block'],
                            [{{ 'list': 'ordered' }}, {{ 'list': 'bullet' }}],
                            [{{ 'indent': '-1' }}, {{ 'indent': '+1' }}],
                            ['link', 'image'],
                            ['clean']
                        ]
                    }},
                    placeholder: 'Edit your content...',
                    theme: 'snow'
                }});
                
                quill.on('text-change', function() {{
                    var html = document.querySelector('#editor-container').firstChild.innerHTML;
                    document.getElementById('{result_id}').value = html;
                    
                    // Send update to Streamlit
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: JSON.stringify({{ key: '{key}', value: html }}),
                    }}, '*');
                }});
                
                // Handle content updates from Streamlit
                window.addEventListener('message', function(e) {{
                    if (e.data.type === 'streamlitUpdateValue') {{
                        try {{
                            const data = JSON.parse(e.data.value);
                            if (data.key === '{key}') {{
                                quill.clipboard.dangerouslyPasteHTML(data.value || '');
                            }}
                        }} catch (err) {{
                            console.error('Error updating Quill content:', err);
                        }}
                    }}
                }});
            </script>
        </body>
    </html>
    """
    
    # Use an HTML component with specified height to display the editor
    components.html(quill_html, height=height+50)
    
    # Create a callback for receiving content updates from the editor
    if f"content_{key}" in st.session_state and st.session_state[f"content_{key}"] != value:
        # Only update if the value has changed
        update_script = f"""
        <script>
            window.parent.postMessage({{
                type: 'streamlit:updateValue',
                value: JSON.stringify({{ key: '{key}', value: '{st.session_state[f"content_{key}"]}' }}),
            }}, '*');
        </script>
        """
        components.html(update_script, height=0, width=0)
    
    # Return the current content value
    return st.session_state.get(f"content_{key}", value)

def prosemirror_editor(value="", height=400, key=None):
    """
    Create a ProseMirror rich text editor embedded in Streamlit
    
    Args:
        value (str): Initial HTML content
        height (int): Height of the editor in pixels
        key (str): Unique key for the component
    
    Returns:
        str: The edited HTML content
    """
    # Generate unique keys for this instance
    if key is None:
        key = generate_random_id()
    
    editor_id = f"prosemirror_{key}"
    result_id = f"result_{key}"
    
    # Store initial value in session state
    if f"content_{key}" not in st.session_state:
        st.session_state[f"content_{key}"] = value
    
    # Create the ProseMirror editor using HTML component
    prosemirror_html = f"""
    <html>
        <head>
            <script src="https://prosemirror.net/examples/prosemirror.js"></script>
            <script src="https://prosemirror.net/examples/menu/menu.js"></script>
            <link rel="stylesheet" href="https://prosemirror.net/examples/menu/menu.css">
            <style>
                .ProseMirror {{
                    height: {height-100}px;
                    overflow-y: auto;
                    padding: 10px;
                    border: 1px solid #ccc;
                }}
                .ProseMirror:focus {{
                    outline: none;
                    border-color: #4361EE;
                }}
                .editor-wrapper {{
                    height: {height}px;
                }}
            </style>
        </head>
        <body>
            <div class="editor-wrapper">
                <div id="{editor_id}"></div>
                <input type="hidden" id="{result_id}" name="content">
            </div>
            
            <script>
                // Initialize ProseMirror
                window.addEventListener('load', function() {{
                    const {{EditorState, Plugin}} = PM.state
                    const {{EditorView}} = PM.view
                    const {{Schema, DOMParser, DOMSerializer}} = PM.model
                    const {{schema, defaultMarkdownParser, defaultMarkdownSerializer}} = PM.markdown
                    const {{exampleSetup}} = PM.example_setup
                    const {{menuBar}} = PM.menu
                    
                    // Create a custom schema
                    const mySchema = new Schema({{
                        nodes: schema.spec.nodes,
                        marks: schema.spec.marks
                    }})
                    
                    // Create the editor state
                    let state = EditorState.create({{
                        doc: defaultMarkdownParser.parse('{value}'),
                        plugins: exampleSetup({{schema: mySchema}}).concat(
                            menuBar({{content: mySchema.spec.nodes}}),
                            new Plugin({{
                                view(editorView) {{
                                    return {{
                                        update: function(view, prevState) {{
                                            const content = defaultMarkdownSerializer.serialize(view.state.doc);
                                            document.getElementById('{result_id}').value = content;
                                            
                                            // Send update to Streamlit
                                            window.parent.postMessage({{
                                                type: 'streamlit:setComponentValue',
                                                value: JSON.stringify({{ key: '{key}', value: content }}),
                                            }}, '*');
                                        }}
                                    }}
                                }}
                            }})
                        )
                    }})
                    
                    // Create the editor view
                    let view = new EditorView(document.getElementById('{editor_id}'), {{
                        state,
                        dispatchTransaction(transaction) {{
                            let newState = view.state.apply(transaction)
                            view.updateState(newState)
                        }}
                    }})
                    
                    // Handle content updates from Streamlit
                    window.addEventListener('message', function(e) {{
                        if (e.data.type === 'streamlitUpdateValue') {{
                            try {{
                                const data = JSON.parse(e.data.value);
                                if (data.key === '{key}') {{
                                    const newState = EditorState.create({{
                                        doc: defaultMarkdownParser.parse(data.value || ''),
                                        plugins: state.plugins
                                    }})
                                    view.updateState(newState)
                                }}
                            }} catch (err) {{
                                console.error('Error updating ProseMirror content:', err);
                            }}
                        }}
                    }});
                }});
            </script>
        </body>
    </html>
    """
    
    # Use an HTML component with specified height to display the editor
    components.html(prosemirror_html, height=height+50)
    
    # Create a callback for receiving content updates from the editor
    if f"content_{key}" in st.session_state and st.session_state[f"content_{key}"] != value:
        # Only update if the value has changed
        update_script = f"""
        <script>
            window.parent.postMessage({{
                type: 'streamlit:updateValue',
                value: JSON.stringify({{ key: '{key}', value: '{st.session_state[f"content_{key}"]}' }}),
            }}, '*');
        </script>
        """
        components.html(update_script, height=0, width=0)
    
    # Return the current content value
    return st.session_state.get(f"content_{key}", value) 