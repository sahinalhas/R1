# Overview

This is a comprehensive Turkish Student Guidance Management System (YKS Çalışma Takip Sistemi) built with Flask. The system provides tools for academic counselors and guidance teachers to manage student information, track academic progress, schedule study programs, conduct interviews, and generate reports. It supports both individual student tracking and school-wide statistical analysis with features like meeting diaries, activity logging, and AI-assisted academic risk assessment.

## Current Status
- **✅ Successfully imported and configured for Replit environment**
- **✅ Flask application running on port 5000**
- **✅ PostgreSQL database configured and available**
- **✅ All dependencies installed and working**
- **✅ Proxy configuration added for Replit hosting**
- **✅ Deployment configuration set for autoscale**
- **✅ Login flow optimized - redirects directly to dashboard after login**
- **✅ Dashboard accessible without requiring student selection**
- **✅ Session system completely removed - no student selection required**
- **✅ All @session_required decorators removed from routes**
- **✅ System works independently without student selection dependencies**

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Flask Application**: Modular blueprint-based architecture with factory pattern
- **Database Layer**: SQLAlchemy ORM with support for both SQLite (development) and PostgreSQL (production)
- **Session Management**: Flask sessions for maintaining active student context across requests
- **Modular Design**: 15+ blueprints for different functional areas (student management, course tracking, reports, etc.)

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive design
- **JavaScript Libraries**: FullCalendar for scheduling, DataTables for data presentation, Chart.js for visualizations
- **CSS Framework**: Custom CSS with Bootstrap integration, including animations and mobile responsiveness
- **Client-side Features**: AJAX-powered search, dynamic form handling, PDF generation capabilities

## Data Models and Relationships
- **Student-Centric Design**: All data models relate back to the Ogrenci (Student) entity
- **Academic Tracking**: Course programs (DersProgrami), progress tracking (DersIlerleme), topic monitoring (KonuTakip)
- **Assessment System**: Mock exam results (DenemeSonuc) with detailed subject-wise scoring
- **Communication Logs**: Meeting records (GorusmeKaydi) with categorization and MEBBİS integration support

## Authentication and Authorization
- **Session-based Authentication**: Decorator-based access control (@session_required)
- **Context Management**: Active student selection maintained across user sessions
- **Role-based Access**: Admin-required routes for sensitive operations
- **Activity Logging**: User action tracking for audit purposes

## Service Layer Pattern
- **Business Logic Separation**: Service classes handle complex operations (OgrenciService, ProgramService, etc.)
- **Data Processing**: Centralized logic for calculations, validations, and transformations
- **Report Generation**: Specialized services for PDF/Excel report creation
- **API Integration**: Services prepare data for both web interface and API consumption

## Report and Analytics System
- **Multi-format Reports**: PDF and Excel generation using WeasyPrint and OpenPyXL
- **Statistical Analysis**: Progress tracking, risk assessment, and performance metrics
- **Data Visualization**: Charts and graphs for academic progress monitoring
- **Export Capabilities**: Bulk data export for external analysis

# External Dependencies

## Core Framework
- **Flask**: Web framework with extensions for SQLAlchemy, session management
- **SQLAlchemy**: ORM for database operations with model relationships
- **Jinja2**: Template rendering with custom filters for Turkish localization

## Data Processing
- **Pandas**: Excel file processing and data manipulation
- **NumPy**: Numerical computations for statistical analysis
- **OpenPyXL**: Excel file generation with formatting and charts

## Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **FullCalendar**: Interactive calendar component for scheduling
- **DataTables**: Advanced table features with search and pagination
- **Chart.js**: Data visualization library for progress charts

## Document Generation
- **WeasyPrint**: HTML to PDF conversion for reports
- **ReportLab**: Alternative PDF generation (optional)

## Machine Learning (Optional)
- **Scikit-learn**: Academic risk prediction models
- **Joblib**: Model serialization and loading

## Database Support
- **SQLite**: Development database with file-based storage (fallback)
- **PostgreSQL**: Production database with connection pooling support (configured in Replit)
- **psycopg2**: PostgreSQL database adapter

## Replit Environment Configuration
- **Host**: 0.0.0.0:5000 for development server
- **Proxy Support**: ProxyFix middleware configured for iframe hosting
- **Environment Variables**: DATABASE_URL and SESSION_SECRET configured
- **Deployment**: Autoscale deployment with Gunicorn for production

## Development Tools
- **Flask-DebugToolbar**: Development debugging assistance
- **Python-dotenv**: Environment variable management