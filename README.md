# Resume Enhancer

An AI-powered application that helps you improve your resume, match it to job descriptions, and optimize it for specific career opportunities.

## Features

- **Resume Feature Extraction**: Extract key information from your resume
- **Resume Scoring**: Evaluate your resume based on various criteria
- **Resume-Job Matching**: Analyze how well your resume matches job descriptions
- **Resume Enhancement**: Get AI-powered suggestions to improve your resume
- **Resume Templates**: Choose from different templates for your enhanced resume

## Installation

### Basic Installation

```bash
# Clone the repository
git clone <repository-url>
cd resume-enhancer

# Install required dependencies
pip install -r requirements.txt

# Run the application
python run_app.py
```

### Enhanced NLP Features (Optional)

For advanced natural language processing features like improved resume section extraction and job matching, install the additional packages:

```bash
# Install Hugging Face Transformers and PyTorch
pip install transformers torch
```

Or uncomment and install these dependencies from the requirements.txt file:

```bash
# Edit requirements.txt and uncomment:
# transformers==4.30.2
# torch==2.0.1

# Then install:
pip install -r requirements.txt
```

## Usage

1. Run the application:
   ```bash
   python run_app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Choose a feature to use:
   - **Resume Enhancer**: Upload your resume and get scores and improvement suggestions
   - **Resume Job Matcher**: Upload both your resume and a job description to see how well they match

## Core Components

- **Resume Feature Extraction**: Uses NLP to identify and extract key sections from resumes
- **Scoring**: Evaluates resumes across multiple dimensions
- **Job Matching**: Uses AI to match resume content to job requirements
- **Resume Tailoring**: Suggests specific improvements to better match job descriptions
- **Template Selection**: Apply professional formatting to your enhanced resume

## Supported File Formats

- PDF (recommended)
- DOCX
- TXT

## Troubleshooting

- **Missing Dependencies**: The application will attempt to install required dependencies automatically. If you encounter any issues, try installing them manually using `pip install -r requirements.txt`
- **Performance Issues**: If the application runs slowly, consider running without the enhanced NLP features
- **File Upload Issues**: Ensure your resume is in PDF, DOCX, or TXT format and is not password protected

## License

[MIT License](LICENSE) 