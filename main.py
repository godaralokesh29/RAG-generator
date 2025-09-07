import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI
from dotenv import load_dotenv  # Import the function

# Load environment variables from the .env file
load_dotenv()

# Load API key from environment variable
# It's safer to store API keys outside of the code
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=API_KEY)

app = FastAPI()

@app.get("/ask")
def ask_gemini(query: str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Use a try...except block to handle potential API errors
    try:
        response = model.generate_content(query)
        return {"query": query, "response": response.text}
    except Exception as e:
        # Log the error for debugging and return a user-friendly message
        print(f"An error occurred while generating content: {e}")
        return {"error": "Failed to get a response from Gemini API."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)