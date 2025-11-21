"""Lightweight regression for image reasoning heuristics.

This test feeds handcrafted metrics into `_describe_scene_from_metrics` to ensure
hardware-like scenes (motherboards, PCBs) trigger the new explanatory text.
"""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agente import _describe_scene_from_metrics


def test_detects_pcb_like_scene() -> None:
    metrics = [
        {
            "brightness": 120.0,
            "saturation": 180.0,
            "hue": 65.0,
            "value": 170.0,
            "edge_density": 0.14,
            "faces": 0.0,
            "green_ratio": 0.42,
            "line_count": 48.0,
        }
    ]
    description = _describe_scene_from_metrics(metrics).lower()
    assert "placa" in description or "hardware" in description


def main() -> None:
    test_detects_pcb_like_scene()
    print("✅ Heurística de placa madre verificada.")


if __name__ == "__main__":
    main()
