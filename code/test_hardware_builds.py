"""Regression checks for the curated hardware dataset.

Ensures the assistant can answer concrete PC build prompts and trigger
hardware brainstorms when the user requests random suggestions.
"""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agente import AssistantCore, TOTAL_HARDWARE_BUILDS  # noqa: E402


def _build_assistant() -> AssistantCore:
    assistant = AssistantCore(voice_enabled=False)
    return assistant


def test_hardware_dataset_has_expected_volume() -> None:
    assert TOTAL_HARDWARE_BUILDS >= 2000, "Se esperaban al menos 2000 combinaciones de hardware entrenadas"


def test_specific_desktop_lookup_mentions_components() -> None:
    assistant = _build_assistant()
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    assistant.handle_text("Necesito armar una PC con RTX 4070 para gaming 1080p")
    assistant.shutdown()
    assert outputs, "El asistente no respondió a la consulta de PC"
    reply = outputs[-1].lower()
    assert "configuración entrenada" in reply, "Debe usar el encabezado de hardware entrenado"
    assert "rtx" in reply or "radeon" in reply, "Debe reflejar la familia de GPU solicitada"
    assert "componentes sugeridos" in reply, "Debe listar los componentes principales"


def test_laptop_brainstorm_when_user_is_unsure() -> None:
    assistant = _build_assistant()
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    assistant.handle_text("Elige por mi una laptop para edición de video y movilidad")
    assistant.shutdown()
    assert outputs, "El asistente no entregó opciones de laptop"
    reply = outputs[-1].lower()
    assert "otras ideas" in reply, "Debe activar el modo brainstorming de hardware"
    assert "laptop" in reply, "Debe mencionar que se trata de laptops"
    assert str(TOTAL_HARDWARE_BUILDS) in reply, "Debe recordar el tamaño del dataset de hardware"


def test_component_detail_request_returns_reasoning() -> None:
    assistant = _build_assistant()
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    assistant.handle_text("Dame detalles de la GPU RTX 4070, por que es buena opcion para gaming 1440p")
    assistant.shutdown()
    assert outputs, "El asistente no respondió con el detalle solicitado"
    reply = outputs[-1].lower()
    assert "detalle entrenado" in reply, "Debe indicar que se trata de una ficha entrenada"
    assert "gpu" in reply, "Debe dejar claro que describe la GPU"
    assert "objetivo" in reply, "Debe explicar contra qué objetivo o resolución se eligió"
