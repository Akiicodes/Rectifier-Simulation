import wikipedia
import urllib.request
import google.generativeai as genai

def check_internet():
    try:
        urllib.request.urlopen('http://google.com', timeout=2)
        return True
    except:
        return False

def get_response(user_input, api_key=None):
    """
    Fetches answers from Gemini (if API key provided) or falls back to Wikipedia.
    """
    user_input_lower = user_input.lower().strip()
    
    # Handle greetings or empty input
    if user_input_lower in ['hello', 'hi', 'hey']:
        return "Hello! 👋 I am your Rectifier AI Tutor. I can answer questions using the internet or an advanced AI if you provide an API key in the sidebar!"
    if not user_input_lower:
        return "Please ask a question!"

    if not check_internet():
        return "⚠️ I couldn't connect to the internet. Please check your connection."

    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            # Dynamically find a valid model for the user's specific API key
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not available_models:
                return "⚠️ **Dr. Jhatka Error:** No text generation models are available for your API key. Please check your Google AI Studio permissions.\n\nFalling back to Wikipedia...\n\n---\n\n" + fetch_wikipedia(user_input)
                
            # Prefer modern models, otherwise pick the first available one
            model_name = available_models[0]
            for pref in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro', 'models/gemini-1.0-pro']:
                if pref in available_models:
                    model_name = pref
                    break

            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                f"You are a helpful physics and electronics tutor. A student asks: '{user_input}'. "
                f"Explain it simply, accurately, and concisely. If they ask for differences, provide a clear comparison."
            )
            return f"✨ **Dr. Jhatka:**\n\n{response.text}"
        except Exception as e:
            return f"⚠️ **Dr. Jhatka Error:** `{str(e)}`\n\nFalling back to Wikipedia...\n\n---\n\n" + fetch_wikipedia(user_input)

    # Fallback to Wikipedia
    return fetch_wikipedia(user_input)

def fetch_wikipedia(user_input):
    try:
        summary = wikipedia.summary(user_input, sentences=4, auto_suggest=True)
        return f"🌍 **Internet Search Results (Wikipedia):**\n\n{summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        options = [opt for opt in e.options if opt.lower() != user_input.lower().strip()][:5]
        return f"There are many topics related to '{user_input}'. Could you be more specific? For example:\n- " + "\n- ".join(options)
    except wikipedia.exceptions.PageError:
        try:
            search_results = wikipedia.search(user_input, results=1)
            if search_results:
                best_match = search_results[0]
                summary = wikipedia.summary(best_match, sentences=4, auto_suggest=False)
                return f"🌍 **Internet Search Results (Closest match: {best_match}):**\n\n{summary}"
            else:
                return f"I couldn't find any internet articles matching '{user_input}'. Try using simpler keywords!"
        except Exception:
            return f"I couldn't find any internet articles matching '{user_input}'. Try rephrasing your question!"
    except Exception as e:
        return "I'm having trouble fetching that answer from the internet right now."
