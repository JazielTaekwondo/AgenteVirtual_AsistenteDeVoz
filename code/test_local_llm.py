"""Pequeño script para verificar rápidamente el modelo local configurado.

Uso:
    .\.venv\Scripts\python.exe code\test_local_llm.py "Escribe un haiku sobre gatos"
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import agente


def build_prompt(question: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "Eres un asistente hispanohablante conciso."
                " Si el usuario no aclara un tema, pide más contexto antes de inventar datos."
            ),
        },
        {"role": "user", "content": question},
    ]


def main() -> None:
    question = "¿Cuál es la capital de Francia?"
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    reply = agente.query_llm(build_prompt(question))
    print("Respuesta del modelo local:\n")
    print(reply)


if __name__ == "__main__":
    main()
