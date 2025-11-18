# Multi-Wizard Platform

A comprehensive platform for creating, configuring, and managing step-by-step wizards. Users can complete wizards, save their progress, create templates, and replay previous sessions.

## Features

- **Wizard Management** - Create, edit, and publish multi-step wizards
- **Session Tracking** - Save progress and resume wizard sessions anytime
- **Template System** - Save and reuse wizard configurations
- **Role-Based Access** - Super Admin, Admin, and User roles
- **Analytics** - Track completion rates and user engagement
- **Modern UI** - Material-UI based responsive interface

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL 15+
- SQLAlchemy 2.0
- JWT Authentication
- Pydantic v2

### Frontend
- React 18+ with TypeScript
- Vite
- Material-UI v5
- React Router v6
- React Query
- Axios

## Quick Start

### Prerequisites

1. **Python 3.11+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)

### Database Setup

1. Create the database:
```sql
CREATE DATABASE wizards;
```

2. Update `.env` file in the root directory with your database credentials:
```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=wizards
DB_USER=postgres
DB_PASSWORD=your_password
DATABASE_URL=postgresql://postgres:your_password@127.0.0.1:5432/wizards
```

3. Run the schema SQL script:
```bash
psql -U postgres -d wizards -f backend/schema.sql
```

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Seed the database:
```bash
python seed_data.py
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

### Default Admin Credentials

After seeding the database:
- **Username:** admin
- **Password:** Admin@123

## Project Structure

```
multi-wizard-platform/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Security utilities
│   │   ├── crud/            # Database operations
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   └── main.py          # FastAPI entry point
│   ├── schema.sql           # Database schema
│   ├── seed_data.py         # Sample data script
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── hooks/           # Custom hooks
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── types/           # TypeScript types
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
├── .claude/
│   └── CLAUDE.md            # Development guidelines
├── docs/                    # Documentation
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (get JWT token)
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/change-password` - Change password

### Wizards
- `GET /api/v1/wizards` - List wizards
- `POST /api/v1/wizards` - Create wizard (Admin)
- `GET /api/v1/wizards/{id}` - Get wizard details
- `PUT /api/v1/wizards/{id}` - Update wizard (Admin)
- `DELETE /api/v1/wizards/{id}` - Delete wizard (Admin)

### Sessions
- `POST /api/v1/sessions` - Start new session
- `GET /api/v1/sessions` - List user sessions
- `GET /api/v1/sessions/{id}` - Get session details
- `POST /api/v1/sessions/{id}/responses` - Save response
- `PUT /api/v1/sessions/{id}/complete` - Complete session

### Templates
- `GET /api/v1/templates` - List templates
- `POST /api/v1/templates/from-session/{id}` - Create from session
- `POST /api/v1/templates/{id}/replay` - Replay template

## Development

### Code Quality

Backend:
```bash
# Format code
black app/

# Check linting
flake8 app/
```

Frontend:
```bash
# Format code
npm run format

# Type checking
npm run lint
```

### Testing

Backend:
```bash
pytest
```

Frontend:
```bash
npm test
```

## Implementation Status

### Completed
- [x] Database schema with 16 tables
- [x] Backend FastAPI application structure
- [x] SQLAlchemy models for all entities
- [x] Authentication (JWT) and authorization (RBAC)
- [x] CRUD operations for all models
- [x] API endpoints for auth, users, wizards, sessions, templates
- [x] Frontend React application with TypeScript
- [x] Authentication context and protected routes
- [x] API services with axios
- [x] Basic page components (Login, Register, Dashboard, etc.)
- [x] Seed data script

### In Progress / To Do
- [ ] Full Wizard Player component with step navigation
- [ ] Option set rendering (radio, checkbox, text, date, etc.)
- [ ] Auto-save functionality
- [ ] Admin dashboard and wizard builder
- [ ] Analytics dashboard
- [ ] Comprehensive testing
- [ ] Production deployment configuration

## Documentation

- [System Overview](01_SYSTEM_OVERVIEW.md) - Complete system architecture
- [Database Schema](02_DATABASE_SCHEMA.md) - PostgreSQL schema details
- [Sample Data](03_SAMPLE_DATA.md) - Test data for development
- [Implementation Plan](wizard_app_implementation_plan.md) - Step-by-step roadmap
- [Development Guidelines](.claude/CLAUDE.md) - Code conventions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

This project is proprietary. All rights reserved.

## Support

For issues and feature requests, please create an issue in the project repository.
