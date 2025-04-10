# WomSoft Server

> **MEDICAL DEVICE SOFTWARE NOTICE**: This software is intended to be used as part of a medical device for biomarker analysis. All formal regulatory documentation is maintained in the company QMS SharePoint. This repository contains the implementation and technical documentation.

## Project Overview

WomSoft Server is a web-based application for biomarker analysis developed for Mimark. The software processes biomarker data (Protein1, Protein2, and Protein3) to generate diagnostic results.

**Intended Use**: <!-- TODO: Add specific intended use statement -->

**Software Safety Classification**: <!-- TODO: Add classification (Class A, B, or C) and justification -->

**QMS Document References**:
- Software Development Plan: <!-- TODO: Add document ID -->
- Software Requirements Specification: <!-- TODO: Add document ID -->
- Risk Management File: <!-- TODO: Add document ID -->

## Technical Architecture

WomSoft Server is built using a modern web stack:

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Frontend**: HTML, JavaScript, Bootstrap
- **Testing**: Pytest, Selenium
- **Deployment**: Docker

### System Components

```
WomSoft Server
├── API Layer (FastAPI)
│   ├── Authentication endpoints
│   ├── Diagnostic endpoints
│   └── User management endpoints
├── Service Layer
│   ├── User service
│   ├── Diagnostic calculation service
│   └── Data persistence service
├── Data Layer (SQLite)
│   ├── User data
│   └── Diagnostic data
└── Frontend
    ├── Authentication UI
    ├── Diagnostic entry form
    └── Results dashboard
```

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/womsoft-server.git
   cd womsoft-server
   ```

2. Start the application:
   ```
   docker-compose up -d
   ```

3. Access the application at http://localhost:8000

### Default Credentials

- Username: <!-- TODO: Add default username -->
- Password: <!-- TODO: Add default password -->

## Development

### Setting Up Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload
```

### Project Structure

```
womsoft_server/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── database.py          # Database configuration
│   ├── auth/                # Authentication modules
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API endpoints
│   └── schemas/             # Pydantic schemas
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── ui/                  # UI tests with Selenium
├── templates/               # HTML templates
├── static/                  # Static assets
├── migrations/              # Database migrations
└── docker-compose.yml       # Docker configuration
```

## Testing

### Running Tests

#### Unit and Integration Tests

```bash
docker-compose -f docker-compose.pytest.yml up
```

#### UI Tests with Visual Feedback

```bash
docker-compose -f docker-compose.selenium.yml up
```

To watch tests execute in real-time, connect to VNC on localhost:5900 or http://localhost:7900

### Test Coverage

<!-- TODO: Add information about test coverage goals and current status -->

## Validation & Verification

All formal V&V activities are documented in the QMS. This repository contains the technical implementation of tests specified in the Verification Plan document <!-- TODO: Add document ID -->.

## Release Process

Releases follow the process defined in the Configuration Management Plan <!-- TODO: Add document ID -->. Each release is tagged with a version number following [Semantic Versioning](https://semver.org/) principles.

### Release History

<!-- TODO: Add release history when available -->

## Risk Management

Risk controls implemented in code are traced to the Risk Management File <!-- TODO: Add document ID -->. Critical risk controls include:

<!-- TODO: List key risk controls implemented in the software -->

## Regulatory Information

- **IEC 62304 Classification**: <!-- TODO: Add classification -->
- **Intended Use**: <!-- TODO: Add concise intended use statement -->
- **Regulatory Status**: <!-- TODO: Add regulatory status information -->

## License

<!-- TODO: Add license information -->

## Acknowledgments

- Mimark Team

---

*This software is developed in compliance with IEC 62304 requirements for medical device software. Complete regulatory documentation is maintained in the company QMS system.*