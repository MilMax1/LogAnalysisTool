from llm_client import ask_llm
from rule_engine import analyze_with_rules, build_structured_context
from template_context import build_template_context


def run_workflow(log_text: str, scenario_id: str, block_id: str) -> str:
    rule_result = analyze_with_rules(log_text)
    rule_context = build_structured_context(rule_result)

    template_context = build_template_context(block_id)
    print("----- TEMPLATE CONTEXT START -----")
    print(template_context)
    print("----- TEMPLATE CONTEXT END -----")
    combined_context = f"""
{rule_context}

---

{template_context}
"""

    prompt = f"""
Du analyserar ett loggscenario från HDFS, ett distribuerat filsystem.

Du får både rå loggdata och en strukturerad kontext som skapats av arbetsflödet.
Använd den strukturerade kontexten som stöd, men basera slutsatser på loggraderna.

Viktigt om strukturerad kontext:
- Den strukturerade kontexten visar endast potentiellt relevanta loggrader, mönster och event-template counts.
- Matchade regler, kandidathändelser eller event counts betyder inte automatiskt att scenariot är en anomali.
- Event-template counts är härledda från loggarna men är inte ground truth.
- Använd kontexten som stöd för analysen, men avgör klassificeringen utifrån hela händelseförloppet.

Strukturerad kontext:
{combined_context}

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