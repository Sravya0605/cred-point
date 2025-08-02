import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
import csv
from io import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

def allowed_file(filename):
    """Check if file has allowed extension"""
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return the filename"""
    if file and file.filename and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Save file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename, filename
    return None, None

def generate_csv_report(certification, activities):
    """Generate CSV report for certification activities"""
    output = StringIO()
    fieldnames = ['Date', 'Activity Type', 'Description', 'CPE Value', 'Proof File']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for activity in activities:
        writer.writerow({
            'Date': activity.activity_date.strftime('%Y-%m-%d'),
            'Activity Type': activity.activity_type,
            'Description': activity.description,
            'CPE Value': activity.cpe_value,
            'Proof File': activity.original_filename or 'None'
        })
    
    return output.getvalue()

def generate_pdf_report(certification, activities):
    """Generate PDF report for certification activities"""
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"CPE Report - {certification.name}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Certification Info
    info_data = [
        ['Certification:', certification.name],
        ['Authority:', certification.authority],
        ['Required CPEs:', str(certification.required_cpes)],
        ['Earned CPEs:', f"{certification.earned_cpes:.1f}"],
        ['Progress:', f"{certification.progress_percentage:.1f}%"],
        ['Renewal Date:', certification.renewal_date.strftime('%Y-%m-%d') if certification.renewal_date else 'N/A']
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Activities Table
    if activities:
        activity_title = Paragraph("Activity History", styles['Heading2'])
        story.append(activity_title)
        story.append(Spacer(1, 0.1*inch))
        
        # Table headers
        activity_data = [['Date', 'Type', 'Description', 'CPE Value']]
        
        # Add activity rows
        for activity in activities:
            description = activity.description[:50] + '...' if len(activity.description) > 50 else activity.description
            activity_data.append([
                activity.activity_date.strftime('%Y-%m-%d'),
                activity.activity_type,
                description,
                f"{activity.cpe_value:.1f}"
            ])
        
        activity_table = Table(activity_data, colWidths=[1*inch, 1.2*inch, 3*inch, 0.8*inch])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(activity_table)
    else:
        no_activities = Paragraph("No activities recorded for this certification.", styles['Normal'])
        story.append(no_activities)
    
    doc.build(story)
    buffer.seek(0)
    return buffer
