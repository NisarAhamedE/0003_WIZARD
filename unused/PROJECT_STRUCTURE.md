# Multi-Wizard Platform - Project Structure

## Overview
This document provides an overview of the project structure, active documentation, and archived files.

---

## Active Documentation (Root Directory)

### Essential Documentation

1. **[README.md](README.md)**
   - Project overview and setup guide
   - Getting started instructions
   - Development commands
   - Database setup
   - Environment configuration

2. **[WIZARD_BUILDER_DOCUMENTATION.md](WIZARD_BUILDER_DOCUMENTATION.md)** ⭐ NEW
   - Comprehensive Wizard Builder guide
   - All 12 selection types documentation
   - Conditional dependencies system
   - Architecture and implementation details
   - Usage examples and best practices
   - 790+ lines of detailed documentation

3. **[WIZARD_MANAGEMENT_FEATURES.md](WIZARD_MANAGEMENT_FEATURES.md)**
   - Wizard management feature overview
   - Session tracking and analytics
   - Template system documentation
   - User workflows

---

## Project Directories

### Backend (`/backend`)
```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── wizard.py
│   │   ├── session.py
│   │   └── template.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── wizard.py
│   │   ├── session.py
│   │   └── template.py
│   ├── api/v1/              # API routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── wizards.py
│   │   ├── sessions.py
│   │   ├── templates.py
│   │   ├── analytics.py
│   │   └── uploads.py
│   ├── crud/                # CRUD operations
│   ├── core/                # Security utilities
│   └── utils/               # Helper functions
├── alembic/                 # Database migrations
└── tests/                   # Backend tests
```

### Frontend (`/frontend`)
```
frontend/
└── src/
    ├── components/          # Reusable UI components
    │   ├── common/          # Common components
    │   └── OptionDependencyManager.tsx  # Dependency manager
    ├── pages/               # Page components
    │   ├── admin/
    │   │   ├── WizardBuilderPage.tsx    # 1,103 lines ⭐
    │   │   ├── UserManagementPage.tsx
    │   │   └── AnalyticsPage.tsx
    │   ├── WizardPlayerPage.tsx         # Wizard execution
    │   ├── SessionsPage.tsx              # Session management
    │   ├── TemplatesPage.tsx             # Template management
    │   ├── LoginPage.tsx
    │   └── DashboardPage.tsx
    ├── contexts/            # React contexts
    │   └── AuthContext.tsx
    ├── hooks/               # Custom hooks
    ├── services/            # API services
    │   ├── api.ts           # Axios configuration
    │   ├── auth.service.ts
    │   ├── wizard.service.ts
    │   ├── session.service.ts
    │   └── template.service.ts
    └── types/               # TypeScript types
        ├── user.types.ts
        ├── wizard.types.ts
        ├── session.types.ts
        └── template.types.ts
```

---

## Archived Files (`/unused`)

The `unused/` folder contains historical documentation, test scripts, and utility files that are no longer actively used but kept for reference.

### Documentation Archives
- `01_SYSTEM_OVERVIEW.md` - Original system overview
- `02_DATABASE_SCHEMA.md` - Initial database schema docs
- `03_SAMPLE_DATA.md` - Sample data documentation
- `COMPLETE_FEATURES_SUMMARY.md` - Old feature summary
- `DATABASE_EMPTY_CONFIRMED.md` - Database reset confirmation
- `SESSION_COMPLETION_FIX.md` - Session completion fix notes
- `SESSIONS_PAGE_FIXES.md` - Sessions page fix documentation
- `WIZARD_UPDATE_FIX.md` - Wizard update fix notes
- Various implementation guides and summaries (20+ files)

### Utility Scripts
- `add_dependencies.py` - Add test dependencies
- `check_dependencies.py` - Verify dependencies
- `check_empty_db.py` - Check database state
- `complete_database_reset.py` - Reset database
- `reset_and_create_wizards.py` - Create test wizards
- `verify_database.py` - Database verification
- `create_sample_wizards.py` - Sample wizard creation
- `create_test_wizard_all_types.py` - Test all selection types
- `delete_all_wizards_direct.py` - Bulk delete wizards
- Various test and debug scripts (15+ files)

