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

// TODO: refactor logic here
