
import os
import numpy as np
import tensorflow as tf
from PIL import Image



# Store conversation context per session
conversation_context = {}

# Load model once at startup to prevent lag during analysis

try:
    from llm_chatbot import ask_llm
except ImportError:
    def ask_llm(m, c): return "AI Advisor Offline. Ensure llm_chatbot.py exists."

CLASS_NAMES = [
    "Apple Scab", "Apple Black Rot", "Apple Cedar Rust", "Apple Healthy",
    "Blueberry Healthy", "Cherry Powdery Mildew", "Cherry Healthy",
    "Corn Cercospora Leaf Spot", "Corn Common Rust", "Corn Northern Leaf Blight", "Corn Healthy",
    "Grape Black Rot", "Grape Esca", "Grape Leaf Blight", "Grape Healthy",
    "Orange Haunglongbing", "Peach Bacterial Spot", "Peach Healthy",
    "Pepper Bell Bacterial Spot", "Pepper Bell Healthy",
    "Potato Early Blight", "Potato Late Blight", "Potato Healthy",
    "Raspberry Healthy", "Soybean Healthy", "Squash Powdery Mildew",
    "Strawberry Leaf Scorch", "Strawberry Healthy",
    "Tomato Bacterial Spot", "Tomato Early Blight", "Tomato Late Blight", "Tomato Leaf Mold",
    "Tomato Septoria Leaf Spot", "Tomato Spider Mites", "Tomato Target Spot", "Tomato Mosaic Virus",
    "Tomato Yellow Leaf Curl Virus", "Tomato Healthy", 
    "Mango Anthracnose", "Mango Malformation", "Mango Healthy"
]




def predict():
    if not model: return jsonify({"error": "Model missing"})
    try:
        file = request.files.get("image")
        loc = request.form.get("location", "India")
        soil = request.form.get("soil", "Alluvial")

        # Faster Preprocessing
        img = Image.open(file).convert("RGB").resize((224, 224))
        img_array = np.expand_dims(np.array(img) / 255.0, axis=0)
        
        preds = model.predict(img_array, verbose=0)[0]
        idx = int(np.argmax(preds))
        disease = CLASS_NAMES[idx]
        conf = round(float(preds[idx]) * 100, 2)

        treatment = ask_llm(f"Provide a detailed analysis with Description, Remedies/Strategies, and Conclusion sections for {disease} in {soil} soil, {loc}.", "Agri Expert")
        print(f"Predict: disease={disease}, treatment length={len(treatment) if isinstance(treatment, str) else 'NA'}")

        # Store crop context in session for chatbot to use
        session_id = request.remote_addr
        conversation_context[session_id] = {
            "disease": disease,
            "location": loc,
            "soil": soil,
            "treatment_summary": treatment,
            "history": []
        }

        return jsonify({
            "disease": disease, 
            "confidence": conf,
            "treatment": treatment,
            "weather": f"📍 {loc}: 24°C, Clear Sky"
        })
    except Exception as e:
        return jsonify({"error": str(e)})


def chat():
    try:
        data = request.json
        user_message = data.get("message", "")
        session_id = request.remote_addr
        
        # Get stored context for this session
        context_data = conversation_context.get(session_id, {})
        disease = context_data.get("disease", "General")
        location = context_data.get("location", "India")
        soil = context_data.get("soil", "Alluvial")
        treatment_summary = context_data.get("treatment_summary", "")
        history = context_data.get("history", [])
        
        # Build conversation history context
        history_context = ""
        for msg in history[-4:]:  # Keep last 4 exchanges for context
            history_context += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"
        
        # Build the context (pass as `context` to ask_llm) and pass only the user's message
        context_text = f"You are an expert agricultural advisor for {disease} in {soil} soil in {location}.\n\n"
        context_text += f"Crop Disease Summary:\n{treatment_summary}\n\n"
        context_text += f"Previous Conversation:\n{history_context}"

        # Ask the LLM with the user's question as `user_message` and the assembled context separately.
        reply = ask_llm(user_message, context_text)
        
        # Store this exchange in history
        if session_id not in conversation_context:
            conversation_context[session_id] = {"disease": disease, "location": location, "soil": soil, "treatment_summary": treatment_summary, "history": []}
        conversation_context[session_id]["history"].append({"user": user_message, "assistant": reply})
        
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"reply": f"System Error: {str(e)}"})





