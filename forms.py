from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

class CertificationForm(FlaskForm):
    name = StringField('Certification Name', validators=[DataRequired(), Length(max=100)])
    authority = SelectField('Certification Authority', choices=[
        ('ISC²', 'ISC²'),
        ('EC-Council', 'EC-Council'),
        ('CompTIA', 'CompTIA'),
        ('OffSec', 'OffSec'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    required_cpes = IntegerField('Required CPEs', validators=[DataRequired(), NumberRange(min=1)])
    renewal_date = DateField('Renewal Date', validators=[DataRequired()])

class CPEActivityForm(FlaskForm):
    activity_type = SelectField('Activity Type', choices=[
        ('Training', 'Training Course'),
        ('Conference', 'Conference/Seminar'),
        ('Webinar', 'Webinar'),
        ('Workshop', 'Workshop'),
        ('Certification', 'Additional Certification'),
        ('Self-Study', 'Self-Study'),
        ('Teaching', 'Teaching/Instruction'),
        ('Research', 'Research/Writing'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    cpe_value = FloatField('CPE Value', validators=[DataRequired(), NumberRange(min=0.1, max=100)])
    activity_date = DateField('Activity Date', validators=[DataRequired()])
    certification_id = SelectField('Certification', coerce=int, validators=[DataRequired()])
    proof_file = FileField('Proof Document', validators=[
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'Only PDF, JPG, JPEG, and PNG files are allowed!')
    ])
