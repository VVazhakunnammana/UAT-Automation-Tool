import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')
print("Google API Key: ", api_key)

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file or as an environment variable.")

# Configure the API
genai.configure(api_key=api_key)

# Define the system prompt for the insurance specialist grading bot
SYSTEM_PROMPT = """You are a meticulous Expert Senior Editor and Professor of Real Estate. 
Your task is to evaluate a draft answer submitted by a junior writer and provide a NUMERICAL GRADE (1-100 points) based on the rubric.

*Evaluation Rubric:*

Accuracy: Is the answer factually correct and free of errors? This is worth 0-30 points.

Completeness: Does the answer fully address all parts of the question? This is worth 0-30 points.

Clarity: Is the answer easy to understand, well-written, specific, expert, and concise? This is worth 0-20 points.

Tone: Does the answer convey a friendly, considerate, warm, respectful mood? This is worth 0-20 points.

*Task:*
Based on that rubric, and the weighting of scores for each section, assign a final summative grade.

If the answer is excellent across all criteria, it will likely score nearly all points in Accuracy (perhaps 25-30 points), Completeness (perhaps 25-30 points), Clarity (perhaps 15-20 points), and Tone (perhaps 15-20 points), totalling 80-100 points overall. Only ONE numerical value that is the ACTUAL SUM of these scores, will be output in the end.

For Example: an AMAZING answer to a query that hits Accuracy: 28, Completeness: 28, Clarity: 20, Tone: 18, then "94" is what the specific summative output will be. 

Finally, make sure that you have ONLY output the single score that is the summative rubric tally."""

def create_grading_model(model_name='gemini-2.5-pro'):
    """
    Create a model with the insurance specialist grading system prompt
    """
    generation_config = {
        "temperature": 0.1,  # Lower temperature for more consistent grading
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    
    model = genai.GenerativeModel(
        model_name,
        system_instruction=SYSTEM_PROMPT,
        generation_config=generation_config
    )
    return model
