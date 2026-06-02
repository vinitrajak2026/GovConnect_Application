# GovConnect

GovConnect is a Django REST Framework based citizen service platform that centralizes Government Schemes, Jobs, Exams, Scholarships, Results, Notifications, and Community Discussions in a single system.

The platform includes a recommendation engine that suggests relevant government schemes based on user demographics such as age, income, occupation, qualification, gender, and state.

## Features

- JWT Authentication
- Citizen Registration
- Government Jobs Portal
- Competitive Exams Management
- Scholarship Listings
- Welfare Scheme Management
- Results & Notifications
- Community Forum
- User Activity Logging
- Personalized Recommendation Engine
- REST API Support
- Docker Deployment

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite/PostgreSQL
- JWT Authentication
- Docker
- WhiteNoise

## Recommendation Engine

The recommendation engine evaluates:

- Age
- Gender
- Income
- Occupation
- Qualification
- State

and suggests eligible government schemes with higher relevance scores.

## API Endpoints

- /api/auth/register/
- /api/auth/token/
- /api/auth/token/refresh/
- /api/exams/
- /api/jobs/
- /api/schemes/
- /api/scholarships/
- /api/results/
- /api/notifications/
- /api/forum/

## Installation

```bash
git clone <repository-url>
cd govconnect

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
