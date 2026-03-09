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
// TODO: refactor logic here
