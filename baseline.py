from llm_client import ask_llm


def run_baseline(log_text: str, scenario_id: str) -> str:
    prompt = f"""
Du analyserar ett loggscenario från HDFS, ett distribuerat filsystem.

Uppgift:
1. Bedöm om loggscenariot som helhet är "Normal" eller "Anomaly".
2. Identifiera de viktigaste logghändelserna som stödjer bedömningen.
3. Ange vilka loggrader som stödjer varje identifierad händelse.
4. Skilj mellan observationer i loggdatan och möjliga tolkningar.
5. Ge korta rekommenderade nästa steg för felsökning.

Viktigt:
- Returnera endast giltig JSON.
- Använd exakt värdena "Normal" eller "Anomaly" för classification.
- Klassificera inte scenariot som "Anomaly" enbart för att enstaka WARN-, Exception-, delete- eller invalid-rader förekommer. Bedöm händelseförloppet som helhet. Ett scenario kan dock vara "Anomaly" även utan ERROR-rader om flera loggrader tillsammans visar ett avvikande, inkonsekvent eller misslyckat blockförlopp.
- supporting_log_lines ska innehålla radnummer från loggtexten, exempelvis [1, 3, 5].
- Varje event ska ha severity: "normal", "warning", "error" eller "anomaly".
- Hitta inte på information som inte stöds av loggraderna.
- Om en möjlig tolkning är osäker och inte har tydligt stöd i loggraderna, placera den i unsupported_claims istället för att placera den som säker slutsats.
- Om du är osäker, ange confidence som "low" eller "medium".

JSON-format:
{{
  "scenario_id": "{scenario_id}",
  "classification": "Normal|Anomaly",
  "confidence": "low|medium|high",
  "classification_reason": "...",
  "summary": "...",
  "events": [
    {{
      "event_type": "...",
      "severity": "normal|warning|error|anomaly",
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