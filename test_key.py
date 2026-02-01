import google.generativeai as genai

# Use your existing key here
API_KEY = "AIzaSyA3FVgDr1K8gz_pWQvPggdXEfVBBvPTeVA"

genai.configure(api_key=API_KEY)

# Change this line from 1.5 to 2.5
model = genai.GenerativeModel('gemini-2.5-flash')

print("--- Starting 2026 Gemini API Test ---")
try:
    response = model.generate_content("Say 'The connection is successful!'")
    print("✅ SUCCESS! Response:")
    print(response.text)
except Exception as e:
    print("❌ STILL FAILED. Error details:")
    print(e)