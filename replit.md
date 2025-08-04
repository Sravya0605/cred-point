# Overview

This is a Continuing Professional Education (CPE) Management Platform built with Flask. It allows cybersecurity professionals to track their continuing education requirements across multiple certification authorities (ISC², EC-Council, CompTIA, OffSec, etc.). Users can log CPE activities, monitor progress toward renewal requirements, and generate professional reports for compliance purposes.

## Key Features (August 2025)
- **Real-World Recommendations**: Dynamic fetching of live CPE opportunities from certification authorities and training providers
- **Intelligent Activity Verification**: Automated verification and CPE point calculation based on authority-specific rules
- **Professional PDF Reports**: Certification-specific formatted reports with QR codes for verification
- **Enhanced User Experience**: Ultra-fast loading with critical CSS inlining and optimized database queries
- **File Upload & Verification**: Secure proof document handling with verification status tracking

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

## Report Generation & Verification
- **Professional PDF Reports**: Authority-specific formatted reports with comprehensive activity details, verification status, and QR codes
- **Single Activity Export**: Individual activity reports for submission to certification authorities
- **Comprehensive Reports**: Complete certification progress reports with compliance information
- **Activity Verification Engine**: Real-time verification of CPE activities using authority rules and provider recognition
- **Recommendation System**: Live fetching of relevant CPE opportunities from certification authorities and training providers
- **CSV Export**: Legacy CSV generation for activity data
- **File Management**: Secure proof document handling with verification tracking

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **Flask-SQLAlchemy**: Database ORM integration with performance optimizations
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Trafilatura**: Web content extraction for recommendation fetching
- **BeautifulSoup4**: HTML parsing for web scraping
- **Requests**: HTTP library for external API calls

## UI and Styling
- **Bootstrap 5**: CSS framework via CDN (bootstrap-agent-dark-theme.min.css)
- **Font Awesome 6.4.0**: Icon library via CDN

## Security and Utilities
- **Werkzeug**: Password hashing and file utilities
- **uuid**: Unique filename generation
- **ReportLab**: PDF report generation

## Data Processing & Intelligence
- **ReportLab**: Professional PDF generation with custom styling and QR codes
- **QRCode**: Verification QR code generation for activity reports
- **Pillow**: Image processing for proof documents
- **csv**: CSV report generation
- **io.StringIO**: In-memory string handling for reports
- **Recommendation Engine**: Real-time CPE opportunity discovery
- **Verification Engine**: Automated activity verification and CPE calculation

## Development Configuration
- **SQLite**: Default database (configurable to PostgreSQL or other databases via DATABASE_URL)
- **ProxyFix**: Werkzeug middleware for proper header handling in production environments

The application is designed to be easily deployable with minimal configuration, supporting both development and production environments through environment variable configuration.