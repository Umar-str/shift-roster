from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.5-flash"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_roster(self, sys_rules, hard_rules, soft_rules, history, shift_repo):
        past_context = ""
        for i, entry in enumerate(history[-2:]):
            past_context += f"\n[PAST VERSION {i+1}]:\n{entry}\n"

        # Dynamically inject the shifts you defined in app.py
        allowed_shifts = ", ".join(shift_repo.keys())

        prompt = f"""
        ACT AS: Senior Hospital Staffing Coordinator.
        GOAL: Generate a 7-day roster.

        ALLOWED SHIFTS: {"Morning","Evening","Night"}

        STAFF: Mark (Doc), Shawn (Anesth), Axel/Sarah (Surgeons), Elena/David/Chloe/James/Maya/Leo (Nurses).

        FORMATTING:
        - Column 1: **Name** <br><small>Designation</small>
        - Columns 2-8: Mon, Tue, Wed, Thu, Fri, Sat, Sun.

        CONSTRAINTS:
        - SYSTEM: {sys_rules}
        - HARD: {hard_rules}
        - SOFT: {soft_rules}

        HISTORY:
        {past_context if past_context else "Initial run."}

        MANDATORY FINAL TASK:
        Perform a 'Self-Audit Compliance Report' after the table. 
        Verify if every row and column meets the provided rules.
        """

        try:
            resp = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            return resp.text
        except Exception as e:
            return f"🚨 API Error: {str(e)}"