import streamlit as st
from google import genai
from google.genai import types

MODEL_NAME = "gemini-3-flash-preview"

class RosterAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_roster(self, system_rules, hard_rules, soft_rules):
        # The prompt defines the 10 employees and their specific roles
        prompt = f"""
        ACT AS: A Senior Hospital Staffing Coordinator.
        GOAL: Generate a 7-day roster (Mon-Sun) for 10 employees.
        
        STAFF MEMBERS:
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

        SHIFT DEFINITIONS:
        - Morning: 9:00am - 6:00pm
        - Afternoon: 1:00pm - 10:00pm
        - Night: 10:00pm - 7:00am
        - OFF: Holiday/Rest

        RULES HIERARCHY:
        
        [SYSTEM RULES]
        {system_rules}
        - MANDATORY: Every person must have exactly ONE 'OFF' day in the 7-day period.

        [HARD RULES - MUST FOLLOW]
        {hard_rules}

        [SOFT RULES - PREFERENCES]
        {soft_rules}

        OUTPUT FORMAT:
        Return ONLY a Markdown Table with columns [Employee, Mon, Tue, Wed, Thu, Fri, Sat, Sun].
        Below the table, add a 'Compliance Report' bullet list explaining if any rules were broken and why.
        """

        resp = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1, # Keep it logical/deterministic
                max_output_tokens=2000
            )
        )
        return resp.text