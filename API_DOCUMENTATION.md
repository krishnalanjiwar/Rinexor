# Rinexor - API Documentation

## Quick Start
- Backend: http://localhost:9000
- API Docs: http://localhost:9000/api/docs

## How to Use
1. Login: POST /api/v1/auth/login
   Body: username=admin@rinexor.com&password=secret

2. Get token from response

3. Use token in all other requests:
   Header: Authorization: Bearer YOUR_TOKEN

## Test Users
- Admin: admin@rinexor.com / secret
- DCA Agent: agent@alphacollections.com / secret

## 🚀 NEW: Complete API Endpoints

### Authentication
- POST /api/v1/auth/login - User login
- GET /api/v1/auth/me - Current user info

### Cases Management
- GET /api/v1/cases - List cases (with filtering)
- POST /api/v1/cases - Create new case (with AI processing)
- GET /api/v1/cases/{case_id} - Get specific case
- PUT /api/v1/cases/{case_id} - Update case
- POST /api/v1/cases/{case_id}/notes - Add case notes
- GET /api/v1/cases/{case_id}/notes - Get case notes
- POST /api/v1/cases/allocate - Bulk allocate cases to DCAs
- GET /api/v1/cases/dashboard/stats - Dashboard statistics

### DCA Management
- GET /api/v1/dcas - List all DCAs

