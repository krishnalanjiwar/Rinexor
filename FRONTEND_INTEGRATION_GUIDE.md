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

