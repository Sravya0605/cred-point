# Overview

This is a Continuing Professional Education (CPE) Management Platform built with Flask. It allows cybersecurity professionals to track their continuing education requirements across multiple certification authorities (ISC², EC-Council, CompTIA, OffSec, etc.). Users can log CPE activities, monitor progress toward renewal requirements, and generate reports for compliance purposes.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask
- **UI Framework**: Bootstrap 5 with dark theme support
- **Styling**: Custom CSS with CSS variables for theming
- **JavaScript**: Vanilla JavaScript for client-side interactions
- **Icons**: Font Awesome for consistent iconography

## Backend Architecture
- **Web Framework**: Flask with modular route organization
- **Authentication**: Flask-Login for session management
- **Forms**: Flask-WTF with WTForms for form handling and validation
- **Password Security**: Werkzeug's security utilities for password hashing
- **File Handling**: Secure file upload system with UUID-based naming

## Data Storage
- **ORM**: SQLAlchemy with Flask-SQLAlchemy integration
- **Database**: SQLite for development, configurable via DATABASE_URL environment variable
- **Models**: Three main entities - User, Certification, and CPEActivity
- **Relationships**: One-to-many relationships between User->Certifications and Certification->Activities
- **File Storage**: Local filesystem storage for proof documents in static/uploads

## Security Features
- **Session Management**: Flask sessions with configurable secret key
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **Password Hashing**: Werkzeug's generate_password_hash/check_password_hash
- **File Upload Security**: Restricted file types (PDF, JPG, JPEG, PNG) with secure filename handling
- **Input Validation**: Server-side validation using WTForms validators

## Report Generation
- **CSV Export**: StringIO-based CSV generation for activity data
- **PDF Export**: ReportLab integration for formatted PDF reports
- **File Management**: Utilities for secure file handling and storage

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering

## UI and Styling
- **Bootstrap 5**: CSS framework via CDN (bootstrap-agent-dark-theme.min.css)
- **Font Awesome 6.4.0**: Icon library via CDN

## Security and Utilities
- **Werkzeug**: Password hashing and file utilities
- **uuid**: Unique filename generation
- **ReportLab**: PDF report generation

## Data Processing
- **csv**: CSV report generation
- **io.StringIO**: In-memory string handling for reports

## Development Configuration
- **SQLite**: Default database (configurable to PostgreSQL or other databases via DATABASE_URL)
- **ProxyFix**: Werkzeug middleware for proper header handling in production environments

The application is designed to be easily deployable with minimal configuration, supporting both development and production environments through environment variable configuration.