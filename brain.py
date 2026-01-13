from google import genai
from google.genai import types

# Updated to the version working for you
MODEL_NAME = "gemini-2.5-flash"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_roster(self, sys_rules, hard_rules, soft_rules, history):
        past_context = ""
        for i, entry in enumerate(history[-2:]):
            past_context += f"\n--- Previous Version {i+1} ---\n{entry}\n"

        prompt = f"""
        ACT AS: Senior Hospital Staffing Coordinator.
        GOAL: Create a 7-day roster for 10 staff members.

        STAFF LIST:
        Mark (Doctor), Shawn (Anesthesiologist), Axel (Surgeon), Sarah (Surgeon),
        Elena (Nurse), David (Nurse), Chloe (Nurse), James (Nurse), Maya (Nurse), Leo (Nurse).

        REQUIRED FORMAT (EXCEL-READY):
        Output a Markdown table with EXACTLY these 9 columns:
        | Name | Designation | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
        | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

        CONSTRAINTS:
        - SYSTEM: {sys_rules}
        - HARD: {hard_rules}
        - SOFT: {soft_rules}
        - MANDATORY: Every person MUST have exactly one "OFF" day.

        SESSION MEMORY:
        {past_context if past_context else "Initial run."}

        INSTRUCTIONS:
        1. Fill shifts: "Morning", "Afternoon", "Night", or "OFF".
        2. Ensure Name and Designation are in separate columns.
        3. Finish with a 'Compliance Report' checking the 'OFF' day rule.
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