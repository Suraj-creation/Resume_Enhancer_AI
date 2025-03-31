"""
AI Service Manager - Centralizes access to various AI services
"""

import streamlit as st
import os
import importlib
import logging

from utils.api_config import API_CONFIG, DEBUG_MODE
from utils.debug_utils import debug_log, log_exception

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIServiceManager:
    """Manages access to various AI services with lazy loading"""
    
    def __init__(self):
        """Initialize the service manager"""
        debug_log("Initializing AIServiceManager")
        
        # Dictionary to store service instances
        self._services = {}
        # Dictionary to store service availability status
        self._availability = {}
        # List of services to register
        self._service_registry = {
            "gemini": {
                "module": "utils.ai_services.gemini_service",
                "class": "GeminiService",
                "api_key_env": "GEMINI_API_KEY",
                "api_key_config": ["google_cloud", "gemini_api_key"],
            },
            "huggingface": {
                "module": "utils.ai_services.huggingface_service",
                "class": "HuggingFaceService",
                "api_key_env": "HUGGINGFACE_API_KEY",
                "api_key_config": ["huggingface", "api_key"],
            },
            "openai": {
                "module": "utils.ai_services.openai_service",
                "class": "OpenAIService",
                "api_key_env": "OPENAI_API_KEY",
                "api_key_config": ["openai", "api_key"],
            },
            "resume_analyzer": {
                "module": "utils.ai_services.resume_analyzer_service",
                "class": "ResumeAnalyzerService",
                "depends_on": ["gemini", "huggingface"]
            },
            "job_matcher": {
                "module": "utils.ai_services.job_matcher_service",
                "class": "JobMatcherService",
                "depends_on": ["gemini", "huggingface"]
            },
            "content_enhancer": {
                "module": "utils.ai_services.content_enhancer_service",
                "class": "ContentEnhancerService",
                "depends_on": ["gemini", "huggingface", "openai"]
            }
        }
        
    def is_available(self, service_name):
        """
        Check if a service is available
        
        Args:
            service_name (str): Name of the service to check
            
        Returns:
            bool: True if the service is available, False otherwise
        """
        # If we've already checked availability, return cached result
        if service_name in self._availability:
            return self._availability[service_name]
            
        # If the service is already loaded, it's available
        if service_name in self._services:
            self._availability[service_name] = True
            return True
            
        # Check if the service is in the registry
        if service_name not in self._service_registry:
            self._availability[service_name] = False
            return False
            
        # Get service info from registry
        service_info = self._service_registry[service_name]
        
        # Check API key for services that require one
        api_key = None
        
        # First try direct API_CONFIG access
        if "api_key_config" in service_info:
            config_path = service_info["api_key_config"]
            if len(config_path) == 2 and config_path[0] in API_CONFIG and config_path[1] in API_CONFIG[config_path[0]]:
                api_key = API_CONFIG[config_path[0]][config_path[1]]
                if api_key:
                    debug_log(f"Found API key for {service_name} in API_CONFIG")
        
        # If no key yet, try environment variable
        if not api_key and "api_key_env" in service_info:
            api_key = os.getenv(service_info["api_key_env"])
            if api_key:
                debug_log(f"Found API key for {service_name} in environment variables")
                
        # If a key is required but not found, service is not available
        if "api_key_env" in service_info or "api_key_config" in service_info:
            if not api_key:
                logger.warning(f"API key for {service_name} not found")
                self._availability[service_name] = False
                return False
                
        # Check dependencies for services that have them
        if "depends_on" in service_info:
            for dependency in service_info["depends_on"]:
                # We need at least one dependency to be available
                if self.is_available(dependency):
                    break
            else:  # If no dependencies are available
                logger.warning(f"No dependencies available for {service_name}")
                self._availability[service_name] = False
                return False
                
        # Check if the module can be imported
        try:
            module = importlib.import_module(service_info["module"])
            if not hasattr(module, service_info["class"]):
                logger.warning(f"Class {service_info['class']} not found in module {service_info['module']}")
                self._availability[service_name] = False
                return False
                
            # Service is available
            self._availability[service_name] = True
            return True
            
        except ImportError as e:
            logger.warning(f"Error importing module {service_info['module']}: {str(e)}")
            self._availability[service_name] = False
            return False
            
    def get_service(self, service_name):
        """
        Get a service instance
        
        Args:
            service_name (str): Name of the service to get
            
        Returns:
            object: Service instance or None if not available
        """
        # If the service is already loaded, return it
        if service_name in self._services:
            return self._services[service_name]
            
        # Check if the service is available
        if not self.is_available(service_name):
            debug_log(f"Service {service_name} is not available", level="WARNING")
            return None
            
        # Get service info from registry
        service_info = self._service_registry[service_name]
        
        # Load and initialize the service
        try:
            debug_log(f"Loading service: {service_name}")
            module = importlib.import_module(service_info["module"])
            service_class = getattr(module, service_info["class"])
            
            # Get API key for services that require one
            kwargs = {}
            
            # First try direct API_CONFIG access
            if "api_key_config" in service_info:
                config_path = service_info["api_key_config"]
                if len(config_path) == 2 and config_path[0] in API_CONFIG and config_path[1] in API_CONFIG[config_path[0]]:
                    kwargs["api_key"] = API_CONFIG[config_path[0]][config_path[1]]
                    
            # If no key yet, try environment variable
            if "api_key_env" in service_info and "api_key" not in kwargs:
                kwargs["api_key"] = os.getenv(service_info["api_key_env"])
                
            # Create instance
            debug_log(f"Initializing {service_name} service with: {kwargs.keys()}")
            service_instance = service_class(**kwargs)
            
            # Store instance for future use
            self._services[service_name] = service_instance
            debug_log(f"Service {service_name} loaded successfully")
            
            return service_instance
            
        except Exception as e:
            error_msg = f"Error loading service {service_name}: {str(e)}"
            logger.error(error_msg)
            log_exception(e, f"Loading service {service_name}")
            return None
            
    def get_available_services(self):
        """
        Get a list of available services
        
        Returns:
            list: List of available service names
        """
        return [name for name in self._service_registry if self.is_available(name)]
        
    @st.cache_resource
    def get_cached_service(self, service_name):
        """
        Get a cached service instance (useful for expensive model loading)
        
        Args:
            service_name (str): Name of the service to get
            
        Returns:
            object: Service instance or None if not available
        """
        return self.get_service(service_name) 