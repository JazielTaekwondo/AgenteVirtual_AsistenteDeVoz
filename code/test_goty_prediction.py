"""Regression check for GOTY 2025 forecast and memory awareness.

This script ensures the assistant now answers "¿Quién crees que gane el GOTY 2025?"
with a concrete favorite drawn from ANTICIPATED_GOTY_TITLES and, on repeated
questioning, acknowledges the stored prediction instead of rambling.
"""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agente import ANTICIPATED_GOTY_TITLES, AssistantCore


def run_check() -> int:
    assistant = AssistantCore(voice_enabled=False)
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)

    prompt = "¿Quién crees que va a ganar el GOTY 2025?"

    outputs.clear()
    assistant.handle_text(prompt)
    if not outputs:
        print("❌ No hubo respuesta para la primera pregunta del GOTY 2025.")
        assistant.shutdown()
        return 1
    first_reply = outputs[-1]

    assistant.handle_text(prompt)
    if len(outputs) < 2:
        print("❌ No se registró la segunda respuesta de seguimiento.")
        assistant.shutdown()
        return 1
    second_reply = outputs[-1]

    assistant.shutdown()

    favorite = ANTICIPATED_GOTY_TITLES[0]["title"]

    if favorite not in first_reply:
        print("❌ La respuesta inicial no mencionó al favorito fijado en ANTICIPATED_GOTY_TITLES.")
        print(f"   Respuesta: {first_reply}")
        return 1

    if "Sigo con la misma apuesta" not in second_reply:
        print("❌ La segunda respuesta no reconoció la memoria de la predicción previa.")
        print(f"   Respuesta: {second_reply}")
        return 1

    print("✅ Predicción del GOTY 2025 emitida y memoria verificada.")
    return 0


def main() -> None:
    raise SystemExit(run_check())


if __name__ == "__main__":
    main()
