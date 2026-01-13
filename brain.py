from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.5-flash"

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
        ALLOWED SHIFTS: {allowed_shifts}

        STAFF: Mark (Doc), Shawn (Anesth), Axel (Surgeon), Sarah (Surgeon), Elena (Nurse), David (Nurse), Chloe (Nurse), James (Nurse), Maya (Nurse), Leo (Nurse).

        TABLE FORMAT:
        | Name | Designation | Mon | Tue | Wed | Thu | Fri | Sat | Sun |

        INSTRUCTIONS:
        1. Fill the table using only the allowed shifts or "OFF".
        2. Do not use HTML inside the table cells.
        3. Perform a 'Self-Audit Compliance Report' after the table.

        RULES: {sys_rules} | {hard_rules} | {soft_rules}
        """

        try:
            resp = self.client.models.generate_content(
                model=MODEL_NAME, contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            return resp.text
        except Exception as e:
            return f"🚨 AI Error: {str(e)}"