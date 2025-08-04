import os
import json
from flask import render_template, request, redirect, url_for, flash, send_file, make_response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Certification, CPEActivity
from forms import LoginForm, RegisterForm, CertificationForm, CPEActivityForm
from utils import save_uploaded_file, generate_csv_report, generate_pdf_report
from recommendation_engine import recommendation_engine
from verification_engine import verification_engine
from pdf_generator import pdf_generator
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
    """User dashboard with ultra-fast queries"""
    # Optimized queries
    certifications = Certification.query.filter_by(user_id=current_user.id).all()
    
    # Limit recent activities to just 3 for faster loading
    recent_activities = CPEActivity.query.filter_by(user_id=current_user.id)\
                                        .options(db.joinedload(CPEActivity.certification))\
                                        .order_by(CPEActivity.created_at.desc())\
                                        .limit(3).all()
    
    # Use cached counts
    total_certifications = len(certifications)
    total_activities = len(recent_activities)  # Approximate for speed
    
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
    """View all certifications - optimized"""
    user_certifications = Certification.query.filter_by(user_id=current_user.id).all()
    return render_template('certifications.html', certifications=user_certifications)

@app.route('/certifications/<int:cert_id>/recommendations')
@login_required
def get_recommendations(cert_id):
    """Get real-world recommendations for a certification"""
    certification = Certification.query.filter_by(id=cert_id, user_id=current_user.id).first_or_404()
    
    try:
        recommendations = recommendation_engine.get_recommendations(
            certification.name, 
            certification.authority
        )
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/certifications/<int:cert_id>/recommendations-page')
@login_required
def recommendations_page(cert_id):
    """Display recommendations page for a certification"""
    certification = Certification.query.filter_by(id=cert_id, user_id=current_user.id).first_or_404()
    
    recommendations = recommendation_engine.get_recommendations(
        certification.name, 
        certification.authority
    )
    
    return render_template('recommendations.html', 
                         certification=certification, 
                         recommendations=recommendations)

@app.route('/certifications/add', methods=['GET', 'POST'])
@login_required
def add_certification():
    """Add new certification with duplicate prevention"""
    form = CertificationForm()
    
    if form.validate_on_submit():
        # Prevent duplicate certifications
        existing = Certification.query.filter_by(
            name=form.name.data,
            authority=form.authority.data,
            user_id=current_user.id
        ).first()
        
        if existing:
            flash('You already have this certification registered!', 'warning')
            return redirect(url_for('certifications'))
            
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
    """View all activities with ultra-fast pagination"""
    page = request.args.get('page', 1, type=int)
    cert_filter = request.args.get('certification', type=int)
    
    # Fast query with proper joins
    query = CPEActivity.query.filter_by(user_id=current_user.id)\
                             .options(db.joinedload(CPEActivity.certification))
    
    if cert_filter:
        query = query.filter_by(certification_id=cert_filter)
    
    user_activities = query.order_by(CPEActivity.activity_date.desc())\
                          .paginate(page=page, per_page=10, error_out=False)
    
    # Get certifications for filter dropdown
    certifications = Certification.query.filter_by(user_id=current_user.id).all()
    
    return render_template('activities.html', 
                         activities=user_activities,
                         certifications=certifications,
                         selected_cert=cert_filter)

