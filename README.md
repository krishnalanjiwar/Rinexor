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
    - Computes risk/priority
    - Selects a DCA based on performance score, SLA breaches, and load

- DCA performance analytics
  - Per‑DCA metrics:
    - Active cases
    - Resolved cases
    - Recovered amount
    - Average resolution days
    - SLA breaches count

- Proof‑backed resolution
  - Marking a case as recovered or resolved requires:
    - `proof_type` (UTR, gateway_reference, settlement_letter, etc.)
    - `proof_reference` (transaction ID, document ID, etc.)

- Audit logging
  - Every important change is logged with:
    - Actor email and role
    - Case ID
    - Timestamp
    - Field‑level before/after details

---

## 2. Tech Stack

- Backend
  - Python 3.x
  - FastAPI
  - Uvicorn
  - python‑jose (JWT)
  - Pydantic models

- Frontend
  - React + TypeScript
  - Vite
  - Tailwind CSS (dark mode + animations)

---

## 3. Project Structure

```text
Rinexor/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  │  ├─ auth.py      # auth, demo users
│  │  │  └─ cases.py     # cases, DCA metrics, uploads
│  │  ├─ main.py         # FastAPI app, CORS
│  │  └─ ...
│  ├─ requirements.txt
│  └─ README.md
│
├─ frontend/
│  ├─ src/
│  │  ├─ app/            # config, auth, TS types, format helpers
│  │  ├─ pages/          # role dashboards and pages
│  │  ├─ components/     # reusable UI (cards, tables, badges)
│  │  └─ App.tsx         # router + layout
│  ├─ tailwind.config.js
│  ├─ package.json
│  └─ README.md
│
├─ docs/
├─ README.md             # this file
└─ LICENSE
```

---

## 4. Getting Started

### 4.1 Prerequisites

- Node.js (LTS)
- npm
- Python 3.10+

### 4.2 Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API URLs:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

### 4.3 Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Then open the Vite dev server URL printed in the terminal, typically:

- `http://localhost:5173`
or
- `http://localhost:5174`

---

## 5. Demo Users and Roles

Defined in `backend/app/api/auth.py`:

- Super Admin
  - Email: `admin@rinexor.com`
  - Password: `admin123`

- Enterprise Admin
  - Email: `enterprise@demo.com`
  - Password: `enterprise123`

- DCA User
  - Email: `dca@demo.com`
  - Password: `dca123`

---

## 6. Main Workflows

- Enterprise Admin
  - Upload cases (bulk demo or CSV)
  - Review AI scores, priorities, SLA risk
  - Reassign cases between DCAs
  - Monitor enterprise‑level and DCA performance

- DCA User
  - See assigned cases sorted by urgency and risk
  - Update status through the lifecycle (pending → in_progress → contacted → promised → recovered/resolved)
  - Provide proof type and reference when marking cases recovered/resolved

- Super Admin
  - View global KPIs (cases, DCAs, enterprises, recovery rate, SLA breaches)
  - Review DCA and enterprise performance
  - Inspect audit‑style activity feed

---

## 7. Development Notes

- All data (users, DCAs, cases, audit log) is in memory for demo purposes.
- The project is intended as a functional prototype and product concept, not a production deployment.
