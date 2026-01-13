from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.5-flash-lite"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_roster(self, sys_rules, hard_rules, soft_rules, history, shift_repo):
        past_context = ""
        for i, entry in enumerate(history):
            past_context += f"\n--- VERSION {i+1} ---\n{entry}\n"

        allowed_shifts = ", ".join(shift_repo)

        prompt = f"""
        ACT AS: Senior Hospital Staffing Coordinator.
        TASK: Create a 7-day roster.
        ALLOWED SHIFTS: {"Morning","Evening","Night"} or OFF.

        STRICT FORMATTING:
        - Markdown table, EXACTLY 8 columns.
        - Column 1: **Name** <br><small>Designation</small>
        
        STAFF: Mark (Doc), Shawn (Anesth), Axel (Surgeon), Sarah (Surgeon), Elena (Nurse), David (Nurse), Chloe (Nurse), James (Nurse), Maya (Nurse), Leo (Nurse).

        RULES:
        [SYSTEM]: {sys_rules}
        [HARD]: {hard_rules}
        [SOFT]: {soft_rules}

        HISTORY: {past_context if past_context else "Initial run."}

        MANDATORY: Provide a BRIEF 'Self-Audit Report' (Short bullet points) after the table.
        """

        try:
            resp = self.client.models.generate_content(
                model=MODEL_NAME, 
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            return resp.text
        except Exception as e:
            return f"🚨 Error: {str(e)}"