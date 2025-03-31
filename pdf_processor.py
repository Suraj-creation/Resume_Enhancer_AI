import io
import os
import tempfile
import requests
from pdfminer.high_level import extract_text
from utils.api_config import API_CONFIG

class PDFProcessor:
    def __init__(self):
        self.smallpdf_api_key = API_CONFIG["smallpdf"]["api_key"]
        self.smallpdf_api_secret = API_CONFIG["smallpdf"]["api_secret"]
        self.smallpdf_base_url = "https://api.smallpdf.com/v1"
        
    def extract_text_from_pdf(self, pdf_file, use_ocr=False):
        """
        Extract text from a PDF file using pdfminer.six
        If OCR is requested or the extracted text is minimal, use SmallPDF OCR API
        
        Args:
            pdf_file: Uploaded file object from Streamlit
            use_ocr: Boolean to force OCR processing
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            # Convert the uploaded file to bytes
            pdf_bytes = pdf_file.getvalue()
            
            # First attempt: Try pdfminer.six for text extraction
            extracted_text = extract_text(io.BytesIO(pdf_bytes))
            
            # If text is minimal or OCR is requested, use SmallPDF OCR
            if len(extracted_text.strip()) < 100 or use_ocr:
                if self.smallpdf_api_key and self.smallpdf_api_secret:
                    return self._extract_with_smallpdf_ocr(pdf_bytes)
                else:
                    return "OCR processing requested but SmallPDF API credentials not configured."
            
            return extracted_text
        
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"
    
    def _extract_with_smallpdf_ocr(self, pdf_bytes):
        """
        Use SmallPDF API to perform OCR on a PDF file
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            str: Extracted text using OCR
        """
        try:
            # Create a temporary file for the PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf.write(pdf_bytes)
                temp_pdf_path = temp_pdf.name
            
            # Step 1: OCR the PDF using SmallPDF API
            headers = {
                'Authorization': f'Bearer {self.smallpdf_api_key}',
                'Content-Type': 'application/pdf'
            }
            
            with open(temp_pdf_path, 'rb') as f:
                ocr_response = requests.post(
                    f"{self.smallpdf_base_url}/ocr",
                    headers=headers,
                    data=f
                )
            
            if ocr_response.status_code != 200:
                return f"OCR request failed with status {ocr_response.status_code}: {ocr_response.text}"
            
            ocr_task_id = ocr_response.json().get('taskId')
            
            # Step 2: Wait for OCR to complete and retrieve the text
            text_response = requests.get(
                f"{self.smallpdf_base_url}/ocr/{ocr_task_id}/text",
                headers={
                    'Authorization': f'Bearer {self.smallpdf_api_key}'
                }
            )
            
            if text_response.status_code != 200:
                return f"OCR text retrieval failed with status {text_response.status_code}: {text_response.text}"
            
            # Cleanup temp file
            os.unlink(temp_pdf_path)
            
            # Return the OCR text
            return text_response.json().get('text', '')
            
        except Exception as e:
            return f"Error using SmallPDF OCR: {str(e)}"

    def get_pdf_metadata(self, pdf_file):
        """
        Extract metadata from a PDF file
        
        Args:
            pdf_file: Uploaded file object from Streamlit
            
        Returns:
            dict: PDF metadata
        """
        # This implementation would extract metadata from the PDF
        # For this example, we'll return a simplified metadata dict
        return {
            "filename": pdf_file.name,
            "size": f"{len(pdf_file.getvalue())/1024:.2f} KB",
            "pages": 0,  # In a real implementation, would count pages
            "created": "Unknown"
        }

# Initialize PDF processor
pdf_processor = PDFProcessor()

# Export the extract_text_from_pdf function for compatibility with existing code
def extract_text_from_pdf(pdf_file, use_ocr=False):
    return pdf_processor.extract_text_from_pdf(pdf_file, use_ocr) 