"""Battery of 50 general-knowledge prompts to validate deterministic answers.

This script instantiates AssistantCore without voice, routes each curated
question through the normal pipeline, and ensures the predefined answer is
returned verbatim. It helps catch regressions in the trivia knowledge base
without requiring external LLM calls.
"""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agente import AssistantCore, GENERAL_KNOWLEDGE_ITEMS


def run_suite() -> int:
    assistant = AssistantCore(voice_enabled=False)
    captured: list[str] = []
    assistant.set_output_handler(lambda text: captured.append(text))
    failures: list[tuple[int, str, str]] = []

    for idx, item in enumerate(GENERAL_KNOWLEDGE_ITEMS, start=1):
        captured.clear()
        prompt = item["question"]
        assistant.handle_text(prompt)
        if not captured:
            failures.append((idx, prompt, "sin respuesta"))
            continue
        reply = captured[-1]
        expected = item["answer"]
        if expected not in reply:
            failures.append((idx, prompt, reply))

    assistant.shutdown()

    if not failures:
        print("✅ 50 preguntas de cultura general respondidas correctamente.")
        return 0

    print("❌ Fallaron las siguientes preguntas de la batería:")
    for idx, question, reply in failures:
        print(f"  {idx:02d}. {question}\n      Respuesta obtenida: {reply}")
    return 1


def main() -> None:
    exit_code = run_suite()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
