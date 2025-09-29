import json
import os
from transformers import pipeline
import torch

class HFSummarizer:
    # Class-level cache for the model (shared across instances)
    _cached_summarizer = None
    _cache_initialized = False
    
    def __init__(self):
        """Initialize hybrid summarizer with cached BART model"""
        # Check if HuggingFace models should be disabled (for cloud deployment)
        if os.getenv("DISABLE_HF", "false").lower() == "true":
            print("🚫 HuggingFace models disabled via DISABLE_HF environment variable")
            print("Using rule-based summaries only (cloud-optimized mode)")
            HFSummarizer._cached_summarizer = None
            self.use_ai = False
            self.summarizer = None
            self.initialized = True
            HFSummarizer._cache_initialized = True
            return
        
        if not HFSummarizer._cache_initialized:
            try:
                print("Loading BART-large-cnn model (this may take a moment on first run)...")
                # Use BART for summarization from structured facts
                HFSummarizer._cached_summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    device=0 if torch.cuda.is_available() else -1
                )
                self.use_ai = True
                print("✅ BART-large-cnn model loaded and cached successfully")
            except Exception as e:
                print(f"❌ Warning: Could not initialize BART model: {e}")
                print("Falling back to rule-based summaries only")
                HFSummarizer._cached_summarizer = None
                self.use_ai = False
            
            HFSummarizer._cache_initialized = True
        else:
            print("✅ Using cached BART model")
            self.use_ai = HFSummarizer._cached_summarizer is not None
        
        self.summarizer = HFSummarizer._cached_summarizer
        self.initialized = True
    
    def summarize(self, host_data: str) -> str:
        """
        Summarize host data using hybrid approach: extract facts, then generate summary.
        
        Args:
            host_data: String representation of host data (JSON format)
        
        Returns:
            Summary of the host data
        """
        try:
            data = json.loads(host_data)
            
            # Extract structured facts
            facts = self._extract_facts(data)
            
            # Use AI to generate natural summary from facts, or fallback to rule-based
            if self.use_ai and self.summarizer:
                return self._generate_ai_summary(facts)
            else:
                return self._create_rule_based_summary(facts)
        
        except Exception as e:
            return f"Error processing host data: {str(e)}"
    
    def _extract_facts(self, data: dict) -> dict:
        """
        Extract structured facts from the host data.
        """
        # Extract basic information
        ip = data.get('ip', 'Unknown IP')
        location = data.get('location', {})
        city = location.get('city', 'Unknown')
        country = location.get('country', 'Unknown')
        
        services = data.get('services', [])
        service_count = len(services)
        
        # Analyze vulnerabilities
        all_vulnerabilities = []
        critical_vulns = []
        high_vulns = []
        malware_detections = []
        
        for service in services:
            # Collect vulnerabilities
            if 'vulnerabilities' in service:
                for vuln in service['vulnerabilities']:
                    all_vulnerabilities.append(vuln)
                    severity = vuln.get('severity', '').lower()
                    cve = vuln.get('cve_id', 'Unknown CVE')
                    score = vuln.get('cvss_score', 0)
                    
                    if severity == 'critical':
                        critical_vulns.append({'cve': cve, 'score': score})
                    elif severity == 'high':
                        high_vulns.append({'cve': cve, 'score': score})
            
            # Collect malware
            if 'malware_detected' in service:
                malware = service['malware_detected']
                malware_detections.append({
                    'name': malware.get('name', 'Unknown malware'),
                    'type': malware.get('type', 'unknown'),
                    'confidence': malware.get('confidence', 0)
                })
        
        risk_level = data.get('threat_intelligence', {}).get('risk_level', 'unknown')
        
        return {
            'ip': ip,
            'city': city,
            'country': country,
            'service_count': service_count,
            'critical_vulns': critical_vulns,
            'high_vulns': high_vulns,
            'malware': malware_detections,
            'risk_level': risk_level
        }
    
    def _generate_ai_summary(self, facts: dict) -> str:
        """
        Generate a natural language summary using T5 from extracted facts.
        """
        try:
            # Create a narrative seed text for BART to polish and condense
            narrative_parts = []
            
            # Opening narrative
            narrative_parts.append(f"Security analysis of host {facts['ip']} in {facts['city']}, {facts['country']} reveals {facts['service_count']} exposed network services")
            
            # Add more detailed vulnerability information
            vuln_details = []
            if facts['critical_vulns']:
                for vuln in facts['critical_vulns']:
                    vuln_details.append(f"{vuln['cve']} with a CVSS score of {vuln['score']}")
                
                if len(facts['critical_vulns']) == 1:
                    narrative_parts.append(f"The system is critically vulnerable to {vuln_details[0]}, which is a known exploited vulnerability that poses significant security risks")
                else:
                    narrative_parts.append(f"The system contains {len(facts['critical_vulns'])} critical vulnerabilities including {vuln_details[0]}, all of which are known exploited vulnerabilities")
            
            # Add detailed malware information
            if facts['malware']:
                malware = facts['malware'][0]
                narrative_parts.append(f"Additionally, the system shows clear evidence of {malware['name']} malware activity, specifically operating as a {malware['type']} with {malware['confidence']:.0%} confidence level, indicating active compromise")
            
            # Add high-severity vulnerabilities if no critical ones
            if facts['high_vulns'] and not facts['critical_vulns']:
                narrative_parts.append(f"The system has {len(facts['high_vulns'])} high-severity vulnerabilities that require attention")
            
            # Enhanced risk assessment
            risk_details = {
                'critical': 'this host presents an immediate critical security threat and must be prioritized for emergency remediation to prevent potential data breaches or system compromise',
                'high': 'this host presents significant security risks with multiple attack vectors that require prompt remediation to prevent exploitation',
                'medium': 'this host shows notable security concerns with vulnerabilities that should be addressed in the next maintenance cycle',
                'low': 'this host appears to have minimal security risks but should continue to be monitored for emerging threats'
            }.get(facts['risk_level'].lower(), f'this host has {facts['risk_level']} risk level requiring assessment')
            
            narrative_parts.append(f"Given these findings, {risk_details}")
            
            # Create a longer narrative for BART to actually summarize
            facts_text = ". ".join(narrative_parts) + "."
            
            # Generate with BART - force it to summarize by setting aggressive parameters
            result = self.summarizer(
                facts_text,
                max_length=100,
                min_length=40,
                do_sample=False,
                truncation=True
            )
            
            if result and len(result) > 0:
                summary = result[0]['summary_text'].strip()
                return summary if summary else self._create_rule_based_summary(facts)
            else:
                return self._create_rule_based_summary(facts)
        
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._create_rule_based_summary(facts)
    
    def _create_rule_based_summary(self, facts: dict) -> str:
        """
        Create a rule-based summary from extracted facts.
        """
        summary_parts = []
        
        # Location and basic info
        summary_parts.append(f"Host {facts['ip']} located in {facts['city']}, {facts['country']} exposes {facts['service_count']} network services")
        
        # Security findings
        security_findings = []
        
        if facts['critical_vulns']:
            if len(facts['critical_vulns']) == 1:
                vuln = facts['critical_vulns'][0]
                security_findings.append(f"contains critical vulnerability {vuln['cve']} (CVSS {vuln['score']})")
            else:
                vuln = facts['critical_vulns'][0]
                security_findings.append(f"contains {len(facts['critical_vulns'])} critical vulnerabilities including {vuln['cve']} (CVSS {vuln['score']})")
        
        if facts['malware']:
            malware = facts['malware'][0]
            security_findings.append(f"shows malware detection: {malware['name']} ({malware['type']}, {malware['confidence']:.0%} confidence)")
        
        if facts['high_vulns'] and not facts['critical_vulns']:
            security_findings.append(f"has {len(facts['high_vulns'])} high-severity vulnerabilities")
        
        if security_findings:
            summary_parts[-1] = summary_parts[-1] + " and " + " and ".join(security_findings)
        
        # Risk assessment
        risk_description = {
            'critical': 'poses critical security risks requiring immediate attention',
            'high': 'presents high security risks that should be addressed promptly', 
            'medium': 'shows moderate security concerns',
            'low': 'appears to have minimal security risks'
        }.get(facts['risk_level'].lower(), f"has {facts['risk_level']} risk level")
        
        summary_parts.append(f"This host {risk_description}")
        
        return ". ".join(summary_parts) + "."
    
    
