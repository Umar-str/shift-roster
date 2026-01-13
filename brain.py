from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.5-flash-lite"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_roster(self, sys_rules, hard_rules, soft_rules, history, shift_repo):
        past_context = ""
        for i, entry in enumerate(history[-2:]):
            past_context += f"\n[PREVIOUS VERSION {i+1}]:\n{entry}\n"

        allowed_shifts = ", ".join(shift_repo)

        prompt = f"""
        ACT AS: Senior Hospital Staffing Coordinator.
        GOAL: Create a 7-day roster. 
        ALLOWED SHIFTS: {allowed_shifts}

        STAFF: Mark (Doc), Shawn (Anesth), Axel (Surgeon), Sarah (Surgeon), Elena (Nurse), David (Nurse), Chloe (Nurse), James (Nurse), Maya (Nurse), Leo (Nurse).

        OUTPUT INSTRUCTIONS:
        1. Produce a Markdown table with EXACTLY these 9 columns: 
           | Name | Designation | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
        2. Do NOT use HTML tags in the table.
        3. Use only the allowed shifts or "OFF".
        4. Provide a 'Compliance Report' as a separate list below the table.

        RULES: {sys_rules} | {hard_rules} | {soft_rules}
        HISTORY: {past_context if past_context else "None."}
        """

        try:
            resp = self.client.models.generate_content(
                model=MODEL_NAME, contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            return resp.text
        except Exception as e:
            return f"🚨 Error: {str(e)}"
