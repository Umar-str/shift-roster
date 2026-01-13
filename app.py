from google import genai
from google.genai import types

MODEL_NAME = "gemini-1.5-flash"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key, vertexai=False)

    def generate_roster(self, sys_rules, hard_rules, soft_rules, history):
        # Format history for context
        past_context = "\n".join(history[-2:]) if history else "No previous history."

        prompt = f"""
        ACT AS: Senior Hospital Staffing Coordinator.
        
        STAFF LIST (10 Employees):
        1. Mark (Doctor - Lead)
        2. Shawn (Anesthesiologist)
        3. Axel (Surgeon)
        4. Sarah (Surgeon)
        5. Elena (Nurse)
        6. David (Nurse)
        7. Chloe (Nurse)
        8. James (Nurse)
        9. Maya (Nurse)
        10. Leo (Nurse)

        REQUIRED FORMAT:
        A Markdown table with exactly these columns:
        [Employee Name & Designation | Mon | Tue | Wed | Thu | Fri | Sat | Sun]

        CONSTRAINTS:
        - SYSTEM: {sys_rules}
        - HARD: {hard_rules}
        - SOFT: {soft_rules}
        - MANDATORY: Every single person MUST have exactly one "OFF" day.

        HISTORY CONTEXT:
        {past_context}

        INSTRUCTIONS:
        - Use "Morning", "Afternoon", "Night", and "OFF" as shift labels.
        - Ensure every row starts with the Name and Designation (e.g., 'Mark (Doctor)').
        - Provide a 'Compliance Report' after the table.
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