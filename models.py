from app import db
from flask_login import UserMixin
from datetime import datetime, date
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    certifications = db.relationship('Certification', backref='user', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('CPEActivity', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    authority = db.Column(db.String(50), nullable=False)  # ISC², EC-Council, CompTIA, OffSec
    required_cpes = db.Column(db.Integer, nullable=False)
    renewal_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('CPEActivity', backref='certification', lazy=True, cascade='all, delete-orphan')
    
    @property
    def earned_cpes(self):
        """Calculate total CPEs earned for this certification"""
        total = db.session.query(func.sum(CPEActivity.cpe_value)).filter_by(certification_id=self.id).scalar()
        return total or 0
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.required_cpes == 0:
            return 100
        return min(100, (self.earned_cpes / self.required_cpes) * 100)
    
    @property
    def status(self):
        """Get certification status"""
        progress = self.progress_percentage
        if progress >= 100:
            return 'complete'
        elif progress >= 75:
            return 'on-track'
        elif progress >= 50:
            return 'behind'
        else:
            return 'critical'
    
    def __repr__(self):
        return f'<Certification {self.name}>'

class CPEActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)  # Training, Conference, Webinar, etc.
    description = db.Column(db.Text, nullable=False)
    cpe_value = db.Column(db.Float, nullable=False)
    activity_date = db.Column(db.Date, nullable=False)
    proof_file = db.Column(db.String(255))  # Path to uploaded proof file
    original_filename = db.Column(db.String(255))  # Original filename for display
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    certification_id = db.Column(db.Integer, db.ForeignKey('certification.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CPEActivity {self.description[:50]}>'
