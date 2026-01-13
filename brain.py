from google import genai
from google.genai import types

# Using the 2026 stable Flash model
MODEL_NAME = "gemini-2.5-flash"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key, vertexai=False)

    def generate_roster(self, sys_rules, hard_rules, soft_rules, history):
        # Injecting session history for contextual memory
        past_context = ""
        for i, entry in enumerate(history[-2:]):
            past_context += f"\n[Previous Attempt {i+1}]:\n{entry}\n"

        prompt = f"""
        ACT AS: Senior Hospital Staffing Coordinator.
        GOAL: Generate a 7-day staff roster.

        STAFF LIST:
        Mark (Doctor), Shawn (Anesthesiologist), Axel (Surgeon), Sarah (Surgeon),
        Elena (Nurse), David (Nurse), Chloe (Nurse), James (Nurse), Maya (Nurse), Leo (Nurse).

        REQUIRED FORMAT (EXCEL-READY):
        Provide a Markdown table with Name and Designation as separate columns.
        | Name | Designation | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
        | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

        CONSTRAINTS:
        - SYSTEM: {sys_rules}
        - HARD: {hard_rules}
        - SOFT: {soft_rules}
        - MANDATORY: Every person MUST have exactly one "OFF" day.

        SESSION MEMORY:
        {past_context if past_context else "Initial run - no history."}

        INSTRUCTIONS:
        1. Fill shifts: "Morning", "Afternoon", "Night", or "OFF".
        2. Perform a self-audit: Does everyone have an 'OFF' day?
        3. Mention any improvements made based on previous history in a 'Compliance Report'.
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

