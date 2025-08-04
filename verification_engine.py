"""
Activity Verification Engine for CPE Management Platform
Provides intelligent verification and CPE point calculation
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CPEVerificationEngine:
    """Engine for verifying CPE activities and calculating appropriate points"""
    
    def __init__(self):
        # Authority-specific rules
        self.authority_rules = {
            'ISC²': {
                'Conference': {'min': 1.0, 'max': 8.0, 'default': 4.0},
                'Training': {'min': 0.5, 'max': 40.0, 'default': 2.0},
                'Webinar': {'min': 0.25, 'max': 2.0, 'default': 1.0},
                'Workshop': {'min': 1.0, 'max': 8.0, 'default': 4.0},
                'Education': {'min': 0.5, 'max': 10.0, 'default': 1.0}
            },
            'EC-Council': {
                'Conference': {'min': 1.0, 'max': 16.0, 'default': 8.0},
                'Training': {'min': 1.0, 'max': 20.0, 'default': 4.0},
                'Webinar': {'min': 0.5, 'max': 2.0, 'default': 1.0},
                'Workshop': {'min': 2.0, 'max': 8.0, 'default': 4.0},
                'Education': {'min': 1.0, 'max': 5.0, 'default': 2.0}
            },
            'CompTIA': {
                'Conference': {'min': 2.0, 'max': 10.0, 'default': 6.0},
                'Training': {'min': 1.0, 'max': 10.0, 'default': 3.0},
                'Webinar': {'min': 0.5, 'max': 2.0, 'default': 1.0},
                'Workshop': {'min': 1.0, 'max': 6.0, 'default': 3.0},
                'Education': {'min': 0.5, 'max': 4.0, 'default': 1.0}
            },
            'OffSec': {
                'Conference': {'min': 1.0, 'max': 12.0, 'default': 6.0},
                'Training': {'min': 2.0, 'max': 40.0, 'default': 8.0},
                'Webinar': {'min': 0.5, 'max': 2.0, 'default': 1.0},
                'Workshop': {'min': 4.0, 'max': 16.0, 'default': 8.0},
                'Education': {'min': 1.0, 'max': 8.0, 'default': 2.0}
            }
        }
        
        # Recognized training providers
        self.recognized_providers = {
            'SANS', 'Cybrary', 'Pluralsight', 'Coursera', 'edX', 'Udemy',
            'ISACA', 'ISC²', 'EC-Council', 'CompTIA', 'OffSec', 'NIST',
            'CISSP', 'CISM', 'CISA', 'CEH', 'OSCP', 'Security+'
        }

    def verify_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a CPE activity and provide suggestions
        
        Args:
            activity_data: Dict containing description, activity_type, cpe_value, authority, proof_file
            
        Returns:
            Dict with verified, suggested_cpe_value, verification_method, verification_notes
        """
        description = activity_data.get('description', '').lower()
        activity_type = activity_data.get('activity_type', 'Education')
        cpe_value = activity_data.get('cpe_value', 0)
        authority = activity_data.get('authority', 'ISC²')
        proof_file = activity_data.get('proof_file')
        
        logger.info(f"Verifying activity: {activity_type} for {authority}")
        
        # Initialize result
        result = {
            'verified': False,
            'suggested_cpe_value': cpe_value,
            'verification_method': 'manual',
            'verification_notes': 'Manual verification required.'
        }
        
        try:
            # Check if provider is recognized
            is_recognized_provider = self._check_recognized_provider(description)
            
            # Get authority rules
            authority_rules = self.authority_rules.get(authority, {})
            activity_rules = authority_rules.get(activity_type, {})
            
            if activity_rules:
                # Validate CPE value against authority rules
                min_cpe = activity_rules.get('min', 0)
                max_cpe = activity_rules.get('max', 100)
                default_cpe = activity_rules.get('default', cpe_value)
                
                # Suggest adjustment if needed
                if cpe_value < min_cpe:
                    result['suggested_cpe_value'] = min_cpe
                    result['verification_notes'] = f'CPE value increased to meet {authority} minimum of {min_cpe} for {activity_type}.'
                elif cpe_value > max_cpe:
                    result['suggested_cpe_value'] = max_cpe
                    result['verification_notes'] = f'CPE value capped at {authority} maximum of {max_cpe} for {activity_type}.'
                else:
                    result['suggested_cpe_value'] = cpe_value
                
                # Auto-verify if conditions are met
                if is_recognized_provider and proof_file:
                    result['verified'] = True
                    result['verification_method'] = 'provider_recognition'
                    result['verification_notes'] = f'Auto-verified: Recognized training provider with proof documentation.'
                elif is_recognized_provider:
                    result['verified'] = True
                    result['verification_method'] = 'provider_recognition'
                    result['verification_notes'] = f'Auto-verified: Recognized training provider.'
                elif proof_file:
                    result['verification_method'] = 'document_review'
                    result['verification_notes'] = f'Proof document uploaded. Manual review recommended for final verification.'
                else:
                    result['verification_notes'] = f'Manual verification required. Consider uploading proof documentation.'
            
            # Additional validation based on activity keywords
            verification_bonus = self._analyze_activity_keywords(description, activity_type)
            if verification_bonus['confidence'] > 0.7:
                if not result['verified']:
                    result['verification_method'] = 'keyword_analysis'
                    result['verification_notes'] += f' {verification_bonus["notes"]}'
                
        except Exception as e:
            logger.error(f"Error in activity verification: {str(e)}")
            result['verification_notes'] = 'Verification error occurred. Manual review required.'
        
        return result

    def _check_recognized_provider(self, description: str) -> bool:
        """Check if the activity mentions a recognized training provider"""
        description_lower = description.lower()
        
        for provider in self.recognized_providers:
            if provider.lower() in description_lower:
                return True
        
        return False

    def _analyze_activity_keywords(self, description: str, activity_type: str) -> Dict[str, Any]:
        """Analyze activity description for verification confidence"""
        
        high_confidence_keywords = {
            'Training': ['course', 'certification', 'bootcamp', 'training program', 'class'],
            'Conference': ['conference', 'summit', 'symposium', 'expo', 'convention'],
            'Webinar': ['webinar', 'online session', 'virtual training', 'web seminar'],
            'Workshop': ['workshop', 'hands-on', 'lab', 'practical session'],
            'Education': ['university', 'degree', 'academic', 'research', 'study']
        }
        
        description_lower = description.lower()
        relevant_keywords = high_confidence_keywords.get(activity_type, [])
        
        matches = sum(1 for keyword in relevant_keywords if keyword in description_lower)
        confidence = min(matches / len(relevant_keywords) if relevant_keywords else 0, 1.0)
        
        if confidence > 0.5:
            notes = f"High confidence match for {activity_type} activity based on description keywords."
        else:
            notes = f"Activity description could be more specific for {activity_type} type."
        
        return {
            'confidence': confidence,
            'notes': notes
        }

# Global instance
verification_engine = CPEVerificationEngine()