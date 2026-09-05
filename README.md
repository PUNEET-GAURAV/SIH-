# DocShield AI — Offline AI-Assisted Document Screening & Forensics

[![Build & Tests](https://img.shields.io/badge/pytest-66%20passed-emerald)](./tests)
[![Offline First](https://img.shields.io/badge/Architecture-Offline--First-cyan)](./docs)
[![Docker](https://img.shields.io/badge/Deployment-Docker%20Compose-blue)](./docker-compose.yml)

DocShield AI is an offline-capable, AI-assisted document screening system designed for SIH26188. It combines classical computer vision quality gates, OCR & ICAO 9303 MRZ check digits, template structural alignment, localized SIFT/ORB copy-move & EfficientNet-B0 CNN manipulation forensics, and ArcFace facial consistency + PAD into an explainable evidence report for authorized border/customs officers.

---

## 🚀 Key Features & Capabilities

- **Classical CV Quality Gate**: Real-time OpenCV analysis for motion blur (Laplacian variance), specular glare, boundary corner detection, and homography perspective correction.
- **ICAO 9303 MRZ Engine**: Pure Python, zero-ML check digit validation (7-3-1 weight cycles) for TD1, TD2, and TD3 documents with MRZ↔VIZ date of birth and document number cross-consistency checks.
- **Document Classification & Structural Conformity**: Heuristic aspect ratio and MRZ line detection supporting TD3 passports, TD1 ID cards, and `UNKNOWN_DOCUMENT_MODE` for un-registered document types.
- **Multi-Detector Forensics**: SIFT/ORB feature matching with RANSAC affine verification for copy-move forgery, alongside a localized patch EfficientNet-B0 manipulation CNN.
- **Biometric Identity & PAD**: InsightFace (RetinaFace + ArcFace) cosine similarity comparison with Presentation Attack Detection (screen moiré, print photo, replay attack).
- **Explainable Evidence Fusion Engine**: Rule-based Engine aggregating findings into 4 key dimensions:
  1. *Document Consistency*
  2. *Structural Conformity*
  3. *Manipulation Evidence*
  4. *Identity Consistency*
  Outputs overall **Concern Level** (`LOW CONCERN` | `REVIEW REQUIRED` | `HIGH CONCERN`) and **Recommendation** (`CLEAR` | `REQUEST RECAPTURE` | `SECONDARY INSPECTION` | `ESCALATE`).
- **Tamper-Evident Audit Trail**: Cryptographic SHA-256 hash-chained audit log with an interactive API verification endpoint (`GET /audit/{session_id}/verify`).
- **Explainable Officer Workbench**: React + TypeScript + Tailwind UI featuring a 3-pane layout, 7 detailed evidence tabs, document canvas overlays, and officer decision action submitter.
- **6 Deterministic Demo Scenarios**: Built-in 1-click test scenarios (`genuine`, `altered_dob`, `expired`, `wrong_face`, `poor_capture`, `unknown_document`).

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, Lucide Icons |
| **Backend** | FastAPI, Pydantic, SQLAlchemy, Uvicorn |
| **CV & AI** | OpenCV, scikit-image, PyTorch, PaddleOCR, InsightFace / ArcFace |
| **Database** | PostgreSQL (Production) / SQLite (Development & Tests) |
| **Deployment** | Docker, Docker Compose, Nginx |

---

## 📦 Quick Start & Running Locally

### Option A: Local Python & Vite Environment

1. **Activate Virtual Environment & Run Backend**:
   ```powershell
   .\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
   ```

2. **Run Frontend Development Server**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Workbench**: Navigate to `http://localhost:3000` (or `http://localhost:8000/docs` for OpenAPI interactive documentation).

---

### Option B: Docker Compose (Full Stack Deployment)

```bash
docker-compose up --build
```
This brings up:
- **PostgreSQL**: Port 5432
- **FastAPI Backend**: Port 8000
- **Frontend Workbench**: Port 3000

---

## 🧪 Test Suite Execution

Run the complete automated test suite (66 tests covering MRZ checksums, fusion engine rules, API endpoints, and all 6 demo scenarios):

```powershell
.\venv\Scripts\python.exe -m pytest
```

---

## 📜 6 Deterministic Demo Scenarios

| Scenario ID | Primary Signal / Trigger | Expected Concern | Recommendation |
|---|---|---|---|
| `genuine` | Check digits pass, MRZ=VIZ, low forensics, face match | **LOW CONCERN** | CLEAR |
| `altered_dob` | MRZ DOB (1988-05-12) != VIZ DOB (1995-05-12) + Copy-Move | **HIGH CONCERN** | ESCALATE |
| `expired` | Valid checksums, but Expiry Date is in the past (2021-01-15) | **REVIEW REQUIRED** | SECONDARY INSPECTION |
| `wrong_face` | ArcFace similarity score 0.22 < threshold 0.60 | **HIGH CONCERN** | ESCALATE |
| `poor_capture` | Laplacian blur 28.5 < 100.0, specular glare 18.0% | **QUALITY FAILED** | REQUEST RECAPTURE |
| `unknown_document` | UNKNOWN_DOCUMENT_MODE active, no registered template | **REVIEW REQUIRED** | SECONDARY INSPECTION |

---

## ⚖️ Legal & Operational Notice

*DocShield AI is an AI-assisted document screening and investigation tool designed to highlight anomalies and assist authorized personnel. It is NOT an automated passport authenticator, DOES NOT claim access to live government databases, and DOES NOT replace human officer decision-making.*
