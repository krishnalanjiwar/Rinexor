/**
 * RINEXOR API Client - Complete JavaScript SDK
 * Use this to integrate with RINEXOR backend
 */

class RinexorAPI {
  constructor(baseURL = 'http://localhost:8001/api/v1') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('rinexor_token');
  }

  // Authentication
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

  async getCurrentUser() {
    return this.apiCall('/auth/me');
  }

  logout() {
    this.token = null;
    localStorage.removeItem('rinexor_token');
  }

  // Generic API call helper
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
      if (response.status === 401) {
        this.logout();
        throw new Error('Authentication required');
      }
      throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Cases Management
  async getCases(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.apiCall(`/cases?${params}`);
  }

  async getCase(caseId) {
    return this.apiCall(`/cases/${caseId}`);
  }

  async createCase(caseData) {
    return this.apiCall('/cases', {
      method: 'POST',
      body: JSON.stringify(caseData)
    });
  }

  async updateCase(caseId, updates) {
    return this.apiCall(`/cases/${caseId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async addCaseNote(caseId, noteData) {
    return this.apiCall(`/cases/${caseId}/notes`, {
      method: 'POST',
      body: JSON.stringify(noteData)
    });
  }

  async getCaseNotes(caseId) {
    return this.apiCall(`/cases/${caseId}/notes`);
  }

  async allocateCases(caseIds, dcaId) {
    return this.apiCall('/cases/allocate', {
      method: 'POST',
      body: JSON.stringify({ case_ids: caseIds, dca_id: dcaId })
    });
  }

  async getDashboardStats() {
    return this.apiCall('/cases/dashboard/stats');
  }

  // DCA Management
  async getDCAs(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.apiCall(`/dcas?${params}`);
  }

  async getDCA(dcaId) {
    return this.apiCall(`/dcas/${dcaId}`);
  }

  async createDCA(dcaData) {
    return this.apiCall('/dcas', {
      method: 'POST',
      body: JSON.stringify(dcaData)
    });
  }

  async updateDCA(dcaId, updates) {
    return this.apiCall(`/dcas/${dcaId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async getDCAPerformance(dcaId) {
    return this.apiCall(`/dcas/${dcaId}/performance`);
  }

  async getDCACases(dcaId) {
    return this.apiCall(`/dcas/${dcaId}/cases`);
  }

  // AI & Analytics
  async analyzeCase(caseData) {
    return this.apiCall('/ai/analyze-case', {
      method: 'POST',
      body: JSON.stringify(caseData)
    });
  }

  async analyzePortfolio(caseIds) {
    return this.apiCall('/ai/analyze-portfolio', {
      method: 'POST',
      body: JSON.stringify({ case_ids: caseIds })
    });
  }

  async getPatterns() {
    return this.apiCall('/ai/patterns');
  }

  async getModelStatus() {
    return this.apiCall('/ai/model-status');
  }

  // Reports
  async getDashboardOverview() {
    return this.apiCall('/reports/dashboard/overview');
  }

  async getDCAPerformanceReport(periodDays = 30, dcaId = null) {
    const params = new URLSearchParams({ period_days: periodDays });
    if (dcaId) params.append('dca_id', dcaId);
    return this.apiCall(`/reports/performance/dcas?${params}`);
  }

  async getRecoveryTrends(periodDays = 90, granularity = 'daily') {
    const params = new URLSearchParams({ period_days: periodDays, granularity });
    return this.apiCall(`/reports/recovery/trends?${params}`);
  }

  async getSLACompliance(periodDays = 30) {
    const params = new URLSearchParams({ period_days: periodDays });
    return this.apiCall(`/reports/sla/compliance?${params}`);
  }

  async getPortfolioAnalysis() {
    return this.apiCall('/reports/portfolio/analysis');
  }

  async exportCases(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.apiCall(`/reports/export/cases?${params}`);
  }

  // Admin Functions
  async getUsers(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.apiCall(`/admin/users?${params}`);
  }

  async createUser(userData) {
    return this.apiCall('/admin/users', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  async uploadCases(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseURL}/admin/upload-cases`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  async getUploadTemplate() {
    return this.apiCall('/admin/upload-template');
  }

  async getSystemStats() {
    return this.apiCall('/admin/system-stats');
  }
}

// Usage Examples:
/*
// Initialize API client
const api = new RinexorAPI();

// Login
await api.login('admin@rinexor.com', 'secret');

// Get dashboard data
const stats = await api.getDashboardStats();
const overview = await api.getDashboardOverview();

// Get cases
const cases = await api.getCases({ status: 'new', priority: 'high' });

// Create new case
const newCase = await api.createCase({
  account_id: 'ACC-001',
  debtor_name: 'John Doe',
  original_amount: 5000.00,
  days_delinquent: 45
});

// Upload CSV
const fileInput = document.getElementById('csvFile');
const result = await api.uploadCases(fileInput.files[0]);

// Get reports
const trends = await api.getRecoveryTrends(30, 'daily');
const compliance = await api.getSLACompliance(30);
*/

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = RinexorAPI;
}

// Global access for browser
if (typeof window !== 'undefined') {
  window.RinexorAPI = RinexorAPI;
}