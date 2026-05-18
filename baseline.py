from llm_client import ask_llm


def run_baseline(log_text: str, scenario_id: str) -> str:
    prompt = f"""
Du analyserar ett loggscenario från HDFS, ett distribuerat filsystem.

Uppgift:
1. Bedöm om loggscenariot är "Normal" eller "Anomaly".
2. Identifiera de viktigaste logghändelserna som stödjer bedömningen.
3. Ange vilka loggrader som stödjer varje identifierad händelse.
4. Skilj mellan observationer i loggdatan och möjliga tolkningar.
5. Ge korta rekommenderade nästa steg för felsökning.

Viktigt:
- Returnera endast giltig JSON.
- Använd exakt värdena "Normal" eller "Anomaly" för classification.
- supporting_log_lines ska innehålla radnummer från loggtexten, exempelvis [1, 3, 5].
- Om scenariot verkar normalt, använd "classification": "Normal".
- Hitta inte på information som inte stöds av loggraderna.
- Om du är osäker, ange confidence som "low" eller "medium".

JSON-format:
{{
  "scenario_id": "{scenario_id}",
  "classification": "Normal|Anomaly",
  "confidence": "low|medium|high",
  "summary": "...",
  "events": [
    {{
      "event_type": "...",
      "supporting_log_lines": [1],
      "observation": "...",
      "interpretation": "...",
      "recommended_next_step": "..."
    }}
  ],
  "unsupported_claims": []
}}

Loggscenario:
{log_text}
"""
    return ask_llm(prompt)