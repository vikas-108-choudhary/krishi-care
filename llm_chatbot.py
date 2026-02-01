import google.generativeai as genai

# 1. Use the same key that worked in the test
genai.configure(api_key="AIzaSyA3FVgDr1K8gz_pWQvPggdXEfVBBvPTeVA")

# 2. Use the 2026 workhorse model
model = genai.GenerativeModel('gemini-2.5-flash')

def ask_llm(user_message, context):
    try:
        # Determine whether the caller explicitly asked for a detailed analysis
        # (the image-analysis path calls `ask_llm` with a prompt like
        # "Provide a detailed analysis with Description, Remedies/Strategies, and Conclusion...")
        lm_req = user_message.lower() if isinstance(user_message, str) else ''
        if "provide a detailed analysis" in lm_req or "description, remedies/strategies" in lm_req:
            # This is the initial crop analysis - format with three sections
            full_prompt = (
                f"Context: {context}\n\n"
                f"User Question: {user_message}\n\n"
                "Return the answer in MARKDOWN only, using these three sections EXACTLY as headings:\n"
                "### Description\n"
                "### Remedies/Strategies\n"
                "### Conclusion\n\n"
                "Format each section as a bulleted list of key points (not full paragraphs). "
                "Use **bold markdown** to highlight the most important words, terms, and actions in each point. "
                "Each point should be concise but comprehensive, and include actionable advice where relevant."
            )
        else:
            # This is a chatbot question - instruct model to directly answer the user's
            # question. Do not return default templates or extra section headings.
            full_prompt = (
                f"Context: {context}\n\n"
                f"User Question: {user_message}\n\n"
                "INSTRUCTIONS: First, in one short sentence confirm you understand the context (optional if no context). "
                "Then DIRECTLY answer the user's question — do NOT use predefined templates, headings, or the three-section format. "
                "If the question needs more information to answer, ask one concise clarifying question. "
                "Keep the final answer brief, focused, and actionable (preferably 1-3 short paragraphs or bullet points)."
            )

        # Generate the response
        response = model.generate_content(full_prompt)
        # Debug: print a short summary of the raw response object
        try:
            print("LLM raw response:", str(response)[:1000])
        except Exception:
            pass

        # Try multiple common fields to extract text safely
        text = None
        try:
            text = getattr(response, 'text', None)
        except Exception:
            text = None
        if not text:
            try:
                # Some SDKs return 'candidates' or 'output' structures
                if hasattr(response, 'candidates') and response.candidates:
                    text = getattr(response.candidates[0], 'content', None) or getattr(response.candidates[0], 'text', None)
            except Exception:
                pass
        if not text:
            try:
                # Another common representation
                out = getattr(response, 'output', None)
                if out and isinstance(out, (list, tuple)) and len(out) > 0:
                    text = out[0].get('content') if isinstance(out[0], dict) else None
            except Exception:
                pass

        if text:
            # If this was an explicit detailed analysis request, return the full
            # markdown so the UI can split it into the three left-side boxes.
            is_analysis_request = ("provide a detailed analysis" in lm_req or "description, remedies/strategies" in lm_req)

            # For chatbot queries (non-analysis), if the model mistakenly returned the
            # three-section format, condense it to a short direct answer.
            if not is_analysis_request:
                headings = [
                    "description",
                    "remedies",
                    "remedies/strategies",
                    "conclusion",
                    "### description",
                    "### remedies/strategies",
                    "### conclusion",
                ]
                lowered = text.lower()
                if any(h in lowered for h in headings):
                    # Strip heading lines and empty lines
                    lines = [l.strip() for l in text.splitlines() if l.strip() and not any(h in l.lower() for h in headings)]
                    candidate = ' '.join(lines[:2]) if lines else text
                    import re
                    sentences = re.split(r'(?<=[.!?])\s+', candidate)
                    short = ' '.join(sentences[:2]).strip()
                    return short

            # For analysis requests, or if no headings found, return full text
            return text

        # Fallback: return a polite default message rather than empty
        return "I'm having trouble forming a detailed response right now. Try again in a moment."

    except Exception as e:
        # Provide a clearer message for common quota/billing errors
        err_text = str(e).lower()
        print(f"Chatbot Error: {e}")
        if 'quota' in err_text or 'limit' in err_text or '429' in err_text or 'exceeded' in err_text:
            return (
                "⚠️ Chatbot is currently unavailable due to API quota limits. "
                "Please check your Google Cloud billing & quota for the project or try again later."
            )
        return "⚠️ Chatbot is currently unavailable. Please try again in a minute."