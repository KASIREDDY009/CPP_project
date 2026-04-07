# SmartPantry - Kitchen Inventory Tracker

A serverless web application that helps users manage their kitchen pantry, track food expiry dates, and reduce food waste using AI-powered image recognition.

## Features
- Add, edit, delete pantry items with categories and expiry dates
- Upload food photos — AWS Rekognition auto-detects and categorizes items
- Dashboard with real-time stats (total items, expiring soon, expired)
- Email notifications via AWS SNS when items are about to expire
- Search and filter items by name or category

## AWS Services Used
1. **S3** — Frontend hosting + food image storage
2. **Lambda** — Serverless backend API
3. **API Gateway** — REST API endpoints
4. **DynamoDB** — NoSQL database for users and pantry items
5. **Rekognition** — AI image analysis for food detection
6. **SNS** — Email notifications for expiry alerts

## Tech Stack
- **Frontend:** React + Tailwind CSS + Vite
- **Backend:** Python (AWS Lambda)
- **Database:** DynamoDB
- **CI/CD:** GitHub Actions
- **Library:** recipe-manager-nci v2.0.0 (PyPI)

## Project Structure
```
├── backend/          # Lambda function code
├── frontend/         # React application
├── library/          # PyPI package (recipe-manager-nci v2.0.0)
├── kasi_cpp/         # LaTeX report
└── .github/workflows # CI/CD pipeline
```

## Author
Kasireddy — National College of Ireland
