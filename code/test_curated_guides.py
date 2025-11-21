"""Regression sweep for curated Easter-egg and quest guides.

Iterates over every curated entry plus its sample prompts to confirm the
assistant always emits the deterministic multi-step walkthrough (regardless of
whether the user explicitly says "busca"). Serves as the requested training
playlist for maps and popular games.
"""

from __future__ import annotations

import os
import sys
import unicodedata

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agente import AssistantCore, CURATED_GUIDE_METADATA


def _ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return normalized.encode("ascii", "ignore").decode("ascii")


def run_check() -> int:
    assistant = AssistantCore(voice_enabled=False)
    outputs: list[str] = []
    assistant.set_output_handler(outputs.append)
    failures: list[str] = []

    for canonical_id, meta in CURATED_GUIDE_METADATA.items():
        steps = meta.get("steps") or []
        prompts = meta.get("sample_prompts") or []
        if not steps or not prompts:
            continue
        titles = [step.get("title", "") for step in steps if step.get("title")]
        step_markers = tuple(f"{idx}." for idx in range(1, len(steps) + 1))
        for prompt in prompts:
            outputs.clear()
            assistant.handle_text(prompt)
            if not outputs:
                failures.append(f"{canonical_id}: sin respuesta para '{prompt}'")
                continue
            reply = outputs[-1]
            ascii_reply = _ascii(reply)
            if "Guia verificada" not in ascii_reply:
                failures.append(f"{canonical_id}: faltó el encabezado en '{prompt}' -> {reply}")
                continue
            if "Recuerda verificar la version del juego" not in ascii_reply:
                failures.append(f"{canonical_id}: faltó el recordatorio final en '{prompt}'")
            missing_titles = [title for title in titles if title and title not in reply]
            if missing_titles:
                failures.append(
                    f"{canonical_id}: no aparecieron los títulos {missing_titles} para '{prompt}'"
                )
                continue
            actual_steps = sum(1 for line in ascii_reply.splitlines() if line.strip().startswith(step_markers))
            if actual_steps < len(steps):
                failures.append(
                    f"{canonical_id}: solo se detectaron {actual_steps}/{len(steps)} pasos para '{prompt}'"
                )

    assistant.shutdown()

    if failures:
        print("❌ Fallaron las siguientes guías curadas:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("✅ Todas las guías curadas respondieron con los pasos verificados.")
    return 0


def main() -> None:
    raise SystemExit(run_check())


if __name__ == "__main__":
    main()
