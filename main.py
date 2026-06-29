# main.py - Social Media Profile Analyzer

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urlparse

class EthicalProfileAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        })
        self.results = {
            'profile_url': None,
            'platform': None,
            'username': None,
            'public_bio': None,
            'public_email': None,
            'public_phone': None,
            'public_website': None,
            'location_hint': None,
            'cross_platform_presence': [],
            'confidence': 'low',
            'disclaimer': 'Only publicly shared information. No private data accessed.'
        }
    
    def identify_platform(self, url):
        """Identify which platform the URL belongs to."""
        domain = urlparse(url).netloc.lower()
        if 'instagram' in domain:
            return 'instagram'
        elif 'twitter' in domain or 'x.com' in domain:
            return 'twitter'
        elif 'linkedin' in domain:
            return 'linkedin'
        elif 'facebook' in domain:
            return 'facebook'
        elif 'github' in domain:
            return 'github'
        else:
            return 'unknown'
    
    def extract_username(self, url):
        """Extract username from URL."""
        path = urlparse(url).path.strip('/')
        # Remove 'in/' for LinkedIn
        if path.startswith('in/'):
            path = path[3:]
        return path.split('/')[0] if path else None
    
    def extract_contact_patterns(self, text):
        """Extract contact info that is explicitly shared in public text."""
        contacts = {
            'emails': [],
            'phones': [],
            'websites': []
        }
        
        if not text:
            return contacts
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        contacts['emails'] = list(set(re.findall(email_pattern, text)))
        
        # Phone pattern
        phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        contacts['phones'] = list(set(re.findall(phone_pattern, text)))
        
        # Website pattern
        web_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        contacts['websites'] = list(set(re.findall(web_pattern, text)))
        
        return contacts
    
    def analyze_github_profile(self, username):
        """GitHub is API-friendly for public profiles."""
        url = f"https://api.github.com/users/{username}"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.results['platform'] = 'github'
                self.results['username'] = username
                self.results['public_bio'] = data.get('bio', '')
                self.results['public_website'] = data.get('blog', '')
                self.results['location_hint'] = data.get('location', '')
                
                # Check bio and blog for contact info
                bio_text = f"{data.get('bio', '')} {data.get('blog', '')} {data.get('company', '')}"
                contacts = self.extract_contact_patterns(bio_text)
                
                self.results['public_email'] = contacts['emails'][0] if contacts['emails'] else None
                self.results['public_phone'] = contacts['phones'][0] if contacts['phones'] else None
                self.results['public_contact_info'] = contacts
                
                self.results['confidence'] = 'medium' if contacts['emails'] or contacts['phones'] else 'low'
                self.results['profile_url'] = f"https://github.com/{username}"
            else:
                self.results['error'] = f"GitHub API returned status {response.status_code}"
            return self.results
        except Exception as e:
            self.results['error'] = str(e)
            return self.results
    
    def search_cross_platform(self, username):
        """Search for same username on other platforms (respectful HEAD requests)."""
        platforms = {
            'github': f"https://github.com/{username}",
            'twitter': f"https://twitter.com/{username}",
            'instagram': f"https://instagram.com/{username}",
            'linkedin': f"https://linkedin.com/in/{username}",
        }
        
        found = []
        for platform, url in platforms.items():
            try:
                resp = self.session.head(url, allow_redirects=True, timeout=5)
                if resp.status_code == 200:
                    found.append({'platform': platform, 'url': url, 'exists': True})
                time.sleep(1)  # Be respectful - 1 second delay
            except Exception as e:
                pass  # Silently skip errors
        
        self.results['cross_platform_presence'] = found
        return found
    
    def analyze_profile(self, url):
        """Main method to analyze any profile URL."""
        self.results['profile_url'] = url
        platform = self.identify_platform(url)
        username = self.extract_username(url)
        self.results['username'] = username
        
        print(f"🔍 Analyzing: {url}")
        print(f"📱 Platform: {platform}")
        print(f"👤 Username: {username}")
        print("-" * 50)
        
        if platform == 'github':
            self.analyze_github_profile(username)
        elif platform == 'twitter':
            print("⚠️  Twitter/X requires API. Use official API only.")
            self.results['error'] = 'Twitter API required'
        elif platform == 'instagram':
            print("⚠️  Instagram has anti-scraping measures. Use official API.")
            self.results['error'] = 'Instagram API required'
        elif platform == 'linkedin':
            print("⚠️  LinkedIn prohibits scraping. Use official API.")
            self.results['error'] = 'LinkedIn API required'
        else:
            print("⚠️  Unknown platform or not supported yet.")
            self.results['error'] = 'Platform not supported'
        
        # Always do cross-platform search
        print("\n🌐 Searching cross-platform presence...")
        self.search_cross_platform(username)
        
        return self.results


def main():
    print("=" * 60)
    print("  🔍 ETHICAL SOCIAL MEDIA PROFILE ANALYZER")
    print("  Only analyzes PUBLICLY SHARED information")
    print("=" * 60)
    print()
    
    # Test with a public GitHub profile (Linus Torvalds - public figure)
    test_url = "https://github.com/torvalds"
    
    analyzer = EthicalProfileAnalyzer()
    results = analyzer.analyze_profile(test_url)
    
    print("\n" + "=" * 60)
    print("  📊 ANALYSIS RESULTS")
    print("=" * 60)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Ask user for their own URL
    print("\n" + "-" * 60)
    user_url = input("\nEnter a profile URL to analyze (or 'exit' to quit): ")
    
    if user_url.lower() != 'exit':
        analyzer2 = EthicalProfileAnalyzer()
        results2 = analyzer2.analyze_profile(user_url)
        print("\n" + "=" * 60)
        print("  📊 YOUR ANALYSIS RESULTS")
        print("=" * 60)
        print(json.dumps(results2, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()