from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import PyPDF2 as pdf
import google.generativeai as genai
import json
import re

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Gemini API response
def get_gemini_response(input_prompt, pdf_content, jd_input):
    # Create the model configuration
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config)
    
    # Combine inputs
    input_data = f"{input_prompt}\n\nResume Content:\n{pdf_content}\n\nJob Description:\n{jd_input}"
    
    # Get the response from the model
    response = model.generate_content([input_data])
    
    # Clean the response text
    cleaned_response = re.sub(r"^```.*?\n|\n```$", "", response.text.strip(), flags=re.DOTALL)
    
    # Parse JSON safely
    try:
        parsed_response = json.loads(cleaned_response)
        return parsed_response
    except json.JSONDecodeError:
        st.error("Invalid response format received. Please try again.")
        return None

# Function to extract text from PDF
def extract_pdf_text(uploaded_file):
    if uploaded_file is not None:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # Handle empty pages gracefully
        return text.strip()
    else:
        raise FileNotFoundError("No PDF File Uploaded")

# Prompts
input_prompt1 = """
Hey, act like a highly skilled ATS (Application Tracking System) with expertise in tech fields like software engineering, data science, and big data.
Your task is to evaluate resumes based on a provided job description. 
Provide accurate percentage matching, missing keywords, and a concise profile summary.
Your response should be in this JSON format:
{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}
"""

input_prompt2 = """
You are an experienced Technical HR Manager. Review the provided resume against the given job description.
Share an evaluation highlighting the strengths and weaknesses of the resume in relation to the role.
Your response MUST STRICTLY follow this JSON format without any explanation or additional text:
{"Strengths": "List of strengths", "Weaknesses": "List of weaknesses", "Overall Evaluation": "Your conclusion here"}
Do not include any backticks, markdown, or extra text.
"""

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Inputs
input_text = st.text_area("Paste the Job Description here:", key="jd_input")
uploaded_file = st.file_uploader("Upload your Resume (PDF)...", type=["pdf"], help="Please upload a PDF file")

# Display success message
if uploaded_file is not None:
    st.success("PDF Uploaded Successfully!")

# Buttons
submit1 = st.button("Percentage Match")
submit2 = st.button("Tell me about my Resume")

# Process uploaded file
if uploaded_file:
    resume_text = extract_pdf_text(uploaded_file)

    if submit1:
        st.subheader("Resume Match Results")
        response = get_gemini_response(input_prompt1, resume_text, input_text)
        if response:
            st.json(response)  # Display clean JSON output

    if submit2:
        st.subheader("HR Evaluation")
        response = get_gemini_response(input_prompt2, resume_text, input_text)
        if response:
            st.json(response)  # Display clean JSON output
