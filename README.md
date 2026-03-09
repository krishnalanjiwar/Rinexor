# Rinexor – AI-Powered DCA Management Platform

Rinexor is a demo web application for managing third‑party debt collection agencies (DCAs).  
It helps lenders and enterprises:

- Onboard DCAs and monitor their performance
- Ingest borrower cases (bulk and CSV)
- Automatically rank and route cases to the best‑suited DCA
- Track DCA execution, recovered amounts, and SLA risk
- Enforce basic governance with audit trails and proof for resolved cases

This repository contains:

- A FastAPI backend (`backend/`) exposing REST APIs
- A React + TypeScript + Vite + Tailwind CSS frontend (`frontend/`) consuming those APIs

---

## 1. Features Overview

- Role‑based access
  - Super Admin, Enterprise Admin, DCA User
  - JWT authentication with role attached to each token

- Cases and AI‑style risk scoring
  - Each case includes borrower info, amount, SLA deadline, AI score, priority
  - Priority is computed from amount + overdue days

- Automatic DCA assignment
  - When cases are created (bulk or CSV), the backend:

