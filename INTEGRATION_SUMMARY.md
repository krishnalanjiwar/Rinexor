# Frontend-Backend Integration Summary

## Overview
This document outlines all the changes made to link the Rinexor frontend with the backend API without modifying the UI.

---

## 1. API Client Service Layer

### File Created: `src/services/apiClient.ts`

A comprehensive TypeScript API client that handles all communication with the backend:

**Key Features:**
- Centralized API configuration with base URL support
- Bearer token authentication management
- Error handling with proper authentication failures
- Request/response typing for all endpoints
- Support for file uploads (CSV cases)

**Implemented Endpoints:**
- **Authentication**
  - `login(credentials)` - User login with email/password
  - `logout()` - Clear authentication

- **Cases Management**
  - `getCases(params?)` - Fetch cases with optional filters
  - `getCase(caseId)` - Fetch single case details
  - `updateCase(caseId, updates)` - Update case status, remarks, etc.

- **KPIs & Analytics**
  - `getKPIs()` - Fetch dashboard KPIs
  - `getDCAs()` - List all registered DCAs
  - `getEnterprises()` - List enterprises (super admin only)

- **Audit & Logging**
  - `getAuditEvents(params?)` - Fetch audit trail

- **File Operations**
  - `uploadCases()` - Bulk case upload
  - `uploadCasesCSV(file)` - CSV case import

---

## 2. Authentication Context Updates

### File Modified: `src/context/AuthContext.tsx`

**Changes Made:**
- Added `loginWithCredentials(email, password)` async method that calls backend login API
- Enhanced `User` interface with `enterprise_id` and `dca_id` fields
- Added `isLoading` and `error` state management
- Integrated token persistence with backend tokens
- Support for `dca_user` role (maps to `dca_agent` in UI)
- Demo credentials mapping for backend validation:
  - `admin@rinexor.com` → Super Admin (admin123)
  - `enterprise@demo.com` → Enterprise Admin (enterprise123)
  - `dca@demo.com` → DCA User (dca123)

---

## 3. Login Page Integration

### File Modified: `src/pages/auth/Login.tsx`

**Changes Made:**
- Updated to use `loginWithCredentials()` for actual backend authentication
- Pre-filled demo credentials matching backend DEMO_USERS
- Async form submission with proper error handling
- Loading state feedback during authentication
- Error messages from backend API

**Demo Credentials:**
```
Super Admin: admin@rinexor.com / admin123
Enterprise Admin: enterprise@demo.com / enterprise123
DCA User: dca@demo.com / dca123
```

---

## 4. Cases Dashboard Integration

### File Modified: `src/pages/dashboard/Cases.tsx`

**Changes Made:**
- Integrated `apiClient.getCases()` to fetch real case data
- Converted API case objects to frontend CaseRow format
- Added SLA deadline calculation (automatically computes days left)
- Status mapping: API statuses → Frontend UI labels
- Loading state with spinner
- Error state with retry button
- Real-time case data from backend:
  - Borrower information
  - Case amounts and priorities
  - SLA deadlines
  - Assignment details
  - Case status

**Data Transformation:**
- API priority → UI priority bands (High/Medium/Low)
- SLA deadline → SLA display (e.g., "2 Days Left", "Overdue")
- API status → Readable status (pending → Active, etc.)

---

## 5. Overview Dashboard Integration

### File Modified: `src/pages/dashboard/Overview.tsx`

**Changes Made:**
- Fetch KPI data from `apiClient.getKPIs()`
- Fetch DCA list from `apiClient.getDCAs()` for top agencies
- Real-time KPI cards showing:
  - Total cases count
  - Active case count
  - Recovery rate percentage
  - SLA breach count
- Dynamic top performing agencies list from backend DCA data
- Loading states for both KPIs and agency list

**Real-time Metrics:**
- Total outstanding amount (calculated from case data)
- Active cases from backend
- Recovery rate from DCA performance scores
- SLA breaches from DCA data

---

## 6. Agencies (DCA) List Integration

### File Modified: `src/pages/dashboard/Agencies.tsx`

**Changes Made:**
- Integrated `apiClient.getDCAs()` for super admin view
- Convert DCA objects to agency table format:
  - Performance score → Recovery Rate %
  - SLA breach data → SLA Compliance %
  - Active + resolved cases → Total cases
  - Average resolution days → Avg Resolution Time
- Loading state with spinner
- Error handling with retry
- Role-based DCA filtering (enterprise admin sees only assigned DCAs)

