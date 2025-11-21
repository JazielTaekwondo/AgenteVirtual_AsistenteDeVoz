"""Quick conversational regression tests for AssistantCore.

Run this script to ensure the agent can answer a diverse batch of
requests without lanzar errores. It exercises greetings, búsqueda,
recomendaciones y reproducción.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("AGENTE_HEADLESS", "1")

import agente


def run_prompts(prompts: List[str]) -> None:
    assistant = agente.AssistantCore(voice_enabled=False)
    transcript: List[str] = []

    def capture(text: str) -> None:
        transcript.append(text)
        print(f"Asistente → {text}")

    assistant.set_output_handler(capture)

    for prompt in prompts:
        print(f"\nUsuario → {prompt}")
        assistant.handle_text(prompt)
        # Give the LLM a brief pause to avoid rate limits on some providers.
        time.sleep(0.5)

    print("\nResumen de respuestas capturadas:")
    for idx, reply in enumerate(transcript, 1):
        print(f" {idx:02d}. {reply}")


if __name__ == "__main__":
    sample_prompts = [
        "Hola, ¿cómo estás hoy?",
        "¿Qué hora es?",
        "Necesito una ruta para llegar a la plaza central desde mi casa",
        "Recomiéndame una canción alegre",
        "Reproduce música relajante en YouTube",
        "Buscá información sobre la energía solar",
        "Necesito ideas para motivar a un equipo remoto",
        "Recomiéndame un anime de ciencia ficción",
        "Crea un documento sobre hábitos saludables",
    ]
    run_prompts(sample_prompts)
