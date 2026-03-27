# CloudChef - Smart Recipe Manager

An AI-powered recipe management application that lets users create, discover, and share recipes with intelligent features like image recognition and NLP-powered recipe insights.

## Tech Stack

- **Frontend:** React + Vite
- **Backend:** AWS Lambda (Python 3.11)
- **Shared Library:** Python package with common utilities

## AWS Services

| Service | Purpose |
|---------|---------|
| **AWS Lambda** | Serverless backend API |
| **API Gateway** | REST API endpoint routing |
| **DynamoDB** | Recipe data storage |
| **S3** | Recipe image storage + frontend hosting |
| **Amazon Rekognition** | Food image recognition |
| **Amazon Comprehend** | NLP analysis - key phrases, sentiment, entities |

## Project Structure

```
kasi/
├── backend/            # Lambda function code
├── frontend/           # React + Vite application
├── library/            # Shared Python library
└── .github/workflows/  # CI/CD pipeline
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 20+
- AWS account with programmatic access

### Local Development

**Library:**
```bash
cd library
pip install -e .
pip install pytest
pytest tests/ -v
```

**Frontend:**
```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```

### Deployment

The project uses GitHub Actions for CI/CD. Add these repository secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Push to `main` to trigger the pipeline, which will:

1. Run library tests
2. Deploy backend (DynamoDB, S3, Lambda, API Gateway)
3. Deploy frontend (S3 static website)

## Deployed URL

**Frontend:** http://cloudchef-frontend-prod-kasireddy.s3-website-eu-west-1.amazonaws.com

**API:** https://{api-id}.execute-api.eu-west-1.amazonaws.com/prod
