from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.5-flash-lite"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key, vertexai=False)

    def generate_roster(self, sys_rules, hard_rules, soft_rules, history):
        # Convert history list into a readable string for the AI
        history_context = ""
        for i, entry in enumerate(history[-3:]): # Only give last 3 to save tokens
            history_context += f"\nVERSION {i+1}:\n{entry['content']}\n"

        prompt = f"""
        ACT AS: Senior Hospital Staffing Coordinator.
        
        <context_history>
        Below are the previous rosters generated in this session. 
        Analyze them to avoid repeating same mistakes or to follow the established pattern:
        {history_context if history_context else "No previous history."}
        </context_history>

        <current_requirements>
        System: {sys_rules}
        Hard: {hard_rules}
        Soft: {soft_rules}
        - MANDATORY: Every person must have exactly ONE 'OFF' day.
        </current_requirements>

        INSTRUCTIONS:
        1. Generate a NEW 7-day Markdown table.
        2. Conduct a self-audit to ensure all staff (Mark, Shawn, Axel, Sarah, Elena, David, Chloe, James, Maya, Leo) have a holiday.
        3. Mention in your report if you successfully adjusted based on previous history.
        """

        try:
            resp = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    thinking_config=types.ThinkingConfig(include_thoughts=False)
                )
            )
            return resp.text
        except Exception as e:

            return f"🚨 API Error: {str(e)}"
