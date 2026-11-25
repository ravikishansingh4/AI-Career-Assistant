
import re
import os
import json
import fitz

from http.server import BaseHTTPRequestHandler, HTTPServer
from email.parser import BytesParser
from email.policy import default
from urllib.parse import urlparse


PORT = int(os.environ.get("PORT", 8000))
MAX_FILE_SIZE = 5 * 1024 * 1024

SKILLS = [
    "python", "java", "javascript", "typescript", "react", "node.js",
    "html", "css", "sql", "mysql", "mongodb", "machine learning",
    "deep learning", "data analysis", "pandas", "numpy", "aws", "azure",
    "docker", "git", "fastapi", "django", "communication", "leadership",
    "problem solving", "excel", "power bi", "tensorflow", "pytorch",
    "scikit-learn", "statistics", "nlp", "computer vision", "flask",
]


def find_skills(text):
    text = text.lower()
    found = []

    for skill in SKILLS:
        pattern = r"(?<![\w])" + re.escape(skill) + r"(?![\w])"

        if re.search(pattern, text):
            found.append(skill)

    return sorted(set(found))


def extract_pdf_text(content):
    try:
        with fitz.open(stream=content, filetype="pdf") as document:
            text = "\n".join(
                page.get_text("text") for page in document
            )
    except Exception:
        raise ValueError("Unable to read this PDF.")

    if not text.strip():
        raise ValueError(
            "No selectable text found. Try a text-based PDF."
        )

    return text


def get_match_result(resume_text, job_description):
    resume_skills = find_skills(resume_text)
    required_skills = find_skills(job_description)

    matching = sorted(set(resume_skills) & set(required_skills))
    missing = sorted(set(required_skills) - set(resume_skills))

    score = (
        round(len(matching) / len(required_skills) * 100)
        if required_skills else 0
    )

    return {
        "match_score": score,
        "matching_skills": matching,
        "missing_skills": missing,
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "suggestions": [
            f"Practice {skill} and add a relevant project if you have genuinely used it."
            for skill in missing
        ],
        "note": "Keyword-based skills indicator, not an ATS score or hiring prediction."
    }


class CareerPilotHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def read_form_data(self):
        content_type = self.headers.get("Content-Type", "")
        length = int(self.headers.get("Content-Length", 0))

        body = self.rfile.read(length)

        message = BytesParser(policy=default).parsebytes(
            b"Content-Type: " + content_type.encode() +
            b"\r\nMIME-Version: 1.0\r\n\r\n" + body
        )

        fields = {}

        if message.is_multipart():
            for part in message.iter_parts():
                name = part.get_param(
                    "name",
                    header="content-disposition"
                )

                if not name:
                    continue

                payload = part.get_payload(decode=True) or b""

                if part.get_filename():
                    fields[name] = {
                        "filename": part.get_filename(),
                        "content": payload
                    }
                else:
                    charset = part.get_content_charset() or "utf-8"
                    fields[name] = payload.decode(charset, errors="replace")

        return fields

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/health":
            self.send_json({
                "status": "running",
                "app": "CareerPilot AI"
            })
        else:
            self.send_json({"detail": "Not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path

        try:
            fields = self.read_form_data()

            if path == "/api/upload-resume":
                file_data = fields.get("file")

                if not file_data:
                    return self.send_json(
                        {"detail": "Please upload a PDF file."}, 400
                    )

                filename = file_data["filename"]
                content = file_data["content"]

                if not filename.lower().endswith(".pdf"):
                    return self.send_json(
                        {"detail": "Please upload a PDF file."}, 400
                    )

                if len(content) > MAX_FILE_SIZE:
                    return self.send_json(
                        {"detail": "PDF must be under 5 MB."}, 413
                    )

                if not content.startswith(b"%PDF"):
                    return self.send_json(
                        {"detail": "Invalid PDF file."}, 400
                    )

                text = extract_pdf_text(content)

                return self.send_json({
                    "filename": filename,
                    "resume_text": text,
                    "skills": find_skills(text)
                })

            resume_text = fields.get("resume_text", "")
            job_description = fields.get("job_description", "")

            if not resume_text.strip() or not job_description.strip():
                return self.send_json({
                    "detail": "Resume and job description are required."
                }, 400)

            result = get_match_result(resume_text, job_description)
            missing = result["missing_skills"]

            if path == "/api/match":
                return self.send_json(result)

            if path == "/api/analyze":
                result["roadmap"] = [
                    {"week": "Week 1", "task": "Study fundamentals of missing skills."},
                    {"week": "Week 2", "task": "Practice with coding exercises."},
                    {"week": "Week 3", "task": "Build a relevant portfolio project."},
                    {"week": "Week 4", "task": "Update resume truthfully and prepare for interviews."}
                ]

                result["projects"] = [
                    {
                        "title": f"Portfolio project using {skill.title()}",
                        "description": f"Build a project that uses {skill}.",
                        "skills": [skill]
                    }
                    for skill in missing[:3]
                ]

                return self.send_json(result)

            if path == "/api/improve-resume":
                matched = result["matching_skills"]

                return self.send_json({
                    "summary": "Write a concise summary that accurately reflects your experience.",
                    "matched_keywords": matched,
                    "suggestions": [
                        "Start bullet points with action verbs.",
                        "Add measurable results only when verified.",
                        "Use job-related terms naturally.",
                        "Keep formatting simple."
                    ],
                    "notice": "Do not add unverified achievements."
                })

            if path == "/api/projects":
                return self.send_json({
                    "projects": [
                        {
                            "title": f"{skill.title()} mini-project",
                            "description": f"Build a project demonstrating {skill}.",
                            "skill": skill
                        }
                        for skill in missing[:5]
                    ]
                })

            if path == "/api/roadmap":
                focus = ", ".join(missing[:4]) if missing else "relevant skills"

                return self.send_json({
                    "roadmap": [
                        {"days": "1–7", "focus": f"Study fundamentals of {focus}."},
                        {"days": "8–14", "focus": "Practice core concepts."},
                        {"days": "15–21", "focus": "Build a practical project."},
                        {"days": "22–30", "focus": "Polish portfolio and prepare for interviews."}
                    ]
                })

            return self.send_json({"detail": "Not found"}, 404)

        except ValueError as error:
            return self.send_json({"detail": str(error)}, 422)

        except Exception as error:
            return self.send_json({
                "detail": "Server error: " + str(error)
            }, 500)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), CareerPilotHandler)

    print(f"CareerPilot AI backend running on port {PORT}")
    server.serve_forever()
