from google import genai
from google.genai import types

MODEL_NAME = "gemini-1.5-flash"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key, vertexai=False)

    def generate_roster(self, sys_rules, hard_rules, soft_rules, history):
        # Convert history list into context
        past_context = ""
        for i, entry in enumerate(history[-2:]):
            past_context += f"\nPrevious Version {i+1}:\n{entry}\n"

        prompt = f"""
        ACT AS: Senior Hospital Staffing Coordinator.
        
        STAFF & DESIGNATIONS:
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

        REQUIRED TABLE FORMAT:
        | Employee (Designation) | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
        | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

        CONSTRAINTS:
        - SYSTEM: {sys_rules}
        - HARD: {hard_rules}
        - SOFT: {soft_rules}
        - MANDATORY: Every person MUST have exactly one "OFF" day.

        HISTORY FROM PREVIOUS RUNS:
        {past_context if history else "No previous history."}

        INSTRUCTIONS:
        1. Use "Morning", "Afternoon", "Night", or "OFF".
        2. Conduct a self-audit: Does every row have one "OFF"?
        3. Output the Markdown table first, then a Compliance Report.
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