### Debug & Test Scripts
- `inspect_sessions.py` - Session inspection
- `reproduce_completion.py` - Completion issue reproduction
- `reproduce_issue.py` - General issue reproduction
- `test_completion_race.py` - Race condition testing
- `test_add_dependency.py` - Dependency testing
- `test_ui_dependency_save.py` - UI dependency save testing

**Total Archived Files**: 45+ files

---

## Startup Scripts

### Windows Batch Files

1. **`start_servers.bat`** ⭐ PRIMARY
   - Starts both backend and frontend servers
   - Opens separate console windows
   - Displays server URLs and credentials

2. **`stop_servers.bat`**
   - Stops all running servers
   - Kills processes on ports 8000 and 3000

3. **`restart_servers.bat`**
   - Stops then starts servers
   - Clean restart

### Usage
```bash
# Start everything
start_servers.bat

# Stop everything
stop_servers.bat

# Restart everything
restart_servers.bat
```

---

## Key Files by Category

### Configuration Files

**Root Level:**
- `.env` - Environment variables
- `.gitignore` - Git ignore rules
- `package.json` - Project metadata (if applicable)

**Backend:**
- `backend/requirements.txt` - Python dependencies
- `backend/alembic.ini` - Alembic configuration
- `backend/.env` - Backend environment variables

**Frontend:**
- `frontend/package.json` - NPM dependencies
- `frontend/vite.config.ts` - Vite configuration
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/.env` - Frontend environment variables

---

## Database Information

**Database**: PostgreSQL 15+
**Database Name**: `wizarddb`
**Connection String**: `postgresql://user:password@localhost:5432/wizarddb`

### Key Tables
- `users` - User accounts
- `roles` - User roles (User, Admin, Super Admin)
- `wizards` - Wizard definitions
- `wizard_categories` - Wizard categories
- `steps` - Wizard steps
- `option_sets` - Input fields/questions
- `options` - Available choices
- `option_dependencies` - Conditional logic
- `user_sessions` - User wizard sessions
- `session_responses` - User answers
- `templates` - Saved templates

---

## Server Information

### Backend (FastAPI)
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Port**: 8000

### Frontend (Vite + React)
- **URL**: http://localhost:3001 (or 3000 if available)
- **Port**: 3001 (auto-increments if 3000 is busy)

### Default Admin Credentials
- **Username**: `admin`
- **Password**: `Admin@123`

---

## Development Commands

### Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Format code
black app/

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Format code
npm run format
```

---

## Recent Fixes Applied

### Session Creation Fix (Nov 19, 2025)
1. **Removed login requirement** - Sessions now work without strict authentication
2. **Fixed metadata serialization** - Added `serialization_alias="metadata"` to schema
3. **Fixed CORS redirect** - Added trailing slash to `/sessions/` endpoint
4. **Improved error messages** - Show actual backend errors in UI

**Files Modified:**
- `backend/app/api/v1/sessions.py`
- `backend/app/schemas/session.py`
- `frontend/src/services/session.service.ts`
- `frontend/src/pages/SessionsPage.tsx`
- `frontend/src/services/api.ts`

---

## Documentation Hierarchy

### For New Developers
1. Start with [README.md](README.md)
2. Read [WIZARD_BUILDER_DOCUMENTATION.md](WIZARD_BUILDER_DOCUMENTATION.md)
3. Review [WIZARD_MANAGEMENT_FEATURES.md](WIZARD_MANAGEMENT_FEATURES.md)

### For Users
1. Admin credentials from `start_servers.bat` output
2. Wizard Builder guide in WIZARD_BUILDER_DOCUMENTATION.md

### For Troubleshooting
1. Check archived fixes in `unused/` folder
2. Review git commit history
3. Check backend logs in terminal

---

## File Counts

- **Root Directory**: 3 markdown files (active documentation)
- **Unused Directory**: 45+ archived files
- **Backend Python Files**: 50+ files
- **Frontend TypeScript Files**: 60+ files
- **Total Project Files**: 200+ files

---

## Maintenance Notes

### Regular Tasks
- Keep unused folder for historical reference
- Update this document when major changes occur
- Archive old documentation when superseded
- Maintain clean root directory with only active docs

### Archive Policy
Files moved to `unused/` when:
- Superseded by newer documentation
- Feature has been completed and stable
- Debug/test scripts no longer needed
- Historical reference value only

---

**Last Updated**: November 19, 2025
**Project Status**: Active Development
**Current Version**: 1.0.0
