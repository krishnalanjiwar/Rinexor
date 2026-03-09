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
- POST /api/v1/dcas - Create new DCA
- GET /api/v1/dcas/{dca_id} - Get specific DCA
- PUT /api/v1/dcas/{dca_id} - Update DCA
- GET /api/v1/dcas/{dca_id}/performance - DCA performance metrics
- GET /api/v1/dcas/{dca_id}/cases - Cases assigned to DCA
- POST /api/v1/dcas/{dca_id}/recalculate-performance - Recalculate performance

### AI & Analytics
- POST /api/v1/ai/analyze-case - Single case AI analysis
- POST /api/v1/ai/analyze-portfolio - Portfolio-level analysis
- GET /api/v1/ai/patterns - Pattern detection
- POST /api/v1/ai/train-model - Train AI model
- GET /api/v1/ai/model-status - Model status
- POST /api/v1/ai/prioritize-cases - Batch case prioritization

### 📊 NEW: Reports & Analytics
- GET /api/v1/reports/dashboard/overview - High-level dashboard stats
- GET /api/v1/reports/performance/dcas - DCA performance report
- GET /api/v1/reports/recovery/trends - Recovery trends over time
- GET /api/v1/reports/sla/compliance - SLA compliance report
- GET /api/v1/reports/portfolio/analysis - Portfolio analysis
- GET /api/v1/reports/export/cases - Export cases (JSON/CSV)

### Admin Functions
- GET /api/v1/admin/users - List all users
- POST /api/v1/admin/users - Create user
- PUT /api/v1/admin/users/{user_id}/deactivate - Deactivate user
- POST /api/v1/admin/sla/check-violations - Check SLA breaches
- GET /api/v1/admin/system-stats - System statistics
- POST /api/v1/admin/recalculate-metrics - Recalculate metrics
- **POST /api/v1/admin/upload-cases** - 📁 **Bulk upload cases from CSV**
- **GET /api/v1/admin/upload-template** - 📋 **Get CSV template and instructions**

## 🔧 Backend Services Now Include:

### WorkflowService
- Automated case processing and state management
- SLA deadline calculation
- Case priority assignment
- Status transition validation

### AllocationService  
- Intelligent DCA allocation based on:
  - Capacity availability
  - Performance scores
  - Specialization matching
  - Current workload
- Bulk allocation strategies
- Allocation recommendations

### NotificationService
- SLA breach alerts
- Case allocation notifications
- Status update notifications
- Daily summary reports
- Performance alerts

### SLA Monitoring
- Automated breach detection
- Case escalation
- Compliance tracking
- Background task scheduling

## 🎯 Key Features:
- ✅ Complete case workflow automation
- ✅ AI-powered recovery scoring
- ✅ Intelligent DCA allocation
- ✅ Real-time SLA monitoring
- ✅ Comprehensive reporting
- ✅ Role-based access control
- ✅ Full audit trails
- ✅ **CSV Bulk Upload** - Enterprise admins can upload cases from CSV files
- ✅ **Template Generation** - Download CSV templates with sample data

## Need Help?
Check live docs: http://localhost:9000/api/docs