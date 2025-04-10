# Development Environment Setup

This document describes how to set up a development environment for WomSoft Server.

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Git
- Code editor (VSCode recommended)

## Local Setup

### Setting Up the Python Environment

1. Clone the repository:

```
   git clone https://github.com/yourusername/womsoft-server.git
   cd womsoft-server
```

2. Create a virtual environment:

```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```
   pip install -r requirements.txt
```

### Database Setup

1. The development environment uses SQLite by default. No additional setup is required.

2. To initialize the database:

```
   python -m app.database
```

### Running the Application

1. Start the application in development mode:

```
   uvicorn app.main:app --reload
```

2. Access the application at http://localhost:8000

## Docker Development Environment

For a consistent development environment, you can use Docker:

```
docker-compose -f docker-compose.dev.yml up -d
```

This will start the application in development mode with hot-reloading.

## Testing Environment

To run tests:

1. Unit and integration tests:

```
   docker-compose -f docker-compose.pytest.yml up
```

2. UI tests with Selenium:

```
   docker-compose -f docker-compose.selenium.yml up
```

## Troubleshooting

For common issues, see troubleshooting.md.

<!-- TODO: Add any environment-specific configuration or requirements -->
<!-- TODO: Add information about default test accounts/credentials -->