"""Generate a curated anime catalog (>3,000 entries of seasons and films).

The dataset is deterministic so the assistant can ship with an offline
knowledge base for anime recommendations. Running this script writes
`data/curated_anime_catalog.json`.
"""

from __future__ import annotations

import itertools
import json
import math
import random
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "curated_anime_catalog.json"
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

RNG = random.Random(20251122)

PREFIXES = [
    "Neon",
    "Crimson",
    "Azure",
    "Ivory",
    "Shadow",
    "Star",
    "Mythic",
    "Aurora",
    "Cyber",
    "Radiant",
    "Echo",
    "Quantum",
    "Iron",
]

CORES = [
    "Nova",
    "Spiral",
    "Phoenix",
    "Serenity",
    "Chronicle",
    "Requiem",
    "Impact",
    "Mirage",
    "Harmony",
    "Genesis",
    "Pulse",
    "Frontier",
    "Odyssey",
]

SUFFIXES = [
    "Saga",
    "Symphony",
    "Eclipse",
    "Protocol",
    "Hearts",
    "Legends",
    "Circuit",
    "Bloom",
    "Drifters",
    "Horizons",
    "Verse",
    "Mirrors",
]

ARC_LABELS = [
    "Arcadia",
    "Resonance",
    "Catalyst",
    "Celestia",
    "Vortex",
    "Sanctum",
    "Equinox",
    "Paradox",
]

GENRES = [
    "shonen",
    "seinen",
    "shojo",
    "josei",
    "accion",
    "drama",
    "romance",
    "comedia",
    "fantasia",
    "ciencia ficcion",
    "misterio",
    "terror",
    "deportes",
    "slice of life",
    "musical",
]

THEMES = [
    "mechas",
    "viajes temporales",
    "idol",
    "magia",
    "samurai",
    "vampiros",
    "espionaje",
    "ia",
    "escolar",
    "gastronomia",
    "space opera",
    "artes marciales",
    "psicologico",
    "detectives",
    "medieval",
]

TONES = ["epica", "intensa", "relajada", "oscura", "optimista", "melancolica"]
AGE_RATINGS = ["PG", "PG-13", "R", "TV-MA"]
STUDIOS = [
    "Studio Aurora",
    "Raijin Works",
    "Moonriver",
    "Polygon Lotus",
    "Hikari Forge",
    "Silver Crane",
    "Blue Ember",
    "Atlas Frame",
]

MOODS = ["motivante", "nostalgica", "confort", "sci-fi", "sports", "emocional"]
STREAMING = ["AniPlus", "CrunchWave", "OtakuNow", "StreamNippon"]
FORMAT_CHOICES = ["TV", "ONA", "OVA"]

FRANCHISE_TARGET = 520


def _franchise_names(limit: int) -> List[str]:
    combos = itertools.product(PREFIXES, CORES, SUFFIXES)
    names: List[str] = []
    for prefix, core, suffix in combos:
        full = f"{prefix} {core} {suffix}".strip()
        names.append(" ".join(full.split()))
        if len(names) >= limit:
            break
    return names


def _season_entry(franchise: str, idx: int, season_number: int, base_year: int, base_genres: List[str], base_themes: List[str]) -> Dict[str, object]:
    release_year = min(2025, base_year + season_number)
    era_tag = "era_clasico" if release_year < 2010 else "era_moderno"
    episode_options = [12, 13, 24, 36]
    episodes = episode_options[(idx + season_number) % len(episode_options)]
    duration_minutes = episodes * 24
    length_tag = "season_larga" if episodes >= 24 else "season_corta"
    format_choice = FORMAT_CHOICES[(idx + season_number) % len(FORMAT_CHOICES)]
    arc_label = ARC_LABELS[(idx + season_number) % len(ARC_LABELS)]
    title = f"{franchise} - Temporada {season_number}: {arc_label}"
    genres = list(dict.fromkeys(base_genres + RNG.sample(GENRES, 2)))[:4]
    themes = list(dict.fromkeys(base_themes + RNG.sample(THEMES, 2)))[:3]
    summary = (
        f"{franchise} regresa con la saga {arc_label}, mezclando {genres[0]} y {themes[0]}"
        f" mientras los protagonistas enfrentan un conflicto en {format_choice} durante {release_year}."
    )
    studio = STUDIOS[(idx + season_number) % len(STUDIOS)]
    tone = TONES[(idx + season_number) % len(TONES)]
    rating = AGE_RATINGS[(idx + season_number) % len(AGE_RATINGS)]
    mood = MOODS[(idx + season_number) % len(MOODS)]
    entry = {
        "franchise": franchise,
        "title": title,
        "type": "season",
        "format": format_choice,
        "season_number": season_number,
        "release_year": release_year,
        "episodes": episodes,
        "duration": f"{episodes} episodios de 24 min",
        "watch_time_hours": round(duration_minutes / 60, 1),
        "length_tag": length_tag,
        "era_tag": era_tag,
        "genres": genres,
        "themes": themes,
        "tone": tone,
        "age_rating": rating,
        "studio": studio,
        "score_tier": "must_watch" if season_number <= 2 else "solid_pick",
        "mood_tags": [mood],
        "streaming": RNG.sample(STREAMING, k=2),
        "summary": summary,
        "aliases": [franchise, f"{franchise} temporada {season_number}", f"{franchise} {arc_label}"],
        "tags": list({
            franchise.lower(),
            f"temporada {season_number}",
            format_choice.lower(),
            tone,
            rating.lower(),
            studio.lower(),
            *(genre.lower() for genre in genres),
            *(theme.lower() for theme in themes),
            mood,
            str(release_year),
            length_tag,
            era_tag,
        }),
    }
    return entry


