from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.0-flash"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_roster(self, sys_rules, hard_rules, soft_rules, history, shift_repo):
        past_context = ""
        for i, entry in enumerate(history[-2:]):
            past_context += f"\n[VERSION {i+1}]:\n{entry}\n"

        allowed_shifts = ", ".join(shift_repo)

        prompt = f"""
        ACT AS: Senior Hospital Staffing Coordinator.
        GOAL: Create a 7-day roster.
        SHIFT OPTIONS: {"Morning","Evening","Night"}

        STAFF LIST:
        Mark (Doc), Shawn (Anesth), Axel (Surgeon), Sarah (Surgeon), 
        Elena (Nurse), David (Nurse), Chloe (Nurse), James (Nurse), Maya (Nurse), Leo (Nurse).

        FORMATTING RULES:
        1. Name Column: Use exactly: **Name** <br><small>Designation</small>
        2. Column Headers: Name & Role, Mon, Tue, Wed, Thu, Fri, Sat, Sun.

        INSTRUCTIONS:
        - Rules: {sys_rules} | {hard_rules} | {soft_rules}
        - History: {past_context if past_context else "None."}

        MANDATORY SELF-AUDIT:
        After the table, provide a 'Compliance Report'. 
        Verify every rule and mark as [PASSED] or [FAILED].
        """

        try:
            resp = self.client.models.generate_content(
                model=MODEL_NAME, contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            return resp.text
        except Exception as e:

            return f"🚨 Error: {str(e)}"
