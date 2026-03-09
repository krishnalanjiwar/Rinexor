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
Body: {
  "name": "New Collection Agency",
  "code": "NCA-001",
  "contact_person": "Jane Manager",
  "email": "contact@newagency.com"
}

// Get Specific DCA
GET /api/v1/dcas/{dca_id}

// Update DCA
PUT /api/v1/dcas/{dca_id}

// Get DCA Performance
GET /api/v1/dcas/{dca_id}/performance

// Get DCA Cases
GET /api/v1/dcas/{dca_id}/cases

// Recalculate Performance
POST /api/v1/dcas/{dca_id}/recalculate-performance
```

### **🧠 AI & Analytics**
```javascript
// Analyze Single Case
POST /api/v1/ai/analyze-case
Body: {
  "original_amount": 5000,
  "days_delinquent": 45,
  "debt_type": "credit_card"
}

// Analyze Portfolio
POST /api/v1/ai/analyze-portfolio
Body: { "case_ids": ["id1", "id2", "id3"] }

// Get Patterns
GET /api/v1/ai/patterns

// Get Model Status
GET /api/v1/ai/model-status

// Prioritize Cases
POST /api/v1/ai/prioritize-cases
Body: { "case_ids": ["id1", "id2"] }
```

### **📊 Reports & Analytics**
```javascript
// Dashboard Overview
GET /api/v1/reports/dashboard/overview

// DCA Performance Report
GET /api/v1/reports/performance/dcas?period_days=30&dca_id=123

// Recovery Trends
GET /api/v1/reports/recovery/trends?period_days=90&granularity=daily

// SLA Compliance
GET /api/v1/reports/sla/compliance?period_days=30

// Portfolio Analysis
GET /api/v1/reports/portfolio/analysis

// Export Cases
GET /api/v1/reports/export/cases?format=json&status=new&date_from=2024-01-01
```

### **👑 Admin Functions**
```javascript
// Get All Users
GET /api/v1/admin/users?skip=0&limit=100

// Create User
POST /api/v1/admin/users
Body: {
  "email": "newuser@company.com",
  "password": "password123",
  "full_name": "New User",
  "role": "collection_manager"
}

// Upload Cases CSV
POST /api/v1/admin/upload-cases
Body: FormData with file

// Get CSV Template
GET /api/v1/admin/upload-template

// System Statistics
GET /api/v1/admin/system-stats

// Check SLA Violations
POST /api/v1/admin/sla/check-violations
```

---

## 💻 **JavaScript Integration Examples**

### **🔐 Authentication Helper**
```javascript
class RinexorAPI {
  constructor(baseURL = 'http://localhost:8001/api/v1') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('rinexor_token');
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      localStorage.setItem('rinexor_token', this.token);
      return data;
    }
    throw new Error('Login failed');
  }

  async apiCall(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
  }
}

// Usage
const api = new RinexorAPI();
await api.login('admin@rinexor.com', 'secret');
const cases = await api.apiCall('/cases');
```

### **📋 Cases Management**
```javascript
// Get cases with filtering
const getCases = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  return api.apiCall(`/cases?${params}`);
};

// Create new case
const createCase = async (caseData) => {
  return api.apiCall('/cases', {
    method: 'POST',
    body: JSON.stringify(caseData)
  });
};

// Update case status
const updateCase = async (caseId, updates) => {
  return api.apiCall(`/cases/${caseId}`, {
    method: 'PUT',
    body: JSON.stringify(updates)
  });
};
```

### **📊 Dashboard Data**

