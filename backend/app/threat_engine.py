import math
import re
from typing import Dict, Any, Tuple, Optional

# Known domain categories map
DOMAIN_CATEGORIES = {
    # Video Streaming
    "youtube.com": "Video Streaming",
    "googlevideo.com": "Video Streaming",
    "netflix.com": "Video Streaming",
    "nflxvideo.net": "Video Streaming",
    "hulu.com": "Video Streaming",
    "disneyplus.com": "Video Streaming",
    "twitch.tv": "Video Streaming",
    "primevideo.com": "Video Streaming",
    "tiktok.com": "Video Streaming",
    "vimeo.com": "Video Streaming",
    
    # Social Media
    "facebook.com": "Social Media",
    "fbcdn.net": "Social Media",
    "instagram.com": "Social Media",
    "cdninstagram.com": "Social Media",
    "whatsapp.com": "Social Media",
    "whatsapp.net": "Social Media",
    "twitter.com": "Social Media",
    "x.com": "Social Media",
    "twimg.com": "Social Media",
    "reddit.com": "Social Media",
    "redd.it": "Social Media",
    "linkedin.com": "Social Media",
    "snapchat.com": "Social Media",
    "pinterest.com": "Social Media",
    "discord.com": "Social Media",
    "discord.gg": "Social Media",
    "telegram.org": "Social Media",
    
    # Search & Cloud Portals
    "google.com": "Search & Cloud",
    "gstatic.com": "Search & Cloud",
    "bing.com": "Search & Cloud",
    "duckduckgo.com": "Search & Cloud",
    "yahoo.com": "Search & Cloud",
    "baidu.com": "Search & Cloud",
    "wikipedia.org": "Reference",
    
    # Tech & Development
    "github.com": "Developer",
    "githubusercontent.com": "Developer",
    "gitlab.com": "Developer",
    "stackoverflow.com": "Developer",
    "npmjs.org": "Developer",
    "pypi.org": "Developer",
    "docker.com": "Developer",
    "aws.amazon.com": "Cloud Infrastructure",
    "azure.microsoft.com": "Cloud Infrastructure",
    "cloudflare.com": "Cloud Infrastructure",
    
    # Ads & Trackers
    "doubleclick.net": "Ads & Tracking",
    "googleadservices.com": "Ads & Tracking",
    "googlesyndication.com": "Ads & Tracking",
    "adnxs.com": "Ads & Tracking",
    "criteo.com": "Ads & Tracking",
    "taboola.com": "Ads & Tracking",
    "outbrain.com": "Ads & Tracking",
    "scorecardresearch.com": "Ads & Tracking",
    "quantserve.com": "Ads & Tracking",
    "analytics.google.com": "Ads & Tracking",
    "telemetry.microsoft.com": "Ads & Tracking",
    
    # Known Malicious / Cryptominer Test Samples
    "coinhive.com": "Cryptomining",
    "coin-have.com": "Cryptomining",
    "cryptoloot.pro": "Cryptomining",
    "webminepool.com": "Cryptomining",
    "minergate.com": "Cryptomining",
    "malware-traffic-analysis.net": "Security Research",
}

# Suspicious TLD list often associated with spam/DGA/malware
SUSPICIOUS_TLDS = {
    "top", "xyz", "tk", "ml", "ga", "cf", "gq", "work", "click", "buzz", "rest", "fit", "surf", "casa"
}

# Phishing targeted keywords
PHISHING_KEYWORDS = [
    "paypal-login", "paypal-verify", "apple-id-verify", "apple-security",
    "microsoft-online-verify", "google-security-alert", "bankofamerica-login",
    "chase-verify-account", "wellsfargo-update", "netflix-billing-update",
    "metamask-restore", "binance-security", "coinbase-login-verify"
]

def calculate_shannon_entropy(domain: str) -> float:
    """Calculate Shannon Entropy of domain string to detect DGA."""
    # Strip TLD and dots
    clean_str = domain.split(".")[0]
    if not clean_str:
        return 0.0
    
    length = len(clean_str)
    counts = {}
    for char in clean_str:
        counts[char] = counts.get(char, 0) + 1
        
    entropy = 0.0
    for count in counts.values():
        p_x = count / length
        entropy += - p_x * math.log2(p_x)
        
    return entropy

def inspect_domain_threat(domain: str, blocked_list: Optional[set] = None) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    Evaluates a domain for security threats.
    Returns: (is_threat: bool, threat_type: str|None, severity: str|None, category: str)
    """
    clean_domain = domain.lower().strip().rstrip(".")
    
    # 1. Check custom network blocklist
    if blocked_list and clean_domain in blocked_list:
        return True, "Blocklisted", "medium", "Blocked Policy"
        
    # 2. Check Cryptomining
    for crypto_kw in ["coinhive", "cryptoloot", "webminepool", "minergate", "coin-have", "xmrpool"]:
        if crypto_kw in clean_domain:
            return True, "Cryptominer", "high", "Cryptomining"
            
    # 3. Check Phishing Lookalikes
    for phish_pat in PHISHING_KEYWORDS:
        if phish_pat in clean_domain:
            return True, "Phishing Lookalike", "critical", "Phishing"
            
    # Lookalike brand replacements (e.g. paypa1, micros0ft, goog1e)
    if re.search(r'(paypa1|micros0ft|goog1e|app1e|amaz0n|netf1ix|wel1sfargo)', clean_domain):
        return True, "Brand Impersonation / Phishing", "critical", "Phishing"

    # 4. Check DGA (Domain Generation Algorithm) / Entropy
    parts = clean_domain.split(".")
    subdomain = parts[0]
    entropy = calculate_shannon_entropy(subdomain)
    
    # High entropy strings > 3.8 with length > 12 usually indicate DGAs (malware C2 beaconing)
    if len(subdomain) >= 12 and entropy >= 3.8:
        # Check consonant density
        consonants = len(re.findall(r'[bcdfghjklmnpqrstvwxyz0-9]', subdomain))
        if consonants / len(subdomain) > 0.75:
            return True, "DGA Botnet / Malware C2", "high", "Suspicious DGA"
            
    # 5. Check Suspicious TLD with unusual structure
    tld = parts[-1] if len(parts) > 1 else ""
    if tld in SUSPICIOUS_TLDS and (entropy > 3.4 or len(subdomain) > 15 or re.search(r'\d{4,}', subdomain)):
        return True, "Suspicious TLD / Anomaly", "medium", "Suspicious TLD"
        
    # 6. Categorize legitimate domain
    for base_domain, category in DOMAIN_CATEGORIES.items():
        if clean_domain == base_domain or clean_domain.endswith("." + base_domain):
            return False, None, None, category
            
    if any(tld_ext in clean_domain for tld_ext in [".edu", ".gov", ".mil"]):
        return False, None, None, "Education & Government"
        
    return False, None, None, "General Internet"
