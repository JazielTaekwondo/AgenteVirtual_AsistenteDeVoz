"""Emotion modulation regression tests."""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agente import AssistantCore  # noqa: E402


def _build_assistant() -> AssistantCore:
    assistant = AssistantCore(voice_enabled=False)
    return assistant


def test_emotion_boost_command_raises_intensity() -> None:
    assistant = _build_assistant()
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    initial_intensity = assistant.emotion_state.intensity
    assistant.handle_text("Aumenta tu estado emocional")
    assistant.shutdown()
    assert outputs, "El asistente no respondió al comando de ánimo"
    reply = outputs[-1].lower()
    assert "más energía" in reply or "mas energia" in reply, "Debe indicar que aumenta su energía"
    assert assistant.emotion_state.current == "alegre", "Debe pasar a un estado alegre"
    assert assistant.emotion_state.intensity > initial_intensity, "La intensidad debe aumentar tras el comando"
