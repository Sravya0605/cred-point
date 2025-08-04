"""
Recommendation Engine for CPE Management Platform
Fetches real-world CPE opportunities from certification authorities
"""

import requests
import trafilatura
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CPERecommendationEngine:
    """Engine for fetching real-world CPE opportunities"""
    
    def __init__(self):
        self.authority_urls = {
            'ISC²': [
                'https://www.isc2.org/Development/CPE-Credits',
                'https://www.isc2.org/Training'
            ],
            'EC-Council': [
                'https://www.eccouncil.org/continuing-education/',
                'https://www.eccouncil.org/programs/'
            ],
            'CompTIA': [
                'https://www.comptia.org/continuing-education',
                'https://www.comptia.org/training'
            ],
            'OffSec': [
                'https://www.offensive-security.com/courses/',
                'https://www.offensive-security.com/training/'
            ]
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; CPE-Bot/1.0; Education)'
        })

    def get_recommendations(self, certification_name: str, authority: str) -> List[Dict]:
        """
        Fetch real-world CPE recommendations for a specific certification
        
        Args:
            certification_name: Name of the certification (e.g., "CISSP")
            authority: Certification authority (e.g., "ISC²")
            
        Returns:
            List of recommendation dictionaries with title, description, type, source, url, cpe_value
        """
        logger.info(f"Fetching recommendations for {certification_name} from {authority}")
        
        recommendations = []
        
        try:
            # Get URLs for the specific authority
            urls = self.authority_urls.get(authority, [])
            
            for url in urls:
                try:
                    recs = self._fetch_from_url(url, authority)
                    recommendations.extend(recs)
                except Exception as e:
                    logger.warning(f"Failed to fetch from {url}: {str(e)}")
                    continue
            
            # Add some general cybersecurity training recommendations if no specific ones found
            if not recommendations:
                recommendations = self._get_fallback_recommendations(authority)
                
        except Exception as e:
            logger.error(f"Error fetching recommendations: {str(e)}")
            recommendations = self._get_fallback_recommendations(authority)
        
        # Limit to 6 recommendations for better UX
        return recommendations[:6]

    def _fetch_from_url(self, url: str, authority: str) -> List[Dict]:
        """Fetch recommendations from a specific URL"""
        recommendations = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Extract text content using trafilatura
            text_content = trafilatura.extract(response.text)
            if not text_content:
                return recommendations
            
            # Parse HTML for structured data
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for training/course links and titles
            course_links = soup.find_all('a', href=True)
            
            for link in course_links[:10]:  # Limit to first 10 links
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Skip if not relevant
                if not self._is_training_related(text, href):
                    continue
                    
                # Build full URL if relative
                if href.startswith('/'):
                    href = url.rsplit('/', 2)[0] + href
                elif not href.startswith('http'):
                    continue
                
                # Create recommendation
                rec = self._create_recommendation(text, href, authority)
                if rec:
                    recommendations.append(rec)
                    
        except Exception as e:
            logger.warning(f"Error processing {url}: {str(e)}")
            
        return recommendations

    def _is_training_related(self, text: str, href: str) -> bool:
        """Check if link is training/CPE related"""
        training_keywords = [
            'training', 'course', 'certification', 'workshop', 'webinar',
            'seminar', 'conference', 'education', 'learning', 'cpe'
        ]
        
        text_lower = text.lower()
        href_lower = href.lower()
        
        return (
            any(keyword in text_lower for keyword in training_keywords) or
            any(keyword in href_lower for keyword in training_keywords)
        ) and len(text) > 5

    def _create_recommendation(self, title: str, url: str, authority: str) -> Optional[Dict]:
        """Create a recommendation dictionary"""
        if len(title) < 5 or len(title) > 100:
            return None
            
        # Determine CPE value based on title keywords
        cpe_value = self._estimate_cpe_value(title)
        
        # Determine activity type
        activity_type = self._determine_activity_type(title)
        
        return {
            'title': title,
            'description': f"Professional development opportunity from {authority}",
            'type': activity_type,
            'source': authority,
            'url': url,
            'cpe_value': cpe_value
        }

    def _estimate_cpe_value(self, title: str) -> float:
        """Estimate CPE value based on activity title"""
        title_lower = title.lower()
        
        if 'conference' in title_lower or 'summit' in title_lower:
            return 8.0
        elif 'workshop' in title_lower or 'bootcamp' in title_lower:
            return 4.0
        elif 'webinar' in title_lower:
            return 1.0
        elif 'course' in title_lower or 'training' in title_lower:
            return 2.0
        else:
            return 1.0

    def _determine_activity_type(self, title: str) -> str:
        """Determine activity type from title"""
        title_lower = title.lower()
        
        if 'conference' in title_lower:
            return 'Conference'
        elif 'webinar' in title_lower:
            return 'Webinar'
        elif 'workshop' in title_lower:
            return 'Workshop'
        elif 'course' in title_lower:
            return 'Training'
        else:
            return 'Education'

    def _get_fallback_recommendations(self, authority: str) -> List[Dict]:
        """Provide fallback recommendations when live data unavailable"""
        
        base_recommendations = [
            {
                'title': f'{authority} Official Training Program',
                'description': f'Explore official training programs and courses from {authority}',
                'type': 'Training',
                'source': authority,
                'url': self.authority_urls.get(authority, ['#'])[0],
                'cpe_value': 4.0
            },
            {
                'title': 'Cybersecurity Webinar Series',
                'description': 'Regular webinars covering current cybersecurity topics and trends',
                'type': 'Webinar',
                'source': authority,
                'url': self.authority_urls.get(authority, ['#'])[0],
                'cpe_value': 1.0
            },
            {
                'title': 'Industry Security Conference',
                'description': 'Annual cybersecurity conference with expert presentations',
                'type': 'Conference',
                'source': authority,
                'url': self.authority_urls.get(authority, ['#'])[0],
                'cpe_value': 8.0
            }
        ]
        
        return base_recommendations

# Global instance
recommendation_engine = CPERecommendationEngine()