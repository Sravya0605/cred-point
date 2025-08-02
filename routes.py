import os
from flask import render_template, request, redirect, url_for, flash, send_file, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Certification, CPEActivity
from forms import LoginForm, RegisterForm, CertificationForm, CPEActivityForm
from utils import save_uploaded_file, generate_csv_report, generate_pdf_report
from datetime import datetime, date

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    certifications = Certification.query.filter_by(user_id=current_user.id).all()
    recent_activities = CPEActivity.query.filter_by(user_id=current_user.id)\
                                        .order_by(CPEActivity.created_at.desc())\
                                        .limit(5).all()
    
    # Calculate overall stats
    total_certifications = len(certifications)
    total_activities = CPEActivity.query.filter_by(user_id=current_user.id).count()
    
    # Check for reminders
    reminders = []
    for cert in certifications:
        if cert.renewal_date:
            days_until_renewal = (cert.renewal_date - date.today()).days
            if days_until_renewal <= 90 and cert.progress_percentage < 100:
                reminders.append({
                    'type': 'renewal',
                    'message': f"{cert.name} renewal is in {days_until_renewal} days and you need {cert.required_cpes - cert.earned_cpes:.1f} more CPEs",
                    'certification': cert
                })
        
        if cert.progress_percentage < 25:
            reminders.append({
                'type': 'low_progress',
                'message': f"{cert.name} has very low progress ({cert.progress_percentage:.1f}%)",
                'certification': cert
            })
    
    return render_template('dashboard.html', 
                         certifications=certifications,
                         recent_activities=recent_activities,
                         total_certifications=total_certifications,
                         total_activities=total_activities,
                         reminders=reminders)

@app.route('/certifications')
@login_required
def certifications():
    """View all certifications"""
    user_certifications = Certification.query.filter_by(user_id=current_user.id).all()
    return render_template('certifications.html', certifications=user_certifications)

@app.route('/certifications/add', methods=['GET', 'POST'])
@login_required
def add_certification():
    """Add new certification"""
    form = CertificationForm()
    
    if form.validate_on_submit():
        certification = Certification(
            name=form.name.data,
            authority=form.authority.data,
            required_cpes=form.required_cpes.data,
            renewal_date=form.renewal_date.data,
            user_id=current_user.id
        )
        
        db.session.add(certification)
        db.session.commit()
        
        flash('Certification added successfully!', 'success')
        return redirect(url_for('certifications'))
    
    return render_template('add_certification.html', form=form)

@app.route('/certifications/<int:cert_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_certification(cert_id):
    """Edit certification"""
    certification = Certification.query.filter_by(id=cert_id, user_id=current_user.id).first_or_404()
    form = CertificationForm(obj=certification)
    
    if form.validate_on_submit():
        certification.name = form.name.data
        certification.authority = form.authority.data
        certification.required_cpes = form.required_cpes.data
        certification.renewal_date = form.renewal_date.data
        
        db.session.commit()
        flash('Certification updated successfully!', 'success')
        return redirect(url_for('certifications'))
    
    return render_template('add_certification.html', form=form, certification=certification)

@app.route('/certifications/<int:cert_id>/delete', methods=['POST'])
@login_required
def delete_certification(cert_id):
    """Delete certification"""
    certification = Certification.query.filter_by(id=cert_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(certification)
    db.session.commit()
    
    flash('Certification deleted successfully!', 'success')
    return redirect(url_for('certifications'))

@app.route('/activities')
@login_required
def activities():
    """View all activities"""
    page = request.args.get('page', 1, type=int)
    cert_filter = request.args.get('certification', type=int)
    
    query = CPEActivity.query.filter_by(user_id=current_user.id)
    
    if cert_filter:
        query = query.filter_by(certification_id=cert_filter)
    
    user_activities = query.order_by(CPEActivity.activity_date.desc())\
                          .paginate(page=page, per_page=20, error_out=False)
    
    certifications = Certification.query.filter_by(user_id=current_user.id).all()
    
    return render_template('activities.html', 
                         activities=user_activities,
                         certifications=certifications,
                         selected_cert=cert_filter)

@app.route('/activities/add', methods=['GET', 'POST'])
@login_required
def add_activity():
    """Add new CPE activity"""
    form = CPEActivityForm()
    
    # Populate certification choices
    certifications = Certification.query.filter_by(user_id=current_user.id).all()
    form.certification_id.choices = [(cert.id, f"{cert.name} ({cert.authority})") for cert in certifications]
    
    if not certifications:
        flash('You need to add at least one certification before logging activities.', 'warning')
        return redirect(url_for('add_certification'))
    
    if form.validate_on_submit():
        # Handle file upload
        proof_filename = None
        original_filename = None
        
        if form.proof_file.data:
            proof_filename, original_filename = save_uploaded_file(form.proof_file.data)
        
        activity = CPEActivity(
            activity_type=form.activity_type.data,
            description=form.description.data,
            cpe_value=form.cpe_value.data,
            activity_date=form.activity_date.data,
            certification_id=form.certification_id.data,
            proof_file=proof_filename,
            original_filename=original_filename,
            user_id=current_user.id
        )
        
        db.session.add(activity)
        db.session.commit()
        
        flash('CPE activity added successfully!', 'success')
        return redirect(url_for('activities'))
    
    return render_template('add_activity.html', form=form)

@app.route('/activities/<int:activity_id>/delete', methods=['POST'])
@login_required
def delete_activity(activity_id):
    """Delete CPE activity"""
    activity = CPEActivity.query.filter_by(id=activity_id, user_id=current_user.id).first_or_404()
    
    # Delete associated file if exists
    if activity.proof_file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], activity.proof_file)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(activity)
    db.session.commit()
    
    flash('Activity deleted successfully!', 'success')
    return redirect(url_for('activities'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/certifications/<int:cert_id>/export/<format>')
@login_required
def export_certification(cert_id, format):
    """Export certification report"""
    certification = Certification.query.filter_by(id=cert_id, user_id=current_user.id).first_or_404()
    activities = CPEActivity.query.filter_by(certification_id=cert_id)\
                                 .order_by(CPEActivity.activity_date.desc()).all()
    
    if format == 'csv':
        csv_data = generate_csv_report(certification, activities)
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={certification.name}_report.csv'
        return response
    
    elif format == 'pdf':
        pdf_buffer = generate_pdf_report(certification, activities)
        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={certification.name}_report.pdf'
        return response
    
    flash('Invalid export format.', 'danger')
    return redirect(url_for('certifications'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
