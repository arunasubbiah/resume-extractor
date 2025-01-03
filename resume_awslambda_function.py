import os
import json
from openai import OpenAI
from pydantic import BaseModel
from typing import List

# Access the API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
        # Use the OpenAI API to get a completion for the resume information extraction task
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            response_format=ResumeInfo,
            temperature=0
        )
        # Parse the response and extract the message content
        extracted_data = response.choices[0].message.content

        # Return the result
        return json.loads(extracted_data)  # Assuming the response is a valid JSON string
    except Exception as e:
        # Handle any error and return the error message
        return {"error": str(e)}

def lambda_handler(event, context):
    # Check if the event has the 'text' key for resume content
    if 'text' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps('Error: Missing "text" field in request body')
        }

    # Extract the resume text from the event
    resume_text = event['text']

    # Extract resume info using the OpenAI API
    result = extract_resume_info_with_openai(resume_text)

    # Return the result as a Lambda response
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
