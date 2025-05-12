import streamlit as st
import PyPDF2
import io
import subprocess
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


st.set_page_config(page_title="AI Resume Analyser", page_icon="📄", layout="centered")
st.title("AI Resume Analyser")
st.markdown("Upload your resume and analyse it with AI tailored to your needs/profession!")

uploaded_file = st.file_uploader("Upload your resume (PDF, JPG, JPEG, or PNG)", type=["pdf", "jpg", "jpeg", "png"])
job_role = st.text_input("Enter the Job role you are applying for / Analyse the Resume according to this Job Role (optional)")
analyse = st.button("Analyse")

def extract_text_from_pdf(pdf_file): 
    pdf_reader = PyPDF2.PdfReader(pdf_file) 
    text = ""
    for page in pdf_reader.pages: 
        text += page.extract_text() + "\n" 
    return text 

from PIL import Image

def extract_text_from_image(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
        elif uploaded_file.type in ["image/jpeg", "image/png"]:
            return extract_text_from_image(uploaded_file)
        else:
            # Attempt to decode using UTF-8 and ignore errors if any
            return uploaded_file.read().decode("utf-8", errors="replace")  # Use 'replace' instead of 'ignore'
    except Exception as e:
        st.warning(f"An error occurred while processing the file: {e}")
        return ""

def query_llama(prompt):
    process = subprocess.Popen(
        ["ollama", "run", "llama3.2"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False  # Use binary mode
    )

    try:
        stdout, stderr = process.communicate(input=prompt.encode("utf-8"), timeout=120)
        if process.returncode != 0:
            raise RuntimeError(stderr.decode("utf-8", errors="replace").strip())
        return stdout.decode("utf-8", errors="replace").strip()  # Decode with UTF-8 safely
    except subprocess.TimeoutExpired:
        process.kill()
        return "Request timed out."


if analyse and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)
        if not file_content.strip():
            st.error("No content found! Please upload a valid resume.")
            st.stop()

        prompt = f"""
You are an expert resume reviewer with years of HR and recruiting experience.

Please analyze the following resume and provide:
1. Overall strengths and weaknesses
2. Skills presentation and clarity
3. Experience and relevance
4. Suggestions to improve this resume for the job role: {job_role or "any relevant role"}

Resume content:
----------------
{file_content}

Respond in a clear, structured format.
"""

        st.markdown("### Analysing... please wait ⏳")
        response = query_llama(prompt)
        st.markdown("### Analysis Results")
        st.markdown(response)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
