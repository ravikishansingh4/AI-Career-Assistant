# CareerPilot AI — Resume & JD Matcher

A runnable React + Vite frontend and FastAPI backend MVP based on the supplied project code/prompt.

## Included
- PDF resume upload and text extraction (PyMuPDF)
- Basic skill detection from a built-in keyword list
- Resume vs. job description skill matching
- Match indicator, matching/missing skills, suggestions, sample project ideas, and 30-day roadmap
- Additional API endpoints for resume improvement, project ideas, and roadmap
- Dark responsive dashboard

## Important scope note
This is a **keyword-based MVP**, not a full LLM product or a real ATS score. The match percentage is a skills coverage indicator only. It does not predict hiring or shortlisting. Scanned PDFs need OCR, which is not included. AI provider integration, authentication, PDF resume export, persistent database, and advanced charts are not included in this starter.

## Requirements
- Python 3.10+
- Node.js 18+

## Run backend (Windows PowerShell)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

## Run frontend (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## API
- `GET /api/health`
- `POST /api/upload-resume` (multipart field: `file`)
- `POST /api/match` (form fields: `resume_text`, `job_description`)
- `POST /api/analyze` (form fields: `resume_text`, `job_description`)
- `POST /api/improve-resume` (form fields: `resume_text`, `job_description`)
- `POST /api/projects` (form fields: `resume_text`, `job_description`)
- `POST /api/roadmap` (form fields: `resume_text`, `job_description`)

## Privacy
Uploaded PDF contents are processed in memory by the backend and are not saved to disk by this starter. Avoid uploading sensitive resumes to shared/public deployments.
