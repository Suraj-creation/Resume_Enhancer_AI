import pusher
import json
import time
import uuid
import streamlit as st
from utils.api_config import API_CONFIG

class PusherClient:
    def __init__(self):
        self.config = API_CONFIG["pusher"]
        self.app_id = self.config["app_id"]
        self.key = self.config["app_key"]
        self.secret = self.config["app_secret"]
        self.cluster = self.config["cluster"]
        self.initialized = all([self.app_id, self.key, self.secret, self.cluster])
        self.client = None
        self.initialize_client()
        
    def initialize_client(self):
        """Initialize Pusher client with API credentials"""
        if not self.initialized:
            return
            
        try:
            self.client = pusher.Pusher(
                app_id=self.app_id,
                key=self.key,
                secret=self.secret,
                cluster=self.cluster,
                ssl=True
            )
            
        except Exception as e:
            st.warning(f"Pusher initialization error: {str(e)}")
    
    def trigger_event(self, channel, event, data):
        """
        Trigger a Pusher event
        
        Args:
            channel: Channel name
            event: Event name
            data: Data to send
            
        Returns:
            bool: True if successful
        """
        if not self.initialized or self.client is None:
            # Simulate event for demo purposes
            return self._simulate_event(channel, event, data)
            
        try:
            # Add timestamp and event ID
            enhanced_data = {
                **data,
                "timestamp": int(time.time()),
                "event_id": str(uuid.uuid4())
            }
            
            # Trigger the event
            self.client.trigger(channel, event, enhanced_data)
            return True
            
        except Exception as e:
            st.warning(f"Pusher event error: {str(e)}")
            return False
    
    def _simulate_event(self, channel, event, data):
        """
        Simulate a Pusher event for demo purposes
        
        Args:
            channel: Channel name
            event: Event name
            data: Event data
            
        Returns:
            bool: Always True
        """
        # Log the event to console
        print(f"[SIMULATED PUSHER EVENT] Channel: {channel}, Event: {event}, Data: {json.dumps(data)}")
        
        # Add a small delay to simulate network latency
        time.sleep(0.2)
        
        return True
    
    def get_client_js(self):
        """
        Get Pusher JavaScript client code for frontend
        
        Returns:
            str: JavaScript code
        """
        if not self.initialized:
            return "console.warn('Pusher not configured');"
            
        js_code = f"""
        <script src="https://js.pusher.com/7.0/pusher.min.js"></script>
        <script>
            // Initialize Pusher
            const pusher = new Pusher('{self.key}', {{
                cluster: '{self.cluster}',
                encrypted: true
            }});
            
            // Function to subscribe to a channel
            function subscribeToChannel(channelName, eventName, callback) {{
                const channel = pusher.subscribe(channelName);
                channel.bind(eventName, callback);
                return channel;
            }}
            
            // For debug purposes
            window.pusherClient = pusher;
        </script>
        """
        
        return js_code
    
    def get_user_channel(self, user_id):
        """
        Get a user-specific channel name
        
        Args:
            user_id: User ID
            
        Returns:
            str: Channel name
        """
        return f"private-user-{user_id}"
    
    def get_resume_channel(self, resume_id):
        """
        Get a resume-specific channel name
        
        Args:
            resume_id: Resume ID
            
        Returns:
            str: Channel name
        """
        return f"private-resume-{resume_id}"
    
    def trigger_resume_update(self, user_id, resume_id, update_type, data):
        """
        Trigger a resume update event
        
        Args:
            user_id: User ID
            resume_id: Resume ID
            update_type: Type of update (e.g., "score", "enhancement")
            data: Update data
            
        Returns:
            bool: True if successful
        """
        # User channel for user-specific updates
        user_channel = self.get_user_channel(user_id)
        
        # Resume channel for resume-specific updates
        resume_channel = self.get_resume_channel(resume_id)
        
        # Trigger event on both channels
        user_result = self.trigger_event(user_channel, f"resume_{update_type}", {
            "resume_id": resume_id,
            "update_type": update_type,
            "data": data
        })
        
        resume_result = self.trigger_event(resume_channel, f"update_{update_type}", {
            "update_type": update_type,
            "data": data
        })
        
        return user_result and resume_result
    
    def trigger_job_match_update(self, user_id, resume_id, job_id, update_type, data):
        """
        Trigger a job match update event
        
        Args:
            user_id: User ID
            resume_id: Resume ID
            job_id: Job ID
            update_type: Type of update (e.g., "score", "suggestions")
            data: Update data
            
        Returns:
            bool: True if successful
        """
        # User channel for user-specific updates
        user_channel = self.get_user_channel(user_id)
        
        # Job match channel
        job_match_channel = f"private-job-match-{resume_id}-{job_id}"
        
        # Trigger event on both channels
        user_result = self.trigger_event(user_channel, f"job_match_{update_type}", {
            "resume_id": resume_id,
            "job_id": job_id,
            "update_type": update_type,
            "data": data
        })
        
        match_result = self.trigger_event(job_match_channel, f"update_{update_type}", {
            "update_type": update_type,
            "data": data
        })
        
        return user_result and match_result

# Initialize Pusher client
pusher_client = PusherClient() 