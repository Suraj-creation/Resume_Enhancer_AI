import boto3
import os
import io
import uuid
import streamlit as st
from datetime import datetime
from utils.api_config import API_CONFIG

class S3Client:
    def __init__(self):
        self.s3_config = API_CONFIG["aws_s3"]
        self.initialized = False
        self.s3_client = None
        self.initialize_s3()
        
    def initialize_s3(self):
        """Initialize AWS S3 client with credentials"""
        if self.initialized:
            return
            
        # Check if AWS credentials are configured
        if not all([self.s3_config["access_key"], 
                   self.s3_config["secret_key"], 
                   self.s3_config["bucket_name"]]):
            # If credentials are missing, we'll store files locally
            os.makedirs("temp_storage", exist_ok=True)
            return
            
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.s3_config["access_key"],
                aws_secret_access_key=self.s3_config["secret_key"],
                region_name=self.s3_config["region"]
            )
            self.initialized = True
        except Exception as e:
            st.warning(f"S3 initialization error: {str(e)}. Files will be stored locally.")
    
    def upload_file(self, file_data, file_name, user_id, content_type=None):
        """
        Upload a file to S3 or local storage
        
        Args:
            file_data: File content as bytes or file-like object
            file_name: Original file name
            user_id: User ID for organizing files
            content_type: MIME type of the file
            
        Returns:
            str: URL or path to the stored file
        """
        # Generate a unique file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = file_name.replace(" ", "_").lower()
        
        # Format: user_id/YYYYMMDD_HHMMSS_uuid_filename
        s3_key = f"{user_id}/{timestamp}_{unique_id}_{safe_filename}"
        
        if not self.initialized or not self.s3_client:
            # Store locally
            local_path = os.path.join("temp_storage", s3_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Check if file_data is file-like or bytes
            if isinstance(file_data, (bytes, bytearray)):
                with open(local_path, 'wb') as f:
                    f.write(file_data)
            else:
                # Assume it's a file-like object
                with open(local_path, 'wb') as f:
                    f.write(file_data.read())
            
            return local_path
        
        try:
            # If file_data is a file-like object (e.g., from st.file_uploader)
            if hasattr(file_data, 'read'):
                file_data = file_data.read()
            
            # Upload to S3
            if content_type:
                self.s3_client.put_object(
                    Bucket=self.s3_config["bucket_name"],
                    Key=s3_key,
                    Body=file_data,
                    ContentType=content_type
                )
            else:
                self.s3_client.put_object(
                    Bucket=self.s3_config["bucket_name"],
                    Key=s3_key,
                    Body=file_data
                )
            
            # Generate S3 URL
            s3_url = f"https://{self.s3_config['bucket_name']}.s3.{self.s3_config['region']}.amazonaws.com/{s3_key}"
            return s3_url
            
        except Exception as e:
            st.error(f"Error uploading to S3: {str(e)}")
            
            # Fallback to local storage
            local_path = os.path.join("temp_storage", s3_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as f:
                if isinstance(file_data, (bytes, bytearray)):
                    f.write(file_data)
                else:
                    # Reopen the file since read() may have consumed it
                    file_data.seek(0)
                    f.write(file_data.read())
            
            return local_path
    
    def get_file(self, file_path_or_url, as_bytes=True):
        """
        Retrieve a file from S3 or local storage
        
        Args:
            file_path_or_url: Path or URL to the file
            as_bytes: Whether to return as bytes (True) or file-like object (False)
            
        Returns:
            bytes or file-like object: The file content
        """
        # Check if it's a local path
        if file_path_or_url.startswith("temp_storage/") or os.path.exists(file_path_or_url):
            if as_bytes:
                with open(file_path_or_url, 'rb') as f:
                    return f.read()
            else:
                return open(file_path_or_url, 'rb')
        
        # It's an S3 URL, extract the key
        if not self.initialized or not self.s3_client:
            st.error("S3 client not initialized but S3 URL provided")
            return None
            
        try:
            # Extract the S3 key from the URL
            url_parts = file_path_or_url.split(f"{self.s3_config['bucket_name']}.s3.{self.s3_config['region']}.amazonaws.com/")
            s3_key = url_parts[1] if len(url_parts) > 1 else file_path_or_url
            
            # Get the file from S3
            response = self.s3_client.get_object(
                Bucket=self.s3_config["bucket_name"],
                Key=s3_key
            )
            
            if as_bytes:
                return response['Body'].read()
            else:
                return response['Body']
                
        except Exception as e:
            st.error(f"Error retrieving file from S3: {str(e)}")
            return None
    
    def delete_file(self, file_path_or_url):
        """
        Delete a file from S3 or local storage
        
        Args:
            file_path_or_url: Path or URL to the file
            
        Returns:
            bool: True if deleted successfully
        """
        # Check if it's a local path
        if file_path_or_url.startswith("temp_storage/") or os.path.exists(file_path_or_url):
            try:
                os.remove(file_path_or_url)
                return True
            except Exception as e:
                st.error(f"Error deleting local file: {str(e)}")
                return False
        
        # It's an S3 URL, extract the key
        if not self.initialized or not self.s3_client:
            st.error("S3 client not initialized but S3 URL provided")
            return False
            
        try:
            # Extract the S3 key from the URL
            url_parts = file_path_or_url.split(f"{self.s3_config['bucket_name']}.s3.{self.s3_config['region']}.amazonaws.com/")
            s3_key = url_parts[1] if len(url_parts) > 1 else file_path_or_url
            
            # Delete the file from S3
            self.s3_client.delete_object(
                Bucket=self.s3_config["bucket_name"],
                Key=s3_key
            )
            
            return True
                
        except Exception as e:
            st.error(f"Error deleting file from S3: {str(e)}")
            return False
            
# Initialize S3 client
s3_client = S3Client() 