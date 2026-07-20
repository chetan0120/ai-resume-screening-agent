 HirePilot AI 🚀
 AI-Powered Resume Screening Agent

A smart resume screening application that helps recruiters compare resumes against a job description using semantic similarity and Large Language Models (LLMs). The application generates match scores, ATS feedback, skill gap analysis, hiring recommendations, and interview questions through an interactive web dashboard.

---

# 📌 Table of Contents

- About the Project
- Features
- How It Works
- Architecture
- Project Structure
- Technology Stack
- Installation
- Configuration
- Running the Application
- Sample Output
- Design Decisions
- Trade-offs
- Limitations
- Future Improvements
- License
- Acknowledgements

---

# 📖 About the Project

Briefly explain:

- Why you built this project
- What problem it solves
- Who can use it
- Main objective

---

# ✨ Features

- Resume PDF Upload
- Job Description Input
- Semantic Resume Matching
- ATS Score Calculation
- Skill Gap Analysis
- Candidate Summary
- Hiring Recommendation
- AI-generated Interview Questions
- Downloadable Reports
- Interactive Dashboard
- Batch Resume Screening
- CSV & JSON Export

---

# ⚙️ How It Works

Resume Upload
        │
        ▼
Extract Resume Text
        │
        ▼
Semantic Similarity Analysis
        │
        ▼
ATS Evaluation
        │
        ▼
LLM Analysis
        │
        ▼
Generate Recruiter Report
        │
        ▼
Display Results

---

# 🏗️ System Architecture

(Add your architecture diagram here.)

Example:

Resume + Job Description
          │
          ▼
     Text Extraction
          │
          ▼
 Sentence Transformers
          │
          ▼
    ATS Evaluation
          │
          ▼
      Groq LLM
          │
          ▼
 Interactive Dashboard

---

# 📂 Project Structure

```text
resume-screening-agent/

├── app.py
├── screen.py
├── requirements.txt
├── README.md
├── .env.example
├── static/
├── templates/
├── uploads/
├── reports/
├── utils/
```

---

# 🛠️ Technology Stack

## Backend

- Python
- Flask

## Frontend

- HTML5
- CSS3
- JavaScript

## AI & NLP

- Groq API
- Llama 3.3
- Sentence Transformers
- Scikit-Learn
- PyMuPDF

## Visualization

- Chart.js
- Font Awesome
- Canvas Confetti

---

# 🚀 Installation

### Clone the repository

```bash
git clone <repository-url>
cd hirepilot-ai
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Configuration

Create a `.env` file.

```env
GROQ_API_KEY=your_api_key
```

---

# ▶️ Running the Project

### Start Flask

```bash
python app.py
```

Open

```
http://localhost:5000
```

or

Run batch screening

```bash
python screen.py
```

---

# 📊 Sample Output

Include screenshots of:

- Landing Page
- Upload Screen
- Dashboard
- Match Score
- Leaderboard
- Skill Analysis
- Download Report

---

# 💡 Design Decisions

Explain why you chose:

- Flask instead of Django
- HTML/CSS instead of React
- Groq API
- Sentence Transformers
- Local embeddings
- JSON responses from the LLM

Keep this section conversational and practical.

---

# ⚖️ Trade-offs

Discuss decisions such as:

- Local embeddings vs. API embeddings
- Lightweight architecture vs. complex microservices
- Simple ATS scoring vs. enterprise ATS engines

Mention what you would improve with more time.

---

# 🚧 Limitations

Current limitations include:

- PDF resumes only
- English language support
- One job description per analysis
- No authentication
- No recruiter database
- No OCR for scanned resumes

---

# 🔮 Future Improvements

Potential enhancements:

- Multi-language support
- Resume OCR
- Recruiter login
- Candidate database
- Vector database (FAISS)
- Email notifications
- AI-powered resume rewriting
- Cloud deployment
- Analytics dashboard

---

# 📄 License

This project is licensed under the MIT License.

---

# 🙏 Acknowledgements

- Groq
- Sentence Transformers
- PyMuPDF
- Flask
- Chart.js
- Font Awesome
- Open Source Community