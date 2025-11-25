"""Regression checks for the curated cooking dataset.

Verifies that the assistant can answer concrete recipe prompts and triggers the
random suggestion flow when the user says "no se que cocinar hoy".
"""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agente import AssistantCore, TOTAL_CURATED_RECIPES  # noqa: E402


def _build_assistant() -> AssistantCore:
    assistant = AssistantCore(voice_enabled=False)
    return assistant


def test_recipe_dataset_has_expected_volume() -> None:
    assert TOTAL_CURATED_RECIPES >= 300, "Se esperaban al menos 300 recetas entrenadas"


def test_specific_recipe_lookup() -> None:
    assistant = _build_assistant()
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    assistant.handle_text("Necesito la receta de tacos de plancha de pollo al limon estilo mexicana")
    assistant.shutdown()
    assert outputs, "El asistente no respondió a la petición de receta específica"
    reply = outputs[-1].lower()
    assert "receta entrenada" in reply, "Debe incluir el encabezado de receta entrenada"
    assert "tacos de plancha" in reply, "Debe referenciar el nombre del platillo solicitado"
    assert "pasos" in reply, "Se esperan pasos enumerados en la respuesta"


def test_recipe_brainstorm_when_user_is_unsure() -> None:
    assistant = _build_assistant()
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    assistant.handle_text("No se que cocinar hoy para la cena, dame opciones")
    assistant.shutdown()
    assert outputs, "El asistente no entregó ideas de cocina"
    reply = outputs[-1].lower()
    assert "ideas frescas" in reply, "Debe activar el modo aleatorio"
    assert "recetas entrenadas" in reply, "Debe recordar el tamaño del dataset"
    assert reply.count("tip:") >= 2, "Se esperan varios tips dentro de la lluvia de ideas"


def test_recipe_alias_request_without_keyword() -> None:
    assistant = _build_assistant()
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    assistant.handle_text("A ver dame detalles de la ensalada templada de camarones salteados")
    assistant.shutdown()
    assert outputs, "El asistente no respondió al alias de receta"
    reply = outputs[-1].lower()
    assert "receta entrenada" in reply, "Debe confirmar que proviene del recetario curado"
    assert "ensalada templada" in reply, "Debe mencionar el nombre del platillo solicitado"
    assert "pasos" in reply, "Debe describir los pasos cuando se piden detalles"