def _movie_entry(franchise: str, idx: int, movie_number: int, base_year: int, base_genres: List[str], base_themes: List[str]) -> Dict[str, object]:
    release_year = min(2025, base_year + 5 + movie_number)
    era_tag = "era_clasico" if release_year < 2010 else "era_moderno"
    duration = 95 + ((idx + movie_number) % 30)
    length_tag = "pelicula_larga" if duration >= 110 else "pelicula_corta"
    title = f"{franchise}: Película {movie_number}"
    genres = list(dict.fromkeys(base_genres + RNG.sample(GENRES, 1)))[:4]
    themes = list(dict.fromkeys(base_themes + RNG.sample(THEMES, 1)))[:3]
    summary = (
        f"Película {movie_number} de {franchise} con {genres[0]} y {themes[0]}"
        f" en un final cinematográfico estrenado en {release_year}."
    )
    studio = STUDIOS[(idx + movie_number) % len(STUDIOS)]
    tone = TONES[(idx + movie_number + 2) % len(TONES)]
    rating = AGE_RATINGS[(idx + movie_number + 1) % len(AGE_RATINGS)]
    mood = MOODS[(idx + movie_number + 1) % len(MOODS)]
    entry = {
        "franchise": franchise,
        "title": title,
        "type": "movie",
        "format": "Film",
        "release_year": release_year,
        "duration": f"Película {duration} min",
        "watch_time_hours": round(duration / 60, 1),
        "length_tag": length_tag,
        "era_tag": era_tag,
        "genres": genres,
        "themes": themes,
        "tone": tone,
        "age_rating": rating,
        "studio": studio,
        "score_tier": "essential" if movie_number == 1 else "special",
        "mood_tags": [mood],
        "streaming": RNG.sample(STREAMING, k=2),
        "summary": summary,
        "aliases": [franchise, f"{franchise} movie {movie_number}", f"{franchise} pelicula"],
        "tags": list({
            franchise.lower(),
            "pelicula",
            "film",
            tone,
            rating.lower(),
            studio.lower(),
            *(genre.lower() for genre in genres),
            *(theme.lower() for theme in themes),
            mood,
            str(release_year),
            length_tag,
            era_tag,
        }),
    }
    return entry


def main() -> None:
    franchises = _franchise_names(FRANCHISE_TARGET)
    entries: List[Dict[str, object]] = []
    entry_id = 1
    for idx, franchise in enumerate(franchises):
        base_year = 1994 + (idx % 25)
        base_genres = RNG.sample(GENRES, 3)
        base_themes = RNG.sample(THEMES, 2)
        seasons = 4 + (idx % 3)  # 4-6 seasons por franquicia
        movies = 2 + (idx % 2)  # 2 o 3 películas
        for season_number in range(1, seasons + 1):
            entry = _season_entry(franchise, idx, season_number, base_year, base_genres, base_themes)
            entry["id"] = f"anime_{entry_id:05d}"
            entries.append(entry)
            entry_id += 1
        for movie_number in range(1, movies + 1):
            entry = _movie_entry(franchise, idx, movie_number, base_year, base_genres, base_themes)
            entry["id"] = f"anime_{entry_id:05d}"
            entries.append(entry)
            entry_id += 1
    with DATA_PATH.open("w", encoding="utf-8") as handler:
        json.dump(entries, handler, ensure_ascii=False, indent=2)
    print(f"Wrote {len(entries)} anime entries to {DATA_PATH}")


if __name__ == "__main__":
    main()