**Backend Data Mapping:**
- `dca.performance_score` → Recovery Rate
- `dca.sla_breaches` → SLA Compliance calculation
- `dca.active_cases + dca.resolved_cases` → Total cases
- `dca.average_resolution_days` → Resolution time

---

## 7. Role-Based Access Control

The frontend now respects backend authentication and role-based permissions:

**Super Admin:**
- Can view all cases across enterprises
- Can view all DCAs and their performance
- Can view all enterprises

**Enterprise Admin:**
- Can view cases only for their enterprise
- Can view DCA agencies assigned to them
- Can manage team members (employees)

**DCA User:**
- Can view only their assigned cases
- Can update case status and add remarks
- Can upload proof of resolution

---

## 8. Error Handling & Loading States

All dashboard pages now feature:
- Centralized error messages from API
- Retry buttons for failed requests
- Loading spinners during data fetch
- Graceful fallbacks for missing data

---

## 9. Backend Endpoints Used

The frontend connects to these backend endpoints:

```
POST   /api/auth/login                    → Login user
GET    /api/cases                         → List cases
GET    /api/cases/{case_id}               → Get single case
PUT    /api/cases/{case_id}               → Update case
GET    /api/dashboard/kpi                 → Get KPI metrics
GET    /api/dcas                          → List all DCAs
GET    /api/dashboard/enterprises         → List enterprises
GET    /api/audit                         → Get audit events
POST   /api/cases/upload                  → Bulk upload cases
POST   /api/cases/upload-csv              → CSV upload
```

---

## 10. Authentication Flow

1. User selects role on RoleSelection page
2. User navigates to Login page with role parameter
3. Pre-filled credentials appear (demo mode)
4. User submits credentials
5. Frontend calls `apiClient.login(email, password)`
6. Backend validates and returns JWT token
7. Frontend stores token in localStorage
8. User is redirected to dashboard
9. All subsequent requests include Bearer token in Authorization header
10. Token is automatically cleared on logout or auth failure

---

## 11. Token Management

- **Storage:** localStorage under `rinexor_token` key
- **Transmission:** `Authorization: Bearer {token}` header
- **Expiry:** 30 minutes (backend configured)
- **Refresh:** Auto-logout on 401 Unauthorized response

---

## 12. Data Flow Example

### Cases Page Load
```
1. Component mounts
2. useEffect calls apiClient.getCases()
3. API request sent with Bearer token
4. Backend validates token and filters by user role
5. Cases data returned in JSON
6. Frontend converts API objects to CaseRow format
7. Cases rendered in table with real data
8. User can interact with real case data
```

---

## 13. No UI Changes

✅ All visual changes are **zero** - the UI remains identical
✅ Only the data source changed (mock data → API calls)
✅ Same component structure, styling, and layout
✅ Same functionality, now backed by real backend

---

## 14. Environment Configuration

The API base URL can be configured via:
- Environment variable: `VITE_API_URL`
- Default: `http://localhost:8000/api`

**For production:**
```typescript
// Create .env file or set environment variable
VITE_API_URL=https://api.rinexor.com/api
```

---

## 15. Testing the Integration

### Prerequisites
1. Backend running on `http://localhost:8000`
2. CORS enabled (already configured in backend)
3. Frontend running on `http://localhost:5173`

### Test Flow
1. Start backend: `python -m uvicorn app.main:run --reload --port 8000`
2. Start frontend: `npm run dev`
3. Navigate to login page
4. Select role (Super Admin, Enterprise Admin, or DCA User)
5. Use pre-filled demo credentials
6. Dashboard loads with real data from backend
7. All tables and charts show live data from API

---

## Summary of Files Modified

1. ✅ **Created:** `src/services/apiClient.ts` - API client layer
2. ✅ **Modified:** `src/context/AuthContext.tsx` - Backend authentication
3. ✅ **Modified:** `src/pages/auth/Login.tsx` - Real login flow
4. ✅ **Modified:** `src/pages/dashboard/Cases.tsx` - Real case data
5. ✅ **Modified:** `src/pages/dashboard/Overview.tsx` - Real KPI data
6. ✅ **Modified:** `src/pages/dashboard/Agencies.tsx` - Real DCA data

---

## Next Steps (Optional Enhancements)

1. **WebSocket Integration** - Real-time case updates
2. **Pagination** - Backend cursor-based pagination
3. **Filtering** - Complex filter combinations
4. **Search** - Full-text case search
5. **Caching** - React Query for optimized caching
6. **Refresh Token** - Implement token refresh mechanism
7. **Error Boundary** - Global error handling component
8. **Analytics** - Track user interactions
