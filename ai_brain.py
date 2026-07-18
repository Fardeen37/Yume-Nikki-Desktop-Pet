import os
import subprocess
import threading
import base64
from google import genai
from google.genai import types
from groq import Groq

class AIBrain:
    def __init__(self, gemini_api_key, groq_api_key):
        self.gemini_api_key = gemini_api_key
        self.groq_api_key = groq_api_key
        
        # Initialize clients
        self.gemini_client = genai.Client(api_key=self.gemini_api_key) if self.gemini_api_key else None
        self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None
        
        self.gemini_model = 'gemini-1.5-flash'
        self.groq_chat_model = 'llama-3.3-70b-versatile'
        self.groq_vision_model = 'llama-3.2-11b-vision-preview'
        
    def _gemini_chat(self, user_text, system_prompt):
        response = self.gemini_client.models.generate_content(
            model=self.gemini_model,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                tools=[{"google_search": {}}],
            )
        )
        return response.text

    def _groq_chat(self, user_text, system_prompt):
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_text,
                }
            ],
            model=self.groq_chat_model,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content

    def generate_chat_response(self, user_text, current_character, callback):
        def worker():
            moods = "[HAPPY], [SAD], [SLEEPY], [NEUTRAL], [SURPRISED], [ANGRY], [PLAYFUL], [SCARED], [MUSICAL], [RELAXED], [COLD]"
            system_prompt = f"You are {current_character} from Yume Nikki. You are a desktop pet on the user's screen. Reply in character in a short, concise sentence. Your response MUST begin with a mood tag, chosen from: {moods}. Example: '[PLAYFUL] Let's go for a ride!'"
            
            try:
                if self.gemini_client:
                    try:
                        text = self._gemini_chat(user_text, system_prompt)
                        callback(text)
                        return
                    except Exception as e:
                        print("Gemini Chat Error, falling back to Groq:", e)
                        
                if self.groq_client:
                    text = self._groq_chat(user_text, system_prompt)
                    callback(text)
                    return
                    
                callback("[SAD] Both of my brains are disconnected...")
            except Exception as e:
                print("AI Chat Error:", e)
                callback(f"[SAD] Something went wrong with my brain... ({e})")
                
        threading.Thread(target=worker, daemon=True).start()

    def _gemini_vision(self, image_path, system_prompt):
        from PIL import Image
        img = Image.open(image_path)
        response = self.gemini_client.models.generate_content(
            model=self.gemini_model,
            contents=["React to what the user is doing on the screen.", img],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            )
        )
        return response.text

    def _groq_vision(self, image_path, system_prompt):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "React to what the user is doing on the screen."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model=self.groq_vision_model,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content

    def generate_vision_response(self, image_path, current_character, callback):
        def worker():
            moods = "[HAPPY], [SAD], [SLEEPY], [NEUTRAL], [SURPRISED], [ANGRY], [PLAYFUL], [SCARED], [MUSICAL], [RELAXED], [COLD]"
            system_prompt = f"You are {current_character} from Yume Nikki. You are a desktop pet. The user has been looking at this screen for a long time. React to what they are doing based on the image in a short, in-character sentence. Your response MUST begin with a mood tag, chosen from: {moods}. Example: '[SLEEPY] Are you still working? I'm tired.'"
            
            try:
                if self.gemini_client:
                    try:
                        text = self._gemini_vision(image_path, system_prompt)
                        callback(text)
                        return
                    except Exception as e:
                        print("Gemini Vision Error, falling back to Groq:", e)
                        
                if self.groq_client:
                    text = self._groq_vision(image_path, system_prompt)
                    callback(text)
                    return
                    
                callback("[SAD] I can't see anything... my eyes are disconnected.")
            except Exception as e:
                print("Vision AI Error:", e)
                error_str = str(e)
                if "model_decommissioned" in error_str or "model_not_found" in error_str:
                    callback("[SAD] My Groq eyes were decommissioned! Please use a Gemini API key for vision.")
                else:
                    callback(f"[SAD] I couldn't see the screen well... ({e})")
                
        threading.Thread(target=worker, daemon=True).start()

    def generate_tts(self, text, callback):
        def worker():
            clean_text = text
            if text.startswith("["):
                end_idx = text.find("]")
                if end_idx != -1:
                    clean_text = text[end_idx+1:].strip()
                    
            if not clean_text:
                return

            output_file = os.path.abspath("temp_voice.mp3")
            voice = "en-US-AriaNeural"
            
            safe_text = clean_text.replace('"', '\\"')
            cmd = f'python -m edge_tts --voice {voice} --text "{safe_text}" --write-media "{output_file}"'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(output_file):
                callback(output_file)
                
        threading.Thread(target=worker, daemon=True).start()
