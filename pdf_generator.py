"""
Enhanced PDF report generator for CPE activities
Generates certification-specific formatted reports
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
import qrcode
from io import BytesIO
import tempfile
import os
from datetime import datetime
from typing import List, Dict, Any

class CPEReportGenerator:
    """Generate professional CPE reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CertificationTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#2E86AB'),
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#1B4965'),
            leftIndent=0
        ))
        
        self.styles.add(ParagraphStyle(
            name='ActivityDetail',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leftIndent=20
        ))
    
    def generate_single_activity_report(self, activity_data: Dict[str, Any], 
                                      certification_data: Dict[str, Any],
                                      verification_data: Dict[str, Any] = None) -> bytes:
        """Generate PDF report for a single CPE activity"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Header with certification info
        story.append(Paragraph(f"CPE Activity Report", self.styles['CertificationTitle']))
        story.append(Paragraph(f"{certification_data.get('name', 'Certification')} - {certification_data.get('authority', '')}", 
                              self.styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Activity details table
        activity_table_data = [
            ['Activity Information', ''],
            ['Activity Type:', activity_data.get('activity_type', 'Training')],
            ['Description:', activity_data.get('description', '')],
            ['Date Completed:', activity_data.get('activity_date', '').strftime('%B %d, %Y') if activity_data.get('activity_date') else ''],
            ['CPE Hours Claimed:', str(activity_data.get('cpe_value', 0))],
            ['Date Logged:', datetime.now().strftime('%B %d, %Y')],
        ]
        
        if verification_data:
            activity_table_data.extend([
                ['Verification Status:', 'Verified' if verification_data.get('verified') else 'Pending'],
                ['Verification Method:', verification_data.get('verification_method', 'Manual')],
                ['Verification Notes:', verification_data.get('verification_notes', '')]
            ])
        
        activity_table = Table(activity_table_data, colWidths=[2*inch, 4*inch])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(activity_table)
        story.append(Spacer(1, 30))
        
        # Certification requirements section
        story.append(Paragraph("Certification Requirements", self.styles['SectionHeader']))
        
        req_table_data = [
            ['Certification Details', ''],
            ['Total CPEs Required:', str(certification_data.get('required_cpes', 0))],
            ['Renewal Date:', certification_data.get('renewal_date', '').strftime('%B %d, %Y') if certification_data.get('renewal_date') else ''],
            ['Current Progress:', f"{certification_data.get('earned_cpes', 0)}/{certification_data.get('required_cpes', 0)} CPEs"],
        ]
        
        req_table = Table(req_table_data, colWidths=[2*inch, 4*inch])
        req_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1B4965')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(req_table)
        story.append(Spacer(1, 30))
        
        # Authority-specific information
        authority_info = self._get_authority_specific_info(certification_data.get('authority', ''))
        if authority_info:
            story.append(Paragraph("Authority Guidelines", self.styles['SectionHeader']))
            story.append(Paragraph(authority_info, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # QR code for verification
        qr_data = f"CPE Activity: {activity_data.get('description', '')} | Date: {activity_data.get('activity_date', '')} | CPEs: {activity_data.get('cpe_value', 0)}"
        qr_img = self._generate_qr_code(qr_data)
        if qr_img:
            story.append(Paragraph("Verification Code", self.styles['SectionHeader']))
            story.append(qr_img)
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | CPE Management Platform"
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    def generate_comprehensive_report(self, activities: List[Dict[str, Any]], 
                                    certification_data: Dict[str, Any],
                                    user_data: Dict[str, Any] = None) -> bytes:
        """Generate comprehensive report for all activities"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Header
        story.append(Paragraph("Comprehensive CPE Report", self.styles['CertificationTitle']))
        story.append(Paragraph(f"{certification_data.get('name', 'Certification')} - {certification_data.get('authority', '')}", 
                              self.styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Summary section
        total_cpes = sum(float(activity.get('cpe_value', 0)) for activity in activities)
        required_cpes = certification_data.get('required_cpes', 0)
        progress_percentage = (total_cpes / required_cpes * 100) if required_cpes > 0 else 0
        
        summary_data = [
            ['CPE Summary', ''],
            ['Total Activities Logged:', str(len(activities))],
            ['Total CPE Hours Earned:', f"{total_cpes:.1f}"],
            ['CPE Hours Required:', str(required_cpes)],
            ['Progress Toward Renewal:', f"{progress_percentage:.1f}%"],
            ['Renewal Date:', certification_data.get('renewal_date', '').strftime('%B %d, %Y') if certification_data.get('renewal_date') else ''],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Activities list
        story.append(Paragraph("Detailed Activity Log", self.styles['SectionHeader']))
        
        if activities:
            # Create activities table
            activities_data = [['Date', 'Activity', 'Type', 'CPE Hours']]
            
            for activity in activities:
                activities_data.append([
                    activity.get('activity_date', '').strftime('%m/%d/%Y') if activity.get('activity_date') else '',
                    activity.get('description', '')[:50] + ('...' if len(activity.get('description', '')) > 50 else ''),
                    activity.get('activity_type', 'Training'),
                    str(activity.get('cpe_value', 0))
                ])
            
            activities_table = Table(activities_data, colWidths=[1*inch, 3*inch, 1*inch, 1*inch])
            activities_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4965')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('ALTERNATEROWCOLORS', (0, 1), (-1, -1), [colors.HexColor('#F8F9FA'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(activities_table)
        else:
            story.append(Paragraph("No activities logged yet.", self.styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Authority compliance section
        authority_info = self._get_authority_specific_info(certification_data.get('authority', ''))
        if authority_info:
            story.append(Paragraph("Compliance Information", self.styles['SectionHeader']))
            story.append(Paragraph(authority_info, self.styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | CPE Management Platform"
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    def _get_authority_specific_info(self, authority: str) -> str:
        """Get authority-specific compliance information"""
        authority_info = {
            'ISC²': "ISC² requires 40 CPE credits every 3 years. Activities must be relevant to the CISSP Common Body of Knowledge (CBK). Group A activities (professional development) can count for up to 40 CPEs, while Group B activities (giving back to the profession) can count for up to 20 CPEs.",
            
            'EC-Council': "EC-Council requires 120 credit hours every 3 years. Activities must be cybersecurity-related and documented with proof of completion. Credits can be earned through training, conferences, self-study, and professional activities.",
            
            'CompTIA': "CompTIA requires 50 Continuing Education Units (CEUs) every 3 years. Activities must be IT or security-related. CEUs can be earned through training, conferences, certifications, and professional experience.",
            
            'Offensive Security': "Offensive Security certification requirements vary by certification. Most require continuous learning and professional development in penetration testing and security assessment domains."
        }
        
        return authority_info.get(authority, "Please refer to your certification authority's official guidelines for specific CPE requirements.")
    
    def _generate_qr_code(self, data: str):
        """Generate QR code for verification"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                qr_img.save(tmp_file.name)
                img = Image(tmp_file.name, width=1*inch, height=1*inch)
                os.unlink(tmp_file.name)  # Clean up temp file
                return img
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None

# Global instance
pdf_generator = CPEReportGenerator()