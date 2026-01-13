import streamlit as st
from google import genai
from google.genai import types

# Use the standard stable name for Gemini 3 series in 2026
MODEL_NAME = "gemini-3-flash"

class RosterAgent:
    def __init__(self, api_key):
        # vertexai=False ensures we use the standard API Key endpoint
        self.client = genai.Client(api_key=api_key, vertexai=False)

    def generate_roster(self, system_rules, hard_rules, soft_rules):
        """
        Cleans the inputs and prompts Gemini to generate a structured roster.
        """
        # 1. Clean inputs to prevent JSON malformation from hidden characters
        def clean_text(text):
            return text.encode("ascii", "ignore").decode().strip()

        sys_clean = clean_text(system_rules)
        hard_clean = clean_text(hard_rules)
        soft_clean = clean_text(soft_rules)

        # 2. Construct the specialized hospital prompt
        prompt = f"""
        ROLE: Senior Hospital Staffing Coordinator.
        TASK: Generate a 7-day staff roster (Mon-Sun) for a surgery unit.
        
        EMPLOYEES (10):
        - Mark (Doctor - Lead)
        - Shawn (Anesthesiologist)
        - Axel (Surgeon)
        - Sarah (Surgeon)
        - Elena (Nurse)
        - David (Nurse)
        - Chloe (Nurse)
        - James (Nurse)
        - Maya (Nurse)
        - Leo (Nurse)

        SHIFT DEFINITIONS:
        - Morning: 9:00am - 6:00pm
        - Afternoon: 1:00pm - 10:00pm
        - Night: 10:00pm - 7:00am
        - OFF: Holiday / Rest Day

        SCHEDULING CONSTRAINTS:
        [SYSTEM RULES]:
        {sys_clean}
        - MANDATORY: Every person must have exactly ONE 'OFF' day in the 7-day period.

        [HARD RULES]:
        {hard_clean}

        [SOFT RULES]:
        {soft_clean}

        INSTRUCTIONS:
        1. Create a logical 7-day schedule.
        2. Ensure every employee has exactly one holiday.
        3. Prioritize Hard Rules over Soft Rules.
        
        OUTPUT FORMAT:
        Return ONLY a Markdown Table [Employee, Mon, Tue, Wed, Thu, Fri, Sat, Sun].
        Below the table, provide a 'Compliance Report' explaining any unavoidable rule breaks.
        """

        try:
            # 3. API Call with updated 2026 configurations
            resp = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for logical accuracy
                    max_output_tokens=2500,
                    # Crucial: include_thoughts=False prevents 400 ClientErrors on reasoning tasks
                    thinking_config=types.ThinkingConfig(include_thoughts=False)
                )
            )
            
            # Return the text content of the response
            if resp.text:
                return resp.text
            else:
                return "⚠️ Model returned an empty response. Please try adjusting your rules."

        except Exception as e:
            # Catching and returning the specific error for UI debugging
            return f"🚨 **Gemini API Error:** {str(e)}\n\n*Check your API key and quota in the Streamlit Secrets.*"
