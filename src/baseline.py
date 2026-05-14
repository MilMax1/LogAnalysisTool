from llm_client import ask_llm

def run_baseline(log_text: str) -> str:
    prompt = f"""
Analysera följande loggar och skapa ett beslutsunderlag för felsökning.

Inkludera:
- Sammanfattning
- Möjliga felorsaker
- Relevanta logghändelser
- Rekommenderade åtgärder

Loggar:
{log_text}
"""
    return ask_llm(prompt)