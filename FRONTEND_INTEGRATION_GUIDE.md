# 🚀 RINEXOR Frontend Integration Guide

## 📡 **Backend API Information**

### **🔗 Base URLs**
- **Development**: `http://localhost:8001`
- **API Base**: `http://localhost:8001/api/v1`
- **API Docs**: `http://localhost:8001/api/docs`

### **🔐 Authentication**
- **Method**: JWT Bearer Token
- **Login Endpoint**: `POST /api/v1/auth/login`
- **Header Format**: `Authorization: Bearer YOUR_JWT_TOKEN`

### **👤 Test Credentials**
```javascript
// Admin User
{
  "username": "admin@rinexor.com",
  "password": "secret"
}

// DCA Agent
{
  "username": "agent@alphacollections.com", 
  "password": "secret"
}
```

---

## 🔌 **Complete API Endpoints**

### **🔐 Authentication**
```javascript
// Login
POST /api/v1/auth/login
Body: { "username": "admin@rinexor.com", "password": "secret" }
Response: { "access_token": "...", "token_type": "bearer", "expires_in": 1800 }

// Get Current User
GET /api/v1/auth/me
Headers: { "Authorization": "Bearer YOUR_TOKEN" }
```

### **📋 Cases Management**
```javascript
// Get All Cases (with filtering)
GET /api/v1/cases?status=new&priority=high&dca_id=123&skip=0&limit=20

// Create New Case
POST /api/v1/cases
Body: {
  "account_id": "ACC-001",
  "debtor_name": "John Doe",
  "debtor_email": "john@email.com",
  "original_amount": 5000.00,
  "days_delinquent": 45,
  "debt_age_days": 45
}

// Get Specific Case
GET /api/v1/cases/{case_id}

// Update Case
PUT /api/v1/cases/{case_id}
Body: { "status": "in_progress", "current_amount": 4500.00 }

// Add Case Note
POST /api/v1/cases/{case_id}/notes
Body: { "content": "Contacted debtor", "note_type": "contact" }

// Get Case Notes
GET /api/v1/cases/{case_id}/notes

// Bulk Allocate Cases
POST /api/v1/cases/allocate
Body: { "case_ids": ["id1", "id2"], "dca_id": "dca123" }

// Dashboard Statistics
GET /api/v1/cases/dashboard/stats
```

### **🏢 DCA Management**
```javascript
// Get All DCAs
GET /api/v1/dcas?active_only=true&skip=0&limit=100

// Create New DCA
POST /api/v1/dcas

