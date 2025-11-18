# Multi-Wizard Platform - Claude Code Guidelines

## Project Overview

This is a Multi-Wizard Platform that enables administrators to create, configure, and manage step-by-step wizards. Users can complete wizards, save progress, create templates, and replay sessions.

## Technology Stack

### Backend
- Python 3.11+ with FastAPI
- PostgreSQL 15+ (Database: `wizarddb`)
- SQLAlchemy 2.0 ORM
- Alembic for migrations
- JWT authentication with bcrypt password hashing
- Pydantic v2 for validation

### Frontend
- React 18+ with TypeScript
- Material-UI (MUI) v5
- React Router v6
- React Hook Form + Zod
- React Query for state management
- Axios for HTTP

## Project Structure

```
multi-wizard-platform/
├── backend/              # FastAPI backend (Port 8000)
│   ├── app/
│   │   ├── main.py       # Entry point
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # DB connection
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── api/v1/       # API routes
│   │   ├── crud/         # CRUD operations
│   │   ├── core/         # Security utilities
│   │   └── utils/        # Helper functions
│   ├── alembic/          # Migrations
│   └── tests/            # Backend tests
├── frontend/             # React frontend (Port 3000)
│   └── src/
│       ├── components/   # UI components
│       ├── pages/        # Page components
│       ├── contexts/     # React contexts
│       ├── hooks/        # Custom hooks
│       ├── services/     # API services
│       └── types/        # TypeScript types
└── docs/                 # Documentation
```

## Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: Use Prettier, strict typing
- **Naming**: Use descriptive names, snake_case for Python, camelCase for TypeScript
- **Comments**: Document complex logic, use docstrings for functions

### Database Conventions
- Table names: plural, lowercase, snake_case (e.g., `wizards`, `option_sets`)
- Primary keys: `id` as UUID
- Foreign keys: `<table_singular>_id` (e.g., `wizard_id`)
- Timestamps: Include `created_at`, `updated_at` on all tables
- Use soft deletes where appropriate (`is_active` flag)

### API Design
- RESTful endpoints: `/api/v1/<resource>`
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Return consistent JSON responses
- Include pagination for list endpoints
- Proper error handling with meaningful messages

### Security Requirements
- All passwords must be hashed with bcrypt
- Use JWT with expiration for authentication
- Implement role-based access control (Super Admin, Admin, User)
- Validate all inputs with Pydantic
- Use parameterized queries (SQLAlchemy handles this)
- Escape user content in frontend (React handles this)

### Testing
- Write unit tests for CRUD operations
- Integration tests for API endpoints
- Frontend component tests with React Testing Library
- Test coverage should be >80%

## Key Concepts

### Wizard Structure
```
Wizard
  └── Steps (ordered)
        └── Option Sets
              └── Options
                    └── Dependencies
```

### User Roles
1. **Super Admin**: Full system access, user management
2. **Admin**: Wizard management, limited analytics
3. **User**: Complete wizards, manage personal sessions/templates

### Session Flow
1. User starts wizard session
2. Navigates through steps
3. Makes selections in option sets
4. Saves progress (auto-save or manual)
5. Completes or abandons session
6. Optionally creates template from completed session

## Common Tasks

### Adding a New API Endpoint
1. Create Pydantic schema in `backend/app/schemas/`
2. Add CRUD operations in `backend/app/crud/`
3. Create route in `backend/app/api/v1/`
4. Register route in main router
5. Test endpoint

### Adding a New Frontend Page
1. Create page component in `frontend/src/pages/`
2. Add route in `App.tsx`
3. Create necessary hooks in `frontend/src/hooks/`
4. Add API service calls in `frontend/src/services/`
5. Define TypeScript types in `frontend/src/types/`

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/wizarddb
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Commands

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Format code
black app/
```

### Frontend
```bash
# Install dependencies
npm install

# Run development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Format code
npm run format
```

## Important Files

- [README.md](../README.md) - Project setup and getting started guide
- [unused/](../unused/) - Archived documentation and utility scripts

## Current Implementation Status

### Completed Features

#### All 12 Selection Types
The platform supports all 12 input selection types:
1. **single_select** - Radio buttons for single choice
2. **multiple_select** - Checkboxes for multiple choices
3. **text_input** - Multi-line text input
4. **number_input** - Numeric input with validation
5. **date_input** - Date picker
6. **time_input** - Time picker
7. **datetime_input** - Combined date and time picker
8. **rating** - Star rating component (1-5 stars)
9. **slider** - Range slider for numeric values
10. **color_picker** - Color selection
11. **file_upload** - File upload with validation
12. **rich_text** - Rich text editor for formatted content

#### Conditional Dependencies
Four dependency types are fully implemented:
- **disable_if**: Disables a field when specified option is selected
- **require_if**: Makes a field required when specified option is selected
- **show_if**: Shows a field only when specified option is selected
- **hide_if**: Hides a field when specified option is selected

#### Key Implementation Details
- Dependencies work at the **option set level** for input types
- Frontend checks dependencies in real-time using `isOptionSetDisabled()` function
- Session responses are stored in flexible JSONB format: `{ value: ... }`
- Session resume feature loads all saved responses and restores to last incomplete step
- MUI components (Rating, Slider) integrated for enhanced UX

### Key Files Modified

**Frontend:**
- `frontend/src/pages/WizardPlayerPage.tsx` - Main wizard player with all 12 selection types and dependency logic
- `frontend/src/pages/admin/WizardBuilderPage.tsx` - Wizard builder with all selection types in dropdown

**Backend:**
- `backend/app/schemas/wizard.py` - Validation regex for all 12 selection types
- `backend/app/api/v1/wizards.py` - Dependency endpoints

### Utility Scripts (in unused/)

All utility scripts have been moved to the `unused/` folder:
- `complete_database_reset.py` - Delete all wizards, sessions, and templates
- `reset_and_create_wizards.py` - Create test wizards with all 12 selection types
- `add_dependencies.py` - Add conditional dependencies to test wizards
- `check_dependencies.py` - Verify dependencies in database
- `verify_database.py` - Check database state vs frontend cache

### Known Issues & Solutions

**Frontend Caching**: React Query caches API responses. After database resets:
- Solution 1: Hard refresh browser (Ctrl + Shift + R)
- Solution 2: Use incognito window
- Solution 3: Clear browser cache completely
- Solution 4: Restart frontend server

## Performance Considerations

1. Use database indexes on foreign keys and frequently queried columns
2. Implement pagination on all list endpoints (default: 20 items)
3. Use React Query caching on frontend
4. Lazy load components with React.lazy()
5. Use connection pooling in SQLAlchemy
6. Prefer async/await for I/O operations

## Error Handling

### Backend
- Use HTTPException for API errors
- Log errors with proper levels (INFO, WARNING, ERROR)
- Return consistent error response format:
```json
{
  "detail": "Error message",
  "error_code": "ERROR_TYPE"
}
```

### Frontend
- Handle API errors in service layer
- Show user-friendly error messages
- Implement retry logic for network failures
- Use error boundaries for component errors

## Git Workflow

1. Create feature branches from `main`
2. Use conventional commits (feat:, fix:, docs:, etc.)
3. Write clear commit messages
4. Review code before merging
5. Keep commits atomic and focused