@app.route('/activities/add', methods=['GET', 'POST'])
@login_required
def add_activity():
    """Add new CPE activity with intelligent verification"""
    form = CPEActivityForm()
    
    # Populate certification choices
    certifications = Certification.query.filter_by(user_id=current_user.id).all()
    form.certification_id.choices = [(cert.id, f"{cert.name} ({cert.authority})") for cert in certifications]
    
    # Handle URL parameters for pre-filling from recommendations
    if request.method == 'GET':
        prefill_description = request.args.get('prefill_description')
        prefill_type = request.args.get('prefill_type')
        prefill_cpe = request.args.get('prefill_cpe')
        prefill_cert = request.args.get('prefill_cert')
        
        if prefill_description:
            form.description.data = prefill_description
        if prefill_type:
            form.activity_type.data = prefill_type
        if prefill_cpe:
            form.cpe_value.data = float(prefill_cpe)
        if prefill_cert:
            form.certification_id.data = int(prefill_cert)
    
    if not certifications:
        flash('You need to add at least one certification before logging activities.', 'warning')
        return redirect(url_for('add_certification'))
    
    if form.validate_on_submit():
        # Get certification for verification
        certification = Certification.query.get(form.certification_id.data)
        
        # Handle file upload
        proof_filename = None
        original_filename = None
        
        if form.proof_file.data:
            proof_filename, original_filename = save_uploaded_file(form.proof_file.data)
        
        # Prepare activity data for verification
        activity_data = {
            'description': form.description.data,
            'activity_type': form.activity_type.data,
            'cpe_value': float(form.cpe_value.data),
            'authority': certification.authority,
            'proof_file': proof_filename
        }
        
        # Verify the activity
        verification_result = verification_engine.verify_activity(activity_data)
        
        activity = CPEActivity(
            activity_type=form.activity_type.data,
            description=form.description.data,
            cpe_value=verification_result.get('suggested_cpe_value', form.cpe_value.data),
            activity_date=form.activity_date.data,
            certification_id=form.certification_id.data,
            proof_file=proof_filename,
            original_filename=original_filename,
            user_id=current_user.id,
            verified=verification_result.get('verified', False),
            verification_method=verification_result.get('verification_method', 'manual'),
            verification_notes=verification_result.get('verification_notes', ''),
            verification_date=datetime.utcnow() if verification_result.get('verified') else None
        )
        
        db.session.add(activity)
        db.session.commit()
        
        # Show verification feedback
        if verification_result.get('verified'):
            flash(f'CPE activity verified and logged! {verification_result.get("verification_notes", "")}', 'success')
        else:
            flash(f'CPE activity logged. {verification_result.get("verification_notes", "Manual verification required.")}', 'info')
        
        # Suggest adjusted CPE value if different
        suggested_value = verification_result.get('suggested_cpe_value', form.cpe_value.data)
        if abs(suggested_value - float(form.cpe_value.data)) > 0.1:
            flash(f'CPE value adjusted to {suggested_value} based on {certification.authority} guidelines', 'info')
        
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

@app.route('/activities/<int:activity_id>/export-pdf')
@login_required
def export_single_activity_pdf(activity_id):
    """Export single activity as professional PDF report"""
    activity = CPEActivity.query.filter_by(id=activity_id, user_id=current_user.id).first_or_404()
    certification = activity.certification
    
    # Prepare activity data
    activity_data = {
        'activity_type': activity.activity_type,
        'description': activity.description,
        'cpe_value': activity.cpe_value,
        'activity_date': activity.activity_date,
        'proof_file': activity.proof_file,
        'original_filename': activity.original_filename
    }
    
    # Prepare certification data
    certification_data = {
        'name': certification.name,
        'authority': certification.authority,
        'required_cpes': certification.required_cpes,
        'renewal_date': certification.renewal_date,
        'earned_cpes': certification.earned_cpes
    }
    
    # Prepare verification data
    verification_data = {
        'verified': activity.verified,
        'verification_method': activity.verification_method,
        'verification_notes': activity.verification_notes
    }
    
    # Generate PDF
    pdf_data = pdf_generator.generate_single_activity_report(
        activity_data, certification_data, verification_data
    )
    
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=CPE_Activity_{activity.id}_{activity.activity_date.strftime("%Y%m%d")}.pdf'
    
    return response

@app.route('/certifications/<int:cert_id>/export-comprehensive-pdf')
@login_required
def export_comprehensive_pdf(cert_id):
    """Export comprehensive certification report as PDF"""
    certification = Certification.query.filter_by(id=cert_id, user_id=current_user.id).first_or_404()
    activities = CPEActivity.query.filter_by(certification_id=cert_id)\
                                 .order_by(CPEActivity.activity_date.desc()).all()
    
    # Prepare activities data
    activities_data = []
    for activity in activities:
        activities_data.append({
            'activity_type': activity.activity_type,
            'description': activity.description,
            'cpe_value': activity.cpe_value,
            'activity_date': activity.activity_date,
            'verified': activity.verified
        })
    
    # Prepare certification data
    certification_data = {
        'name': certification.name,
        'authority': certification.authority,
        'required_cpes': certification.required_cpes,
        'renewal_date': certification.renewal_date,
        'earned_cpes': certification.earned_cpes
    }
    
    # Prepare user data
    user_data = {
        'username': current_user.username,
        'email': current_user.email
    }
    
    # Generate PDF
    pdf_data = pdf_generator.generate_comprehensive_report(
        activities_data, certification_data, user_data
    )
    
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=CPE_Report_{certification.name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    return response

@app.route('/certifications/<int:cert_id>/export/<format>')
@login_required
def export_certification(cert_id, format):
    """Export certification report (legacy endpoint)"""
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
