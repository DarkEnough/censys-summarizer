import os
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

class GroqSummarizer:
    def __init__(self):
        """Initialize Groq client with API key from environment"""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("Warning: GROQ_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"
    
    def summarize(self, host_data: str) -> str:
        """
        Summarize host data using Groq API with Llama model.
        
        Args:
            host_data: String representation of host data (JSON format)
        
        Returns:
            Summary of the host data
        """
        if not self.client:
            return "Groq API key not configured. Please set GROQ_API_KEY in your environment."
        
        try:
            # Create a comprehensive prompt for host data summarization
            prompt = f"""You are a cybersecurity analyst creating a professional threat intelligence summary. Analyze this Censys host data and provide a structured security assessment.

Host Data:
{host_data}

Create a concise summary using this EXACT format:

**Host:** [IP] in [City, Country]
**Critical Findings:** [List 2-3 most critical security issues with CVE numbers and CVSS scores]
**Services at Risk:** [Key exposed services and ports]
**Threat Level:** [Critical/High/Medium/Low] - [Brief justification]

Keep it professional, factual, and under 150 words. Focus on actionable security intelligence."""
            
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior cybersecurity analyst specializing in threat intelligence. Create structured, actionable security summaries from network scan data. Always follow the requested format exactly and prioritize the most critical findings."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.1,  # Very low temperature for consistent formatting
                max_tokens=300,
            )
            
            return chat_completion.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Error generating summary with Groq: {str(e)}"
