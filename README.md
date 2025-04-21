# HarperDB Platform Operations Challenge

This repository contains a solution for deploying and testing HarperDB in a containerized environment. The solution includes container orchestration, automated testing, and performance metrics collection.

## Features

- Docker Compose configuration for HarperDB
- Automated workflow for testing HarperDB functionality
- Performance metrics collection
- GitHub Actions integration for CI/CD
- Comprehensive logging and error handling

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Git

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd harper-platform-ops
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start HarperDB:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

## Running the Workflow

The workflow can be run in two ways:

1. Locally:
```bash
python scripts/workflow.py
```

2. Via GitHub Actions:
- Push to the main branch or create a pull request
- The workflow will automatically run and generate metrics

## Workflow Steps

1. Container Validation
   - Checks if the HarperDB container is running
   - Validates API accessibility

2. Schema and Table Creation
   - Creates a test schema
   - Creates a test table with proper configuration

3. Data Operations
   - Loads test data
   - Updates records
   - Validates changes

4. Metrics Collection
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk I/O

## Metrics

Metrics are collected at key points during the workflow and saved to `metrics/workflow_metrics.json`. The metrics include:
- Timestamp
- CPU usage
- Memory usage
- Network I/O statistics
- Disk I/O statistics

## Security Considerations

- Default credentials are used for demonstration purposes
- In production, use environment variables or secrets management
- The Docker Compose file uses environment variables for sensitive data