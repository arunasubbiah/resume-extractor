import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
from pydantic import BaseModel, EmailStr, ValidationError
from typing import List
import os
import json

#import load_dotenv to import environtment variables
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Streamlit app title
st.title("Resume Information Extractor with OpenAI")

class ProjectInfo(BaseModel):
    CompanyName: str
    StartDate: str
    EndDate: str
    Summary: str

class ResumeInfo(BaseModel):
    Name: str
    Phone: str
    Email: str
    YrsOfExp: int
    Skills: List[str]
    Education: List[str]
    ProjectExperience: List[ProjectInfo]
    

# Function to call OpenAI API for resume information extraction
def extract_resume_info_with_openai(text):
    system_prompt = """
    You are an AI assistant that extracts structured information from resumes.
    When given a resume's text, extract the following fields:
    - Name: The candidate's full name.
    - Phone: Candidate's Phone number
    - Email: candidate's email
    - YrsOfExp: Total years of experience
    - Skills: Technical skillset 
    - Education: List of all educations
    - ProjectExperience: List of each project experience with nested list of Company Name, Start Date, End Date and Summary of responsibilities in each project.
    If a field is not present, provide a default value (e.g., "Not Found" for Name, an empty list for Skills).
    Ensure your response is a valid JSON object.
    If the uploaded document is not a resume then send a message to upload resume in pdf format. 
    """

    # Call the OpenAI API
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            response_format=ResumeInfo,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": str(e)})

# Upload PDF file
uploaded_file = st.file_uploader("Upload a resume (PDF format)", type="pdf")

if uploaded_file:
    # Extract text from the uploaded PDF
    pdf_reader = PdfReader(uploaded_file)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    # Extract structured information from the resume using OpenAI
    if st.button("Extract Information"):
        st.write("Extracting information using OpenAI...")
        extracted_info = extract_resume_info_with_openai(pdf_text)
        extracted_json = json.loads(extracted_info)
        print(extracted_info)

        # Display the extracted information
        st.subheader("Extracted Information")
        try:   
            st.text(extracted_json)
        except ValidationError as ve:
            st.error("Validation Error:")
            st.text(ve)
        except Exception as e:
            st.error("Failed to process the response:")
            st.text(extracted_info)