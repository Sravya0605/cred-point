"""
Professional PDF Report Generator for CPE Management Platform
Generates authority-specific formatted reports with QR codes
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
import qrcode
from io import BytesIO
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class CPEPDFGenerator:
    """Professional PDF generator for CPE reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom styles for PDF generation"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1  # Center alignment
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e'),
            borderWidth=1,
            borderColor=colors.HexColor('#bdc3c7'),
            borderPadding=5
        ))
        
        # Subheader style
        self.styles.add(ParagraphStyle(
            name='CustomSubheader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=6,
            spaceAfter=6,
            textColor=colors.HexColor('#7f8c8d')
        ))

    def generate_single_activity_report(self, activity_data: Dict[str, Any], 
                                      certification_data: Dict[str, Any],
                                      verification_data: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Generate PDF report for a single CPE activity
        
        Args:
            activity_data: Activity information
            certification_data: Certification details
            verification_data: Verification status and notes
            
        Returns:
            PDF data as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=72, bottomMargin=72)
        story = []
        
        # Title
        title = Paragraph("CPE Activity Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Activity Details Section
        story.append(Paragraph("Activity Information", self.styles['CustomHeader']))
        
        activity_table_data = [
            ['Activity Type:', activity_data.get('activity_type', 'N/A')],
            ['Description:', activity_data.get('description', 'N/A')],
            ['CPE Value:', f"{activity_data.get('cpe_value', 0)} CPE Credits"],
            ['Activity Date:', activity_data.get('activity_date', 'N/A').strftime('%B %d, %Y') if activity_data.get('activity_date') else 'N/A'],
            ['Proof File:', activity_data.get('original_filename', 'No file uploaded')]
        ]
        
        activity_table = Table(activity_table_data, colWidths=[2*inch, 4*inch])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(activity_table)
        story.append(Spacer(1, 20))
        
        # Certification Details Section
        story.append(Paragraph("Certification Information", self.styles['CustomHeader']))
        
        cert_table_data = [
            ['Certification:', certification_data.get('name', 'N/A')],
            ['Authority:', certification_data.get('authority', 'N/A')],
            ['Required CPEs:', str(certification_data.get('required_cpes', 'N/A'))],
            ['Earned CPEs:', str(certification_data.get('earned_cpes', 'N/A'))],
            ['Renewal Date:', certification_data.get('renewal_date', 'N/A').strftime('%B %d, %Y') if certification_data.get('renewal_date') else 'N/A']
        ]
        
        cert_table = Table(cert_table_data, colWidths=[2*inch, 4*inch])
        cert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(cert_table)
        story.append(Spacer(1, 20))
        
        # Verification Section
        if verification_data:
            story.append(Paragraph("Verification Status", self.styles['CustomHeader']))
            
            verification_status = "Verified" if verification_data.get('verified') else "Pending Verification"
            verification_color = colors.green if verification_data.get('verified') else colors.orange
            
            verification_table_data = [
                ['Status:', verification_status],
                ['Method:', verification_data.get('verification_method', 'Manual')],
                ['Notes:', verification_data.get('verification_notes', 'No additional notes')]
            ]
            
            verification_table = Table(verification_table_data, colWidths=[2*inch, 4*inch])
            verification_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('TEXTCOLOR', (1, 0), (1, 0), verification_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(verification_table)
            story.append(Spacer(1, 20))
        
        # QR Code for verification
        story.append(Paragraph("Verification QR Code", self.styles['CustomHeader']))
        qr_code_image = self._generate_qr_code(f"CPE Activity: {activity_data.get('description', 'N/A')}")
        if qr_code_image:
            story.append(qr_code_image)
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        footer = Paragraph(footer_text, self.styles['CustomSubheader'])
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_comprehensive_report(self, activities_data: List[Dict[str, Any]], 
                                    certification_data: Dict[str, Any],
                                    user_data: Dict[str, Any]) -> bytes:
        """
        Generate comprehensive CPE report for all activities
        
        Args:
            activities_data: List of all activities
            certification_data: Certification details
            user_data: User information
            
        Returns:
            PDF data as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=72, bottomMargin=72)
        story = []
        
        # Title
        title = Paragraph(f"CPE Comprehensive Report - {certification_data.get('name', 'Unknown Certification')}", 
                         self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # User Information
        story.append(Paragraph("Professional Information", self.styles['CustomHeader']))
        
        user_table_data = [
            ['Name:', user_data.get('username', 'N/A')],
            ['Email:', user_data.get('email', 'N/A')],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        user_table = Table(user_table_data, colWidths=[2*inch, 4*inch])
        user_table.setStyle(self._get_table_style())
        story.append(user_table)
        story.append(Spacer(1, 20))
        
        # Certification Summary
        story.append(Paragraph("Certification Summary", self.styles['CustomHeader']))
        
        total_earned = sum(activity.get('cpe_value', 0) for activity in activities_data)
        progress_percentage = (total_earned / certification_data.get('required_cpes', 1)) * 100
        
        summary_table_data = [
            ['Certification:', certification_data.get('name', 'N/A')],
            ['Authority:', certification_data.get('authority', 'N/A')],
            ['Required CPEs:', str(certification_data.get('required_cpes', 'N/A'))],
            ['Earned CPEs:', f"{total_earned:.1f}"],
            ['Progress:', f"{progress_percentage:.1f}%"],
            ['Renewal Date:', certification_data.get('renewal_date', 'N/A').strftime('%B %d, %Y') if certification_data.get('renewal_date') else 'N/A']
        ]
        
        summary_table = Table(summary_table_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(self._get_table_style())
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Activities Table
        story.append(Paragraph("CPE Activities Log", self.styles['CustomHeader']))
        
        if activities_data:
            # Table headers
            activities_table_data = [
                ['Date', 'Type', 'Description', 'CPE Value', 'Status']
            ]
            
            # Add activity rows
            for activity in activities_data:
                status = "✓ Verified" if activity.get('verified') else "⏳ Pending"
                activities_table_data.append([
                    activity.get('activity_date', 'N/A').strftime('%m/%d/%Y') if activity.get('activity_date') else 'N/A',
                    activity.get('activity_type', 'N/A'),
                    activity.get('description', 'N/A')[:40] + '...' if len(activity.get('description', '')) > 40 else activity.get('description', 'N/A'),
                    f"{activity.get('cpe_value', 0):.1f}",
                    status
                ])
            
            activities_table = Table(activities_table_data, colWidths=[1*inch, 1*inch, 2.5*inch, 0.8*inch, 0.7*inch])
            activities_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(activities_table)
        else:
            story.append(Paragraph("No activities logged yet.", self.styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # QR Code for verification
        story.append(Paragraph("Report Verification", self.styles['CustomHeader']))
        qr_code_image = self._generate_qr_code(f"CPE Report: {certification_data.get('name', 'Unknown')} - {total_earned:.1f} CPEs")
        if qr_code_image:
            story.append(qr_code_image)
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | CPE Management Platform"
        footer = Paragraph(footer_text, self.styles['CustomSubheader'])
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _get_table_style(self) -> TableStyle:
        """Get standard table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])

    def _generate_qr_code(self, data: str) -> Optional[Image]:
        """Generate QR code for verification"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Create ReportLab Image
            qr_image = Image(img_buffer, width=1.5*inch, height=1.5*inch)
            return qr_image
            
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            return None

# Global instance
pdf_generator = CPEPDFGenerator()