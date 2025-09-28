import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.summarizer_groq import GroqSummarizer
from backend.summarizer_hf import HFSummarizer

# Sample test host data
SAMPLE_HOST = {
    "ip": "192.168.1.100",
    "hostname": "test-server.example.com",
    "services": [
        {
            "port": 80,
            "protocol": "http",
            "software": "nginx",
            "version": "1.21.0"
        },
        {
            "port": 443,
            "protocol": "https",
            "software": "nginx",
            "version": "1.21.0"
        }
    ],
    "os": "Ubuntu 22.04 LTS",
    "tags": ["web-server", "test"],
    "last_updated": "2024-01-15T10:30:00Z"
}

def test_groq_summarizer():
    """Test that Groq summarizer returns a non-empty summary"""
    summarizer = GroqSummarizer()
    
    # Convert sample host to JSON string
    host_json = json.dumps(SAMPLE_HOST, indent=2)
    
    # Generate summary
    summary = summarizer.summarize(host_json)
    
    # Check that summary is not empty
    assert summary is not None
    assert len(summary) > 0
    assert isinstance(summary, str)
    
    print(f"Groq Summary: {summary}")

def test_hf_summarizer():
    """Test that HuggingFace summarizer returns a non-empty summary"""
    summarizer = HFSummarizer()
    
    # Convert sample host to JSON string
    host_json = json.dumps(SAMPLE_HOST, indent=2)
    
    # Generate summary
    summary = summarizer.summarize(host_json)
    
    # Check that summary is not empty
    assert summary is not None
    assert len(summary) > 0
    assert isinstance(summary, str)
    
    print(f"HuggingFace Summary: {summary}")

def test_summarizers_with_complex_data():
    """Test both summarizers with more complex host data"""
    complex_host = {
        "ip": "203.0.113.42",
        "hostname": "complex-server.example.org",
        "autonomous_system": {
            "asn": 13335,
            "name": "CLOUDFLARENET",
            "country_code": "US"
        },
        "services": [
            {
                "port": 21,
                "protocol": "ftp",
                "software": "vsftpd",
                "version": "3.0.5",
                "anonymous_login": False
            },
            {
                "port": 80,
                "protocol": "http",
                "software": "Apache",
                "version": "2.4.54"
            },
            {
                "port": 8080,
                "protocol": "http",
                "software": "Tomcat",
                "version": "9.0.71"
            }
        ],
        "os": {
            "family": "Linux",
            "vendor": "Debian",
            "version": "11"
        },
        "vulnerabilities": [
            {
                "cve": "CVE-2023-24998",
                "severity": "MEDIUM"
            }
        ],
        "tags": ["multi-service", "public"],
        "location": {
            "city": "New York",
            "country": "United States"
        }
    }
    
    host_json = json.dumps(complex_host, indent=2)
    
    # Test Groq
    groq = GroqSummarizer()
    groq_summary = groq.summarize(host_json)
    assert groq_summary is not None
    assert len(groq_summary) > 0
    
    # Test HuggingFace
    hf = HFSummarizer()
    hf_summary = hf.summarize(host_json)
    assert hf_summary is not None
    assert len(hf_summary) > 0
    
    print(f"\nComplex Host - Groq Summary: {groq_summary}")
    print(f"\nComplex Host - HF Summary: {hf_summary}")

if __name__ == "__main__":
    # Run tests manually
    print("Running Censys Summarizer Tests...")
    print("-" * 50)
    
    print("\n1. Testing Groq Summarizer...")
    try:
        test_groq_summarizer()
        print("✅ Groq test passed")
    except Exception as e:
        print(f"❌ Groq test failed: {e}")
    
    print("\n2. Testing HuggingFace Summarizer...")
    try:
        test_hf_summarizer()
        print("✅ HuggingFace test passed")
    except Exception as e:
        print(f"❌ HuggingFace test failed: {e}")
    
    print("\n3. Testing with Complex Data...")
    try:
        test_summarizers_with_complex_data()
        print("✅ Complex data test passed")
    except Exception as e:
        print(f"❌ Complex data test failed: {e}")
    
    print("\n" + "-" * 50)
    print("Tests completed!")
