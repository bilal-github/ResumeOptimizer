import os
import fitz  # PyMuPDF for PDFs
import docx
import openai
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# Set OpenAI API Key (Use Environment Variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("API key is missing! Set OPENAI_API_KEY in system variables.")

print("OpenAI API Key Loaded Successfully")  # Just for testing, remove in production

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Function to analyze resume using AI
def analyze_resume_with_ai(resume_text, job_description):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Replace with your actual API key

    prompt = f"""
    You are a professional resume optimization assistant. Analyze the following resume and compare it to the job description.
    
    Resume:
    {resume_text}

    Job Description:
    {job_description}

    - List missing skills and keywords needed for this job.
    - Suggest improvements to wording, formatting, and clarity.
    - Provide a professional resume score (out of 10) with feedback.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in resume optimization."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Resume Upload & Analysis Route
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    file = request.files["resume"]
    job_description = request.form["job_description"]

    if not file or not job_description:
        return jsonify({"error": "Please upload a resume and enter a job description."})

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Extract text based on file type
    if filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(filepath)
    elif filename.endswith(".docx"):
        resume_text = extract_text_from_docx(filepath)
    else:
        return jsonify({"error": "Unsupported file format. Upload PDF or DOCX only."})

    # AI Resume Analysis
    ai_feedback = analyze_resume_with_ai(resume_text, job_description)

    return jsonify({"analysis": ai_feedback})

if __name__ == "__main__":
    app.run(debug=True)
