"""Regression checks for the curated anime catalog."""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agente import AssistantCore, TOTAL_CURATED_ANIME_TITLES  # noqa: E402


def _build_assistant() -> AssistantCore:
    assistant = AssistantCore(voice_enabled=False)
    return assistant


def test_anime_dataset_has_expected_volume() -> None:
    assert TOTAL_CURATED_ANIME_TITLES >= 3000, "Se esperaban al menos 3000 títulos de anime entrenados"


def test_specific_anime_lookup_mentions_dataset() -> None:
    assistant = _build_assistant()
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    assistant.handle_text("Recomiendame un anime shonen de mechas con drama politico")
    assistant.shutdown()
    assert outputs, "El asistente no entregó una recomendación concreta"
    reply = outputs[-1].lower()
    assert "anime entrenado" in reply, "Debe indicar que proviene del catálogo entrenado"
    assert "mecha" in reply or "mechas" in reply, "Debe reflejar el género solicitado"
    assert str(TOTAL_CURATED_ANIME_TITLES) in reply, "Debe recordar el tamaño del dataset"


def test_anime_brainstorm_triggers_with_random_prompt() -> None:
    assistant = _build_assistant()
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    assistant.handle_text("No se que anime ver, elige por mi una pelicula de romance slice of life")
    assistant.shutdown()
    assert outputs, "El asistente no generó ideas de anime"
    reply = outputs[-1].lower()
    assert "ideas de anime" in reply, "Debe activar el modo lluvia de ideas"
    assert "pelicula" in reply or "film" in reply, "Debe considerar el filtro de película"
