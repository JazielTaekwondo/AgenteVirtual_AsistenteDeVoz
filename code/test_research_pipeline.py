import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import agente


def main() -> None:
    query = "pasos easter egg origins black ops 2"
    summary, sources = agente.summarize_web_research(
        query,
        limit=0,
        force_steps=True,
        alt_queries=None,
        additional_context=agente.detect_curated_game_entries(query.lower()),
    )
    print("Summary length:", len(summary))
    print("Summary preview:", summary[:400])
    print("Sources:", sources[:3])


if __name__ == "__main__":
    main()
