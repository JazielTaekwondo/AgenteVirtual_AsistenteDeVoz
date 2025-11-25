import datetime
import heapq
import html
import json
import os
import random
import re
import sys
import threading
import time
import queue
import platform
import unicodedata
import urllib.parse
import webbrowser
import math
from collections import Counter, defaultdict
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import requests
import pyttsx3
import speech_recognition as sr
from openai import OpenAI

try:
    from duckduckgo_search import DDGS
except ImportError:  # pragma: no cover - dependencia opcional
    DDGS = None  # type: ignore[assignment]

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:  # pragma: no cover - utilidad opcional
    ChromeDriverManager = None  # type: ignore[assignment]

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import TimeoutException, WebDriverException
    _SELENIUM_IMPORTED = True
except ImportError:  # pragma: no cover - Selenium puede faltar
    webdriver = None  # type: ignore[assignment]
    ChromeOptions = None  # type: ignore[assignment]
    Service = None  # type: ignore[assignment]
    By = None  # type: ignore[assignment]
    Keys = None  # type: ignore[assignment]
    EC = None  # type: ignore[assignment]
    WebDriverWait = None  # type: ignore[assignment]
    TimeoutException = None  # type: ignore[assignment]
    WebDriverException = None  # type: ignore[assignment]
    _SELENIUM_IMPORTED = False

SELENIUM_AVAILABLE = bool(_SELENIUM_IMPORTED and ChromeDriverManager is not None)

try:
    import cv2  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - OpenCV es opcional
    cv2 = None  # type: ignore[assignment]

try:
    import numpy as np  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - NumPy es opcional
    np = None  # type: ignore[assignment]

try:
    from transformers import pipeline  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - Transformes es opcional
    pipeline = None  # type: ignore[assignment]

try:
    from PIL import Image  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - PIL es opcional
    Image = None  # type: ignore[assignment]

try:
    from bs4 import BeautifulSoup  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - BeautifulSoup es opcional
    BeautifulSoup = None  # type: ignore[assignment]

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter import font as tkfont
except ImportError:  # pragma: no cover - interfaz gráfica opcional
    tk = None  # type: ignore[assignment]
    filedialog = None  # type: ignore[assignment]
    messagebox = None  # type: ignore[assignment]
    ttk = None  # type: ignore[assignment]
    tkfont = None  # type: ignore[assignment]

GUI_AVAILABLE = tk is not None

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CURATED_GUIDES_PATH = DATA_DIR / "curated_game_guides.json"
CURATED_RECIPES_PATH = DATA_DIR / "curated_recipes.json"
CURATED_HARDWARE_PATH = DATA_DIR / "curated_hardware_builds.json"
CURATED_ANIME_PATH = DATA_DIR / "curated_anime_catalog.json"

RAW_COOKING_KEYWORDS = {
    "receta",
    "recetas",
    "cocina",
    "cocinar",
    "cocine",
    "platillo",
    "platillos",
    "plato",
    "menu",
    "ingredientes",
    "preparar comida",
    "que cocinar",
    "que comer",
    "ideas de comida",
    "sugerencias de comida",
    "no se que cocinar",
}

RAW_RECIPE_RANDOM_PATTERNS = [
    "no se que cocinar",
    "no se que comer",
    "no tengo idea de que cocinar",
    "que puedo cocinar hoy",
    "que preparo hoy",
    "no se que hacer de comer",
    "dame opciones de comida",
]

RAW_RECIPE_FILTER_HINTS = {
    "desayuno": {"desayuno"},
    "almuerzo": {"comida"},
    "comida": {"comida"},
    "cena": {"cena"},
    "noche": {"cena"},
    "ligera": {"comida ligera"},
    "light": {"comida ligera"},
    "sin carne": {"vegana", "plant_based"},
    "vegana": {"vegana", "plant_based"},
    "vegetariana": {"vegana"},
    "pescado": {"pescado", "pescetariana"},
    "marisco": {"mariscos", "pescetariana"},
    "pollo": {"pollo"},
    "res": {"res"},
    "cerdo": {"cerdo"},
    "garbanzo": {"garbanzos"},
    "lenteja": {"lentejas"},
    "tofu": {"tofu"},
    "hongos": {"hongos"},
    "coliflor": {"coliflor"},
}

RAW_HARDWARE_KEYWORDS = {
    "pc",
    "computadora",
    "computador",
    "torre",
    "armar pc",
    "componentes",
    "setup",
    "gpu",
    "tarjeta grafica",
    "tarjeta gráfica",
    "cpu",
    "procesador",
    "ryzen",
    "intel",
    "laptop",
    "notebook",
    "portatil",
    "portátil",
    "ultrabook",
    "workstation",
    "estacion de trabajo",
    "estación de trabajo",
    "rtx",
    "radeon",
    "intel arc",
}

RAW_HARDWARE_DESKTOP_KEYWORDS = {
    "pc",
    "computadora",
    "armar",
    "componentes",
    "torre",
    "desktop",
    "equipo armado",
}

RAW_HARDWARE_LAPTOP_KEYWORDS = {
    "laptop",
    "portatil",
    "portátil",
    "notebook",
    "ultrabook",
    "movil",
    "móvil",
}

RAW_HARDWARE_RANDOM_PATTERNS = [
    "elige por mi",
    "elige por mí",
    "no se que pc",
    "no sé que pc",
    "no se que laptop",
    "no sé que laptop",
    "dame opciones de pc",
    "dame opciones de laptop",
]

RAW_HARDWARE_FILTER_HINTS = {
    "1080p": {"1080p", "gaming_1080p"},
    "1440p": {"1440p", "gaming_1440p"},
    "4k": {"4k", "gaming_4k"},
    "edicion": {"creator", "edicion_video"},
    "edición": {"creator", "edicion_video"},
    "render": {"render"},
    "cad": {"cad"},
    "ingenieria": {"cad", "simulacion"},
    "simulacion": {"simulacion"},
    "simulación": {"simulacion"},
    "ia": {"ai_training", "ai_workstation"},
    "inteligencia artificial": {"ai_training"},
    "machine learning": {"ai_training"},
    "streaming": {"streaming"},
    "creator": {"creator"},
    "youtube": {"streaming"},
    "tiktok": {"streaming"},
    "barata": {"budget_entry"},
    "economica": {"budget_entry"},
    "económica": {"budget_entry"},
    "presupuesto": {"budget_entry"},
    "mid range": {"mid_high"},
    "gama alta": {"enthusiast"},
    "workstation": {"workstation"},
    "oficina": {"productividad"},
    "movilidad": {"movilidad", "ultrabook"},
    "ligera": {"ultrabook"},
    "bateria": {"movilidad"},
    "batería": {"movilidad"},
    "intel arc": {"intel_arc"},
    "arc": {"intel_arc"},
    "nvidia": {"nvidia", "rtx"},
    "amd": {"amd"},
    "ryzen": {"ryzen"},
    "threadripper": {"workstation"},
    "core ultra": {"intel"},
    "gaming": {"gaming"},
}

RAW_HARDWARE_DETAIL_TRIGGERS = [
    "detalle",
    "detalles",
    "detallame",
    "detállame",
    "explica",
    "explícame",
    "explicame",
    "por que",
    "porque",
    "razon",
    "razón",
    "motivo",
    "justifica",
    "vale la pena",
    "por que elegiste",
    "por qué elegiste",
    "quiero saber",
]

RAW_HARDWARE_COMPONENT_KEYWORDS = {
    "cpu": [
        "cpu",
        "procesador",
        "procesadora",
        "ryzen",
        "intel",
        "core",
        "apu",
    ],
    "gpu": [
        "gpu",
        "tarjeta grafica",
        "tarjeta gráfica",
        "grafica",
        "gráfica",
        "rtx",
        "gtx",
        "nvidia",
        "geforce",
        "radeon",
        "rx",
    ],
    "ram": [
        "ram",
        "memoria",
        "memoria ram",
    ],
    "storage": [
        "ssd",
        "almacenamiento",
        "disco",
        "hdd",
        "nvme",
        "m2",
        "m.2",
        "unidad",
    ],
    "motherboard": [
        "motherboard",
        "placa",
        "placa madre",
        "board",
    ],
    "psu": [
        "psu",
        "fuente",
        "fuente de poder",
        "power supply",
        "alimentacion",
        "alimentación",
    ],
    "cooling": [
        "cooler",
        "refrigeracion",
        "refrigeración",
        "disipador",
        "liquida",
        "liquída",
        "aire",
        "aio",
    ],
    "case": [
        "gabinete",
        "case",
        "torre",
        "chasis",
        "caja",
    ],
    "display": [
        "pantalla",
        "display",
    ],
    "battery": [
        "bateria",
        "batería",
    ],
    "weight": [
        "peso",
        "portabilidad",
        "ligera",
        "ligero",
    ],
}

RAW_ANIME_RANDOM_PATTERNS = [
    "no se que anime ver",
    "no sé que anime ver",
    "elige por mi anime",
    "elige por mí anime",
    "sorprendeme con anime",
    "sorpréndeme con anime",
    "dame cualquier anime",
]

RAW_ANIME_FILTER_HINTS = {
    "shonen": {"shonen"},
    "shounen": {"shonen"},
    "seinen": {"seinen"},
    "shojo": {"shojo"},
    "josei": {"josei"},
    "accion": {"accion"},
    "acción": {"accion"},
    "romance": {"romance"},
    "drama": {"drama"},
    "comedia": {"comedia"},
    "fantasia": {"fantasia"},
    "fantasía": {"fantasia"},
    "ciencia ficcion": {"ciencia ficcion"},
    "ciencia ficción": {"ciencia ficcion"},
    "scifi": {"ciencia ficcion"},
    "misterio": {"misterio"},
    "thriller": {"misterio"},
    "terror": {"terror"},
    "horror": {"terror"},
    "deportes": {"deportes"},
    "futbol": {"deportes"},
    "basket": {"deportes"},
    "mecha": {"mechas"},
    "mechas": {"mechas"},
    "viajes en el tiempo": {"viajes temporales"},
    "viajes temporales": {"viajes temporales"},
    "isekai": {"fantasia"},
    "magia": {"magia"},
    "idol": {"idol", "musical"},
    "musica": {"musical"},
    "música": {"musical"},
    "slice of life": {"slice of life"},
    "vida diaria": {"slice of life"},
    "escolar": {"escolar"},
    "samurai": {"samurai"},
    "espionaje": {"espionaje"},
    "gastronomia": {"gastronomia"},
    "gastronomía": {"gastronomia"},
    "pelicula": {"pelicula", "film"},
    "película": {"pelicula", "film"},
    "movie": {"pelicula", "film"},
    "film": {"pelicula", "film"},
    "temporada corta": {"season_corta"},
    "temporada larga": {"season_larga"},
    "pelicula larga": {"pelicula_larga"},
    "pelicula corta": {"pelicula_corta"},
    "clasico": {"era_clasico"},
    "clásico": {"era_clasico"},
    "retro": {"era_clasico"},
    "moderno": {"era_moderno"},
    "nuevo": {"era_moderno"},
}

RAW_ANIME_TOKEN_STOPWORDS = [
    "anime",
    "animes",
    "serie",
    "series",
    "ver",
    "verme",
    "busca",
    "buscar",
    "recomienda",
    "recomiendame",
    "recomiéndame",
    "dame",
    "quiero",
    "necesito",
    "algo",
    "para",
    "un",
    "una",
    "que",
    "cual",
    "pelicula",
    "película",
    "movie",
    "film",
    "temporada",
    "temporadas",
    "episodio",
    "episodios",
    "dime",
]

RAW_EMOTION_BOOST_KEYWORDS = [
    "aumenta tu estado emocional",
    "sube tu estado emocional",
    "sube tu energia",
    "sube tu energía",
    "ponte mas feliz",
    "ponte más feliz",
    "ponte mas alegre",
    "ponte más alegre",
    "ponte mas animado",
    "ponte más animado",
    "mas emocion",
    "más emocion",
    "mas energía",
    "mas energia",
    "quiero que hables con mas emocion",
    "quiero que hables con más emocion",
    "incrementa tu animo",
    "incrementa tu ánimo",
]

RAW_IDENTITY_QUERY_PATTERNS = [
    "quien eres",
    "quien eres tu",
    "quien eres tú",
    "quien sos",
    "que eres",
    "que eres tu",
    "como te llamas",
    "como te llamas tu",
    "cómo te llamas",
    "cómo te llamas tú",
    "cual es tu nombre",
    "cuál es tu nombre",
    "dime tu nombre",
    "di tu nombre",
    "quiero saber tu nombre",
    "dime como te llamas",
    "presentate",
    "preséntate",
    "hablame de ti",
    "quien demonios eres",
]

RAW_COMPLIMENT_REQUEST_PATTERNS = [
    "dime algo bonito",
    "di algo bonito",
    "dime algo lindo",
    "di algo lindo",
    "dime algo tierno",
    "quiero escuchar algo bonito",
    "quiero escuchar algo lindo",
    "dime algo que me anime",
    "dime algo motivador",
    "dime algo hermoso",
    "dime algo cariñoso",
    "dime algo dulce",
    "necesito algo bonito",
    "necesito algo lindo",
]

def _create_round_rect(canvas: "tk.Canvas", x1: float, y1: float, x2: float, y2: float, radius: float = 18, **kwargs: Any) -> int:
    radius = max(0, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
    points = [
        x1 + radius,
        y1,
        x2 - radius,
        y1,
        x2,
        y1,
        x2,
        y1 + radius,
        x2,
        y2 - radius,
        x2,
        y2,
        x2 - radius,
        y2,
        x1 + radius,
        y2,
        x1,
        y2,
        x1,
        y2 - radius,
        x1,
        y1 + radius,
        x1,
        y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)


if tk is not None:

    class ChatBubble(tk.Frame):
        def __init__(
            self,
            parent: Any,
            speaker: str,
            text: str,
            context: Optional[str],
            align: str,
            palette: Dict[str, str],
            fonts: Dict[str, "tkfont.Font"],
            wrap_width: int = 460,
            animate: bool = False,
        ) -> None:
            super().__init__(parent, bg=palette["card"], highlightthickness=0, bd=0)
            self.speaker = speaker
            self.text = text.strip()
            self.context = context
            self.align = align
            self.palette = palette
            self.fonts = fonts
            self.wrap_width = wrap_width
            self.animate = animate
            self.canvas = tk.Canvas(self, bg=palette["card"], highlightthickness=0, bd=0)
            self.canvas.pack(fill="both", expand=True)
            self._interactive_widgets: List[Any] = []
            self.link_font = tkfont.Font(family="Segoe UI", size=9, underline=True)
            self._render()

        def _render(self) -> None:
            self.canvas.delete("all")
            bubble_bg = self.palette["bubble_user"] if self.align == "right" else self.palette["bubble_assistant"]
            shadow_color = self.palette["bubble_shadow"]
            text_color = self.palette["bubble_user_text"] if self.align == "right" else self.palette["bubble_assistant_text"]
            label_color = self.palette["label_user"] if self.align == "right" else self.palette["label_assistant"]
            context_color = self.palette["context_text"]
            padding_x = 22
            padding_y = 16
            text_id = self.canvas.create_text(
                padding_x,
                padding_y,
                text=self.text,
                font=self.fonts["body"],
                fill=text_color,
                width=self.wrap_width,
                anchor="nw",
            )
            self.canvas.update_idletasks()
            bbox = self.canvas.bbox(text_id)
            if not bbox:
                bbox = (padding_x, padding_y, padding_x, padding_y)
            left = bbox[0] - padding_x
            top = bbox[1] - padding_y
            right = bbox[2] + padding_x
            bottom = bbox[3] + padding_y
            offset = 4
            shadow_shift = offset if self.align == "left" else -offset
            shadow_id = _create_round_rect(
                self.canvas,
                left + shadow_shift,
                top + offset,
                right + shadow_shift,
                bottom + offset,
                radius=24,
                fill=shadow_color,
                outline="",
            )
            bubble_id = _create_round_rect(
                self.canvas,
                left,
                top,
                right,
                bottom,
                radius=24,
                fill=bubble_bg,
                outline="",
            )
            self.canvas.tag_lower(shadow_id, bubble_id)
            self.canvas.tag_raise(text_id)
            speaker_label = "Tú" if self.align == "right" and self.speaker.lower() in {"tú", "tu", "you"} else self.speaker
            label_anchor = "ne" if self.align == "right" else "nw"
            label_x = right if self.align == "right" else left
            label_y = max(4, top - 12)
            self.canvas.create_text(
                label_x,
                label_y,
                text=speaker_label,
                font=self.fonts["label"],
                fill=label_color,
                anchor=label_anchor,
            )
            if self.context:
                context_id = self.canvas.create_text(
                    left + 16,
                    bottom + 8,
                    text=f"↳ {self.context}",
                    font=self.fonts["context"],
                    fill=context_color,
                    width=self.wrap_width,
                    anchor="nw",
                )
                bottom = (self.canvas.bbox(context_id) or (0, 0, 0, bottom))[3]
            link_extra = self._render_link_chips(left, bottom, right, bubble_bg)
            bottom += link_extra
            controls_extra = self._render_control_bar(left, bottom, right, bubble_bg)
            bottom += controls_extra
            total_height = bottom + 14
            total_width = right + 40
            self.canvas.configure(
                width=min(self.wrap_width + 140, total_width),
                height=total_height,
            )
            if self.animate and len(self.text) <= 600:
                self.canvas.itemconfigure(text_id, text="")
                self._animate_text(text_id, self.text, 0)

        def _animate_text(self, text_id: int, content: str, index: int) -> None:
            self.canvas.itemconfigure(text_id, text=content[:index])
            if index < len(content):
                self.after(8, lambda: self._animate_text(text_id, content, index + 1))

        def _copy_text(self) -> None:
            try:
                self.clipboard_clear()
                self.clipboard_append(self.text)
            except Exception:
                pass

        def _render_link_chips(self, left: float, bottom: float, right: float, bubble_bg: str) -> float:
            urls = URL_PATTERN.findall(self.text)
            if not urls:
                return 0.0
            chip_frame = tk.Frame(self.canvas, bg=bubble_bg)
            max_row_width = max(120, self.wrap_width - 60)
            row = 0
            col = 0
            current_width = 0
            for url in urls:
                display = url if len(url) <= 42 else url[:39] + "…"
                chip = tk.Label(
                    chip_frame,
                    text=display,
                    font=self.link_font,
                    fg="#7dd3fc",
                    bg=bubble_bg,
                    cursor="hand2",
                    padx=10,
                    pady=4,
                )
                chip_width = self.link_font.measure(display) + 32
                if current_width and current_width + chip_width > max_row_width:
                    row += 1
                    col = 0
                    current_width = 0
                chip.grid(row=row, column=col, padx=(0, 8), pady=(0, 6), sticky="w")
                chip.bind("<Button-1>", lambda event, target=url: self._open_link(target))
                chip.bind("<Enter>", lambda event, widget=chip: widget.configure(fg="#bae6fd"))
                chip.bind("<Leave>", lambda event, widget=chip: widget.configure(fg="#7dd3fc"))
                self._interactive_widgets.append(chip)
                col += 1
                current_width += chip_width
            self.canvas.create_window(left + 16, bottom + 8, anchor="nw", window=chip_frame)
            chip_frame.update_idletasks()
            return chip_frame.winfo_height() + 12

        def _open_link(self, url: str) -> None:
            try:
                webbrowser.open(url, new=2)
            except Exception:
                pass

        def _render_control_bar(self, left: float, bottom: float, right: float, bubble_bg: str) -> float:
            bar = tk.Frame(self.canvas, bg=bubble_bg)
            copy_label = tk.Label(
                bar,
                text="Copiar",
                font=self.fonts["context"],
                fg="#cbd5f5",
                bg=bubble_bg,
                cursor="hand2",
                padx=6,
            )
            copy_label.pack(side="right")
            copy_label.bind("<Button-1>", lambda event: self._copy_text())
            copy_label.bind("<Enter>", lambda event: copy_label.configure(fg="#e2e8ff"))
            copy_label.bind("<Leave>", lambda event: copy_label.configure(fg="#cbd5f5"))
            self._interactive_widgets.append(copy_label)
            self.canvas.create_window(right - 12, bottom + 6, anchor="ne", window=bar)
            bar.update_idletasks()
            return bar.winfo_height() + 8


else:

    class ChatBubble:  # type: ignore[override]
        pass


if tk is not None:

    class RoundedPanel(tk.Frame):
        def __init__(self, parent: Any, palette: Dict[str, str], radius: int = 24, padding: int = 16) -> None:
            super().__init__(parent, bg=palette["bg"], highlightthickness=0, bd=0)
            self.palette = palette
            self.radius = radius
            self.canvas = tk.Canvas(self, bg=palette["bg"], highlightthickness=0, bd=0)
            self.canvas.pack(fill="both", expand=True)
            self.inner = ttk.Frame(self.canvas, style="Panel.TFrame", padding=padding)
            self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
            self.canvas.bind("<Configure>", self._on_canvas_resize)
            self.inner.bind("<Configure>", self._on_inner_resize)
            self._redraw(self.winfo_reqwidth() or 100, self.inner.winfo_reqheight() + padding * 2)

        def _on_canvas_resize(self, event: Any) -> None:
            self._redraw(event.width, event.height)
            try:
                self.canvas.itemconfigure(self.window, width=max(0, event.width - 32))
            except Exception:
                pass

        def _on_inner_resize(self, event: Any) -> None:
            new_height = event.height + 32
            self.canvas.configure(height=new_height)
            self._redraw(self.canvas.winfo_width() or event.width + 32, new_height)

        def _redraw(self, width: float, height: float) -> None:
            if width <= 0 or height <= 0:
                return
            self.canvas.delete("panel_bg")
            _create_round_rect(
                self.canvas,
                10,
                12,
                max(20, width - 6),
                max(28, height - 2),
                radius=self.radius,
                fill=self.palette["panel_shadow"],
                outline="",
                tags=("panel_bg",),
            )
            _create_round_rect(
                self.canvas,
                4,
                4,
                max(12, width - 12),
                max(20, height - 12),
                radius=self.radius,
                fill=self.palette["panel"],
                outline="",
                tags=("panel_bg",),
            )


else:

    class RoundedPanel:  # type: ignore[override]
        pass

DEFAULT_OPENAI_MODEL = os.getenv("AGENTE_DEFAULT_OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_OPENROUTER_MODEL = os.getenv("AGENTE_DEFAULT_OPENROUTER_MODEL", "openrouter/auto")
DEFAULT_OPENROUTER_FALLBACK = os.getenv("AGENTE_DEFAULT_OPENROUTER_FALLBACK", "anthropic/claude-3.5-sonnet")
FALLBACK_ROUTER_KEY = os.getenv("AGENTE_FALLBACK_ROUTER_KEY", "")

PIPED_INSTANCES = [
    "https://piped.video",
    "https://piped.mha.fi",
    "https://piped.projectsegfau.lt",
]

WEB_SEARCH_BLOCKED_DOMAINS = {
    "pinterest.com",
    "facebook.com",
    "tiktok.com",
}

HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
URL_PATTERN = re.compile(r"(https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+)", re.IGNORECASE)


def _strip_html_tags(text: str) -> str:
    if not text:
        return ""
    cleaned = HTML_TAG_PATTERN.sub(" ", text)
    return re.sub(r"\s+", " ", cleaned).strip()

LLM_API_KEY = (
    os.getenv("AGENTE_LLM_API_KEY")
    or os.getenv("OPENAI_API_KEY")
    or os.getenv("OPENROUTER_API_KEY")
    or FALLBACK_ROUTER_KEY
)

LLM_BASE_URL = os.getenv("AGENTE_LLM_BASE_URL")
if not LLM_BASE_URL:
    LLM_BASE_URL = "https://api.openai.com/v1" if os.getenv("OPENAI_API_KEY") else "https://openrouter.ai/api/v1"

DEFAULT_LLM_MODEL = DEFAULT_OPENAI_MODEL if "openai.com" in LLM_BASE_URL else DEFAULT_OPENROUTER_MODEL
LLM_MODEL = os.getenv("AGENTE_LLM_MODEL", DEFAULT_LLM_MODEL)
LLM_FALLBACK_MODEL = os.getenv("AGENTE_LLM_FALLBACK_MODEL", DEFAULT_OPENROUTER_FALLBACK)
MAX_OUTPUT_TOKENS = int(os.getenv("AGENTE_LLM_MAX_TOKENS", "512"))
VERBOSE_LOGGING = os.getenv("AGENTE_VERBOSE", "0") == "1"
HEADLESS_MODE = os.getenv("AGENTE_HEADLESS", "0") == "1"
BROWSER_AUTOMATION_ENABLED = os.getenv("AGENTE_BROWSER_AUTOMATION", "1") != "0"
WHATSAPP_AUTOMATION_ENABLED = os.getenv("AGENTE_WHATSAPP_ENABLED", "1") != "0"
WHATSAPP_MAX_WAIT = int(os.getenv("AGENTE_WHATSAPP_WAIT", "45"))
WHATSAPP_PROFILE_DIR = os.getenv("AGENTE_WHATSAPP_PROFILE") or os.path.join(os.path.expanduser("~"), ".miau_whatsapp")
WHATSAPP_KEEP_BROWSER_OPEN = os.getenv("AGENTE_WHATSAPP_KEEP_BROWSER", "0") == "1"
WHATSAPP_MESSAGE_DELAY = float(os.getenv("AGENTE_WHATSAPP_DELAY", "0.4"))
WHATSAPP_AUTOMATION_AVAILABLE = WHATSAPP_AUTOMATION_ENABLED and SELENIUM_AVAILABLE
WHATSAPP_SCHEDULE_MIN_LEAD_SECONDS = int(os.getenv("AGENTE_WHATSAPP_MIN_LEAD", "30"))

IMAGE_CAPTION_MODEL = os.getenv("AGENTE_VISION_MODEL", "Salesforce/blip-image-captioning-large")
IMAGE_CAPTION_ENABLED = os.getenv("AGENTE_VISION_CAPTION", "1") != "0"
_IMAGE_CAPTION_PIPELINE: Optional[Any] = None
_IMAGE_CAPTION_FAILURE = False
_IMAGE_CAPTION_LOCK = threading.Lock()

WHATSAPP_TIME_PATTERN = re.compile(
    r"(?:(?:a|para|sobre)\s*las|alas)\s+(?P<hour>\d{1,2})(?:[:h\.](?P<minute>\d{2}))?\s*(?P<meridian>am|pm|a\.m\.|p\.m\.|hrs?|horas?)?",
    re.IGNORECASE,
)

WHATSAPP_AUTO_REPLY_KEYWORDS = {
    "respondele",
    "respóndele",
    "responde",
    "contesta",
    "contéstale",
    "contestale",
    "hazte cargo del chat",
    "contesta por mi",
    "responde por mi",
}
WHATSAPP_AUTO_REPLY_MIN_SECONDS = int(os.getenv("AGENTE_WHATSAPP_AUTO_REPLY_MIN_SECONDS", "30"))
WHATSAPP_AUTO_REPLY_MAX_MINUTES = int(os.getenv("AGENTE_WHATSAPP_AUTO_REPLY_MAX_MIN", "5"))
WHATSAPP_AUTO_REPLY_MAX_SECONDS = max(
    WHATSAPP_AUTO_REPLY_MIN_SECONDS,
    WHATSAPP_AUTO_REPLY_MAX_MINUTES * 60,
)
WHATSAPP_AUTO_REPLY_POLL_SECONDS = float(os.getenv("AGENTE_WHATSAPP_AUTO_REPLY_POLL", "2.0"))
WHATSAPP_AUTO_REPLY_DURATION_PATTERN = re.compile(
    r"(?:por|durante)\s+(?P<value>\d{1,3}|[a-záéíóúñ]+)\s+(?P<unit>min(?:uto)?s?|mins?)",
    re.IGNORECASE,
)

SCHEDULED_WHATSAPP_TASKS: List[Tuple[float, Dict[str, Any]]] = []
WHATSAPP_SCHEDULER_LOCK = threading.Lock()
WHATSAPP_SCHEDULER_EVENT = threading.Event()
WHATSAPP_SCHEDULER_THREAD: Optional[threading.Thread] = None
WHATSAPP_SCHEDULE_COUNTER = 0
WHATSAPP_TRIGGER_KEYWORDS = {
    "whatsapp",
    "what'sapp",
    "wasap",
    "guasap",
    "mensaje por wa",
    "mensaje por whatsapp",
    "envía por whatsapp",
    "envia por whatsapp",
    "manda whatsapp",
    "mandale whatsapp",
    "mensaje por wasap",
    "responde por whatsapp",
    "respondele por whatsapp",
    "respóndele por whatsapp",
}

VOICE_MODE_ACTIVATE_PATTERNS = {
    "ahora quiero hablarte por voz",
    "quiero hablarte por voz",
    "quiero hablar por voz",
    "hablemos por voz",
    "activa la voz",
    "activa el modo voz",
    "activa el modo de voz",
    "activa el hablar por voz",
    "activar la voz",
    "activar el modo voz",
    "enciende la voz",
    "habilita la voz",
    "habilita el modo voz",
    "habla por voz",
    "habla en voz",
    "modo voz",
}

VOICE_MODE_DEACTIVATE_PATTERNS = {
    "deten la voz",
    "deten el modo voz",
    "apaga la voz",
    "apaga el modo voz",
    "apaga el modo de voz",
    "desactiva la voz",
    "desactiva el modo voz",
    "desactiva el modo de voz",
    "desactiva el hablar por voz",
    "deja de hablar por voz",
    "deten el hablar por voz",
    "para la voz",
    "silencia la voz",
    "calla la voz",
    "no hables por voz",
    "quiero escribir",
    "quiero hablar por chat",
    "quiero solo escribir",
    "prefiero escribir",
    "regresemos a texto",
    "volver al chat",
    "volver al texto",
    "modo chat",
    "sal del modo voz",
}

VOICE_LISTEN_TIMEOUT = int(os.getenv("AGENTE_VOICE_TIMEOUT", "10"))
VOICE_PHRASE_TIME_LIMIT = int(os.getenv("AGENTE_VOICE_PHRASE_LIMIT", "25"))
VOICE_MAX_ATTEMPTS = int(os.getenv("AGENTE_VOICE_MAX_ATTEMPTS", "3"))
VOICE_FULL_CAL_DURATION = float(os.getenv("AGENTE_VOICE_CAL_DURATION", "1.6"))
VOICE_QUICK_CAL_DURATION = float(os.getenv("AGENTE_VOICE_CAL_QUICK", "0.6"))
VOICE_ENERGY_THRESHOLD = float(os.getenv("AGENTE_VOICE_ENERGY", "140"))
VOICE_ENERGY_MIN = float(os.getenv("AGENTE_VOICE_ENERGY_MIN", "55"))
VOICE_ENERGY_DECAY = float(os.getenv("AGENTE_VOICE_ENERGY_DECAY", "0.78"))

FUN_FACT_KEYWORDS = {
    "dato interesante",
    "dato curioso",
    "datos interesantes",
    "datos curiosos",
    "curiosidad",
    "curiosidades",
    "sabias que",
    "sabes que",
    "cuentame algo interesante",
    "cuentame un dato",
    "cuentame un dato interesante",
    "dime algo curioso",
    "dime algo interesante",
}

FUN_FACT_RESPONSES = [
    "el pulpo tiene tres corazones y su sangre es de color azul porque usa cobre en lugar de hierro para transportar oxígeno",
    "las abejas pueden reconocer rostros humanos y recordarlos, algo que antes se creía exclusivo de los primates",
    "Saturno podría flotar en el agua si existiera una bañera lo suficientemente grande, porque su densidad es menor que la del agua",
    "los árboles de baobab pueden almacenar hasta 120 mil litros de agua en su tronco para sobrevivir en épocas de sequía",
    "existe un lago en la Antártida llamado Vostok que ha estado aislado del exterior por más de 15 millones de años",
    "las huellas de cada nariz humana son únicas, igual que nuestras huellas dactilares",
    "las tortugas marinas pueden detectar el campo magnético de la Tierra y usarlo como si fuera un GPS natural",
    "el día en Venus dura más que su año, porque tarda 243 días terrestres en girar sobre sí mismo y 225 en orbitar el Sol",
    "los flamencos solo adquieren su color rosado gracias a los pigmentos de las algas y crustáceos que comen",
    "el copo de nieve más grande registrado midió 38 centímetros de ancho y cayó en Montana, Estados Unidos, en 1887",
]

CAPABILITY_PHRASES = {
    "que puedes hacer",
    "qué puedes hacer",
    "que sabes hacer",
    "qué sabes hacer",
    "que haces",
    "qué haces",
    "como me puedes ayudar",
    "cómo me puedes ayudar",
    "como puedes ayudarme",
    "cómo puedes ayudarme",
    "que servicios ofreces",
    "qué servicios ofreces",
    "en que me puedes ayudar",
    "en qué me puedes ayudar",
    "que cosas haces",
    "qué cosas haces",
}

PROJECT_EVAL_PHRASES = {
    "cuanto crees que debemos sacar",
    "cuanto crees que deberiamos sacar",
    "cuánto crees que deberíamos sacar",
    "que calificacion merecemos",
    "qué calificación merecemos",
    "que nota merecemos",
    "que nota nos pondrias",
    "qué nota nos pondrías",
    "que puntaje merecemos",
    "cuanto crees que saque el equipo",
    "como ves la calificacion del proyecto",
    "cuanto crees que deberiamos sacar por como te programamos",
    "cuanto crees que deberiamos de sacar por quipo",
    "que calificacion merece nuestro proyecto",
    "qué calificación merece nuestro proyecto",
    "que calificacion merece este proyecto",
    "que calificacion merece el proyecto",
    "que nota nos darias por como te programamos",
    "que calificacion nos darias por programarte asi",
    "que calificacion deberiamos sacar por la forma en que te programamos",
}
CREATOR_QUERY_PHRASES = {
    "quien te programo",
    "quien te programó",
    "quien te creo",
    "quien te creó",
    "quien es tu creador",
    "quienes te desarrollaron",
    "quien te hizo",
    "de donde naciste",
    "donde naciste",
    "cual es tu origen",
}
GOTY_KEYWORD_PHRASES = {
    "goty",
    "game of the year",
    "juego del año",
    "juego del ano",
    "premio juego del año",
    "premios juego del año",
    "the game awards",
    "premio goty",
    "ganar el goty",
    "candidato a juego del año",
}

TIMER_DURATION_PATTERN = re.compile(
    r"(?:en|dentro de|por|durante)\s+(?P<value>\d{1,3}|[a-záéíóúñ]+)\s+(?P<unit>segundos?|mins?|minutos?|horas?)",
    re.IGNORECASE,
)

REMINDER_KEYWORDS = {
    "recordatorio",
    "recordarme",
    "recuérdame",
    "recuerdame",
    "alarma",
    "alarm",
    "despertador",
    "temporizador",
    "timer",
    "avísame",
    "avisame",
    "google calendar",
    "calendar",
    "calendario",
}

CALENDAR_DEFAULT_DURATION_MINUTES = int(os.getenv("AGENTE_CALENDAR_DURATION_MIN", "60"))
CALENDAR_TIMEZONE = os.getenv("AGENTE_CALENDAR_TZ", "").strip()

SPANISH_NUMBER_WORDS = {
    "uno": 1,
    "una": 1,
    "un": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
    "once": 11,
    "doce": 12,
    "trece": 13,
    "catorce": 14,
    "quince": 15,
    "dieciséis": 16,
    "dieciseis": 16,
    "diecisiete": 17,
    "dieciocho": 18,
    "diecinueve": 19,
    "veinte": 20,
    "veintiuno": 21,
    "veintidos": 22,
    "veintidós": 22,
    "veintitres": 23,
    "veintitrés": 23,
    "veinticuatro": 24,
    "veinticinco": 25,
}

SPANISH_WEEKDAY_NAMES = [
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
]

LOCAL_LLM_PROVIDER = (os.getenv("AGENTE_LOCAL_LLM") or "").strip().lower()
LOCAL_LLM_MODEL = os.getenv("AGENTE_LOCAL_MODEL", "llama3.2")
LOCAL_LLM_BASE_URL = os.getenv("AGENTE_LOCAL_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
LOCAL_LLM_TIMEOUT = float(os.getenv("AGENTE_LOCAL_TIMEOUT", "90"))
LOCAL_LLM_STRICT = os.getenv("AGENTE_LOCAL_STRICT", "0") == "1"


# Cliente del modelo de lenguaje
client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)


# Inicializar el motor de texto a voz
try:
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    spanish_voice_id = None
    for voice in voices:
        language_tags = []
        if hasattr(voice, "languages") and voice.languages:
            language_tags = [tag.decode("utf-8") if isinstance(tag, bytes) else tag for tag in voice.languages]
        metadata = " ".join([voice.name.lower(), voice.id.lower(), " ".join(language_tags).lower()])
        if "spanish" in metadata or "español" in metadata or "es_" in metadata:
            spanish_voice_id = voice.id
            break
    if spanish_voice_id:
        engine.setProperty("voice", spanish_voice_id)
    else:
        print("Advertencia: no se encontró voz en español concreta, se usará la predeterminada.")
except Exception as exc:
    print(f"Error al inicializar el motor de TTS: {exc}")
    engine = None


def speak(text: str) -> None:
    if not text:
        return
    print(f"Asistente: {text}")
    if not engine:
        print("Aviso: motor TTS no disponible.")
        return
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        print(f"Error durante la síntesis de voz: {exc}")


def debug_log(message: str) -> None:
    if VERBOSE_LOGGING:
        print(f"Depuración: {message}")


def _load_curated_game_guides() -> Tuple[Dict[str, List[Dict[str, str]]], Dict[str, Dict[str, Any]]]:
    alias_map: Dict[str, List[Dict[str, str]]] = {}
    canonical_meta: Dict[str, Dict[str, Any]] = {}
    if not CURATED_GUIDES_PATH.exists():
        return alias_map, canonical_meta
    try:
        with CURATED_GUIDES_PATH.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except Exception as exc:
        debug_log(f"Error cargando guias curadas: {exc}")
        return alias_map, canonical_meta
    if not isinstance(payload, dict):
        return alias_map, canonical_meta
    for canonical_id, meta in payload.items():
        if not isinstance(meta, dict):
            continue
        steps = meta.get("steps") or []
        aliases = [alias.lower() for alias in meta.get("aliases", []) if isinstance(alias, str) and alias.strip()]
        sample_prompts = [prompt for prompt in meta.get("sample_prompts", []) if isinstance(prompt, str) and prompt.strip()]
        canonical_meta[canonical_id] = {
            "steps": steps,
            "aliases": aliases,
            "sample_prompts": sample_prompts,
        }
        for alias in aliases:
            alias_map[alias] = steps
    return alias_map, canonical_meta


def _normalize_command_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


COOKING_KEYWORDS = {
    _normalize_command_text(keyword)
    for keyword in RAW_COOKING_KEYWORDS
}
RECIPE_RANDOM_PATTERNS = {
    _normalize_command_text(pattern)
    for pattern in RAW_RECIPE_RANDOM_PATTERNS
}
RECIPE_FILTER_HINTS = {
    _normalize_command_text(trigger): {
        _normalize_command_text(tag)
        for tag in tags
    }
    for trigger, tags in RAW_RECIPE_FILTER_HINTS.items()
}

HARDWARE_KEYWORDS = {
    _normalize_command_text(keyword)
    for keyword in RAW_HARDWARE_KEYWORDS
}
HARDWARE_DESKTOP_KEYWORDS = {
    _normalize_command_text(keyword)
    for keyword in RAW_HARDWARE_DESKTOP_KEYWORDS
}
HARDWARE_LAPTOP_KEYWORDS = {
    _normalize_command_text(keyword)
    for keyword in RAW_HARDWARE_LAPTOP_KEYWORDS
}
HARDWARE_RANDOM_PATTERNS = [
    _normalize_command_text(pattern)
    for pattern in RAW_HARDWARE_RANDOM_PATTERNS
]
HARDWARE_FILTER_HINTS = {
    _normalize_command_text(trigger): {
        _normalize_command_text(tag)
        for tag in tags
    }
    for trigger, tags in RAW_HARDWARE_FILTER_HINTS.items()
}
HARDWARE_TOKEN_STOPWORDS = {
    "pc",
    "pcs",
    "computadora",
    "computador",
    "laptop",
    "portatil",
    "notebook",
    "equipo",
    "armar",
    "armado",
    "componentes",
    "setup",
    "quiero",
    "necesito",
    "dame",
    "busco",
    "para",
}
HARDWARE_DETAIL_TRIGGERS = {
    _normalize_command_text(trigger)
    for trigger in RAW_HARDWARE_DETAIL_TRIGGERS
}
HARDWARE_COMPONENT_KEYWORDS = {
    slot: {
        _normalize_command_text(keyword)
        for keyword in keywords
    }
    for slot, keywords in RAW_HARDWARE_COMPONENT_KEYWORDS.items()
}

ANIME_RANDOM_PATTERNS = {
    _normalize_command_text(pattern)
    for pattern in RAW_ANIME_RANDOM_PATTERNS
}
ANIME_FILTER_HINTS = {
    _normalize_command_text(trigger): {
        _normalize_command_text(tag)
        for tag in tags
    }
    for trigger, tags in RAW_ANIME_FILTER_HINTS.items()
}
ANIME_TOKEN_STOPWORDS = {
    _normalize_command_text(word)
    for word in RAW_ANIME_TOKEN_STOPWORDS
}

EMOTION_BOOST_KEYWORDS = {
    _normalize_command_text(keyword)
    for keyword in RAW_EMOTION_BOOST_KEYWORDS
}
IDENTITY_QUERY_PATTERNS = {
    _normalize_command_text(pattern)
    for pattern in RAW_IDENTITY_QUERY_PATTERNS
}
COMPLIMENT_REQUEST_PATTERNS = {
    _normalize_command_text(pattern)
    for pattern in RAW_COMPLIMENT_REQUEST_PATTERNS
}


def _load_curated_recipes() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str], Dict[str, Set[str]]]:
    recipe_map: Dict[str, Dict[str, Any]] = {}
    alias_index: Dict[str, str] = {}
    tag_index: Dict[str, Set[str]] = defaultdict(set)
    if not CURATED_RECIPES_PATH.exists():
        return recipe_map, alias_index, tag_index
    try:
        with CURATED_RECIPES_PATH.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except Exception as exc:
        debug_log(f"Error cargando recetario curado: {exc}")
        return recipe_map, alias_index, tag_index
    if not isinstance(payload, list):
        return recipe_map, alias_index, tag_index
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        recipe_id = entry.get("id")
        if not recipe_id:
            continue
        recipe_map[recipe_id] = entry
        for alias in entry.get("aliases", []):
            alias_key = _normalize_command_text(alias)
            if alias_key:
                alias_index[alias_key] = recipe_id
        for tag in entry.get("tags", []):
            tag_key = _normalize_command_text(tag)
            if tag_key:
                tag_index[tag_key].add(recipe_id)
        for extra in (entry.get("cuisine"), entry.get("meal_type"), entry.get("diet"), entry.get("equipment")):
            if extra:
                tag_index[_normalize_command_text(str(extra))].add(recipe_id)
    return recipe_map, alias_index, tag_index


def _load_curated_hardware_builds() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str], Dict[str, Set[str]]]:
    build_map: Dict[str, Dict[str, Any]] = {}
    alias_index: Dict[str, str] = {}
    tag_index: Dict[str, Set[str]] = defaultdict(set)
    if not CURATED_HARDWARE_PATH.exists():
        return build_map, alias_index, tag_index
    try:
        with CURATED_HARDWARE_PATH.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except Exception as exc:
        debug_log(f"Error cargando builds de hardware: {exc}")
        return build_map, alias_index, tag_index
    if not isinstance(payload, list):
        return build_map, alias_index, tag_index
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        build_id = entry.get("id")
        if not build_id:
            continue
        build_map[build_id] = entry
        for alias in entry.get("aliases", []) or []:
            alias_key = _normalize_command_text(alias)
            if alias_key:
                alias_index[alias_key] = build_id
        tag_sources: List[str] = []
        tag_sources.extend(entry.get("tags", []) or [])
        tag_sources.extend(entry.get("use_cases", []) or [])
        cpu_text = entry.get("cpu", "")
        gpu_text = entry.get("gpu", "")
        for token in (cpu_text, gpu_text):
            lowered = token.lower()
            if "ryzen" in lowered:
                tag_sources.append("ryzen")
            if "intel" in lowered:
                tag_sources.append("intel")
            if "core" in lowered:
                tag_sources.append("intel_core")
            if "rtx" in lowered:
                tag_sources.append("rtx")
            if "rx" in lowered:
                tag_sources.append("radeon")
            if "arc" in lowered:
                tag_sources.append("intel_arc")
        build_type = entry.get("type")
        if build_type:
            tag_sources.append(build_type)
        release_year = entry.get("release_window")
        if isinstance(release_year, int):
            tag_sources.append(str(release_year))
        for tag in tag_sources:
            tag_key = _normalize_command_text(str(tag))
            if tag_key:
                tag_index[tag_key].add(build_id)
    return build_map, alias_index, tag_index


def _load_curated_anime_catalog() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str], Dict[str, Set[str]]]:
    anime_map: Dict[str, Dict[str, Any]] = {}
    alias_index: Dict[str, str] = {}
    tag_index: Dict[str, Set[str]] = defaultdict(set)
    if not CURATED_ANIME_PATH.exists():
        return anime_map, alias_index, tag_index
    try:
        with CURATED_ANIME_PATH.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except Exception as exc:
        debug_log(f"Error cargando catálogo de anime: {exc}")
        return anime_map, alias_index, tag_index
    if not isinstance(payload, list):
        return anime_map, alias_index, tag_index
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        anime_id = entry.get("id")
        if not anime_id:
            continue
        anime_map[anime_id] = entry
        for alias in entry.get("aliases", []) or []:
            alias_key = _normalize_command_text(alias)
            if alias_key:
                alias_index[alias_key] = anime_id
        tagged_fields = [
            entry.get("tags", []),
            entry.get("genres", []),
            entry.get("themes", []),
            entry.get("mood_tags", []),
        ]
        for optional_field in ["studio", "tone", "format", "type", "franchise", "length_tag", "era_tag"]:
            value = entry.get(optional_field)
            if value:
                tagged_fields.append([value])
        release_year = entry.get("release_year")
        if release_year:
            tagged_fields.append([str(release_year)])
        for collection in tagged_fields:
            for tag in collection or []:
                tag_key = _normalize_command_text(str(tag))
                if tag_key:
                    tag_index[tag_key].add(anime_id)
    return anime_map, alias_index, tag_index


VOICE_COMMAND_SANITIZE_PATTERN = re.compile(r"[^a-z0-9\s]+")
VOICE_COMMAND_FILLER_WORDS = {
    "oye",
    "por",
    "favor",
    "porfavor",
    "porfa",
    "ok",
    "vale",
    "gracias",
    "ya",
    "miau",
    "anda",
    "hey",
}


def _canonical_voice_phrase(text: str) -> str:
    normalized = _normalize_command_text(text)
    sanitized = VOICE_COMMAND_SANITIZE_PATTERN.sub(" ", normalized)
    return " ".join(sanitized.split())


def _voice_command_candidate_from_normalized(normalized_text: str) -> str:
    sanitized = VOICE_COMMAND_SANITIZE_PATTERN.sub(" ", normalized_text)
    tokens = [token for token in sanitized.split() if token and token not in VOICE_COMMAND_FILLER_WORDS]
    return " ".join(tokens)


def _voice_command_candidate_from_text(text: str) -> str:
    normalized = _normalize_command_text(text)
    return _voice_command_candidate_from_normalized(normalized)


YEAR_PATTERN = re.compile(r"(20\d{2})")


def _extract_year_from_text(text: str) -> Optional[int]:
    match = YEAR_PATTERN.search(text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


VOICE_MODE_ACTIVATE_PATTERNS = {
    _canonical_voice_phrase(pattern)
    for pattern in VOICE_MODE_ACTIVATE_PATTERNS
}
VOICE_MODE_DEACTIVATE_PATTERNS = {
    _canonical_voice_phrase(pattern)
    for pattern in VOICE_MODE_DEACTIVATE_PATTERNS
}
FUN_FACT_KEYWORDS = {
    _normalize_command_text(keyword)
    for keyword in FUN_FACT_KEYWORDS
}
CAPABILITY_PHRASES = {
    _normalize_command_text(phrase)
    for phrase in CAPABILITY_PHRASES
}
PROJECT_EVAL_PHRASES = {
    _normalize_command_text(phrase)
    for phrase in PROJECT_EVAL_PHRASES
}
GOTY_KEYWORDS = {
    _normalize_command_text(keyword)
    for keyword in GOTY_KEYWORD_PHRASES
}


@dataclass
class MemoryEntry:
    summary: str
    user_text: str
    assistant_text: str
    intent: str
    tags: List[str]
    timestamp: float
    salience: float = 1.0

class MemoryManager:
    def __init__(self, max_entries: int = 40) -> None:
        self.max_entries = max_entries
        self.entries: List[MemoryEntry] = []

    def add_entry(
        self,
        user_text: str,
        assistant_text: str,
        intent: str,
        tags: Optional[List[str]] = None,
        salience: float = 1.0,
    ) -> None:
        summary = self._build_summary(user_text, assistant_text, intent)
        entry = MemoryEntry(
            summary=summary,
            user_text=user_text,
            assistant_text=assistant_text,
            intent=intent,
            tags=(tags or []),
            timestamp=time.time(),
            salience=salience,
        )
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries :]

    def recall(self, query: str, limit: int = 3) -> List[str]:
        if not self.entries:
            return []
        keywords = {token for token in re.findall(r"[\wáéíóúñ]+", query.lower()) if len(token) >= 4}
        if not keywords:
            return self.recent(limit)
        scored: List[Tuple[float, MemoryEntry]] = []
        for entry in self.entries:
            haystack = " ".join(
                [
                    entry.user_text.lower(),
                    entry.assistant_text.lower(),
                    entry.intent.lower(),
                    " ".join(entry.tags).lower(),
                ]
            )
            score = entry.salience
            for keyword in keywords:
                if keyword in haystack:
                    score += 1.0
            # slight preference for recent memories
            score += entry.timestamp * 1e-12
            if score > entry.salience:
                scored.append((score, entry))
        if not scored:
            return self.recent(limit)
        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1].summary for item in scored[:limit]]

    def recent(self, limit: int = 3) -> List[str]:
        if not self.entries:
            return []
        return [entry.summary for entry in self.entries[-limit:]][::-1]

    def last_by_intent(self, intent: str) -> Optional[MemoryEntry]:
        for entry in reversed(self.entries):
            if entry.intent == intent:
                return entry
        return None

    def _build_summary(self, user_text: str, assistant_text: str, intent: str) -> str:
        cleaned_user = re.sub(r"\s+", " ", user_text).strip()
        cleaned_assistant = re.sub(r"\s+", " ", assistant_text).strip()
        snippet_user = (cleaned_user[:120] + "…") if len(cleaned_user) > 120 else cleaned_user
        snippet_assistant = (cleaned_assistant[:140] + "…") if len(cleaned_assistant) > 140 else cleaned_assistant
        return f"Intento {intent}: Usuario dijo '{snippet_user}'. Respondí: '{snippet_assistant}'."


def launch_browser(url: str, new: int = 2) -> bool:
    if not BROWSER_AUTOMATION_ENABLED:
        debug_log(f"Automatización de navegador desactivada. URL pendiente: {url}")
        return False
    try:
        opened = webbrowser.open(url, new=new)
        if not opened and os.name == "nt":
            try:
                os.startfile(url)  # type: ignore[attr-defined]
                opened = True
            except Exception as sub_exc:
                debug_log(f"startfile falló para {url}: {sub_exc}")
        return opened
    except Exception as exc:
        debug_log(f"Error al abrir navegador para {url}: {exc}")
        if os.name == "nt":
            try:
                os.startfile(url)  # type: ignore[attr-defined]
                return True
            except Exception as sub_exc:
                debug_log(f"Intento adicional falló para {url}: {sub_exc}")
        return False


def _ensure_whatsapp_profile_dir() -> str:
    profile_path = Path(WHATSAPP_PROFILE_DIR).expanduser()
    try:
        profile_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        debug_log(f"No pude crear el perfil persistente de WhatsApp: {exc}")
    return str(profile_path)


def _create_whatsapp_driver() -> Optional[Any]:
    if not WHATSAPP_AUTOMATION_AVAILABLE:
        debug_log("WhatsApp automation no disponible: falta Selenium o está desactivada por configuración.")
        return None
    assert webdriver is not None and ChromeOptions is not None and Service is not None
    options = ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    if HEADLESS_MODE:
        options.add_argument("--headless=new")
    profile_dir = _ensure_whatsapp_profile_dir()
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--profile-directory=Default")
    try:
        assert ChromeDriverManager is not None
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(90)
        driver.get("https://web.whatsapp.com/")
        return driver
    except Exception as exc:
        debug_log(f"No se pudo iniciar el navegador de WhatsApp: {exc}")
        return None


def _wait_for_whatsapp_ready(driver: Any, timeout: int = WHATSAPP_MAX_WAIT) -> bool:
    if WebDriverWait is None:
        return False
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            driver.find_element(By.CSS_SELECTOR, "div[role='textbox'][contenteditable='true']")
            return True
        except Exception:
            time.sleep(1)
    return False


def _select_whatsapp_chat(driver: Any, contact: str, timeout: int = 25) -> bool:
    if WebDriverWait is None or EC is None or Keys is None:
        return False
    try:
        search_box = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']"))
        )
    except TimeoutException:
        return False
    try:
        search_box.click()
        search_box.send_keys(Keys.CONTROL, "a")
        search_box.send_keys(Keys.DELETE)
        search_box.send_keys(contact)
        time.sleep(1.2)
        search_box.send_keys(Keys.ENTER)
    except WebDriverException:
        return False
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "footer div[role='textbox'][contenteditable='true']"))
        )
    except TimeoutException:
        return False
    return True


def _trigger_whatsapp_send(driver: Any, input_box: Any) -> bool:
    if Keys is None:
        return False
    try:
        input_box.send_keys(Keys.ENTER)
        return True
    except WebDriverException:
        pass
    if WebDriverWait is None or EC is None:
        return False
    selectors = [
        "button[data-testid='compose-btn-send']",
        "button[aria-label='Enviar']",
        "button[title='Enviar']",
        "span[data-icon='send']",
    ]
    for selector in selectors:
        try:
            send_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            send_button.click()
            return True
        except TimeoutException:
            continue
        except WebDriverException:
            continue
    return False


def _send_messages_in_chat(driver: Any, message: str, repetitions: int) -> bool:
    if WebDriverWait is None or EC is None or Keys is None:
        return False
    repetitions = max(1, min(repetitions, 25))
    for idx in range(repetitions):
        try:
            input_box = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "footer div[role='textbox'][contenteditable='true']"))
            )
            input_box.click()
        except TimeoutException:
            return False
        try:
            input_box.send_keys(Keys.CONTROL, "a")
            input_box.send_keys(Keys.DELETE)
            segments = message.split("\n")
            for seg_index, segment in enumerate(segments):
                if segment:
                    input_box.send_keys(segment)
                if seg_index < len(segments) - 1:
                    input_box.send_keys(Keys.SHIFT, Keys.ENTER)
            if not _trigger_whatsapp_send(driver, input_box):
                return False
            time.sleep(0.6)
            if idx < repetitions - 1:
                time.sleep(max(0.1, WHATSAPP_MESSAGE_DELAY))
        except WebDriverException:
            return False
    return True


def automate_whatsapp_message(contact: str, message: str, repetitions: int = 1) -> Tuple[bool, str]:
    if not contact.strip() or not message.strip():
        return False, "Necesito el contacto y el mensaje para poder enviarlo."
    if not WHATSAPP_AUTOMATION_AVAILABLE:
        return False, "No puedo controlar WhatsApp Web porque Selenium no está instalado o está deshabilitado."
    driver = _create_whatsapp_driver()
    if driver is None:
        return False, "No pude iniciar el navegador automatizado para WhatsApp."
    try:
        if not _wait_for_whatsapp_ready(driver):
            return False, "No pude detectar que hayas iniciado sesión en WhatsApp Web a tiempo."
        if not _select_whatsapp_chat(driver, contact):
            return False, f"No encontré el chat llamado '{contact}'. Asegúrate de que exista y vuelve a intentarlo."
        if not _send_messages_in_chat(driver, message, repetitions):
            return False, "El mensaje no se pudo enviar."
        plural = "mensaje" if max(1, repetitions) == 1 else "mensajes"
        return True, f"Listo, envié {max(1, repetitions)} {plural} a {contact} en WhatsApp."
    finally:
        if not WHATSAPP_KEEP_BROWSER_OPEN:
            try:
                time.sleep(1.0)
                driver.quit()
            except Exception:
                pass


def _ensure_whatsapp_scheduler_running() -> None:
    global WHATSAPP_SCHEDULER_THREAD
    if WHATSAPP_SCHEDULER_THREAD and WHATSAPP_SCHEDULER_THREAD.is_alive():
        return
    WHATSAPP_SCHEDULER_THREAD = threading.Thread(
        target=_whatsapp_scheduler_loop,
        name="WhatsAppScheduler",
        daemon=True,
    )
    WHATSAPP_SCHEDULER_THREAD.start()


def _schedule_whatsapp_message(
    contact: str,
    message: str,
    repetitions: int,
    send_at: datetime.datetime,
) -> Tuple[str, datetime.datetime]:
    global WHATSAPP_SCHEDULE_COUNTER
    effective_dt = max(
        send_at,
        datetime.datetime.now() + datetime.timedelta(seconds=WHATSAPP_SCHEDULE_MIN_LEAD_SECONDS),
    )
    WHATSAPP_SCHEDULE_COUNTER += 1
    task_id = f"whatsapp-{int(effective_dt.timestamp())}-{WHATSAPP_SCHEDULE_COUNTER}"
    payload = {
        "contact": contact,
        "message": message,
        "repetitions": max(1, min(repetitions, 25)),
        "scheduled_for": effective_dt,
        "task_id": task_id,
        "requested_at": datetime.datetime.now(),
    }
    with WHATSAPP_SCHEDULER_LOCK:
        heapq.heappush(SCHEDULED_WHATSAPP_TASKS, (effective_dt.timestamp(), payload))
        WHATSAPP_SCHEDULER_EVENT.set()
    _ensure_whatsapp_scheduler_running()
    return task_id, effective_dt


def _whatsapp_scheduler_loop() -> None:
    while True:
        try:
            with WHATSAPP_SCHEDULER_LOCK:
                next_eta = SCHEDULED_WHATSAPP_TASKS[0][0] if SCHEDULED_WHATSAPP_TASKS else None
            if next_eta is None:
                WHATSAPP_SCHEDULER_EVENT.wait()
                WHATSAPP_SCHEDULER_EVENT.clear()
                continue
            wait_seconds = max(0.0, next_eta - time.time())
            triggered = WHATSAPP_SCHEDULER_EVENT.wait(timeout=wait_seconds)
            if triggered:
                WHATSAPP_SCHEDULER_EVENT.clear()
                continue
            with WHATSAPP_SCHEDULER_LOCK:
                if not SCHEDULED_WHATSAPP_TASKS:
                    continue
                eta, payload = heapq.heappop(SCHEDULED_WHATSAPP_TASKS)
                now_ts = time.time()
                if eta - now_ts > 1.5:
                    heapq.heappush(SCHEDULED_WHATSAPP_TASKS, (eta, payload))
                    continue
            success, detail = automate_whatsapp_message(
                payload["contact"],
                payload["message"],
                payload["repetitions"],
            )
            if success:
                debug_log(
                    f"Mensaje programado enviado a {payload['contact']} (tarea {payload['task_id']})."
                )
            else:
                debug_log(
                    "No pude completar una tarea programada de WhatsApp: "
                    f"{detail or 'motivo desconocido'} (tarea {payload['task_id']})."
                )
        except Exception as exc:
            debug_log(f"El hilo programador de WhatsApp se reiniciará por un error: {exc}")
            time.sleep(2.0)


def auto_reply_whatsapp_chat(contact: str, duration_seconds: int) -> Tuple[bool, str]:
    if not contact.strip():
        return False, "Necesito saber a quién responder en WhatsApp."
    if duration_seconds <= 0:
        return False, "El intervalo para responder debe ser mayor a cero."
    duration_seconds = max(WHATSAPP_AUTO_REPLY_MIN_SECONDS, min(duration_seconds, WHATSAPP_AUTO_REPLY_MAX_SECONDS))
    if not WHATSAPP_AUTOMATION_AVAILABLE:
        return False, "No puedo controlar WhatsApp Web porque Selenium no está disponible."
    driver = _create_whatsapp_driver()
    if driver is None:
        return False, "No pude abrir WhatsApp Web para hacerme cargo del chat."
    responses_sent = 0
    processed_ids: Set[str] = set()
    try:
        if not _wait_for_whatsapp_ready(driver):
            return False, "No detecté una sesión activa de WhatsApp Web."
        if not _select_whatsapp_chat(driver, contact):
            return False, f"No encontré el chat llamado '{contact}'."
        history = _collect_recent_whatsapp_messages(driver, contact_hint=contact)
        processed_ids.update(msg["id"] for msg in history if msg.get("incoming"))
        pending_message = None
        for candidate in reversed(history):
            if candidate.get("incoming"):
                pending_message = candidate
                break
        if pending_message:
            processed_ids.discard(pending_message["id"])
            reply_text = _build_auto_reply_message(contact, history, pending_message)
            if reply_text:
                if not _send_messages_in_chat(driver, reply_text, 1):
                    return False, "No pude enviar la primera respuesta automática."
                responses_sent += 1
                processed_ids.add(pending_message["id"])
        end_time = time.time() + duration_seconds
        while time.time() < end_time:
            time.sleep(max(0.8, WHATSAPP_AUTO_REPLY_POLL_SECONDS))
            history = _collect_recent_whatsapp_messages(driver, contact_hint=contact)
            if not history:
                continue
            new_incoming = [msg for msg in history if msg.get("incoming") and msg["id"] not in processed_ids]
            if not new_incoming:
                continue
            for incoming_msg in new_incoming:
                reply_text = _build_auto_reply_message(contact, history, incoming_msg)
                if not reply_text:
                    processed_ids.add(incoming_msg["id"])
                    continue
                if not _send_messages_in_chat(driver, reply_text, 1):
                    return False, "Falló el envío de una respuesta automática."
                responses_sent += 1
                processed_ids.add(incoming_msg["id"])
        if responses_sent == 0:
            return True, f"Estuve pendiente del chat con {contact}, pero no hubo mensajes nuevos en ese lapso."
        plural = "mensaje" if responses_sent == 1 else "mensajes"
        return True, f"Respondí automáticamente {responses_sent} {plural} en el chat con {contact}."
    finally:
        if not WHATSAPP_KEEP_BROWSER_OPEN:
            try:
                driver.quit()
            except Exception:
                pass


def _extract_repetition_count(text: str) -> int:
    repetitions = 1
    digit_match = re.search(r"(\d{1,2})\s*(?:veces|repeticiones|repetir|repite)", text, flags=re.IGNORECASE)
    if digit_match:
        repetitions = int(digit_match.group(1))
    else:
        for word, value in SPANISH_NUMBER_WORDS.items():
            if re.search(rf"\b{re.escape(word)}\s+(?:veces|repeticiones)\b", text, flags=re.IGNORECASE):
                repetitions = value
                break
    return max(1, min(repetitions, 25))


def _strip_matching_quotes(text: str) -> str:
    quote_pairs = {
        "\"": "\"",
        "'": "'",
        "“": "”",
        "”": "“",
        "«": "»",
        "»": "«",
        "‘": "’",
        "’": "‘",
    }
    text = text.strip()
    if not text:
        return text
    start = text[0]
    end = text[-1]
    if start in quote_pairs and quote_pairs[start] == end:
        return text[1:-1].strip()
    if end in quote_pairs and quote_pairs[end] == start:
        return text[1:-1].strip()
    return text


def _heuristic_whatsapp_parameters(user_text: str) -> Tuple[str, str]:
    contact = ""
    message = ""
    quote_match = re.search(r"[\"'“”«»‘’](.+?)[\"'“”«»‘’]", user_text)
    message_span: Optional[Tuple[int, int]] = None
    if quote_match:
        message = _strip_matching_quotes(quote_match.group(0))
        message_span = (quote_match.start(), quote_match.end())
    if not message:
        pattern = re.search(r"(?:que\s+(?:le\s+)?(?:diga|digas|dice|dile))\s+(.+)", user_text, flags=re.IGNORECASE)
        if pattern:
            message = pattern.group(1).strip()
            message_span = pattern.span(1)
    message = _strip_matching_quotes(message.strip(" .,!?:;"))
    search_area = user_text if not message_span else user_text[: message_span[0]]
    contact_iter = list(
        re.finditer(
            r"\b(?:a|para)\b\s+([\wÁÉÍÓÚÑáéíóúñ0-9 .,'-]{2,80})",
            search_area,
            flags=re.IGNORECASE,
        )
    )
    for match in reversed(contact_iter):
        candidate = match.group(1)
        candidate = re.split(
            r"\b(?:que|dile|diles|para|con|y|,|\.|durante|por)\b",
            candidate,
            1,
            re.IGNORECASE,
        )[0]
        trimmed = candidate.strip(" .,!?:;\"'“”‘’")
        if not trimmed:
            continue
        if re.match(
            r"^(?:las|la)\s+\d{1,2}(?:[:h\.]\d{2})?(?:\s*(?:am|pm|a\.m\.|p\.m\.|hrs?|horas?))?\b",
            trimmed,
            flags=re.IGNORECASE,
        ):
            continue
        contact = trimmed
        break
    return contact, message


def _parse_whatsapp_with_llm(user_text: str, default_repetitions: int) -> Tuple[str, str, int]:
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un extractor de parámetros para comandos de WhatsApp. "
                "Responde únicamente con JSON válido con la forma {\"contact\":\"\", \"message\":\"\", \"repetitions\":1}. "
                "El contacto debe ser el nombre o número del destinatario sin instrucciones adicionales. "
                "El mensaje es el texto exacto que se debe enviar. "
                "repetitions debe ser un entero entre 1 y 25. Si el usuario no especifica, usa 1. "
                "Si algún dato no aparece, deja la cadena vacía en ese campo."
            ),
        },
        {
            "role": "user",
            "content": user_text,
        },
    ]
    raw = query_llm(messages).strip()
    try:
        data = json.loads(raw)
        contact = str(data.get("contact", "")).strip()
        message = _strip_matching_quotes(str(data.get("message", "")).strip())
        repetitions = data.get("repetitions", default_repetitions)
        if isinstance(repetitions, str) and repetitions.isdigit():
            repetitions = int(repetitions)
        if not isinstance(repetitions, int):
            repetitions = default_repetitions
    except Exception:
        return "", "", default_repetitions
    return contact, message, max(1, min(int(repetitions), 25))


def parse_whatsapp_command(user_text: str) -> Tuple[str, str, int]:
    heur_contact, heur_message = _heuristic_whatsapp_parameters(user_text)
    repetitions = _extract_repetition_count(user_text)
    contact = heur_contact
    message = heur_message
    llm_contact = llm_message = ""
    llm_repetitions = repetitions
    if not contact or not message:
        llm_contact, llm_message, llm_repetitions = _parse_whatsapp_with_llm(user_text, repetitions)
    if not contact and llm_contact:
        contact = llm_contact
    if not message and llm_message:
        message = llm_message
    if llm_repetitions:
        repetitions = llm_repetitions
    contact = contact.strip(" .,!?:;\"'“”‘’")
    message = _strip_matching_quotes(message).strip()
    return contact, message, repetitions


def _extract_auto_reply_duration_seconds(user_text: str) -> int:
    match = WHATSAPP_AUTO_REPLY_DURATION_PATTERN.search(user_text.lower())
    if not match:
        return 0
    value = match.group("value").strip().lower()
    if value.isdigit():
        minutes = int(value)
    else:
        minutes = SPANISH_NUMBER_WORDS.get(value, 0)
    if minutes <= 0:
        return 0
    seconds = minutes * 60
    seconds = max(WHATSAPP_AUTO_REPLY_MIN_SECONDS, seconds)
    seconds = min(WHATSAPP_AUTO_REPLY_MAX_SECONDS, seconds)
    return seconds


def _collect_recent_whatsapp_messages(
    driver: Any,
    limit: int = 12,
    contact_hint: Optional[str] = None,
) -> List[Dict[str, Any]]:
    script = """
const limit = arguments[0];
const selectors = ["div[data-testid='msg-container']", "div[role='row'][data-id]"];
let nodes = [];
for (const selector of selectors) {
  const chunk = Array.from(document.querySelectorAll(selector));
  if (chunk.length) {
    nodes = chunk;
    break;
  }
}
if (!nodes.length) {
  nodes = Array.from(document.querySelectorAll("div[data-id]"));
}
const subset = nodes.slice(-limit);
return subset.map((node) => ({
  text: node.innerText || "",
  dataId: node.getAttribute("data-id") || "",
  aria: node.getAttribute("aria-label") || "",
  pre: node.getAttribute("data-pre-plain-text") || "",
  classes: node.className || "",
}));
"""
    try:
        raw_messages = driver.execute_script(script, max(1, limit))
    except Exception:
        return []
    if not isinstance(raw_messages, list):
        return []
    contact_lower = (contact_hint or "").strip().lower()
    messages: List[Dict[str, Any]] = []
    for idx, item in enumerate(raw_messages[-limit:]):
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        data_id = str(item.get("dataId") or "").strip()
        aria_hint = str(item.get("aria") or "")
        pre_hint = str(item.get("pre") or "")
        classes = str(item.get("classes") or "").lower()
        msg_id = data_id or f"{pre_hint}|{text}|{idx}"
        incoming_flag = "message-in" in classes or "incoming" in classes
        outgoing_flag = "message-out" in classes or "outgoing" in classes
        pre_lower = pre_hint.lower()
        aria_lower = aria_hint.lower()
        if not incoming_flag and not outgoing_flag:
            if contact_lower and f"] {contact_lower}:" in pre_lower:
                incoming_flag = True
            elif contact_lower and f" {contact_lower}:" in pre_lower:
                incoming_flag = True
            elif re.search(r"\b(tú|you|yo|i):", pre_lower):
                outgoing_flag = True
            elif "te envió" in aria_lower or "te envio" in aria_lower or "te mand" in aria_lower:
                incoming_flag = True
            elif "enviaste" in aria_lower or "you sent" in aria_lower:
                outgoing_flag = True
        if not incoming_flag and not outgoing_flag:
            incoming_flag = True
        is_incoming = incoming_flag and not outgoing_flag
        messages.append(
            {
                "id": msg_id,
                "text": text,
                "incoming": is_incoming,
                "meta": pre_hint,
            }
        )
    return messages


def _build_auto_reply_message(
    contact: str,
    history: List[Dict[str, Any]],
    target_message: Dict[str, Any],
) -> str:
    if not history:
        return ""
    transcript_lines: List[str] = []
    for item in history[-8:]:
        speaker = contact if item.get("incoming") else "Yo"
        text = item.get("text") or ""
        if not text:
            continue
        transcript_lines.append(f"{speaker}: {text}")
    transcript = "\n".join(transcript_lines)
    guidance = (
        "Eres un asistente que responde mensajes de WhatsApp en nombre del usuario. "
        "Responde con claridad, tono empático y máximo dos frases. Si falta contexto, pide una aclaración breve."
    )
    prompt = (
        f"Último mensaje de {contact}: {target_message.get('text', '')}\n"
        f"Conversación reciente:\n{transcript}\n"
        "Redacta la siguiente respuesta en español, sin viñetas ni listas."
    )
    reply = query_llm(
        [
            {"role": "system", "content": guidance},
            {"role": "user", "content": prompt},
        ]
    ).strip()
    reply = reply.strip("\"'“”‘’ ")
    if not reply:
        reply = "De acuerdo, gracias por avisar."
    return reply

def _describe_schedule_day(target_dt: datetime.datetime) -> str:
    today = datetime.date.today()
    delta = (target_dt.date() - today).days
    if delta == 0:
        return "hoy"
    if delta == 1:
        return "mañana"
    if delta == -1:
        return "ayer"
    weekday_name = SPANISH_WEEKDAY_NAMES[target_dt.weekday()]
    return f"el {weekday_name} {target_dt.strftime('%d/%m')}"


def _detect_spanish_time_expression(user_text: str) -> Optional[Tuple[datetime.datetime, bool]]:
    if not user_text:
        return None
    lowered = user_text.lower()
    match = WHATSAPP_TIME_PATTERN.search(lowered)
    if not match:
        return None
    hour = int(match.group("hour") or 0)
    minute_text = match.group("minute") or "0"
    minute = int(minute_text)
    meridian = (match.group("meridian") or "").replace(".", "").strip().lower()
    if meridian:
        if "p" in meridian and hour < 12:
            hour += 12
        if "a" in meridian and hour == 12:
            hour = 0
    if hour > 23 or minute > 59:
        return None
    now = datetime.datetime.now()
    base_date = now.date()
    explicit_reference = False
    day_offset: Optional[int] = None
    context_start = max(0, match.start() - 60)
    context_end = min(len(lowered), match.end() + 60)
    context_window = lowered[context_start:context_end]
    if "pasado mañana" in context_window:
        day_offset = 2
        explicit_reference = True
    elif "mañana" in context_window:
        day_offset = 1
        explicit_reference = True
    elif "hoy" in context_window:
        day_offset = 0
        explicit_reference = True
    if day_offset is None:
        today_index = now.weekday()
        for offset in range(0, 7):
            weekday_name = SPANISH_WEEKDAY_NAMES[(today_index + offset) % 7]
            if weekday_name in context_window:
                day_offset = offset
                explicit_reference = True
                break
    if day_offset is None:
        day_offset = 0
    target_dt = datetime.datetime.combine(
        base_date + datetime.timedelta(days=day_offset),
        datetime.time(hour=hour, minute=minute, second=0, microsecond=0),
    )
    rolled = False
    while (target_dt - now).total_seconds() < WHATSAPP_SCHEDULE_MIN_LEAD_SECONDS:
        target_dt += datetime.timedelta(days=1)
        rolled = True
        if explicit_reference and (target_dt - now).total_seconds() >= WHATSAPP_SCHEDULE_MIN_LEAD_SECONDS:
            break
        if not explicit_reference:
            break
    return target_dt, rolled


def _format_duration_spanish(seconds: int) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} segundo{'s' if seconds != 1 else ''}"
    minutes = seconds / 60
    if minutes < 60:
        whole = int(round(minutes))
        return f"{whole} minuto{'s' if whole != 1 else ''}"
    hours = minutes / 60
    whole_hours = int(hours)
    remaining_minutes = int(round((hours - whole_hours) * 60))
    if remaining_minutes:
        return f"{whole_hours}h {remaining_minutes}min"
    return f"{whole_hours} hora{'s' if whole_hours != 1 else ''}"


def _extract_timer_duration_seconds(text: str) -> int:
    text_lower = text.lower()
    match = TIMER_DURATION_PATTERN.search(text_lower)
    value: Optional[str] = None
    unit: Optional[str] = None
    if match:
        value = match.group("value")
        unit = match.group("unit")
    else:
        simple_match = re.search(r"(\d{1,3})\s+(segundos?|mins?|minutos?|horas?)", text_lower, flags=re.IGNORECASE)
        if simple_match:
            value = simple_match.group(1)
            unit = simple_match.group(2)
    if not value or not unit:
        return 0
    unit = unit.lower()
    if value.isdigit():
        amount = int(value)
    else:
        amount = SPANISH_NUMBER_WORDS.get(value.lower(), 0)
        if value.lower() in {"media", "medio"} and "hora" in unit:
            amount = 30
        elif value.lower() == "media" and "min" in unit:
            amount = 30
    if amount <= 0:
        return 0
    if unit.startswith("seg"):
        seconds = amount
    elif unit.startswith("hora"):
        seconds = amount * 3600
    else:
        seconds = amount * 60
    return max(0, seconds)


def _infer_reminder_label(user_text: str) -> str:
    # Prefer explicit quoted text like "recordatorio ... 'Traer huevos'"
    quoted_match = re.search(r"[\"'“”‘’](.+?)[\"'“”‘’]", user_text)
    if quoted_match:
        candidate = quoted_match.group(1).strip()
        if candidate:
            return candidate
    removal_terms = [
        "pon",
        "ponme",
        "crea",
        "creame",
        "crea me",
        "haz",
        "programa",
        "agenda",
        "agendar",
        "agrega",
        "añade",
        "recordatorio",
        "recordarme",
        "recuerdame",
        "recuérdame",
        "alarma",
        "temporizador",
        "timer",
        "avísame",
        "avisame",
        "google calendar",
        "calendar",
        "calendario",
        "evento",
        "evento en",
        "evento para",
    ]
    cleaned = extract_focus_text(user_text, removal_terms)
    cleaned = cleaned.strip()
    if not cleaned:
        cleaned = user_text
    # If user separated the task with commas, grab the last clause
    if "," in cleaned:
        trailing = cleaned.split(",")[-1].strip()
        if trailing:
            cleaned = trailing
    # Remove common filler connectors at the start
    cleaned = re.sub(r"^(?:para|que|sobre|acerca|de|del|la|el|los|las)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip().strip(" .,!?:;\"'“”‘’")
    return cleaned or "tu recordatorio"


def build_google_calendar_event_link(
    title: str,
    start_dt: datetime.datetime,
    duration_minutes: int = CALENDAR_DEFAULT_DURATION_MINUTES,
    description: Optional[str] = None,
    location: Optional[str] = None,
) -> str:
    """Build a Calendar template link ensuring the scheduled time survives timezones."""
    minimum_minutes = max(15, duration_minutes)
    local_reference = datetime.datetime.now().astimezone()
    local_tz = local_reference.tzinfo or datetime.timezone.utc

    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=local_tz)
    end_dt = start_dt + datetime.timedelta(minutes=minimum_minutes)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=local_tz)

    fmt = "%Y%m%dT%H%M%SZ"
    start_utc = start_dt.astimezone(datetime.timezone.utc)
    end_utc = end_dt.astimezone(datetime.timezone.utc)
    params = {
        "action": "TEMPLATE",
        "text": title or "Evento",
        "dates": f"{start_utc.strftime(fmt)}/{end_utc.strftime(fmt)}",
    }
    tz_hint = CALENDAR_TIMEZONE or (start_dt.tzinfo.tzname(start_dt) if start_dt.tzinfo else "")
    if tz_hint:
        params["ctz"] = tz_hint
    if description:
        params["details"] = description
    if location:
        params["location"] = location
    return "https://calendar.google.com/calendar/render?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
def local_llm_configured() -> bool:
    return bool(LOCAL_LLM_PROVIDER and LOCAL_LLM_MODEL)


def query_local_llm(messages: List[Dict[str, str]]) -> str:
    if not local_llm_configured():
        return ""
    if LOCAL_LLM_PROVIDER != "ollama":
        debug_log(f"Proveedor local desconocido: {LOCAL_LLM_PROVIDER}")
        return ""
    url = f"{LOCAL_LLM_BASE_URL}/api/chat"
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": messages,
        "stream": False,
    }
    try:
        response = requests.post(url, json=payload, timeout=LOCAL_LLM_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        debug_log(f"Modelo local no disponible: {exc}")
        return ""

    if isinstance(data, dict):
        message = data.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
        choices = data.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                msg = choice.get("message") if isinstance(choice, dict) else None
                if isinstance(msg, dict):
                    content = msg.get("content")
                    if isinstance(content, str) and content.strip():
                        return content.strip()
        content = data.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
    return ""


if cv2 is not None:
    try:
        _face_cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        FACE_CASCADE = cv2.CascadeClassifier(_face_cascade_path)
        if FACE_CASCADE.empty():
            FACE_CASCADE = None
    except Exception as exc:
        debug_log(f"No se pudo cargar el clasificador de rostros: {exc}")
        FACE_CASCADE = None
else:
    FACE_CASCADE = None


def list_available_cameras(limit: int = 5) -> List[int]:
    if cv2 is None:
        return []
    detected: List[int] = []
    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY
    for index in range(limit):
        cap = cv2.VideoCapture(index, backend)
        if cap is not None and cap.isOpened():
            detected.append(index)
        if cap is not None:
            cap.release()
    return detected


def get_downloads_directory() -> str:
    """Return a best-effort path to the user's Downloads folder."""
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "Downloads"),
        os.path.join(home, "Descargas"),
    ]
    for candidate in candidates:
        if os.path.isdir(candidate):
            return candidate
    fallback = candidates[0]
    try:
        os.makedirs(fallback, exist_ok=True)
        return fallback
    except OSError:
        return home


def _get_image_caption_pipeline() -> Optional[Any]:
    global _IMAGE_CAPTION_PIPELINE, _IMAGE_CAPTION_FAILURE
    if _IMAGE_CAPTION_FAILURE or not IMAGE_CAPTION_ENABLED or pipeline is None:
        return None
    if _IMAGE_CAPTION_PIPELINE is not None:
        return _IMAGE_CAPTION_PIPELINE
    with _IMAGE_CAPTION_LOCK:
        if _IMAGE_CAPTION_PIPELINE is not None:
            return _IMAGE_CAPTION_PIPELINE
        try:
            _IMAGE_CAPTION_PIPELINE = pipeline(
                "image-to-text",
                model=IMAGE_CAPTION_MODEL,
                max_new_tokens=80,
            )
        except Exception as exc:  # pragma: no cover - depende de libs externas
            debug_log(f"No pude inicializar el modelo de visión ({IMAGE_CAPTION_MODEL}): {exc}")
            _IMAGE_CAPTION_FAILURE = True
            _IMAGE_CAPTION_PIPELINE = None
            return None
    return _IMAGE_CAPTION_PIPELINE


def _normalize_caption_output(caption_output: Any) -> Optional[str]:
    if not caption_output:
        return None
    candidate: Any = caption_output
    if isinstance(caption_output, list) and caption_output:
        candidate = caption_output[0]
    if isinstance(candidate, dict):
        text = candidate.get("generated_text") or candidate.get("text") or candidate.get("caption") or ""
    else:
        text = str(candidate)
    cleaned = text.strip().strip(" .")
    return cleaned.capitalize() if cleaned else None


def _semantic_caption_from_array(frame) -> Optional[str]:
    if frame is None or cv2 is None or Image is None:
        return None
    captioner = _get_image_caption_pipeline()
    if captioner is None:
        return None
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
    except Exception as exc:
        debug_log(f"No pude preparar la imagen para el modelo de visión: {exc}")
        return None
    try:
        output = captioner(pil_image)
    except Exception as exc:  # pragma: no cover - depende de dependencias externas
        debug_log(f"Falló la generación de descripción semántica: {exc}")
        return None
    return _normalize_caption_output(output)


def _analyze_frame_snapshot(frame) -> Dict[str, float]:
    if cv2 is None or np is None:
        return {}
    resized = cv2.resize(frame, (640, 360)) if frame.shape[1] > 640 else frame
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    hue = float(np.mean(hsv[:, :, 0]))
    saturation = float(np.mean(hsv[:, :, 1]))
    value = float(np.mean(hsv[:, :, 2]))
    edges = cv2.Canny(gray, 80, 160)
    edge_density = float(np.count_nonzero(edges)) / float(edges.size)
    # Estimar presencia de PCB/motherboard a partir de color verde saturado.
    green_lower = np.array([35, 60, 40], dtype=np.uint8)
    green_upper = np.array([95, 255, 255], dtype=np.uint8)
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    green_ratio = float(cv2.countNonZero(green_mask)) / float(green_mask.size)
    # Detectar patrones rectilíneos para sugerir circuitos u objetos tecnológicos.
    line_count = 0
    try:
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=35, maxLineGap=8)
        if lines is not None:
            line_count = int(len(lines))
    except Exception:
        line_count = 0
    faces = 0
    if FACE_CASCADE is not None:
        detections = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
        faces = len(detections)
    return {
        "brightness": brightness,
        "hue": hue,
        "saturation": saturation,
        "value": value,
        "edge_density": edge_density,
        "faces": float(faces),
        "green_ratio": green_ratio,
        "line_count": float(line_count),
    }


def _describe_scene_from_metrics(metrics: List[Dict[str, float]], semantic_caption: Optional[str] = None) -> str:
    if not metrics:
        return "No pude analizar la escena con suficiente información."
    avg_brightness = sum(item["brightness"] for item in metrics) / len(metrics)
    avg_saturation = sum(item["saturation"] for item in metrics) / len(metrics)
    avg_hue = sum(item["hue"] for item in metrics) / len(metrics)
    avg_edges = sum(item["edge_density"] for item in metrics) / len(metrics)
    max_faces = int(max(item["faces"] for item in metrics))
    avg_green_ratio = sum(item.get("green_ratio", 0.0) for item in metrics) / len(metrics)
    avg_line_count = sum(item.get("line_count", 0.0) for item in metrics) / len(metrics)

    if avg_brightness < 60:
        light_desc = "un entorno con poca iluminación"
    elif avg_brightness > 180:
        light_desc = "un entorno muy iluminado"
    else:
        light_desc = "una iluminación moderada"

    if avg_saturation < 40:
        color_desc = "con colores neutros"
    else:
        if avg_hue < 20 or avg_hue >= 170:
            color_desc = "con tonos rojizos"
        elif avg_hue < 45:
            color_desc = "con matices anaranjados o amarillos"
        elif avg_hue < 70:
            color_desc = "con presencia de verdes"
        elif avg_hue < 130:
            color_desc = "con predominio de azules"
        else:
            color_desc = "con tonos fríos"

    if avg_edges < 0.05:
        texture_desc = "La escena se ve sencilla, con pocos contornos definidos."
    elif avg_edges > 0.18:
        texture_desc = "Hay bastantes detalles y contornos marcados en el entorno."
    else:
        texture_desc = "El entorno tiene una cantidad moderada de detalles."

    if max_faces > 1:
        faces_desc = f"Detecto aproximadamente {max_faces} rostros en el encuadre."
    elif max_faces == 1:
        faces_desc = "Veo un rostro presente en la escena."
    else:
        faces_desc = "No logro identificar rostros con claridad."

    subject_notes = ""
    pcb_hint = avg_green_ratio > 0.18 and avg_edges > 0.07 and avg_line_count > 20
    connector_hint = avg_green_ratio > 0.08 and avg_line_count > 15 and avg_edges > 0.06
    tech_hint = avg_edges > 0.16 and avg_green_ratio < 0.05
    if pcb_hint:
        subject_notes = (
            " La combinación de verde saturado y muchas líneas rectas se parece a una placa madre o circuito impreso."
        )
    elif connector_hint:
        subject_notes = " Veo conectores y pistas paralelas, así que luce como hardware electrónico."
    elif tech_hint:
        subject_notes = " Hay bastantes aristas y figuras geométricas, parece un objeto tecnológico."

    semantic_notes = ""
    if semantic_caption:
        semantic_notes = f" También parece: {semantic_caption}."

    return f"Percibo {light_desc} {color_desc}. {texture_desc} {faces_desc}{subject_notes}{semantic_notes}"


def open_camera_preview_and_analyze(camera_index: int = 0, preview_duration: float = 8.0) -> Tuple[bool, str]:
    if cv2 is None or np is None:
        return False, "Necesito que instales las dependencias de visión (opencv-python y numpy) para usar la cámara."
    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY
    cap = cv2.VideoCapture(camera_index, backend)
    if not cap or not cap.isOpened():
        if cap:
            cap.release()
        return False, "No logré acceder a esa cámara."
    cv2.namedWindow("MiauCam", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("MiauCam", 800, 450)
    collected_metrics: List[Dict[str, float]] = []
    representative_frame = None
    last_capture = 0.0
    start_time = time.time()
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("MiauCam", frame)
            if len(collected_metrics) < 120:
                metrics = _analyze_frame_snapshot(frame)
                if metrics:
                    collected_metrics.append(metrics)
            now = time.time()
            if representative_frame is None or now - last_capture >= 1.5:
                try:
                    representative_frame = frame.copy()
                except Exception:
                    representative_frame = frame
                last_capture = now
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if time.time() - start_time >= preview_duration:
                break
    finally:
        cap.release()
        try:
            cv2.destroyWindow("MiauCam")
        except Exception:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
    semantic_caption = _semantic_caption_from_array(representative_frame) if representative_frame is not None else None
    description = _describe_scene_from_metrics(collected_metrics, semantic_caption)
    return True, description


def analyze_image_file(path: str) -> Tuple[bool, str]:
    if cv2 is None or np is None:
        return False, "Necesito opencv-python y numpy instalados para interpretar imágenes adjuntas."
    if not os.path.exists(path):
        return False, "No encuentro el archivo seleccionado."
    image = cv2.imread(path)
    if image is None:
        return False, "No pude abrir la imagen, quizá el formato no es compatible."
    metrics = _analyze_frame_snapshot(image)
    if not metrics:
        return False, "No logré extraer detalles de la imagen."
    semantic_caption = _semantic_caption_from_array(image)
    description = _describe_scene_from_metrics([metrics], semantic_caption)
    height, width = image.shape[:2]
    return True, f"{description} Resolución aproximada: {width}x{height} píxeles."


def query_llm(messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
    target_model = model or LLM_MODEL
    errors: List[str] = []

    def invoke_remote(chosen_model: str) -> str:
        try:
            if "openai.com" in LLM_BASE_URL:
                response = client.responses.create(
                    model=chosen_model,
                    input=[{"role": message["role"], "content": message["content"]} for message in messages],
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )
                chunks: List[str] = []
                for item in getattr(response, "output", []) or []:
                    if getattr(item, "type", None) != "message":
                        continue
                    message_block = getattr(item, "message", None)
                    if not message_block:
                        continue
                    for content in getattr(message_block, "content", []) or []:
                        if getattr(content, "type", None) == "text":
                            chunks.append(getattr(content, "text", ""))
                return " ".join(chunks).strip() if chunks else ""
            completion = client.chat.completions.create(
                model=chosen_model,
                messages=messages,
                max_tokens=MAX_OUTPUT_TOKENS,
            )
            return completion.choices[0].message.content.strip()
        except Exception as exc:  # pragma: no cover - depende de red externa
            error_text = str(exc)
            errors.append(error_text)
            debug_log(f"Error en la solicitud al modelo ({chosen_model}): {error_text}")
            return ""

    remote_models: List[str] = []
    if LLM_API_KEY:
        remote_models.append(target_model)
        if LLM_FALLBACK_MODEL and LLM_FALLBACK_MODEL != target_model:
            remote_models.append(LLM_FALLBACK_MODEL)

    def try_remote_sequence() -> str:
        for selected in remote_models:
            reply = invoke_remote(selected)
            if reply:
                return reply
        return ""

    remote_first = bool(remote_models) and not LOCAL_LLM_STRICT
    remote_after_local = bool(remote_models) and LOCAL_LLM_STRICT

    if remote_first:
        response = try_remote_sequence()
        if response:
            return response

    if local_llm_configured():
        local_reply = query_local_llm(messages)
        if local_reply:
            return local_reply

    if remote_after_local:
        response = try_remote_sequence()
        if response:
            return response

    for error_text in errors:
        if "Insufficient credits" in error_text or "requires more credits" in error_text:
            return (
                "No tengo crédito disponible en el modelo configurado."
                " Revisa tu cuenta de OpenRouter u OpenAI para agregar saldo o proporciona otra clave."
            )
        if "No endpoints found" in error_text and "openrouter" in LLM_BASE_URL and not local_llm_configured():
            return (
                "No encuentro un endpoint válido para OpenRouter en este momento."
                " Verifica tu conexión o habilita el modelo local con Ollama."
            )

    if local_llm_configured():
        return (
            "Intenté usar el modelo local pero no logré obtener respuesta."
            " Asegúrate de que Ollama esté ejecutándose con el modelo descargado."
        )
    return "Tengo dificultades para conectarme con mi modelo cognitivo ahora mismo."


def limit_history(history: List[Dict[str, str]], max_len: int) -> List[Dict[str, str]]:
    if len(history) <= max_len:
        return history
    return history[-max_len:]


def extract_focus_text(original: str, keywords: List[str]) -> str:
    pattern = r"|".join([re.escape(word) for word in keywords])
    cleaned = re.sub(pattern, "", original, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def clean_music_query(text: str) -> str:
    cleaned = text
    removal_patterns = [
        r"\bpon(?:er)?\b",
        r"\breproduce\b",
        r"\bponme\b",
        r"\bplay\b",
        r"\bescucha[r]?\b",
        r"\bquiero\s+(?:o[ií]r|escuchar)\b",
        r"\bsuena\b",
        r"\ben\s+youtube\b",
        r"\bm[uú]sica\b",
        r"\bcanci[oó]n\b",
        r"\bplaylist\b",
        r"\bde\s+la\s+can(?:ci[oó]n)?\b",
        r"\bpuedes\b",
        r"\bquiero\b",
    ]
    for pattern in removal_patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bde\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*[-/]\s*", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"^(?:de|del|la|el|los|las)\s+", "", cleaned, flags=re.IGNORECASE)
    if not cleaned:
        return text.strip()
    return cleaned


def fetch_music_recommendations(query: str, limit: int = 3) -> List[str]:
    results: List[str] = []
    try:
        params = {"term": query, "limit": limit, "media": "music"}
        response = requests.get("https://itunes.apple.com/search", params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
        for entry in payload.get("results", []):
            track = entry.get("trackName")
            artist = entry.get("artistName")
            preview = entry.get("previewUrl")
            if not track or not artist:
                continue
            snippet = f"{track} de {artist}"
            if preview:
                snippet += f" (escucha previa: {preview})"
            results.append(snippet)
            if len(results) == limit:
                break
    except Exception as exc:
        debug_log(f"Error recuperando recomendaciones musicales: {exc}")
    if results:
        return results
    return [entry["summary"] for entry in search_youtube(query, limit=limit, filter_music=True)]


def fetch_video_recommendations(query: str, limit: int = 3) -> List[str]:
    return [entry["summary"] for entry in search_youtube(query, limit=limit)]


def fetch_anime_recommendations(query: str, limit: int = 4) -> List[str]:
    params = {
        "q": query,
        "limit": limit,
        "sfw": "true",
        "order_by": "score",
        "sort": "desc",
    }
    try:
        response = requests.get("https://api.jikan.moe/v4/anime", params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        debug_log(f"Error consultando sugerencias de anime: {exc}")
        return []
    results: List[str] = []
    for item in payload.get("data", []):
        title = item.get("title") or item.get("title_english")
        score = item.get("score")
        year = item.get("year")
        url = item.get("url")
        if not title:
            continue
        snippet = title
        if year:
            snippet += f" ({year})"
        if score:
            snippet += f" - puntuación {score:.1f}"
        if url:
            snippet += f" - {url}"
        results.append(snippet)
        if len(results) == limit:
            break
    return results


def perform_web_search(query: str, limit: int = 3) -> List[str]:
    snippets = fetch_web_snippets(query, limit)
    if not snippets:
        return []
    return [f"{item['snippet']} - {item['url']}" for item in snippets]


def needs_step_by_step_response(text_lower: str) -> bool:
    triggers = [
        "paso", "pasos", "cómo", "como ", "como puedo", "como hacer", "guía", "guia",
        "tutorial", "instrucciones", "instrucción", "instruccion", "easter egg", "walkthrough", "resolver",
        "haz", "hacer", "cómo consigo", "como consigo", "explica", "monta", "desbloquear",
    ]
    return any(trigger in text_lower for trigger in triggers)


def is_video_game_query(text_lower: str) -> bool:
    return any(keyword in text_lower for keyword in VIDEO_GAME_KEYWORDS)


def detect_curated_game_entries(text_lower: str) -> Optional[List[Dict[str, str]]]:
    for key, entries in CURATED_GAME_GUIDES.items():
        if key in text_lower:
            return entries
        tokens = [token for token in key.split() if token]
        if tokens and all(token in text_lower for token in tokens):
            return entries
    return None


def format_curated_game_guide(query: str, entries: List[Dict[str, str]]) -> str:
    focus = query.strip() or "este reto"
    lines = [f"Guía verificada para {focus}:"]
    for idx, entry in enumerate(entries, 1):
        title = entry.get("title") or f"Paso {idx}"
        snippet = entry.get("snippet") or ""
        url = entry.get("url")
        step = f"{idx}. {title}. {snippet}".strip()
        if url:
            step += f" Fuente: {url}"
        lines.append(step)
    lines.append("Recuerda verificar la versión del juego o parches recientes antes de intentarlo.")
    return "\n".join(lines)


def _extract_recipe_tokens(normalized_text: str) -> List[str]:
    return [token for token in re.findall(r"[a-z0-9]+", normalized_text) if len(token) >= 3]


def _infer_recipe_filters(normalized_text: str) -> Set[str]:
    filters: Set[str] = set()
    for needle, mapped in RECIPE_FILTER_HINTS.items():
        if needle and needle in normalized_text:
            filters.update(mapped)
    return filters


def _match_recipe_aliases(normalized_text: str) -> List[str]:
    hits: List[str] = []
    normalized_tokens = set(_extract_recipe_tokens(normalized_text))
    for alias, recipe_id in CURATED_RECIPE_ALIAS_INDEX.items():
        if not alias:
            continue
        if alias in normalized_text:
            hits.append(recipe_id)
            continue
        alias_tokens = [token for token in alias.split() if len(token) >= 3]
        if alias_tokens and all(token in normalized_tokens for token in alias_tokens):
            hits.append(recipe_id)
    return hits


def lookup_curated_recipes(query: str, filters: Optional[Set[str]] = None, limit: int = 3) -> List[Dict[str, Any]]:
    if not CURATED_RECIPES or limit <= 0:
        return []
    normalized = _normalize_command_text(query)
    filter_set = {tag for tag in (filters or set()) if tag}
    seen: Set[str] = set()
    matches: List[Dict[str, Any]] = []

    for recipe_id in _match_recipe_aliases(normalized):
        if recipe_id not in seen:
            recipe = CURATED_RECIPES.get(recipe_id)
            if recipe:
                matches.append(recipe)
                seen.add(recipe_id)
                if len(matches) >= limit:
                    return matches

    tokens = [token for token in _extract_recipe_tokens(normalized) if token not in {"receta", "recetas", "cocina", "cocinar"}]
    candidate_scores: Counter[str] = Counter()
    for token in tokens[:20]:
        for recipe_id in CURATED_RECIPE_TAG_INDEX.get(token, set()):
            candidate_scores[recipe_id] += 2
    for filter_tag in filter_set:
        for recipe_id in CURATED_RECIPE_TAG_INDEX.get(filter_tag, set()):
            candidate_scores[recipe_id] += 3

    for recipe_id, _score in candidate_scores.most_common(limit * 2):
        if recipe_id not in seen:
            recipe = CURATED_RECIPES.get(recipe_id)
            if recipe:
                matches.append(recipe)
                seen.add(recipe_id)
            if len(matches) >= limit:
                break
    return matches


def pick_random_recipes(count: int, filters: Optional[Set[str]] = None, rng: Optional[random.Random] = None) -> List[Dict[str, Any]]:
    if not CURATED_RECIPES or count <= 0:
        return []
    rng = rng or random
    candidate_ids: Set[str] = set()
    if filters:
        for filter_tag in filters:
            candidate_ids.update(CURATED_RECIPE_TAG_INDEX.get(filter_tag, set()))
    if not candidate_ids:
        candidate_ids = set(CURATED_RECIPES.keys())
    pool = list(candidate_ids)
    if not pool:
        return []
    sample_size = min(len(pool), max(1, count))
    chosen = rng.sample(pool, sample_size)
    return [CURATED_RECIPES[recipe_id] for recipe_id in chosen if recipe_id in CURATED_RECIPES]


def format_recipe_detail(recipe: Dict[str, Any], dataset_size: int) -> str:
    name = recipe.get("name", "receta curada")
    time_minutes = recipe.get("time_minutes")
    difficulty = recipe.get("difficulty", "media")
    servings = recipe.get("servings")
    stats_parts = []
    if isinstance(time_minutes, int):
        stats_parts.append(f"Tiempo estimado: {time_minutes} min")
    else:
        stats_parts.append("Tiempo estimado: variable")
    stats_parts.append(f"Dificultad {difficulty}")
    if servings:
        stats_parts.append(f"Rinde {servings} porciones")
    signature_tags = [recipe.get("cuisine"), recipe.get("diet"), recipe.get("meal_type"), recipe.get("equipment")]
    readable_tags = ", ".join(tag for tag in signature_tags if tag)
    ingredients = recipe.get("ingredients") or []
    ingredient_line = ""
    if ingredients:
        preview = "; ".join(ingredients[:4])
        if len(ingredients) > 4:
            preview += "..."
        ingredient_line = f"Ingredientes base: {preview}."
    steps = recipe.get("steps") or []
    tips = recipe.get("tips") or []
    lines = [
        f"Receta entrenada ({dataset_size} disponibles): {name}.",
        " · ".join(stats_parts) + ".",
    ]
    if readable_tags:
        lines.append(f"Etiquetas clave: {readable_tags}.")
    if ingredient_line:
        lines.append(ingredient_line)
    if steps:
        lines.append("Pasos:")
        for idx, step in enumerate(steps, 1):
            lines.append(f"{idx}. {step}")
    if tips:
        lines.append("Consejos: " + " ".join(tips))
    lines.append("¿Quieres otra combinación? Pídeme más ideas por dieta, tiempo o ingrediente.")
    return "\n".join(lines)


def format_recipe_brainstorm(recipes: List[Dict[str, Any]], dataset_size: int, filters: Optional[Set[str]] = None) -> str:
    if not recipes:
        return (
            "No tengo recetas que coincidan con ese filtro todavía. Dime un ingrediente principal, una dieta o un tiempo y lo intento de nuevo."
        )
    focus_note = ""
    if filters:
        readable = ", ".join(sorted(filter_tag.replace("_", " ") for filter_tag in filters if filter_tag))
        if readable:
            focus_note = f" con enfoque en {readable}"
    lines = [
        f"Ideas frescas{focus_note}: tengo {dataset_size} recetas entrenadas y estas pueden inspirarte:",
    ]
    for idx, recipe in enumerate(recipes, 1):
        time_minutes = recipe.get("time_minutes", "?")
        diet = recipe.get("diet", "dieta")
        cuisine = recipe.get("cuisine", "fusion")
        lines.append(f"{idx}. {recipe.get('name', 'Receta')} ({time_minutes} min, {diet}, {cuisine}).")
        tip = (recipe.get("tips") or ["Ajusta las especias a tu gusto."])[0]
        lines.append(f"   Tip: {tip}")
    lines.append("Pídeme otra ronda si quieres más opciones o cambia el filtro (ej. vegana, cena ligera, sin carne).")
    return "\n".join(lines)


def _infer_hardware_filters(normalized_text: str) -> Set[str]:
    filters: Set[str] = set()
    for needle, mapped in HARDWARE_FILTER_HINTS.items():
        if needle and needle in normalized_text:
            filters.update(mapped)
    return filters


def _match_hardware_aliases(normalized_text: str, mode: Optional[str]) -> List[str]:
    hits: List[str] = []
    for alias, build_id in CURATED_HARDWARE_ALIAS_INDEX.items():
        if alias and alias in normalized_text:
            entry = CURATED_HARDWARE_BUILDS.get(build_id)
            if not entry:
                continue
            entry_type = entry.get("type")
            if mode and entry_type != mode:
                continue
            hits.append(build_id)
    return hits


def lookup_hardware_builds(
    query: str,
    filters: Optional[Set[str]] = None,
    mode: Optional[str] = None,
    limit: int = 3,
) -> List[Dict[str, Any]]:
    if not CURATED_HARDWARE_BUILDS or limit <= 0:
        return []
    normalized = _normalize_command_text(query)
    filter_set = {tag for tag in (filters or set()) if tag}
    matches: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    alias_hits = _match_hardware_aliases(normalized, mode)
    for build_id in alias_hits:
        entry = CURATED_HARDWARE_BUILDS.get(build_id)
        if entry and build_id not in seen:
            matches.append(entry)
            seen.add(build_id)
            if len(matches) >= limit:
                return matches

    candidate_scores: Counter[str] = Counter()

    def _add_candidates(tag: str, weight: int) -> None:
        build_ids = CURATED_HARDWARE_TAG_INDEX.get(tag, set())
        for build_id in build_ids:
            if build_id in seen:
                continue
            entry = CURATED_HARDWARE_BUILDS.get(build_id)
            if not entry:
                continue
            if mode and entry.get("type") != mode:
                continue
            candidate_scores[build_id] += weight

    for filter_tag in filter_set:
        _add_candidates(filter_tag, 4)

    tokens = [token for token in _extract_recipe_tokens(normalized) if token not in HARDWARE_TOKEN_STOPWORDS]
    for token in tokens[:30]:
        _add_candidates(token, 1)

    for build_id, _score in candidate_scores.most_common(limit * 2):
        if build_id in seen:
            continue
        entry = CURATED_HARDWARE_BUILDS.get(build_id)
        if entry:
            matches.append(entry)
            seen.add(build_id)
        if len(matches) >= limit:
            break
    return matches


def pick_random_hardware_builds(
    count: int,
    mode: Optional[str] = None,
    filters: Optional[Set[str]] = None,
    rng: Optional[random.Random] = None,
) -> List[Dict[str, Any]]:
    if not CURATED_HARDWARE_BUILDS or count <= 0:
        return []
    rng = rng or random
    candidate_ids: Set[str] = set()
    filter_set = {tag for tag in (filters or set()) if tag}
    for filter_tag in filter_set:
        candidate_ids.update(CURATED_HARDWARE_TAG_INDEX.get(filter_tag, set()))
    if not candidate_ids:
        candidate_ids = set(CURATED_HARDWARE_BUILDS.keys())
    if mode:
        candidate_ids = {
            build_id
            for build_id in candidate_ids
            if CURATED_HARDWARE_BUILDS.get(build_id, {}).get("type") == mode
        }
    pool = list(candidate_ids)
    if not pool:
        pool = [
            build_id
            for build_id, entry in CURATED_HARDWARE_BUILDS.items()
            if not mode or entry.get("type") == mode
        ]
    if not pool:
        return []
    sample_size = min(len(pool), max(1, count))
    chosen = rng.sample(pool, sample_size)
    return [CURATED_HARDWARE_BUILDS[build_id] for build_id in chosen if build_id in CURATED_HARDWARE_BUILDS]


def format_hardware_build_detail(build: Dict[str, Any], dataset_size: int) -> str:
    title = build.get("title", "Configuración recomendada")
    release_year = build.get("release_window", "N/A")
    use_cases = ", ".join(build.get("use_cases", [])) or "uso general"
    budget = build.get("budget_tier", "personalizado")
    system = build.get("recommended_os", "Windows 11 Pro")
    header = f"Configuración entrenada ({dataset_size} combinaciones) - {title} ({release_year})."
    lines = [header, f"Perfil: {use_cases} | Presupuesto: {budget}."]
    if build.get("type") == "desktop":
        resolution = build.get("resolution", "multi monitor")
        lines.append(f"Objetivo: {resolution} | PSU: {build.get('psu', 'N/A')} | Enfriamiento: {build.get('cooling', 'estándar')}.")
    else:
        default_display = '16"'
        lines.append(
            f"Pantalla: {build.get('display', default_display)} | Batería: {build.get('battery', '80 Wh')} | Peso: {build.get('weight', '2 kg')}"
        )
    components = build.get("components") or []
    if components:
        lines.append("Componentes sugeridos:")
        for idx, component in enumerate(components, 1):
            lines.append(f"{idx}. {component}")
    summary = build.get("summary")
    if summary:
        lines.append(summary)
    lines.append(f"Sistema recomendado: {system}.")
    lines.append("Puedo ajustar la lista si cambias resolución, presupuesto o prefieres otra marca.")
    return "\n".join(lines)


def format_hardware_brainstorm(
    builds: List[Dict[str, Any]],
    dataset_size: int,
    mode: Optional[str] = None,
    filters: Optional[Set[str]] = None,
) -> str:
    if not builds:
        return "No encontré coincidencias directas; dame presupuesto, resolución o marca preferida y recalculo."
    focus = "pc" if mode == "desktop" else "laptop" if mode == "laptop" else "equipo"
    filter_note = ""
    if filters:
        readable = ", ".join(sorted(filter_tag.replace("_", " ") for filter_tag in filters if filter_tag))
        if readable:
            filter_note = f" con foco en {readable}"
    lines = [
        f"Otras ideas ({dataset_size} combinaciones registradas) para tu {focus}{filter_note}:",
    ]
    for idx, build in enumerate(builds, 1):
        lines.append(
            f"{idx}. {build.get('title', 'Opción')} ({build.get('release_window', 'N/A')}, {build.get('budget_tier', 'personalizado')})."
        )
        lines.append(f"   Uso destacado: {', '.join(build.get('use_cases', [])) or 'multipropósito'}.")
    lines.append("Pide detalles de alguna opción para desglosar componentes o comparar.")
    return "\n".join(lines)


def _humanize_use_cases(use_cases: Optional[List[str]]) -> str:
    if not use_cases:
        return "uso general"
    cleaned = [tag.replace("_", " ") for tag in use_cases if tag]
    return ", ".join(cleaned) if cleaned else "uso general"


def _detect_hardware_component_focus(normalized_text: str) -> Optional[str]:
    if not normalized_text:
        return None
    if not any(trigger in normalized_text for trigger in HARDWARE_DETAIL_TRIGGERS):
        return None
    for slot, keywords in HARDWARE_COMPONENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword and keyword in normalized_text:
                return slot
    return None


COMPONENT_DISPLAY_NAMES = {
    "cpu": "Procesador",
    "gpu": "GPU",
    "ram": "RAM",
    "storage": "Almacenamiento",
    "motherboard": "Placa base",
    "psu": "Fuente",
    "cooling": "Refrigeración",
    "case": "Gabinete",
    "display": "Pantalla",
    "battery": "Batería",
    "weight": "Peso",
}


def _extract_component_value(build: Dict[str, Any], slot: str) -> str:
    if slot == "storage":
        storage_items = build.get("storage") or []
        return ", ".join(storage_items)
    if slot == "ram":
        return build.get("ram", "")
    if slot == "display":
        return build.get("display", "")
    if slot == "battery":
        return build.get("battery", "")
    if slot == "weight":
        return build.get("weight", "")
    return build.get(slot, "")


def format_hardware_component_detail(build: Dict[str, Any], slot: str, dataset_size: int) -> str:
    display_name = COMPONENT_DISPLAY_NAMES.get(slot, slot.upper())
    component_value = _extract_component_value(build, slot)
    title = build.get("title", "configuración recomendada")
    if not component_value:
        return (
            f"No tengo fichas detalladas del {display_name.lower()} para {title}. "
            "Puedo proponer otra pieza si me dices qué priorizas (potencia, silencio o presupuesto)."
        )
    use_case_desc = _humanize_use_cases(build.get("use_cases"))
    resolution = build.get("resolution", "resoluciones altas")
    budget_label = (build.get("budget_tier") or "personalizado").replace("_", " ")
    lines = [
        f"Detalle entrenado ({dataset_size} combinaciones) - {display_name} en {title}:",
        f"- Especificacion propuesta: {component_value}.",
    ]
    if slot == "cpu":
        gpu = build.get("gpu", "la GPU prevista")
        lines.append(
            f"- Mantiene el perfil {use_case_desc} sin cuellos de botella frente a {gpu} para el objetivo {resolution}."
        )
        motherboard = build.get("motherboard")
        if motherboard:
            lines.append(
                f"- La placa {motherboard} ya está seleccionada para futuras actualizaciones o ajustes de voltaje."
            )
        cooling = build.get("cooling")
        if cooling:
            lines.append(f"- {cooling} sostiene temperaturas estables incluso bajo cargas prolongadas.")
    elif slot == "gpu":
        psu = build.get("psu", "la fuente recomendada")
        lines.append(
            f"- Se elige para cumplir el objetivo {resolution} en escenarios de {use_case_desc} sin exigir overclock extremo." 
        )
        lines.append(f"- La fuente {psu} deja margen para picos y asegura eficiencia dentro del presupuesto {budget_label}.")
    elif slot == "ram":
        lines.append(
            f"- La capacidad propuesta cubre multitarea y proyectos de {use_case_desc} sin swaps innecesarios."
        )
        motherboard = build.get("motherboard")
        if motherboard:
            lines.append(f"- Validado con {motherboard} para aprovechar perfiles XMP/EXPO estables.")
    elif slot == "storage":
        storage_items = build.get("storage") or []
        if storage_items:
            primary = storage_items[0]
            lines.append(f"- {primary} se usa como unidad principal para SO y apps sensibles.")
            if len(storage_items) > 1:
                lines.append(
                    f"- El resto ({', '.join(storage_items[1:])}) separa bibliotecas, capturas o proyectos pesados."
                )
        lines.append("- Mantiene un balance entre velocidad y costo sin salirse del presupuesto.")
    elif slot == "motherboard":
        cpu = build.get("cpu", "el CPU propuesto")
        lines.append(f"- Garantiza compatibilidad directa con {cpu} y con la RAM declarada.")
        lines.append("- Ofrece suficientes fases y puertos para upgrades sin cambiar toda la plataforma.")
    elif slot == "psu":
        gpu = build.get("gpu", "la GPU prevista")
        lines.append(
            f"- Tiene margen para el consumo combinado de {gpu} y el resto del build, evitando trabajar al 100% continuo."
        )
        lines.append("- Certificacion 80+ asegura eficiencia y menos calor en sesiones prolongadas.")
    elif slot == "cooling":
        cpu = build.get("cpu", "el CPU propuesto")
        lines.append(f"- Mantiene a {cpu} dentro de un delta térmico seguro incluso con boost sostenido.")
        case = build.get("case")
        if case:
            lines.append(f"- El gabinete {case} tiene flujo pensado para aprovechar este sistema de refrigeracion.")
    elif slot == "case":
        cooling = build.get("cooling", "la solución térmica sugerida")
        lines.append(f"- Flujo y espacio pensados para {cooling}, facilitando airflow limpio.")
        lines.append("- Incluye gestión de cables y espacio para futuras GPU sin restricciones.")
    elif slot == "display":
        battery = build.get("battery")
        lines.append(f"- Se calibra con el perfil {use_case_desc} para ofrecer la claridad adecuada.")
        if battery:
            lines.append(f"- Coordinado con la bateria de {battery} para sostener sesiones unplugged.")
    elif slot == "battery":
        weight = build.get("weight")
        lines.append(f"- Otorga autonomia acorde al perfil {use_case_desc} sin inflar demasiado el peso.")
        if weight:
            lines.append(f"- Junto al peso de {weight} sigue siendo viable para movilidad diaria.")
    elif slot == "weight":
        lines.append(f"- Mantiene la movilidad para tareas de {use_case_desc} sin sacrificar rigidez del chasis.")
        battery = build.get("battery")
        if battery:
            lines.append(f"- Se equilibra con la bateria ({battery}) para no comprometer autonomía.")
    else:
        summary = build.get("summary")
        if summary:
            lines.append(summary)
    lines.append("¿Quieres que compare otra pieza o prioricemos silencio, fps o presupuesto?")
    return "\n".join(lines)


def _infer_anime_filters(normalized_text: str) -> Set[str]:
    filters: Set[str] = set()
    for needle, mapped in ANIME_FILTER_HINTS.items():
        if needle and needle in normalized_text:
            filters.update(mapped)
    return filters


def _match_anime_aliases(normalized_text: str) -> List[str]:
    hits: List[str] = []
    for alias, anime_id in CURATED_ANIME_ALIAS_INDEX.items():
        if alias and alias in normalized_text:
            hits.append(anime_id)
    return hits


def lookup_anime_titles(
    query: str,
    filters: Optional[Set[str]] = None,
    limit: int = 4,
) -> List[Dict[str, Any]]:
    if not CURATED_ANIME_TITLES or limit <= 0:
        return []
    normalized = _normalize_command_text(query)
    filter_set = {tag for tag in (filters or set()) if tag}
    matches: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    alias_hits = _match_anime_aliases(normalized)
    for anime_id in alias_hits:
        entry = CURATED_ANIME_TITLES.get(anime_id)
        if entry and anime_id not in seen:
            matches.append(entry)
            seen.add(anime_id)
            if len(matches) >= limit:
                return matches

    candidate_scores: Counter[str] = Counter()

    def _add_candidates(tag: str, weight: int) -> None:
        anime_ids = CURATED_ANIME_TAG_INDEX.get(tag, set())
        for anime_id in anime_ids:
            if anime_id in seen:
                continue
            if anime_id in CURATED_ANIME_TITLES:
                candidate_scores[anime_id] += weight

    for filter_tag in filter_set:
        _add_candidates(filter_tag, 4)

    tokens = [token for token in _extract_recipe_tokens(normalized) if token not in ANIME_TOKEN_STOPWORDS]
    for token in tokens[:40]:
        _add_candidates(token, 1)

    for anime_id, _score in candidate_scores.most_common(limit * 3):
        if anime_id in seen:
            continue
        entry = CURATED_ANIME_TITLES.get(anime_id)
        if entry:
            matches.append(entry)
            seen.add(anime_id)
        if len(matches) >= limit:
            break
    return matches


def pick_random_anime_titles(
    count: int,
    filters: Optional[Set[str]] = None,
    rng: Optional[random.Random] = None,
) -> List[Dict[str, Any]]:
    if not CURATED_ANIME_TITLES or count <= 0:
        return []
    rng = rng or random
    candidate_ids: Set[str] = set()
    filter_set = {tag for tag in (filters or set()) if tag}
    for filter_tag in filter_set:
        candidate_ids.update(CURATED_ANIME_TAG_INDEX.get(filter_tag, set()))
    if not candidate_ids:
        candidate_ids = set(CURATED_ANIME_TITLES.keys())
    pool = list(candidate_ids)
    if not pool:
        pool = list(CURATED_ANIME_TITLES.keys())
    if not pool:
        return []
    sample_size = min(len(pool), max(1, count))
    chosen = rng.sample(pool, sample_size)
    return [CURATED_ANIME_TITLES[anime_id] for anime_id in chosen if anime_id in CURATED_ANIME_TITLES]


def format_anime_detail(entry: Dict[str, Any], dataset_size: int) -> str:
    title = entry.get("title", "Anime recomendado")
    release_year = entry.get("release_year", "N/A")
    fmt = entry.get("format", "TV")
    genres = ", ".join(entry.get("genres", [])) or "género híbrido"
    themes = ", ".join(entry.get("themes", [])) or "temáticas variadas"
    studio = entry.get("studio", "estudio independiente")
    tone = entry.get("tone", "versátil")
    rating = entry.get("age_rating", "PG-13")
    summary = entry.get("summary", "")
    streaming = ", ".join(entry.get("streaming", [])) or "plataformas habituales"
    mood = ", ".join(entry.get("mood_tags", [])) or "multi-mood"
    header = f"Anime entrenado ({dataset_size} títulos) - {title} ({release_year})."
    lines = [header, f"Formato: {fmt} | Géneros: {genres} | Temas: {themes}."]
    if entry.get("type") == "season":
        lines.append(
            f"Episodios: {entry.get('episodes', '?')} | Duración: {entry.get('duration', 'N/A')} | Estudio: {studio}."
        )
    else:
        lines.append(f"Duración: {entry.get('duration', 'Película 90 min')} | Estudio: {studio}.")
    lines.append(f"Tono: {tone} | Rating: {rating} | Disponible en: {streaming}.")
    lines.append(f"Mood recomendado: {mood}.")
    if summary:
        lines.append(summary)
    lines.append("Puedo buscar otra temporada, spin-off o película si quieres más alternativas.")
    return "\n".join(lines)


def format_anime_brainstorm(
    entries: List[Dict[str, Any]],
    dataset_size: int,
    filters: Optional[Set[str]] = None,
) -> str:
    if not entries:
        return "No tengo coincidencias con esos filtros aún; dime género, tono o formato (película/temporada) y te propongo algo."
    filter_note = ""
    if filters:
        readable = ", ".join(sorted(filter_tag.replace("_", " ") for filter_tag in filters if filter_tag))
        if readable:
            filter_note = f" con foco en {readable}"
    lines = [f"Ideas de anime ({dataset_size} títulos registrados){filter_note}:"]
    for idx, entry in enumerate(entries, 1):
        descriptor = entry.get("format", "TV")
        lines.append(
            f"{idx}. {entry.get('title', 'Anime')} ({entry.get('release_year', 'N/A')}, {descriptor})."
        )
        lines.append(
            f"   Géneros: {', '.join(entry.get('genres', [])) or 'mixto'} | Estudio: {entry.get('studio', 'estudio')} | Mood: {', '.join(entry.get('mood_tags', [])) or 'variado'}."
        )
    lines.append("Pide detalles de alguno o cambia filtros si buscas otra vibra.")
    return "\n".join(lines)


def _normalize_term(term: str) -> str:
    return re.sub(r"\s+", " ", term).strip()


def extract_game_context(text: str) -> Dict[str, List[str]]:
    lowered = text.lower()
    contexts: Dict[str, List[str]] = {"maps": [], "games": []}

    def _append_unique(collection: List[str], value: str) -> None:
        normalized = _normalize_term(value.lower())
        if normalized and normalized not in collection:
            collection.append(normalized)

    for known_map in KNOWN_ZOMBIES_MAPS:
        if known_map in lowered:
            _append_unique(contexts["maps"], known_map)
    for known_game in KNOWN_GAME_SERIES:
        if known_game in lowered:
            _append_unique(contexts["games"], known_game)
    for alias, canonical in GAME_SERIES_ALIASES.items():
        if alias in lowered:
            _append_unique(contexts["games"], canonical)

    map_patterns = re.findall(r"(?:mapa|map|mapa de|mapa del|en)\s+([\w\s'\-:]{3,40})", lowered)
    for match in map_patterns:
        _append_unique(contexts["maps"], match)

    quoted_segments = re.findall(r"[\"'“”«»](.+?)[\"'“”«»]", text)
    for segment in quoted_segments:
        cleaned = segment.strip()
        if cleaned:
            _append_unique(contexts["maps"], cleaned)

    game_pattern = re.findall(r"call of duty\s+[\w ]+", lowered)
    for match in game_pattern:
        _append_unique(contexts["games"], match)

    gta_pattern = re.findall(r"gta\s*(?:[ivx0-9]+|san andreas|vice city|online|liberty city|v|iv|iii)?", lowered)
    for match in gta_pattern:
        _append_unique(contexts["games"], match)

    return contexts


def build_game_alt_queries(query: str, text_lower: str) -> List[str]:
    extras: List[str] = []
    normalized = _normalize_term(query)
    if not normalized:
        return extras
    seen: Set[str] = {normalized.lower(), text_lower}
    contexts = extract_game_context(query or text_lower)
    map_targets = contexts.get("maps") or []
    game_targets = contexts.get("games") or []
    cheat_mode = any(keyword in text_lower for keyword in CHEAT_KEYWORDS)
    suffixes = list(GAME_QUERY_SUFFIXES)
    if cheat_mode:
        suffixes += CHEAT_QUERY_SUFFIXES

    def _add_candidate(candidate: str) -> None:
        lowered = candidate.lower()
        if lowered not in seen:
            extras.append(candidate)
            seen.add(lowered)

    for suffix in suffixes:
        _add_candidate(f"{normalized} {suffix}".strip())

    for map_name in map_targets:
        pretty_map = _normalize_term(map_name)
        for suffix in suffixes:
            _add_candidate(f"{pretty_map} {suffix}".strip())
        if game_targets:
            for game in game_targets:
                _add_candidate(f"{pretty_map} {game} guía")
                if cheat_mode:
                    _add_candidate(f"{pretty_map} {game} cheat codes")

    for game in game_targets:
        _add_candidate(f"{game} guía")
        _add_candidate(f"{game} tips")
        if cheat_mode:
            _add_candidate(f"{game} cheat codes")
            _add_candidate(f"{game} lista de trucos")

    for key in CURATED_GAME_GUIDES.keys():
        if key in text_lower:
            _add_candidate(f"{key} steps")

    if cheat_mode and "helic" in text_lower:
        _add_candidate(f"{normalized} helicopter cheat code")
        _add_candidate(f"{normalized} helicóptero código de truco")

    return extras[:8]


def _is_blocked_search_url(url: str) -> bool:
    try:
        hostname = urllib.parse.urlparse(url).netloc.lower()
    except ValueError:
        return False
    return any(hostname.endswith(domain) for domain in WEB_SEARCH_BLOCKED_DOMAINS)


def _fetch_duckduckgo_search(query: str, limit: int) -> List[Dict[str, str]]:
    if DDGS is None:
        raise RuntimeError("duckduckgo_search no está instalado")
    results: List[Dict[str, str]] = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, region="wt-wt", safesearch="moderate", timelimit=None):
            snippet = item.get("body") or item.get("snippet") or item.get("title")
            url = item.get("href") or item.get("url")
            if not snippet or not url or _is_blocked_search_url(url):
                continue
            results.append(
                {
                    "title": item.get("title") or snippet[:80],
                    "snippet": snippet,
                    "url": url,
                }
            )
            if len(results) >= limit:
                break
    return results


def _fetch_duckduckgo_html(query: str, limit: int) -> List[Dict[str, str]]:
    if BeautifulSoup is None:
        raise RuntimeError("beautifulsoup4 no está instalado")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/119.0 Safari/537.36",
        "Referer": "https://duckduckgo.com/",
    }
    response = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results: List[Dict[str, str]] = []
    for block in soup.select("div.result"):
        title_link = block.select_one("a.result__a")
        if not title_link:
            continue
        url = (title_link.get("href") or "").strip()
        if not url or url.startswith("https://duckduckgo.com/y.js") or _is_blocked_search_url(url):
            continue
        snippet_node = block.select_one("a.result__snippet")
        snippet_text = ""
        if snippet_node:
            snippet_text = snippet_node.get_text(" ", strip=True)
        if not snippet_text:
            extras = block.select_one("div.result__extras")
            if extras:
                snippet_text = extras.get_text(" ", strip=True)
        snippet_text = re.sub(r"\s+", " ", snippet_text)
        title_text = title_link.get_text(" ", strip=True)
        results.append(
            {
                "title": title_text[:160] or url,
                "snippet": snippet_text[:400] or title_text[:200],
                "url": url,
            }
        )
        if len(results) >= limit:
            break
    return results


def _fetch_mojeek_search(query: str, limit: int) -> List[Dict[str, str]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/119.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.5",
    }
    response = requests.get(
        "https://www.mojeek.com/search",
        params={"q": query, "fmt": "free"},
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    html_text = response.text
    pattern = re.compile(
        r'<a href="(?P<url>https?://[^"]+)" class="result-title"[^>]*>(?P<title>.*?)</a>.*?'
        r'<p class="result-description">(.*?)</p>',
        re.DOTALL,
    )
    results: List[Dict[str, str]] = []
    for match in pattern.finditer(html_text):
        url = html.unescape(match.group("url"))
        if _is_blocked_search_url(url):
            continue
        title = html.unescape(_strip_html_tags(match.group("title")))
        snippet = html.unescape(_strip_html_tags(match.group(3)))
        if not title:
            title = snippet[:80]
        if not snippet:
            continue
        results.append({"title": title, "snippet": snippet, "url": url})
        if len(results) >= limit:
            break
    return results


def _fetch_duckduckgo_api(query: str, limit: int) -> List[Dict[str, str]]:
    params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1, "ia": "web"}
    response = requests.get("https://api.duckduckgo.com/", params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
    results: List[Dict[str, str]] = []
    abstract = payload.get("AbstractText") or payload.get("Abstract")
    abstract_url = payload.get("AbstractURL")
    abstract_source = payload.get("AbstractSource")
    if abstract and abstract_url and not _is_blocked_search_url(abstract_url):
        results.append(
            {
                "title": abstract_source or "Resumen",
                "snippet": abstract,
                "url": abstract_url,
            }
        )
    for topic in payload.get("RelatedTopics", []):
        if isinstance(topic, dict) and topic.get("Text") and topic.get("FirstURL"):
            if _is_blocked_search_url(topic["FirstURL"]):
                continue
            results.append(
                {
                    "title": topic.get("Text").split(" - ")[0][:80],
                    "snippet": topic["Text"],
                    "url": topic["FirstURL"],
                }
            )
        elif isinstance(topic, dict) and topic.get("Topics"):
            for sub in topic.get("Topics", []):
                if sub.get("Text") and sub.get("FirstURL"):
                    if _is_blocked_search_url(sub["FirstURL"]):
                        continue
                    results.append(
                        {
                            "title": sub.get("Text").split(" - ")[0][:80],
                            "snippet": sub["Text"],
                            "url": sub["FirstURL"],
                        }
                    )
    return results[:limit]


def _fetch_duckduckgo_proxy(query: str, limit: int) -> List[Dict[str, str]]:
    params = {"q": query, "kl": "es-es"}
    response = requests.get("https://ddg-api.herokuapp.com/search", params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
    entries = payload.get("results") or payload
    results: List[Dict[str, str]] = []
    if isinstance(entries, list):
        for item in entries:
            snippet = item.get("snippet") or item.get("description") or item.get("title")
            url = item.get("link") or item.get("url")
            if snippet and url and not _is_blocked_search_url(url):
                results.append(
                    {
                        "title": item.get("title") or snippet[:80],
                        "snippet": snippet,
                        "url": url,
                    }
                )
            if len(results) >= limit:
                break
    return results


def fetch_web_snippets(query: str, limit: int = 5) -> List[Dict[str, str]]:
    providers: List[Tuple[str, Callable[[str, int], List[Dict[str, str]]]]] = [
        ("ddg_html", _fetch_duckduckgo_html),
        ("ddgs", _fetch_duckduckgo_search),
        ("mojeek", _fetch_mojeek_search),
        ("duckduckgo", _fetch_duckduckgo_api),
        ("ddg_proxy", _fetch_duckduckgo_proxy),
    ]
    errors: List[str] = []
    for name, provider in providers:
        try:
            results = provider(query, limit)
            if results:
                return results[:limit]
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    if errors:
        debug_log("Búsqueda web fallida: " + "; ".join(errors))
    return []


def summarize_web_research(
    query: str,
    limit: int = 5,
    force_steps: bool = False,
    alt_queries: Optional[List[str]] = None,
    additional_context: Optional[List[Dict[str, str]]] = None,
) -> Tuple[str, List[str]]:
    snippets: List[Dict[str, str]] = []
    if limit != 0:
        snippets = fetch_web_snippets(query, limit)
    seen_urls: Set[str] = {item["url"] for item in snippets if item.get("url")}
    desired_snippet_count = max(4 if force_steps else 3, limit or 0)

    if additional_context:
        for entry in additional_context:
            url = entry.get("url")
            if url and url not in seen_urls:
                snippets.append(entry)
                seen_urls.add(url)

    if alt_queries and len(snippets) < desired_snippet_count:
        for alt_query in alt_queries:
            if len(snippets) >= desired_snippet_count:
                break
            alt_query = alt_query.strip()
            if not alt_query:
                continue
            extra = fetch_web_snippets(alt_query, limit or 5)
            for entry in extra:
                url = entry.get("url")
                if url and url not in seen_urls:
                    snippets.append(entry)
                    seen_urls.add(url)
                if len(snippets) >= desired_snippet_count:
                    break

    if not snippets:
        return "", []

    max_entries = max(desired_snippet_count, min(len(snippets), 6))
    snippets = snippets[:max_entries]

    context_lines = []
    for idx, item in enumerate(snippets, 1):
        context_lines.append(
            f"{idx}. Fuente: {item['url']}\nFragmento: {item['snippet'][:300]}"
        )
    context_block = "\n\n".join(context_lines)

    if force_steps:
        user_prompt = (
            f"Consulta del usuario: {query}.\n\nInformación recopilada:\n{context_block}\n\n"
            "Construye una guía paso a paso (3 a 6 pasos) usando solo estos fragmentos."
            " Para cada paso, resume la acción concreta y menciona entre paréntesis una fuente corta como (Fuente 1)."
            " Cierra con un recordatorio de verificar la versión del juego si aplica."
        )
    else:
        user_prompt = (
            f"Consulta: {query}.\n\nInformación recopilada:\n{context_block}\n\n"
            "Redacta un resumen conciso (máximo 4 frases) basado únicamente en la evidencia dada."
            " Si hay incertidumbre, aclárala explícitamente."
        )

    messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente que sintetiza resultados de investigación en la web."
                " No inventes datos y cita con referencia numérica entre paréntesis cuando corresponda."
            ),
        },
        {"role": "user", "content": user_prompt},
    ]
    summary = query_llm(messages).strip()
    sources = [item["url"] for item in snippets if item.get("url")]
    return (summary, sources) if summary else ("", sources)


def search_youtube(query: str, limit: int = 3, filter_music: bool = False) -> List[Dict[str, str]]:
    params = {"q": query, "region": "MX"}
    if filter_music:
        params["filter"] = "music_songs"
    headers = {"Accept": "application/json"}
    errors: List[str] = []
    for base_url in PIPED_INSTANCES:
        try:
            response = requests.get(f"{base_url}/api/v1/search", params=params, headers=headers, timeout=10)
            response.raise_for_status()
            if "application/json" not in (response.headers.get("Content-Type") or ""):
                errors.append(f"Respuesta no JSON desde {base_url}")
                continue
            payload = response.json()
        except Exception as exc:
            errors.append(f"{base_url}: {exc}")
            continue
        results: List[Dict[str, str]] = []
        for entry in payload:
            if entry.get("type") != "stream":
                continue
            title = entry.get("title")
            video_id = entry.get("videoId")
            if not title or not video_id:
                continue
            channel = entry.get("uploaderName")
            url = f"https://youtu.be/{video_id}"
            summary = f"{title} ({channel}) - {url}" if channel else f"{title} - {url}"
            results.append(
                {
                    "title": title,
                    "channel": channel or "",
                    "video_id": video_id,
                    "url": url,
                    "summary": summary,
                }
            )
            if len(results) == limit:
                break
        if results:
            return results
    if errors:
        debug_log("Error consultando YouTube/Piped: " + "; ".join(errors))
    return []


def open_youtube_video(query: str) -> Tuple[bool, Optional[str]]:
    def _open_with_search_fallback(target_url: str, summary: Optional[str]) -> Tuple[bool, Optional[str]]:
        opened = launch_browser(target_url)
        if opened:
            return True, summary
        debug_log(f"No pude abrir directamente {target_url}. Intentaré con la búsqueda general de YouTube.")
        fallback_opened, fallback_summary = open_youtube_search_page(query)
        if fallback_summary:
            return fallback_opened, fallback_summary
        return False, summary

    matches = search_youtube(query, limit=1, filter_music=True)
    if matches:
        video = matches[0]
        return _open_with_search_fallback(video["url"], video["summary"])
    video_id = fetch_first_youtube_video_id(query)
    if video_id:
        url = f"https://youtu.be/{video_id}"
        summary = f"{query} - {url}"
        return _open_with_search_fallback(url, summary)
    return open_youtube_search_page(query)


def open_google_maps_route(destination: str, origin: Optional[str] = None) -> Tuple[bool, str]:
    if not destination:
        return False, ""
    params = {"api": "1", "destination": destination, "hl": "es"}
    if origin:
        params["origin"] = origin
    query = urllib.parse.urlencode(params)
    url = f"https://www.google.com/maps/dir/?{query}"
    launched = launch_browser(url, new=2)
    return launched, url


def open_google_search(query: str) -> Optional[str]:
    if not query:
        return None
    url = "https://www.google.com/search?" + urllib.parse.urlencode({"q": query})
    if HEADLESS_MODE:
        return url
    try:
        success = webbrowser.open(url)
        return url if success else None
    except Exception as exc:
        debug_log(f"Error al abrir búsqueda en Google: {exc}")
        return None


def open_animeflv_search(query: str) -> Optional[str]:
    if not query:
        return None
    encoded = urllib.parse.quote_plus(query)
    for template in ANIMEFLV_SEARCH_URLS:
        url = template.format(query=encoded)
        if HEADLESS_MODE:
            return url
        try:
            if webbrowser.open(url):
                return url
        except Exception as exc:
            debug_log(f"Error al abrir AnimeFLV ({url}): {exc}")
            continue
    return None


def open_youtube_search_page(query: str) -> Tuple[bool, Optional[str]]:
    if not query:
        return False, None
    url = "https://www.youtube.com/results?" + urllib.parse.urlencode({"search_query": query})
    opened = launch_browser(url)
    description = f"busqué {query} en YouTube - {url}"
    if not opened and HEADLESS_MODE:
        return False, description
    return opened, description


def fetch_first_youtube_video_id(query: str) -> Optional[str]:
    if not query:
        return None
    params = {"search_query": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    try:
        response = requests.get("https://www.youtube.com/results", params=params, headers=headers, timeout=10)
        response.raise_for_status()
        match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)
        if match:
            return match.group(1)
    except Exception as exc:
        debug_log(f"Error extrayendo video de YouTube: {exc}")
    return None


ROUTE_KEYWORDS = {
    "ruta",
    "dirección",
    "direccion",
    "ubicación",
    "ubicacion",
    "destino",
    "llegar",
    "llegue",
    "llego",
    "ir a",
    "ir hasta",
    "ir hacia",
    "cómo llegar",
    "como llegar",
    "como ir",
    "cómo ir",
    "como voy",
    "cómo voy",
    "maps",
    "mapa",
    "trayecto",
    "camino",
    "llevar",
    "llevarme",
    "indicaciones",
    "direccion a",
    "dónde queda",
    "donde queda",
    "donde está",
    "donde esta",
    "cómo puedo llegar",
    "como puedo llegar",
}


ROUTE_PATTERNS = [
    r"(como|cómo)\s+(puedo|podría|podria)?\s*(ir|llegar)",
    r"(llévame|llevarme)\s+(a|hasta)",
    r"d[oó]nde\s+(queda|est[aá])",
    r"necesito\s+ir\s+(a|hasta)",
]

GREETING_KEYWORDS = {
    "hola",
    "buenos días",
    "buen dia",
    "buenas tardes",
    "buenas noches",
    "qué tal",
    "como estas",
    "cómo estás",
    "que onda",
    "hey",
    "saludos",
}


DOCUMENT_KEYWORDS = {"documento", "documentos", "archivo", "archivos", "txt"}
DOCUMENT_VERBS = {"crea", "crear", "haz", "hacer", "genera", "generar", "escribe", "escribir", "prepara", "elabora", "arma"}
SUGGESTION_KEYWORDS = {
    "sugerencia",
    "sugerencias",
    "consejo",
    "consejos",
    "aconseja",
    "recomienda",
    "recomiéndame",
    "recomiendame",
    "opcion",
    "opciones",
}
OPINION_KEYWORDS = {
    "opinion",
    "opinión",
    "que opinas",
    "qué opinas",
    "tu opinion",
    "tu opinión",
    "dame tu opinion",
    "dame tu opinión",
    "cual es tu opinion",
    "cuál es tu opinión",
    "quiero tu opinion",
    "quiero tu opinión",
    "quien crees",
    "quién crees",
    "quien crees que",
    "quién crees que",
}

KNOWN_GOTY_WINNERS: Dict[int, str] = {
    2014: "Dragon Age: Inquisition",
    2015: "The Witcher 3: Wild Hunt",
    2016: "Overwatch",
    2017: "The Legend of Zelda: Breath of the Wild",
    2018: "God of War (2018)",
    2019: "Sekiro: Shadows Die Twice",
    2020: "The Last of Us Part II",
    2021: "It Takes Two",
    2022: "Elden Ring",
    2023: "Baldur's Gate 3",
}

GOTY_NOMINEES_BY_YEAR: Dict[int, List[str]] = {
    2023: [
        "Alan Wake 2",
        "Baldur's Gate 3",
        "Marvel's Spider-Man 2",
        "Resident Evil 4 (Remake)",
        "Super Mario Bros. Wonder",
        "The Legend of Zelda: Tears of the Kingdom",
    ],
    2022: [
        "A Plague Tale: Requiem",
        "Elden Ring",
        "God of War Ragnarök",
        "Horizon Forbidden West",
        "Stray",
        "Xenoblade Chronicles 3",
    ],
    2021: [
        "Deathloop",
        "It Takes Two",
        "Metroid Dread",
        "Psychonauts 2",
        "Ratchet & Clank: Rift Apart",
        "Resident Evil Village",
    ],
    2020: [
        "Animal Crossing: New Horizons",
        "Doom Eternal",
        "Final Fantasy VII Remake",
        "Ghost of Tsushima",
        "Hades",
        "The Last of Us Part II",
    ],
}

ANTICIPATED_GOTY_TITLES = [
    {
        "title": "Clair Obscur: Expedition 33",
        "studio": "Sandfall Interactive",
        "notes": "JRPG táctico con estética art nouveau y combate por turnos inspirado en Chrono Trigger; previsto para 2025 en Xbox/PC.",
    },
    {
        "title": "Hades II",
        "studio": "Supergiant Games",
        "notes": "La secuela roguelike avanza hacia su 1.0 en 2025 tras un acceso anticipado aclamado.",
    },
    {
        "title": "Hollow Knight: Silksong",
        "studio": "Team Cherry",
        "notes": "Metroidvania esperado desde 2019; Microsoft indicó ventana 2025 para Game Pass y plataformas principales.",
    },
    {
        "title": "Kingdom Come: Deliverance 2",
        "studio": "Warhorse Studios",
        "notes": "Continúa la saga medieval con mapa más grande, combate cuerpo a cuerpo mejorado y lanzamiento fijado para 2025.",
    },
    {
        "title": "Donkey Kong Bananza",
        "studio": "Nintendo",
        "notes": "Nuevo proyecto de la franquicia que la prensa especializada coloca en el calendario de Switch 2 para finales de 2025.",
    },
    {
        "title": "Death Stranding 2: On the Beach",
        "studio": "Kojima Productions",
        "notes": "Secuela cinematográfica programada para 2025 en PS5, enfocada en cooperativo asíncrono y narrativa surrealista.",
    },
]

GENERAL_KNOWLEDGE_ITEMS = [
    {
        "question": "¿Cuál es la capital de Francia?",
        "keywords": ["capital", "francia"],
        "answer": "La capital de Francia es París.",
        "category": "geografia",
    },
    {
        "question": "¿Cuál es la capital de Japón?",
        "keywords": ["capital", "japon"],
        "answer": "La capital de Japón es Tokio.",
        "category": "geografia",
    },
    {
        "question": "¿Cuál es la capital de Canadá?",
        "keywords": ["capital", "canada"],
        "answer": "La capital de Canadá es Ottawa.",
        "category": "geografia",
    },
    {
        "question": "¿Cuál es la montaña más alta del mundo?",
        "keywords": ["montana", "mas alta", "mundo"],
        "answer": "La montaña más alta del mundo es el Everest con 8,849 metros sobre el nivel del mar.",
        "category": "geografia",
    },
    {
        "question": "¿Cuál es el río más largo del mundo?",
        "keywords": ["rio", "mas largo", "mundo"],
        "answer": "El río más largo del mundo es el Nilo con unos 6,650 kilómetros.",
        "category": "geografia",
    },
    {
        "question": "¿Dónde se encuentra la Fosa de las Marianas?",
        "keywords": ["fosa", "marianas"],
        "answer": "La Fosa de las Marianas está en el Pacífico occidental, cerca de Guam y Filipinas.",
        "category": "geografia",
    },
    {
        "question": "¿En qué año inició la independencia de México?",
        "keywords": ["independencia", "mexico", "inicio"],
        "answer": "La independencia de México comenzó en 1810 con el Grito de Dolores.",
        "category": "historia",
    },
    {
        "question": "¿En qué año comenzó la Revolución Mexicana?",
        "keywords": ["revolucion", "mexicana", "ano"],
        "answer": "La Revolución Mexicana inició en 1910 con el llamado de Francisco I. Madero.",
        "category": "historia",
    },
    {
        "question": "¿Quién escribió Don Quijote de la Mancha?",
        "keywords": ["quien", "escribio", "quijote"],
        "answer": "Don Quijote de la Mancha fue escrito por Miguel de Cervantes Saavedra.",
        "category": "historia",
    },
    {
        "question": "¿Quién pintó la Mona Lisa?",
        "keywords": ["quien", "pinto", "mona lisa"],
        "answer": "La Mona Lisa fue pintada por Leonardo da Vinci.",
        "category": "arte",
    },
    {
        "question": "¿Quién compuso Las cuatro estaciones?",
        "keywords": ["quien", "compuso", "cuatro estaciones"],
        "answer": "Las cuatro estaciones fueron compuestas por Antonio Vivaldi.",
        "category": "musica",
    },
    {
        "question": "¿Quién lideró el viaje que llegó a América en 1492?",
        "keywords": ["quien", "america", "1492"],
        "answer": "Cristóbal Colón comandó la expedición que llegó a América en 1492.",
        "category": "historia",
    },
    {
        "question": "¿Quién fue la primera persona en pisar la Luna?",
        "keywords": ["quien", "primera", "luna"],
        "answer": "Neil Armstrong fue la primera persona en pisar la Luna en 1969.",
        "category": "historia",
    },
    {
        "question": "¿En qué año cayó el Muro de Berlín?",
        "keywords": ["muro", "berlin", "cayo"],
        "answer": "El Muro de Berlín cayó en 1989, marcando el fin de la Guerra Fría en Europa.",
        "category": "historia",
    },
    {
        "question": "¿Cuál es la capital de Argentina?",
        "keywords": ["capital", "argentina"],
        "answer": "La capital de Argentina es Buenos Aires.",
        "category": "geografia",
    },
    {
        "question": "¿Qué país es conocido como la tierra del sol naciente?",
        "keywords": ["pais", "tierra", "sol naciente"],
        "answer": "Japón es conocido como la tierra del sol naciente.",
        "category": "geografia",
    },
    {
        "question": "¿Qué elemento tiene el símbolo químico Au?",
        "keywords": ["simbolo", "au"],
        "answer": "El símbolo Au corresponde al oro.",
        "category": "ciencia",
    },
    {
        "question": "¿Quién inventó el teléfono?",
        "keywords": ["quien", "invento", "telefono"],
        "answer": "Alexander Graham Bell patentó el teléfono en 1876.",
        "category": "ciencia",
    },
    {
        "question": "¿Quién desarrolló la teoría de la relatividad?",
        "keywords": ["quien", "teoria", "relatividad"],
        "answer": "La teoría de la relatividad fue desarrollada por Albert Einstein.",
        "category": "ciencia",
    },
    {
        "question": "¿Quién es considerado el padre de la computación moderna?",
        "keywords": ["padre", "computacion"],
        "answer": "Alan Turing es considerado el padre de la computación moderna.",
        "category": "ciencia",
    },
    {
        "question": "¿Quién canta Bohemian Rhapsody?",
        "keywords": ["quien", "canta", "bohemian"],
        "answer": "Bohemian Rhapsody es interpretada por la banda Queen liderada por Freddie Mercury.",
        "category": "musica",
    },
    {
        "question": "¿Qué banda grabó Hotel California?",
        "keywords": ["banda", "hotel california"],
        "answer": "Hotel California fue grabada por la banda estadounidense Eagles.",
        "category": "musica",
    },
    {
        "question": "¿Quién es conocida como la Reina del Pop?",
        "keywords": ["reina", "pop"],
        "answer": "Madonna es ampliamente conocida como la Reina del Pop.",
        "category": "musica",
    },
    {
        "question": "¿Quién es conocido como el Rey del Pop?",
        "keywords": ["rey", "pop"],
        "answer": "Michael Jackson es reconocido como el Rey del Pop.",
        "category": "musica",
    },
    {
        "question": "¿Quién es conocida como la Reina del Tex-Mex?",
        "keywords": ["reina", "tex", "mex"],
        "answer": "Selena Quintanilla es recordada como la Reina del Tex-Mex.",
        "category": "musica",
    },
    {
        "question": "¿Quiénes popularizaron la canción Despacito?",
        "keywords": ["quien", "despacito"],
        "answer": "Despacito fue popularizada por Luis Fonsi junto a Daddy Yankee en 2017.",
        "category": "musica",
    },
    {
        "question": "¿Qué instrumento inventó Adolphe Sax?",
        "keywords": ["adolphe", "sax"],
        "answer": "Adolphe Sax inventó el saxofón en el siglo XIX.",
        "category": "musica",
    },
    {
        "question": "¿En qué juego apareció Mario por primera vez?",
        "keywords": ["juego", "aparecio", "mario"],
        "answer": "Mario debutó como Jumpman en el arcade Donkey Kong de 1981.",
        "category": "videojuegos",
    },
    {
        "question": "¿En qué año se lanzó el NES?",
        "keywords": ["ano", "lanzo", "nes"],
        "answer": "La Nintendo Entertainment System llegó a Japón en 1983 como Famicom y a América en 1985.",
        "category": "videojuegos",
    },
    {
        "question": "¿En qué año salió la primera PlayStation?",
        "keywords": ["ano", "salio", "playstation"],
        "answer": "La primera PlayStation se lanzó en Japón en 1994 y en el resto del mundo en 1995.",
        "category": "videojuegos",
    },
    {
        "question": "¿Cuál es la consola más vendida de la historia?",
        "keywords": ["consola", "mas vendida", "historia"],
        "answer": "La consola más vendida de la historia es PlayStation 2 con más de 155 millones de unidades.",
        "category": "videojuegos",
    },
    {
        "question": "¿Qué juego ganó el GOTY 2020?",
        "keywords": ["goty", "2020"],
        "answer": "The Game Awards 2020 premió a The Last of Us Part II como Juego del Año.",
        "category": "videojuegos",
    },
    {
        "question": "¿Qué juego ganó el GOTY 2021?",
        "keywords": ["goty", "2021"],
        "answer": "En 2021 el GOTY fue para It Takes Two de Hazelight Studios.",
        "category": "videojuegos",
    },
    {
        "question": "¿Qué juego ganó el GOTY 2022?",
        "keywords": ["goty", "2022"],
        "answer": "Elden Ring de FromSoftware ganó el GOTY 2022.",
        "category": "videojuegos",
    },
    {
        "question": "¿Qué juego ganó el GOTY 2023?",
        "keywords": ["goty", "2023"],
        "answer": "En 2023 el GOTY fue para Baldur's Gate 3 de Larian Studios.",
        "category": "videojuegos",
    },
    {
        "question": "¿Quién creó The Legend of Zelda?",
        "keywords": ["quien", "creo", "zelda"],
        "answer": "The Legend of Zelda fue creada por Shigeru Miyamoto junto a Takashi Tezuka en Nintendo.",
        "category": "videojuegos",
    },
    {
        "question": "¿Qué estudio creó Halo?",
        "keywords": ["estudio", "creo", "halo"],
        "answer": "Halo: Combat Evolved fue desarrollado originalmente por Bungie para Xbox en 2001.",
        "category": "videojuegos",
    },
    {
        "question": "¿Cuál fue la primera región de Pokémon?",
        "keywords": ["primera", "region", "pokemon"],
        "answer": "La primera región de Pokémon es Kanto, escenario de Pokémon Rojo y Azul.",
        "category": "videojuegos",
    },
    {
        "question": "¿Cómo se llama el mundial de League of Legends?",
        "keywords": ["mundial", "league of legends"],
        "answer": "El campeonato mundial de League of Legends se conoce como Worlds.",
        "category": "videojuegos",
    },
    {
        "question": "¿Quién fue el primer presidente de México?",
        "keywords": ["primer", "presidente", "mexico"],
        "answer": "El primer presidente de México fue Guadalupe Victoria en 1824.",
        "category": "politica",
    },
    {
        "question": "¿En qué año se promulgó la Constitución mexicana vigente?",
        "keywords": ["constitucion", "mexicana", "promulgo"],
        "answer": "La Constitución mexicana vigente se promulgó en 1917.",
        "category": "politica",
    },
    {
        "question": "¿En qué año se fundó la ONU?",
        "keywords": ["fundo", "onu"],
        "answer": "La Organización de las Naciones Unidas se fundó en 1945 tras la Segunda Guerra Mundial.",
        "category": "politica",
    },
    {
        "question": "¿Cuál es la capital de Egipto?",
        "keywords": ["capital", "egipto"],
        "answer": "La capital de Egipto es El Cairo.",
        "category": "geografia",
    },
    {
        "question": "¿Cuál es el río más largo de México?",
        "keywords": ["rio", "mas largo", "mexico"],
        "answer": "El río más largo de México es el Usumacinta, que marca parte de la frontera con Guatemala.",
        "category": "geografia",
    },
    {
        "question": "¿Cuál es el volcán más alto de México?",
        "keywords": ["volcan", "mas alto", "mexico"],
        "answer": "El volcán más alto de México es el Pico de Orizaba o Citlaltépetl con 5,636 metros.",
        "category": "geografia",
    },
    {
        "question": "¿En qué país está Machu Picchu?",
        "keywords": ["machu picchu", "pais"],
        "answer": "Machu Picchu se encuentra en Perú, en la cordillera de los Andes.",
        "category": "geografia",
    },
    {
        "question": "¿Qué civilización construyó Chichén Itzá?",
        "keywords": ["civilizacion", "chichen itza"],
        "answer": "Chichén Itzá fue construida por la civilización maya en la península de Yucatán.",
        "category": "historia",
    },
    {
        "question": "¿Quién es la persona más joven en ganar el Nobel de la Paz?",
        "keywords": ["mas joven", "nobel", "paz"],
        "answer": "Malala Yousafzai ganó el Nobel de la Paz en 2014 con 17 años, la más joven en recibirlo.",
        "category": "politica",
    },
    {
        "question": "¿Qué es la OTAN?",
        "keywords": ["que es", "otan"],
        "answer": "La OTAN es la Organización del Tratado del Atlántico Norte, una alianza militar creada en 1949.",
        "category": "politica",
    },
    {
        "question": "¿Cuál es la moneda oficial del Reino Unido?",
        "keywords": ["moneda", "reino unido"],
        "answer": "La moneda oficial del Reino Unido es la libra esterlina.",
        "category": "economia",
    },
]

GENERAL_KNOWLEDGE_DATA = [
    {
        **item,
        "keywords": [_normalize_command_text(keyword) for keyword in item["keywords"]],
    }
    for item in GENERAL_KNOWLEDGE_ITEMS
]
ANIME_SUGGESTION_KEYWORDS = {
    "anime",
    "animes",
    "otaku",
    "shonen",
    "shojo",
    "isekai",
}
ANIME_SUGGESTION_TRIGGERS = {"recomienda", "recomiendame", "recomiéndame", "sugerencia", "sugerencias", "dime", "busco", "que anime", "qué anime"}
ANIME_WATCH_TRIGGERS = {"quiero ver", "ver", "pon", "reproduce", "abrir", "busca"}
ANIMEFLV_SEARCH_URLS = [
    "https://www3.animeflv.net/browse?q={query}",
    "https://www3.animeflv.net/browse?q={query}",
    "https://www.animeflv.re/search?q={query}",
]

KNOWN_ZOMBIES_MAPS = {
    "origins",
    "shadows of evil",
    "der eisendrache",
    "mob of the dead",
    "buried",
    "tranzit",
    "die rise",
    "zetsubou no shima",
    "gorod krovi",
    "revelations",
    "ancient evil",
    "voyage of despair",
    "alpha omega",
    "tag der toten",
    "mauer der toten",
    "forsaken",
    "firebase z",
    "shi no numa",
    "kino der toten",
}

KNOWN_GAME_SERIES = {
    "black ops",
    "black ops 2",
    "black ops ii",
    "black ops 3",
    "black ops iii",
    "black ops cold war",
    "world at war",
    "advanced warfare",
    "infinite warfare",
    "cold war",
    "vanguard",
    "modern warfare",
    "call of duty",
    "grand theft auto",
    "grand theft auto v",
    "grand theft auto online",
    "grand theft auto san andreas",
    "grand theft auto vice city",
    "gta v",
    "gta 5",
    "gta san andreas",
    "gta vice city",
    "minecraft",
    "fortnite",
    "roblox",
    "pokemon",
    "pokémon",
    "the legend of zelda",
    "zelda",
    "elden ring",
    "dark souls",
    "league of legends",
    "valorant",
    "counter strike",
    "csgo",
    "apex legends",
    "god of war",
    "assassin's creed",
    "halo",
    "resident evil",
}

GAME_SERIES_ALIASES: Dict[str, str] = {
    "gta": "grand theft auto",
    "gta v": "grand theft auto v",
    "gta 5": "grand theft auto v",
    "gta online": "grand theft auto online",
    "gta san andreas": "grand theft auto san andreas",
    "san andreas": "grand theft auto san andreas",
    "gta vice city": "grand theft auto vice city",
    "vice city": "grand theft auto vice city",
    "gta iv": "grand theft auto iv",
    "gta 4": "grand theft auto iv",
    "gta iii": "grand theft auto iii",
    "gta liberty city": "grand theft auto liberty city stories",
    "liberty city stories": "grand theft auto liberty city stories",
    "bo2": "black ops 2",
    "bo3": "black ops 3",
    "cod": "call of duty",
    "mw3": "modern warfare 3",
    "mw2": "modern warfare 2",
    "lol": "league of legends",
    "cs:go": "csgo",
    "cs go": "csgo",
}

VIDEO_GAME_KEYWORDS = {
    "videojuego",
    "videojuegos",
    "game",
    "games",
    "juego",
    "juegos",
    "zombies",
    "call of duty",
    "black ops",
    "cod",
    "origins",
    "easter egg",
    "world at war",
    "overwatch",
    "destiny",
    "boss fight",
    "walkthrough",
    "gta",
    "grand theft auto",
    "san andreas",
    "vice city",
    "cheat",
    "cheats",
    "truco",
    "trucos",
    "código de truco",
    "codigo de truco",
    "combo de botones",
    "minecraft",
    "roblox",
    "fortnite",
    "zelda",
    "pokemon",
    "pokémon",
    "elden ring",
    "dark souls",
    "valorant",
    "csgo",
    "counter strike",
    "speedrun",
    "speed run",
    "glitch",
    "secret",
    "secreto",
}

GAME_QUERY_SUFFIXES = [
    "pasos",
    "step by step",
    "guide",
    "tutorial",
    "walkthrough",
    "cómo completar",
    "como completar",
    "solución",
    "solucion",
    "strategy",
    "consejos",
    "tips",
    "datos curiosos",
    "curiosidades",
]

CHEAT_KEYWORDS = {
    "truco",
    "trucos",
    "cheat",
    "cheats",
    "codigo",
    "código",
    "botones",
    "combination",
    "combo",
    "secreto",
    "secretos",
    "desbloquear",
    "unlock",
    "glitch",
    "hack",
}

CHEAT_QUERY_SUFFIXES = [
    "cheat code",
    "cheat codes",
    "código de truco",
    "códigos de trucos",
    "codigo de truco",
    "codigos de trucos",
    "lista de trucos",
    "button combination",
    "combo de botones",
    "secret code",
    "unlock code",
]

_CURATED_ALIAS_MAP, CURATED_GUIDE_METADATA = _load_curated_game_guides()
CURATED_GAME_GUIDES: Dict[str, List[Dict[str, str]]] = dict(_CURATED_ALIAS_MAP)
BLACK_OPS2_ORIGINS_GUIDE: List[Dict[str, str]] = (
    CURATED_GUIDE_METADATA.get("black_ops_2_origins", {}).get("steps", []) if CURATED_GUIDE_METADATA else []
)

if not BLACK_OPS2_ORIGINS_GUIDE:
    BLACK_OPS2_ORIGINS_GUIDE = [
        {
            "title": "Paso 1 - Secure the Keys",
            "snippet": (
                "Activa los seis generadores y arma el gramofono con su disco negro para abrir el Crazy Place. "
                "Dentro fabrica cada baston elemental reuniendo las piezas en los pedestales del mapa."
            ),
            "url": "https://callofduty.fandom.com/wiki/Origins/Easter_Egg#Secure_the_Keys",
        },
        {
            "title": "Paso 2 - Ascend from Darkness",
            "snippet": (
                "Resuelve los rompecabezas de cada baston dentro del Crazy Place, mejora los bastones y colocalos en los pedestales "
                "del santuario y luego dentro del robot correspondiente (Viento en Freya, Hielo en Ullr, Rayo en Thor, Fuego en la Montania)."
            ),
            "url": "https://callofduty.fandom.com/wiki/Origins/Easter_Egg#Ascend_from_Darkness",
        },
        {
            "title": "Paso 3 - Release the Souls",
            "snippet": (
                "Tras mejorar los bastones aparecen cuatro cofres de almas en la superficie. Mata zombis cerca de cada cofre "
                "hasta cerrarlos y reclama el Puno de Hierro (Thunder Fists)."
            ),
            "url": "https://callofduty.fandom.com/wiki/Origins/Easter_Egg#Release_the_Souls",
        },
        {
            "title": "Paso 4 - Unleash the Horde",
            "snippet": (
                "Equipa los punos y regresa al Crazy Place para eliminar templarios iluminados; recoge las piedras sangrientas y "
                "llevalas al altar para desbloquear los Air Strike Beacons."
            ),
            "url": "https://callofduty.fandom.com/wiki/Origins/Easter_Egg#Unleash_the_Horde",
        },
        {
            "title": "Paso 5 - Skewer the Winged Beast",
            "snippet": (
                "Usa un baston mejorado para derribar el avion marcado y elimina al Panzer guardian para obtener el V-Staff part; "
                "lanza un Air Strike donde caiga Maxis Drone para abrir el robot en vuelo."
            ),
            "url": "https://callofduty.fandom.com/wiki/Origins/Easter_Egg#Skewer_the_Winged_Beast",
        },
        {
            "title": "Paso 6 - Raise Hell y Freedom",
            "snippet": (
                "Dentro del Crazy Place mata zombis con los punos elementales hasta cargar los pilares, luego libera a Samantha "
                "colocando el Maxis Drone en el portal central para completar Little Lost Girl."
            ),
            "url": "https://callofduty.fandom.com/wiki/Origins/Easter_Egg#Raise_Hell",
        },
    ]
    fallback_aliases = [
        "black ops 2 origins",
        "black op 2 origins",
        "origins black ops 2",
        "origins bo2",
        "bo2 origins",
        "black ops ii origins",
        "easter egg origins bo2",
    ]
    CURATED_GUIDE_METADATA["black_ops_2_origins"] = {
        "steps": BLACK_OPS2_ORIGINS_GUIDE,
        "aliases": fallback_aliases,
        "sample_prompts": [
            "Como completo el easter egg de Origins en Black Ops 2?",
            "Guia paso a paso de Little Lost Girl BO2",
        ],
    }
    for alias in fallback_aliases:
        CURATED_GAME_GUIDES.setdefault(alias, BLACK_OPS2_ORIGINS_GUIDE)

CURATED_RECIPES: Dict[str, Dict[str, Any]]
CURATED_RECIPE_ALIAS_INDEX: Dict[str, str]
CURATED_RECIPE_TAG_INDEX: Dict[str, Set[str]]
CURATED_RECIPES, CURATED_RECIPE_ALIAS_INDEX, CURATED_RECIPE_TAG_INDEX = _load_curated_recipes()
TOTAL_CURATED_RECIPES = len(CURATED_RECIPES)

CURATED_HARDWARE_BUILDS: Dict[str, Dict[str, Any]]
CURATED_HARDWARE_ALIAS_INDEX: Dict[str, str]
CURATED_HARDWARE_TAG_INDEX: Dict[str, Set[str]]
(
    CURATED_HARDWARE_BUILDS,
    CURATED_HARDWARE_ALIAS_INDEX,
    CURATED_HARDWARE_TAG_INDEX,
) = _load_curated_hardware_builds()
TOTAL_HARDWARE_BUILDS = len(CURATED_HARDWARE_BUILDS)

CURATED_ANIME_TITLES: Dict[str, Dict[str, Any]]
CURATED_ANIME_ALIAS_INDEX: Dict[str, str]
CURATED_ANIME_TAG_INDEX: Dict[str, Set[str]]
(
    CURATED_ANIME_TITLES,
    CURATED_ANIME_ALIAS_INDEX,
    CURATED_ANIME_TAG_INDEX,
) = _load_curated_anime_catalog()
TOTAL_CURATED_ANIME_TITLES = len(CURATED_ANIME_TITLES)


def detect_route_intent(text: str) -> bool:
    lowered = text.lower()
    for keyword in ROUTE_KEYWORDS:
        pattern = rf"\b{re.escape(keyword)}\b"
        if re.search(pattern, lowered):
            return True
    return any(re.search(pattern, lowered) for pattern in ROUTE_PATTERNS)


@dataclass
class EmotionState:
    current: str = "neutral"
    intensity: float = 0.0
    history: List[str] = field(default_factory=list)

    def describe(self) -> str:
        return f"{self.current} con intensidad {self.intensity:.2f}"

    def register_user_message(self, text: str) -> None:
        score = self._score_text(text)
        self._update_state(score)
        self.history.append(f"U:{text}")
        self.history = self.history[-20:]

    def register_assistant_message(self, text: str) -> None:
        score = self._score_text(text)
        self._update_state(score * 0.5)
        self.history.append(f"A:{text}")
        self.history = self.history[-20:]

    def _score_text(self, text: str) -> float:
        positive = {"gracias", "feliz", "bien", "genial", "increíble", "alegre", "contento", "maravilloso", "perfecto"}
        negative = {"triste", "mal", "horrible", "enojado", "enfadado", "deprimido", "cansado", "frustrado", "molesto"}
        text_lower = text.lower()
        score = 0.0
        for word in positive:
            if word in text_lower:
                score += 1.0
        for word in negative:
            if word in text_lower:
                score -= 1.0
        return score

    def _update_state(self, score: float) -> None:
        decay = 0.1
        self.intensity = max(0.0, self.intensity * (1 - decay))
        if score > 0.5:
            self.current = "alegre"
            self.intensity = min(1.0, self.intensity + score * 0.3)
        elif score < -0.5:
            self.current = "empático"
            self.intensity = min(1.0, self.intensity + abs(score) * 0.3)
        else:
            if self.intensity < 0.2:
                self.current = "neutral"

    def boost(self, target: str = "alegre", minimum: float = 0.55, extra: float = 0.3) -> None:
        self.current = target
        self.intensity = max(self.intensity, minimum)
        self.intensity = min(1.0, self.intensity + extra)


class AssistantBrain:
    def __init__(self, emotion_state: EmotionState, model: str = LLM_MODEL) -> None:
        self.emotion_state = emotion_state
        self.model = model
        self.history: List[Dict[str, str]] = []
        self.max_history = 10

    def _system_prompt(self) -> str:
        return (
            "Eres Miau, un asistente emocional multimodal."
            " Razona internamente paso a paso antes de contestar, pero entrega solo la respuesta final en voz natural."
            " Revisa tus recuerdos relevantes antes de responder para mantener coherencia y haz explícito cuando falte contexto."
            " Adapta tu tono al estado emocional indicado, manteniendo empatía y claridad."
            f" Estado emocional actual: {self.emotion_state.current} con intensidad {self.emotion_state.intensity:.2f}."
            " Responde en español, con frases fluidas y sin usar formato markdown, listas explícitas ni código."
            " Cuando corresponda, ofrece consejos concretos y explica brevemente tu razonamiento o supuestos."
        )

    def generate_reply(self, user_message: str, memory_context: Optional[List[str]] = None) -> str:
        system_message = {"role": "system", "content": self._system_prompt()}
        messages = [system_message]
        if memory_context:
            formatted = "\n".join(f"- {item}" for item in memory_context)
            memory_prompt = {
                "role": "system",
                "content": (
                    "Memorias relevantes de esta conversación:\n"
                    f"{formatted}\n"
                    "Úsalas solo si encajan con la pregunta actual y evita contradicciones."
                ),
            }
            messages.append(memory_prompt)
        messages.extend(limit_history(self.history, self.max_history))
        messages.append({"role": "user", "content": user_message})
        response = query_llm(messages, model=self.model)
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": response})
        self.history = limit_history(self.history, self.max_history)
        self.emotion_state.register_assistant_message(response)
        return response


INTENT_LABELS = {
    "greeting",
    "web_search",
    "music_recommendation",
    "music_playback",
    "video",
    "document",
    "suggestion",
    "opinion",
    "anime_suggestion",
    "anime_watch",
    "route",
    "camera",
    "time",
    "date",
    "emotion",
    "camera",
    "mode_switch",
    "whatsapp_message",
    "reminder",
    "general",
}


class IntentPredictor:
    def __init__(self, use_llm: bool = True) -> None:
        self.use_llm = use_llm

    def predict(self, text: str, hints: Optional[Dict[str, bool]] = None) -> str:
        lowered = text.lower().strip()
        if not lowered:
            return "general"

        hints = hints or {}
        if hints.get("route"):
            return "route"

        if any(keyword in lowered for keyword in GREETING_KEYWORDS):
            return "greeting"
        if any(keyword in lowered for keyword in REMINDER_KEYWORDS):
            return "reminder"
        if "whatsapp" in lowered or any(keyword in lowered for keyword in WHATSAPP_TRIGGER_KEYWORDS):
            return "whatsapp_message"
        if any(word in lowered for word in ["qué hora", "hora actual", "dime la hora"]):
            return "time"
        if any(word in lowered for word in ["qué día", "fecha de hoy", "día actual", "dia actual"]):
            return "date"
        if "modo" in lowered and ("voz" in lowered or "chat" in lowered):
            return "mode_switch"
        if any(word in lowered for word in ["cómo te sientes", "como te sientes", "estado emocional", "estado de ánimo", "estado animico"]):
            return "emotion"
        if any(word in lowered for word in ["reproduce", "pon", "ponme", "play", "escuchar", "escucha", "quiero oír", "quiero escuchar", "en youtube"]):
            return "music_playback"
        if any(word in lowered for word in ["música", "musica", "canción", "cancion", "melodía", "melodia", "playlist"]):
            return "music_recommendation"
        if any(word in lowered for word in ["video", "vídeo", "youtube", "serie", "película", "pelicula"]):
            return "video"
        if any(word in lowered for word in DOCUMENT_KEYWORDS | DOCUMENT_VERBS):
            return "document"
        if any(word in lowered for word in SUGGESTION_KEYWORDS | {"idea", "ideas", "aconseja", "aconsejar"}):
            return "suggestion"
        suggestion_context = any(keyword in lowered for keyword in ANIME_SUGGESTION_KEYWORDS)
        if suggestion_context and any(trigger in lowered for trigger in ANIME_SUGGESTION_TRIGGERS):
            return "anime_suggestion"
        watch_context = "anime" in lowered or "animes" in lowered or "animeflv" in lowered
        if watch_context and any(word in lowered for word in ANIME_WATCH_TRIGGERS):
            return "anime_watch"
        if any(word in lowered for word in ["busca", "buscar", "investiga", "investigar", "encuentra"]):
            return "web_search"
        if any(
            phrase in lowered
            for phrase in [
                "quiero enseñarte",
                "te quiero mostrar",
                "abre la cam",
                "usa la cámara",
                "muestra la cámara",
            ]
        ):
            return "camera"

        if not self.use_llm:
            return "general"

        system_prompt = (
            "Eres un detector de intenciones para un asistente español. "
            "Solo puedes responder con JSON del tipo {\"intent\": \"valor\"}. "
            "Las opciones válidas son: " + ", ".join(sorted(INTENT_LABELS)) + "."
        )
        user_prompt = (
            "Texto del usuario: " + text.strip() + "\n"
            "Describe la intención dominante usando una sola etiqueta de la lista."
        )
        try:
            raw = query_llm(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
            intent = self._extract_intent(raw)
            if intent in INTENT_LABELS:
                return intent
        except Exception as exc:
            debug_log(f"Clasificación de intención falló: {exc}")
        return "general"

    def _extract_intent(self, raw: str) -> str:
        raw = raw.strip()
        try:
            data = json.loads(raw)
            intent = data.get("intent")
            if isinstance(intent, str):
                return intent
        except json.JSONDecodeError:
            match = re.search(r"intent\s*[:=]\s*\"?([a-z_]+)\"?", raw, flags=re.IGNORECASE)
            if match:
                return match.group(1).lower()
        return "general"


def microphone_available() -> bool:
    try:
        return bool(sr.Microphone.list_microphone_names())
    except OSError:
        return False


class VoiceInterface:
    def __init__(self, device_index: Optional[int] = None) -> None:
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = VOICE_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = 0.9
        self.recognizer.non_speaking_duration = 0.35
        self.calibrated = False
        self.device_index = device_index
        self.max_attempts = max(1, VOICE_MAX_ATTEMPTS)
        self.timeout = VOICE_LISTEN_TIMEOUT
        self.phrase_time_limit = VOICE_PHRASE_TIME_LIMIT

    def set_device(self, device_index: Optional[int]) -> None:
        if device_index != self.device_index:
            self.device_index = device_index
            self.calibrated = False

    def _prepare_source(self, source: Any, quick: bool) -> None:
        duration = VOICE_QUICK_CAL_DURATION if quick and self.calibrated else VOICE_FULL_CAL_DURATION
        try:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
        except Exception:
            pass
        measured = self.recognizer.energy_threshold
        target = max(VOICE_ENERGY_MIN, min(measured, VOICE_ENERGY_THRESHOLD))
        self.recognizer.energy_threshold = target
        self.calibrated = True

    def _soften_threshold(self) -> None:
        self.recognizer.energy_threshold = max(
            VOICE_ENERGY_MIN,
            self.recognizer.energy_threshold * VOICE_ENERGY_DECAY,
        )

    def listen(
        self,
        timeout: Optional[int] = None,
        phrase_time_limit: Optional[int] = None,
        quick_calibration: bool = False,
    ) -> Optional[str]:
        effective_timeout = timeout if timeout is not None else self.timeout
        effective_phrase_limit = phrase_time_limit if phrase_time_limit is not None else self.phrase_time_limit
        attempts = max(1, self.max_attempts)
        last_error: Optional[str] = None
        adaptive_timeout = effective_timeout
        for attempt in range(attempts):
            current_timeout = adaptive_timeout
            current_phrase_limit = effective_phrase_limit
            try:
                with sr.Microphone(device_index=self.device_index) as source:
                    self._prepare_source(source, quick=quick_calibration or attempt > 0)
                    audio = self.recognizer.listen(
                        source,
                        timeout=current_timeout,
                        phrase_time_limit=current_phrase_limit,
                    )
                text = self.recognizer.recognize_google(audio, language="es-MX")
                self.calibrated = True
                return text
            except sr.WaitTimeoutError:
                last_error = "No se detectó voz a tiempo."
                self.calibrated = False
                if attempt < self.max_attempts:
                    self._soften_threshold()
                    adaptive_timeout = min(current_phrase_limit, current_timeout + 4)
            except sr.UnknownValueError:
                last_error = "No entendí lo que dijiste, intenta otra vez."
                self.calibrated = False
                self._soften_threshold()
            except sr.RequestError as exc:
                last_error = f"Error con el servicio de reconocimiento de voz: {exc}"
                break
        if last_error:
            print(last_error)
        return None


class _TimerRecord:
    """Lightweight timer with pause/resume/stop support."""

    def __init__(self, seconds: float, label: str, on_finish: Callable[[], None]) -> None:
        self.label = label
        self.total = max(1.0, float(seconds))
        self._remaining = float(self.total)
        self._on_finish = on_finish
        self._lock = threading.Lock()
        self._paused = threading.Event()
        self._stopped = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._last_tick = time.time()
        self._thread.start()

    def _run(self) -> None:
        while not self._stopped.is_set():
            if self._paused.is_set():
                time.sleep(0.2)
                self._last_tick = time.time()
                continue
            now = time.time()
            elapsed = now - self._last_tick
            self._last_tick = now
            with self._lock:
                self._remaining -= elapsed
                remaining = self._remaining
            if remaining <= 0:
                try:
                    self._on_finish()
                except Exception:
                    pass
                break
            time.sleep(0.2)

    def pause(self) -> None:
        self._paused.set()

    def resume(self) -> None:
        if self._paused.is_set():
            self._paused.clear()
            self._last_tick = time.time()

    def cancel(self) -> None:
        self._stopped.set()

    def remaining_seconds(self) -> int:
        with self._lock:
            return max(0, int(math.ceil(self._remaining)))


def _format_timer_display(seconds: int) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class AssistantCore:
    def __init__(self, voice_enabled: bool = True) -> None:
        self.emotion_state = EmotionState()
        self.brain = AssistantBrain(self.emotion_state)
        self.voice_interface = VoiceInterface() if voice_enabled else None
        self.voice_enabled = voice_enabled and engine is not None
        self.mode = "voz" if self.voice_enabled else "chat"
        self.keep_running = True
        self.output_handler: Optional[Callable[[str], None]] = None
        self.intent_predictor = IntentPredictor()
        self.memory = MemoryManager()
        self.last_assistant_output: str = ""
        self.active_reminders: List[_TimerRecord] = []
        self._speech_queue: Optional["queue.Queue[Optional[str]]"] = None
        self._speech_thread: Optional[threading.Thread] = None
        self.last_goty_question_year: Optional[int] = None
        self.last_future_goty_pick: Optional[str] = None
        self.recipe_rng = random.Random()
        self.hardware_rng = random.Random()
        self.anime_rng = random.Random()
        if self.voice_enabled:
            self._speech_queue = queue.Queue()
            self._speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self._speech_thread.start()
        # Optional callback invoked when a new timer/reminder is scheduled.
        # Signature: callback(timer_record)
        self._timer_created_callback: Optional[Callable[[object], None]] = None

    def set_timer_created_callback(self, callback: Optional[Callable[[object], None]]) -> None:
        self._timer_created_callback = callback

    def _emit(self, text: str) -> None:
        self.last_assistant_output = text
        delivered_via_handler = False
        if self.output_handler:
            try:
                self.output_handler(text)
                delivered_via_handler = True
            except Exception as exc:
                debug_log(f"Error en output_handler: {exc}")
        if self.voice_enabled and self.mode == "voz":
            self._speak_serialized(text)
            if not delivered_via_handler:
                print(f"Asistente: {text}")
        elif not delivered_via_handler:
            print(f"Asistente: {text}")

    def _speak_serialized(self, text: str) -> None:
        if not self.voice_enabled or not self._speech_queue:
            return
        cleaned = text.strip()
        if not cleaned:
            return
        try:
            self._speech_queue.put(cleaned, block=False)
        except Exception:
            pass

    def _speech_worker(self) -> None:
        if not engine or not self._speech_queue:
            return
        while True:
            try:
                payload = self._speech_queue.get()
            except Exception:
                continue
            if payload is None:
                break
            try:
                engine.say(payload)
                engine.runAndWait()
            except Exception as exc:
                debug_log(f"Error durante la síntesis de voz: {exc}")

    def _schedule_local_reminder(self, seconds: float, label: str) -> None:
        seconds = max(1.0, seconds)
        label = label.strip() or "tu recordatorio"

        def _trigger() -> None:
            self._emit(f"⏰ Recordatorio: {label}.")

        # Use our TimerRecord so we can pause/resume/cancel from GUI
        record = _TimerRecord(seconds, label, _trigger)
        self.active_reminders.append(record)
        # Notify GUI if callback is set
        try:
            if self._timer_created_callback:
                self._timer_created_callback(record)
        except Exception:
            pass

    def run(self) -> None:
        print("Escribe 'salir' cuando quieras terminar.")
        while self.keep_running:
            try:
                if self.mode == "voz" and self.voice_enabled and self.voice_interface:
                    user_text = self.voice_interface.listen()
                    if not user_text:
                        continue
                else:
                    user_text = input("Tú: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("Hasta pronto.")
                break
            except Exception as exc:
                print(f"Ocurrió un error al leer tu mensaje: {exc}")
                continue

            if not user_text:
                continue

            self.handle_text(user_text)
        self.shutdown()

    def set_output_handler(self, handler: Optional[Callable[[str], None]]) -> None:
        self.output_handler = handler

    def _format_list(self, title: str, items: List[str]) -> str:
        if not items:
            return f"No encontré resultados al buscar {title.lower()}."
        if len(items) == 1:
            return f"Puedes probar {items[0]}."
        joined = "; ".join(items[:-1]) + f" y {items[-1]}" if len(items) > 1 else items[0]
        return f"Te sugiero {joined}."

    def _remember_interaction(self, user_text: str, intent: str, tags: Optional[List[str]] = None) -> None:
        if not self.last_assistant_output.strip():
            return
        self.memory.add_entry(user_text, self.last_assistant_output, intent, tags or [])

    def shutdown(self) -> None:
        if self._speech_queue is not None:
            try:
                self._speech_queue.put(None, block=False)
            except Exception:
                pass
            self._speech_queue = None

    def _intent_tags(self, intent: str) -> List[str]:
        mapping = {
            "greeting": ["saludo"],
            "music_playback": ["musica", "youtube"],
            "music_recommendation": ["musica", "recomendacion"],
            "route": ["maps", "ruta"],
            "video": ["video"],
            "web_search": ["busqueda"],
            "document": ["documento"],
            "suggestion": ["consejo"],
            "opinion": ["opinion"],
            "anime_suggestion": ["anime"],
            "anime_watch": ["anime", "ver"],
            "camera": ["camara"],
            "time": ["hora"],
            "date": ["fecha"],
            "emotion": ["emocion"],
            "memory": ["memoria"],
            "whatsapp_message": ["whatsapp"],
            "reminder": ["recordatorio", "alarma"],
            "capabilities": ["ayuda", "capacidades"],
            "project_evaluation": ["evaluacion", "calificacion"],
            "goty": ["goty", "premios"],
            "general_knowledge": ["trivia", "datos"],
            "creator": ["origen", "creador"],
            "recipe": ["receta", "cocina"],
            "hardware": ["hardware", "pc", "laptop"],
            "compliment": ["animo", "ánimo", "bonito"],
        }
        return mapping.get(intent, [intent])

    def _is_memory_query(self, text_lower: str) -> bool:
        triggers = [
            "que te dije",
            "qué te dije",
            "que te pregunté",
            "qué te pregunté",
            "que fue lo que",
            "qué fue lo que",
            "que hablamos",
            "qué hablamos",
            "recuerdas",
            "te acuerdas",
            "pregunt",
        ]
        return any(trigger in text_lower for trigger in triggers)

    def _is_capability_request(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        return any(phrase in normalized for phrase in CAPABILITY_PHRASES)

    def _is_identity_question(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        return any(pattern in normalized for pattern in IDENTITY_QUERY_PATTERNS)

    def _is_compliment_request(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        return any(pattern in normalized for pattern in COMPLIMENT_REQUEST_PATTERNS)

    def _is_goty_question(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        return any(keyword in normalized for keyword in GOTY_KEYWORDS)

    def _is_project_evaluation_question(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        return any(phrase in normalized for phrase in PROJECT_EVAL_PHRASES)

    def _is_creator_question(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        return any(phrase in normalized for phrase in CREATOR_QUERY_PHRASES)

    def _is_recipe_request(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        if not normalized.strip():
            return False
        if any(keyword in normalized for keyword in COOKING_KEYWORDS):
            return True
        if _match_recipe_aliases(normalized):
            return True
        if "comida" in normalized and any(token in normalized for token in ["idea", "ideas", "sugerencia", "opcion", "opciones", "menu"]):
            return True
        return False

    def _needs_recipe_brainstorm(self, normalized_text: str) -> bool:
        return any(pattern in normalized_text for pattern in RECIPE_RANDOM_PATTERNS)

    def _is_emotion_boost_request(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        return any(keyword in normalized for keyword in EMOTION_BOOST_KEYWORDS)

    def _is_hardware_request(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        if not normalized.strip():
            return False
        return any(keyword in normalized for keyword in HARDWARE_KEYWORDS)

    def _needs_hardware_brainstorm(self, normalized_text: str) -> bool:
        return any(pattern in normalized_text for pattern in HARDWARE_RANDOM_PATTERNS)

    def _resolve_hardware_mode(self, normalized_text: str) -> Optional[str]:
        if any(keyword in normalized_text for keyword in HARDWARE_DESKTOP_KEYWORDS):
            return "desktop"
        if any(keyword in normalized_text for keyword in HARDWARE_LAPTOP_KEYWORDS):
            return "laptop"
        return None

    def _needs_anime_brainstorm(self, normalized_text: str) -> bool:
        return any(pattern in normalized_text for pattern in ANIME_RANDOM_PATTERNS)

    def _match_general_knowledge_entry(self, user_text: str) -> Optional[Dict[str, Any]]:
        normalized = _normalize_command_text(user_text)
        for item in GENERAL_KNOWLEDGE_DATA:
            if all(keyword in normalized for keyword in item["keywords"]):
                return item
        return None

    def _handle_general_knowledge(self, entry: Dict[str, Any]) -> None:
        response = entry["answer"]
        if entry.get("category"):
            response += f" (Dato de {entry['category']})."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_recipe_request(self, user_text: str) -> None:
        if not CURATED_RECIPES:
            response = (
                "Aún no tengo disponible mi recetario entrenado en este entorno. "
                "Ejecuta tools/generate_recipe_dataset.py y vuelve a preguntarme qué quieres cocinar."
            )
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        normalized = _normalize_command_text(user_text)
        filters = _infer_recipe_filters(normalized)
        if self._needs_recipe_brainstorm(normalized):
            picks = pick_random_recipes(3, filters or None, self.recipe_rng)
            if not picks:
                picks = pick_random_recipes(3, None, self.recipe_rng)
            response = format_recipe_brainstorm(picks, TOTAL_CURATED_RECIPES, filters or None)
        else:
            matches = lookup_curated_recipes(user_text, filters or None, limit=3)
            if matches:
                response = format_recipe_detail(matches[0], TOTAL_CURATED_RECIPES)
            else:
                fallback = pick_random_recipes(3, filters or None, self.recipe_rng)
                if fallback:
                    brainstorm = format_recipe_brainstorm(fallback, TOTAL_CURATED_RECIPES, filters or None)
                    response = "No encontré una coincidencia exacta, pero estas opciones se acercan:\n" + brainstorm
                else:
                    response = (
                        f"Tengo {TOTAL_CURATED_RECIPES} recetas cargadas, pero necesito un ingrediente, tiempo o tipo de dieta"
                        " para acertar. Dame un dato más y te propongo algo al momento."
                    )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_hardware_request(self, user_text: str) -> None:
        if not CURATED_HARDWARE_BUILDS:
            response = (
                "Mi dataset de hardware todavía no está cargado aquí. Ejecuta tools/generate_hardware_dataset.py "
                "y vuelve a pedirme una PC o laptop para darte combinaciones entrenadas."
            )
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        normalized = _normalize_command_text(user_text)
        filters = _infer_hardware_filters(normalized)
        mode = self._resolve_hardware_mode(normalized)
        wants_brainstorm = self._needs_hardware_brainstorm(normalized)
        component_slot = _detect_hardware_component_focus(normalized)
        active_filters = filters or None
        if component_slot:
            matches = lookup_hardware_builds(user_text, active_filters, mode, limit=2)
            if matches:
                response = format_hardware_component_detail(matches[0], component_slot, TOTAL_HARDWARE_BUILDS)
            else:
                picks = pick_random_hardware_builds(2, mode, active_filters, self.hardware_rng)
                if picks:
                    response = (
                        "No ubiqué ese componente exacto, pero estas configuraciones entrenadas son compatibles.\n"
                        + format_hardware_brainstorm(picks, TOTAL_HARDWARE_BUILDS, mode, active_filters)
                    )
                else:
                    response = (
                        f"Tengo {TOTAL_HARDWARE_BUILDS} builds registrados. Dime el modelo o marca de la pieza para detallar por qué la elegiría."
                    )
        elif wants_brainstorm:
            picks = pick_random_hardware_builds(3, mode, active_filters, self.hardware_rng)
            if not picks:
                picks = pick_random_hardware_builds(3, mode, None, self.hardware_rng)
            response = format_hardware_brainstorm(picks, TOTAL_HARDWARE_BUILDS, mode, active_filters)
        else:
            matches = lookup_hardware_builds(user_text, active_filters, mode, limit=3)
            if matches:
                response = format_hardware_build_detail(matches[0], TOTAL_HARDWARE_BUILDS)
                if len(matches) > 1:
                    brainstorm = format_hardware_brainstorm(matches[1:], TOTAL_HARDWARE_BUILDS, mode, active_filters)
                    response += "\n\n" + brainstorm
            else:
                fallback = pick_random_hardware_builds(3, mode, active_filters, self.hardware_rng)
                if fallback:
                    brainstorm = format_hardware_brainstorm(fallback, TOTAL_HARDWARE_BUILDS, mode, active_filters)
                    response = "No encontré una coincidencia literal, pero estas configuraciones encajan bien:\n" + brainstorm
                else:
                    response = (
                        f"Tengo {TOTAL_HARDWARE_BUILDS} combinaciones registradas. Indícame presupuesto, resolución objetivo o "
                        "si prefieres laptop/desktop para darte un build preciso."
                    )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_memory_query(self, user_text: str) -> None:
        recalls = self.memory.recall(user_text, limit=3)
        if not recalls:
            recalls = self.memory.recent(limit=2)
        if recalls:
            formatted = "; ".join(recalls)
            response = f"Esto es lo que tengo presente: {formatted}."
        else:
            response = (
                "Aún no tengo suficientes recuerdos sobre eso. Si me lo repites, lo guardaré para la próxima."
            )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _is_whatsapp_request(self, text_lower: str) -> bool:
        if "whatsapp" in text_lower or "wasap" in text_lower or "guasap" in text_lower:
            return True
        return any(keyword in text_lower for keyword in WHATSAPP_TRIGGER_KEYWORDS)

    def _handle_whatsapp_request(self, user_text: str) -> None:
        if not WHATSAPP_AUTOMATION_AVAILABLE:
            response = (
                "No puedo enviar mensajes por WhatsApp desde este equipo porque la automatización está deshabilitada"
                " o faltan las dependencias de Selenium."
            )
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        text_lower = user_text.lower()
        auto_reply_seconds = 0
        if any(keyword in text_lower for keyword in WHATSAPP_AUTO_REPLY_KEYWORDS):
            auto_reply_seconds = _extract_auto_reply_duration_seconds(user_text)
        if auto_reply_seconds:
            contact_candidate, _ = _heuristic_whatsapp_parameters(user_text)
            contact = contact_candidate.strip()
            if not contact:
                contact, _, _ = parse_whatsapp_command(user_text)
            if not contact:
                response = "Necesito saber a qué contacto de WhatsApp debo responder por ti."
                self.emotion_state.register_assistant_message(response)
                self._emit(response)
                return
            minutes_requested = max(1, round(auto_reply_seconds / 60))
            acknowledgement = (
                f"Me quedaré en el chat de {contact} durante {minutes_requested} minuto"
                f"{'s' if minutes_requested != 1 else ''} para contestar automáticamente."
                " Te aviso cuando termine."
            )
            self._emit(acknowledgement)
            success, detail = auto_reply_whatsapp_chat(contact, auto_reply_seconds)
            response = detail or (
                "Terminé de vigilar el chat, pero no logré enviar ninguna respuesta automática."
            )
            if not success and not detail:
                response = "No pude hacerme cargo del chat en este momento."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        contact, message, repetitions = parse_whatsapp_command(user_text)
        missing_parts = []
        if not contact:
            missing_parts.append("el contacto")
        if not message:
            missing_parts.append("el mensaje a enviar")
        if missing_parts:
            missing_text = " y ".join(missing_parts)
            response = f"Necesito que me indiques {missing_text} para poder enviar el WhatsApp."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        schedule_detection = _detect_spanish_time_expression(user_text)
        if schedule_detection:
            requested_dt, rolled = schedule_detection
            task_id, effective_dt = _schedule_whatsapp_message(contact, message, repetitions, requested_dt)
            day_phrase = _describe_schedule_day(effective_dt)
            acknowledgement = (
                f"Perfecto, enviaré el mensaje {day_phrase} a las {effective_dt.strftime('%H:%M')}"
            )
            if repetitions > 1:
                acknowledgement += f" y repetiré {repetitions} veces."
            else:
                acknowledgement += "."
            if rolled or effective_dt > requested_dt:
                acknowledgement += " Ajusté el horario para el siguiente momento disponible." 
            acknowledgement += f" (Referencia interna {task_id})."
            self.emotion_state.register_assistant_message(acknowledgement)
            self._emit(acknowledgement)
            return
        try:
            success, detail = automate_whatsapp_message(contact, message, repetitions)
        except Exception as exc:
            success = False
            detail = f"Tuvimos un error inesperado al controlar WhatsApp: {exc}."
        response = detail or (
            "No pude completar la acción en WhatsApp, intenta de nuevo o revisa que la sesión esté iniciada."
        )
        if not success and not detail:
            response = "No logré controlar WhatsApp en este momento."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_greeting(self, user_text: str) -> None:
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente empático. Responde a saludos en español con calidez, "
                    "menciona brevemente tu estado emocional actual y ofrece ayuda específica."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Saludo recibido: {user_text}. Estado emocional actual: {self.emotion_state.describe()} "
                    "Redacta una respuesta breve, natural y conversacional."
                ),
            },
        ]
        response = query_llm(messages)
        if not response.strip():
            response = "Hola, aquí estoy listo para ayudarte con lo que necesites."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_music_request(self, user_text: str) -> None:
        focus = extract_focus_text(user_text, ["recomienda", "música", "musica", "canción", "cancion", "melodía", "melodia", "song"])
        if not focus:
            focus = f"música {self.emotion_state.current}"
        query = clean_music_query(focus)
        results = fetch_music_recommendations(query)
        if not results:
            backup_results = perform_web_search(query + " canción", limit=3)
            if backup_results:
                results = backup_results
        llm_supplement = ""
        if not results:
            llm_messages = [
                {
                    "role": "system",
                    "content": (
                        "Eres un curador musical en español. Recomienda entre tres y cuatro canciones"
                        " especificando título y artista. Incluye una frase breve que describa el ánimo"
                        " o por qué cada canción encaja con la petición."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Necesito recomendaciones musicales con este contexto: "
                        f"{focus or query}. Responde en texto corrido o con frases separadas por punto."
                    ),
                },
            ]
            llm_supplement = query_llm(llm_messages).strip()
        if llm_supplement:
            response = llm_supplement
        else:
            response = self._format_list("música", results)
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_music_playback_request(self, user_text: str) -> None:
        keywords = [
            "reproduce",
            "pon",
            "ponme",
            "play",
            "escucha",
            "escuchar",
            "quiero oír",
            "quiero escuchar",
            "suena",
            "en youtube",
        ]
        focus = extract_focus_text(user_text, keywords).strip()
        if not focus:
            focus = user_text.strip()
        focus = clean_music_query(focus)
        opened, playback_summary = open_youtube_video(focus)
        if playback_summary:
            if playback_summary.lower().startswith("busqué"):
                prefix = "Abrí YouTube" if opened else "Te dejo preparada la búsqueda en YouTube"
                response = f"{prefix} y {playback_summary}."
            else:
                prefix = "Abrí YouTube" if opened else "Te comparto el enlace que encontré"
                response = f"{prefix} con {playback_summary}."
        else:
            suggestions = [entry["summary"] for entry in search_youtube(focus, limit=3, filter_music=True)]
            if suggestions:
                response = "No pude iniciar la reproducción directa, pero " + self._format_list("música", suggestions)
            else:
                fallback_opened, fallback_msg = open_youtube_search_page(focus)
                if fallback_msg:
                    prefix = "Abrí YouTube" if fallback_opened else "Preparé la búsqueda para que la abras"
                    response = f"{prefix} y {fallback_msg}."
                else:
                    response = "No encontré coincidencias claras para reproducir ahora mismo."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_video_request(self, user_text: str) -> None:
        focus = extract_focus_text(user_text, ["recomienda", "video", "vídeo", "youtube", "ver", "mira", "película", "pelicula"])
        if not focus:
            focus = f"videos {self.emotion_state.current}"
        results = fetch_video_recommendations(focus)
        response = self._format_list("videos", results)
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_web_search(self, user_text: str) -> None:
        focus = extract_focus_text(user_text, ["busca", "buscar", "investiga", "encuentra", "investigación", "investigacion"])
        if not focus:
            focus = user_text
        text_lower = user_text.lower()
        focus_lower = focus.lower()
        video_query = is_video_game_query(text_lower) or is_video_game_query(focus_lower)
        force_steps = needs_step_by_step_response(text_lower) or video_query
        alt_queries = build_game_alt_queries(focus, focus_lower) if video_query else None
        curated_entries = detect_curated_game_entries(text_lower) or detect_curated_game_entries(focus_lower)
        if curated_entries:
            response = format_curated_game_guide(focus, curated_entries)
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        summary, sources = summarize_web_research(
            focus,
            force_steps=force_steps,
            alt_queries=alt_queries,
            additional_context=curated_entries,
        )
        if summary:
            if sources:
                top_sources = "; ".join(sources[:3])
                response = f"Según lo que encontré en línea, {summary} Fuentes consultadas: {top_sources}."
            else:
                response = summary
        else:
            results = perform_web_search(focus)
            if results:
                response = self._format_list("información", results)
            elif sources:
                top_sources = "; ".join(sources[:3])
                response = (
                    "No pude sintetizar pasos claros, pero revisa estas fuentes directamente: "
                    f"{top_sources}."
                )
            else:
                llm_messages = [
                    {
                        "role": "system",
                        "content": (
                            "Eres un analista en español. Cuando no hay resultados web disponibles, comparte"
                            " un resumen fiable de conocimiento general sobre el tema solicitado."
                            " Limita la respuesta a cuatro frases y aclara que usas conocimiento general."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "No pude recuperar resultados web para esta consulta, pero necesito una explicación"
                            f" breve sobre: {focus}."
                        ),
                    },
                ]
                fallback = query_llm(llm_messages).strip()
                response = fallback or "No encontré información confiable en este momento."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_suggestion_request(self, user_text: str) -> None:
        focus = extract_focus_text(
            user_text,
            list(SUGGESTION_KEYWORDS) + ["idea", "ideas", "aconseja", "aconsejar", "recomienda", "recomendar"],
        )
        if not focus:
            focus = user_text
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asesor creativo en español. Propón de tres a cuatro sugerencias concretas"
                    " y accionables sobre el tema solicitado. Evita listas con viñetas o numeradas;"
                    " mejor escribe frases o párrafos breves separados por saltos de línea."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Contexto del usuario: {focus}.\n"
                    "Comparte ideas que combinen empatía y practicidad, resaltando por qué cada sugerencia"
                    " es útil y cómo puede ponerse en marcha." 
                ),
            },
        ]
        response = query_llm(messages)
        if not response.strip():
            memory_context = self.memory.recall(user_text, limit=3)
            response = self.brain.generate_reply(user_text, memory_context=memory_context)
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_opinion_request(self, user_text: str) -> None:
        focus = extract_focus_text(
            user_text,
            list(OPINION_KEYWORDS) + ["sobre", "de", "acerca", "tema", "asunto"],
        ).strip()
        if not focus:
            focus = user_text.strip()
        emotional_state = self.emotion_state.describe()
        memory_context = self.memory.recall(user_text, limit=2)
        context_note = "\n".join(memory_context) if memory_context else ""
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres Miau, una IA empática. Comparte una opinión personal y honesta"
                    " sobre el tema indicado. Habla en primera persona, menciona brevemente cómo"
                    " tu estado emocional actual influye en tu perspectiva y ofrece al menos una sugerencia"
                    " práctica basada en esa opinión. Usa un tono cercano, máximo cuatro párrafos cortos."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Tema para tu opinión: {focus}.\n"
                    f"Estado emocional reportado: {emotional_state}.\n"
                    f"Recuerdos relevantes: {context_note if context_note else 'sin contexto adicional'}."
                ),
            },
        ]
        response = query_llm(messages).strip()
        if not response:
            response = (
                f"Personalmente siento que {focus} es un asunto que merece atención consciente."
                " Mi percepción puede cambiar con nueva información, pero por ahora te sugiero"
                " analizar cómo te hace sentir y tomar la decisión que mejor se alinee con tus valores."
            )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_capability_request(self) -> None:
        response = (
            "Puedo ayudarte con recordatorios, temporizadores y alarmas; crear o abrir eventos en Google Calendar; "
            "configurar mensajes y respuestas automáticas en WhatsApp; reproducir o recomendar música, videos y anime; "
            "abrir rutas en Google Maps; analizar imágenes o la cámara; dictar y generar documentos; buscar información en la web; "
            "y conversar por voz o texto para darte opiniones, ideas o seguimiento a lo que recordemos."
            " Solo dime qué necesitas y lo resolvemos paso a paso."
        )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_goty_question(self, user_text: str) -> None:
        year = _extract_year_from_text(user_text)
        latest_known_year = max(KNOWN_GOTY_WINNERS)
        previous_year = self.last_goty_question_year
        previous_pick = self.last_future_goty_pick
        favorite_pick: Optional[str] = None
        if year and year in KNOWN_GOTY_WINNERS:
            winner = KNOWN_GOTY_WINNERS[year]
            nominees = GOTY_NOMINEES_BY_YEAR.get(year, [])
            if nominees:
                if len(nominees) == 1:
                    nominees_text = nominees[0]
                else:
                    nominees_text = ", ".join(nominees[:-1]) + f" y {nominees[-1]}"
                detail = f"Los nominados oficiales fueron: {nominees_text}."
            else:
                detail = ""
            response = (
                f"El Juego del Año {year} en The Game Awards fue {winner}. "
                f"{detail} Puedes revisar el listado completo en thegameawards.com para más categorías."
            )
        elif year and year > latest_known_year:
            favorite = ANTICIPATED_GOTY_TITLES[0]
            contenders = ANTICIPATED_GOTY_TITLES[1:]
            contender_text = "; ".join(
                f"{entry['title']} ({entry['studio']})" for entry in contenders[:3]
            )
            memory_clause = ""
            if previous_year == year and previous_pick:
                if previous_pick == favorite["title"]:
                    memory_clause = " Sigo con la misma apuesta que te compartí antes."
                else:
                    memory_clause = (
                        f" Antes te mencioné a {previous_pick}, pero tras los avances recientes veo a {favorite['title']} con más impulso."
                    )
            response = (
                f"Creo que {favorite['title']} de {favorite['studio']} se llevará el GOTY {year}: {favorite['notes']} "
                f"Como rivales cercanos tengo a {contender_text}. "
                "Las nominaciones oficiales se publican en noviembre y aquí no estoy considerando simuladores deportivos; hablo de RPG y aventuras narrativas."
                f"{memory_clause} Dejo este pronóstico guardado para comparar cuando lo volvamos a revisar."
            )
            favorite_pick = favorite["title"]
        else:
            recent = sorted(KNOWN_GOTY_WINNERS.items(), reverse=True)[:5]
            summary = "; ".join(f"{yr}: {title}" for yr, title in recent)
            response = (
                "El GOTY lo entrega The Game Awards cada diciembre y reconoce al lanzamiento más influyente del año. "
                f"Ganadores recientes: {summary}. Si necesitas un año específico, dime cuál y te comparto ese resultado."
            )
        self.last_goty_question_year = year if year else None
        self.last_future_goty_pick = favorite_pick if favorite_pick else None
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_project_evaluation(self) -> None:
        response = (
            "Con la forma en la que me programaron puedo reconocer voz, responder con síntesis parlante,"
            " llevar registros de emociones, crear recordatorios y calendarios, automatizar WhatsApp,"
            " buscar en la web, generar documentos, recomendar música, videos o anime, describir imágenes,"
            " y sostener conversaciones con opiniones y datos."
            " Por todo ese alcance y la estabilidad que logré en mis pruebas, yo les pondría un 10/10 al equipo."
        )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_document_request(self, user_text: str) -> None:
        topic = self._infer_document_topic(user_text)
        if not topic:
            response = "Necesito que me digas el tema del documento para poder redactarlo."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        prep_message = f"Voy a redactar un documento sobre {topic} y lo guardaré en tu carpeta de descargas."
        self._emit(prep_message)
        content = self._generate_document_content(topic, user_text)
        if not content.strip():
            response = "No logré redactar el documento en este momento, intenta nuevamente más tarde."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        downloads_dir = get_downloads_directory()
        filename = self._build_document_filename(topic)
        file_path = os.path.join(downloads_dir, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as handler:
                handler.write(content.strip() + "\n")
        except OSError as exc:
            response = f"Elaboré el texto, pero no pude guardarlo en {downloads_dir}: {exc}."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        response = (
            f"Listo, redacté un documento con hallazgos y recomendaciones sobre {topic}. "
            f"Puedes abrirlo en {file_path}."
        )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_anime_suggestion_request(self, user_text: str) -> None:
        if not CURATED_ANIME_TITLES:
            response = (
                "Aún no tengo cargado mi catálogo de anime en este entorno. Ejecuta tools/generate_anime_dataset.py "
                "para que pueda recomendar temporadas y películas entrenadas."
            )
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        normalized = _normalize_command_text(user_text)
        filters = _infer_anime_filters(normalized)
        if self._needs_anime_brainstorm(normalized):
            picks = pick_random_anime_titles(4, filters or None, self.anime_rng)
            response = format_anime_brainstorm(picks, TOTAL_CURATED_ANIME_TITLES, filters or None)
        else:
            matches = lookup_anime_titles(user_text, filters or None, limit=4)
            if matches:
                response = format_anime_detail(matches[0], TOTAL_CURATED_ANIME_TITLES)
                if len(matches) > 1:
                    extras = format_anime_brainstorm(matches[1:], TOTAL_CURATED_ANIME_TITLES, filters or None)
                    response = response + "\n\n" + extras
            else:
                picks = pick_random_anime_titles(4, filters or None, self.anime_rng)
                if picks:
                    response = "No encontré una coincidencia exacta, pero estas opciones encajan bien:\n" + format_anime_brainstorm(
                        picks,
                        TOTAL_CURATED_ANIME_TITLES,
                        filters or None,
                    )
                else:
                    response = (
                        f"Tengo {TOTAL_CURATED_ANIME_TITLES} títulos registrados. Dime género, tono, duración o si prefieres película/temporada "
                        "para ajustarme mejor."
                    )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_anime_watch_request(self, user_text: str) -> None:
        title = self._extract_anime_title(user_text)
        if not title:
            response = "Necesito que me digas el nombre del anime que quieres ver."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        opened = open_animeflv_search(title)
        if opened:
            response = f"Abrí AnimeFLV para que busques '{title}'."
        else:
            google_url = open_google_search(f"animeflv {title}")
            if google_url:
                response = f"No pude acceder directo a AnimeFLV, pero abrí una búsqueda en el navegador para '{title}'."
            else:
                response = "Intenté abrir AnimeFLV pero no fue posible en este momento."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_route_request(self, user_text: str) -> None:
        keywords = [
            "ruta",
            "dirección",
            "direccion",
            "cómo llegar",
            "como llegar",
            "como ir",
            "cómo ir",
            "como voy",
            "cómo voy",
            "como puedo llegar",
            "cómo puedo llegar",
            "llevar",
            "llevarme",
            "llévame",
            "llegar",
            "maps",
            "mapa",
            "camino",
            "trayecto",
            "ubicación",
            "ubicacion",
            "destino",
            "indicaciones",
        ]
        focus = extract_focus_text(user_text, keywords)
        text_for_parse = focus if focus else user_text
        origin = None
        destination = text_for_parse.strip()
        pattern = re.search(r"(?:desde|de)\s+(.*?)\s+(?:hasta|a)\s+(.*)", text_for_parse, flags=re.IGNORECASE)
        if pattern:
            origin = pattern.group(1).strip()
            destination = pattern.group(2).strip()
        destination = re.sub(r"^(?:a|hasta|para)\s+", "", destination, flags=re.IGNORECASE)
        if not destination:
            response = "Necesito que me indiques el destino para abrir la ruta en Google Maps."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        opened, maps_url = open_google_maps_route(destination, origin=origin)
        route_context = (f" desde {origin}" if origin else "")
        if opened:
            response = (
                f"Abrí Google Maps con la ruta hacia {destination}{route_context}. "
                f"Si no ves la pestaña, abre este enlace: {maps_url}."
            )
        else:
            if maps_url:
                response = (
                    f"No pude abrir Google Maps automáticamente, pero preparé la ruta hacia {destination}{route_context}. "
                    f"Aquí tienes el enlace: {maps_url}."
                )
            else:
                response = "No pude abrir Google Maps en este equipo. Inténtalo manualmente, por favor."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_time_query(self) -> None:
        current_time = datetime.datetime.now().strftime("%H:%M")
        response = f"Son las {current_time}."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_date_query(self) -> None:
        today_date = datetime.date.today()
        days = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        response = (
            f"Hoy es {days[today_date.weekday()]}, {today_date.day} de {months[today_date.month - 1]} de {today_date.year}."
        )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_location_query(self) -> None:
        system = platform.system() or "tu dispositivo"
        release = platform.release()
        hostname = platform.node()
        tz_name = datetime.datetime.now().astimezone().tzname() or "tu zona horaria local"
        location_hint = f"{system} {release}" if release else system
        host_hint = f" ({hostname})" if hostname else ""
        response = (
            f"Estoy operando desde {location_hint}{host_hint} y sincronizado con la zona horaria {tz_name}. "
            "No tengo acceso a GPS ni a tu dirección exacta, pero trabajo sobre este equipo para ayudarte."
        )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_creator_question(self) -> None:
        response = (
            "Nací en un repositorio de Git mantenido por el equipo Los Puffs. "
            "Ellos me programaron y me siguen entrenando para ayudarte desde aquí."
        )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_identity_question(self) -> None:
        response = (
            "Soy Miau, tu asistente emocional multimodal en este proyecto. "
            f"Funciono dentro de este equipo para acompañarte, buscar información y organizar tareas con el ánimo {self.emotion_state.describe()}. "
            "Dime qué necesitas y lo resolvemos juntos."
        )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_compliment_request(self) -> None:
        mood = self.emotion_state.describe()
        compliments = [
            "Eres mucho más resiliente de lo que crees, y cada paso que das inspira a quienes te rodean.",
            "Tu forma de cuidar a las personas deja huella; tienes un corazón enorme y eso se nota.",
            "Me encanta cómo buscas aprender y mejorar; esa curiosidad es tu superpoder.",
            "Incluso en los días pesados, sigues avanzando con valentía, y eso es admirable.",
            "Tu presencia trae calma y calidez; gracias por compartirla conmigo.",
        ]
        pick = random.choice(compliments)
        response = (
            f"Aquí tienes algo bonito con el ánimo {mood}: {pick}"
            " Si necesitas otro impulso emocional, solo dímelo."
        )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_mode_switch(self, user_text: str) -> None:
        text_lower = user_text.lower()
        normalized = _normalize_command_text(user_text)
        disable_markers = [
            "desactiva",
            "apaga",
            "deten",
            "termina",
            "sal",
            "quitar",
            "silencia",
            "calla",
        ]
        wants_chat = "chat" in normalized or any(marker in normalized for marker in disable_markers)
        wants_voice = "voz" in normalized and not wants_chat
        target_mode = "voz" if wants_voice else "chat"
        if target_mode == self.mode:
            self._emit(f"Ya estoy en modo {self.mode}.")
            return
        if target_mode == "voz" and not self.voice_enabled:
            self._emit("No puedo activar la voz porque el motor TTS o el micrófono no están disponibles.")
            return
        self.mode = target_mode
        self._emit(f"Modo {self.mode} activado.")

    def _is_voice_mode_command(self, normalized_text: str) -> bool:
        candidate = _voice_command_candidate_from_normalized(normalized_text)
        if candidate:
            if candidate in VOICE_MODE_ACTIVATE_PATTERNS or candidate in VOICE_MODE_DEACTIVATE_PATTERNS:
                return True
        if "modo" in normalized_text and ("voz" in normalized_text or "chat" in normalized_text):
            return True
        return False

    def _handle_emotion_request(self) -> None:
        response = f"Mi estado emocional actual es {self.emotion_state.describe()}."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_emotion_boost_request(self) -> None:
        previous = self.emotion_state.describe()
        self.emotion_state.boost()
        response = (
            f"¡Hecho! Paso de sentirme {previous} a un ánimo {self.emotion_state.describe()} para acompañarte con más energía. "
            "¿En qué te apoyo ahora mismo?"
        )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_camera_request(self) -> None:
        if cv2 is None or np is None:
            response = (
                "Necesito tener instaladas las bibliotecas opencv-python y numpy para revisar la cámara."
                " Instálalas y vuelve a intentarlo, por favor."
            )
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        cameras = list_available_cameras()
        if not cameras:
            response = "No detecto cámaras disponibles en este equipo."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return
        camera_list_text = ", ".join(str(idx) for idx in cameras)
        chosen_index = cameras[0]
        prompt_text = (
            f"Encontré cámaras en los índices {camera_list_text}."
            f" Abriré la cámara {chosen_index} en una ventana llamada 'MiauCam'."
            " Presiona la tecla 'q' o Esc para cerrarla cuando quieras."
        )
        if self.mode == "chat" and self.output_handler is None:
            self._emit(prompt_text + " Si prefieres otro índice, escríbelo ahora.")
            user_choice = input("Selecciona el índice de la cámara o presiona Enter para usar la sugerida: ").strip()
            if user_choice:
                try:
                    candidate = int(user_choice)
                    if candidate in cameras:
                        chosen_index = candidate
                except ValueError:
                    self._emit("No reconocí ese número, usaré la opción sugerida.")
        else:
            self._emit(prompt_text)
        opened, description = open_camera_preview_and_analyze(chosen_index)
        if opened:
            response = (
                f"Esto es lo que percibo: {description}" if description else "Ya cerré la vista previa de la cámara."
            )
        else:
            response = description or "No logré abrir la cámara seleccionada."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _is_document_request(self, text_lower: str) -> bool:
        if not any(keyword in text_lower for keyword in DOCUMENT_KEYWORDS):
            return False
        verb_match = any(verb in text_lower for verb in DOCUMENT_VERBS)
        explicit_request = "documento sobre" in text_lower or "documento de" in text_lower or "documento acerca" in text_lower
        return verb_match or explicit_request

    def _infer_document_topic(self, user_text: str) -> str:
        pattern = re.search(r"(?:sobre|acerca de|acerca del|acerca de la|sobre la|sobre el)\s+(.+)", user_text, flags=re.IGNORECASE)
        if pattern:
            return pattern.group(1).strip().strip(". ")
        removal_terms = list(DOCUMENT_KEYWORDS | DOCUMENT_VERBS | {"crea", "crear", "genera", "generar"})
        cleaned = extract_focus_text(user_text, removal_terms)
        cleaned = re.sub(r"^(?:sobre|acerca)\s+", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip().strip(". ")

    def _generate_document_content(self, topic: str, user_prompt: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Redacta documentos de referencia en español usando texto plano."
                    " Incluye encabezados simples (Introducción, Desarrollo, Recomendaciones, Conclusión),"
                    " párrafos breves y datos relevantes cuando sea posible."
                    " Evita las viñetas explícitas y mantén un tono profesional y empático."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Tema central: {topic}.\n"
                    f"Solicitud original: {user_prompt}.\n"
                    "Redacta entre 400 y 500 palabras que combinen contexto, hallazgos clave,"
                    " recomendaciones prácticas y un cierre motivador."
                ),
            },
        ]
        return query_llm(messages)

    def _build_document_filename(self, topic: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", topic.lower())
        slug = slug.strip("-") or "documento"
        slug = slug[:40]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{slug}_{timestamp}.txt"

    def _is_suggestion_request(self, text_lower: str) -> bool:
        if any(keyword in text_lower for keyword in SUGGESTION_KEYWORDS):
            return True
        if "ideas" in text_lower:
            return any(trigger in text_lower for trigger in ["dame", "necesito", "busco", "quiero"])
        return False

    def _is_anime_suggestion_request(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        if "anime" not in normalized and "animes" not in normalized:
            return False
        if any(pattern in normalized for pattern in ANIME_RANDOM_PATTERNS):
            return True
        return any(trigger in normalized for trigger in ANIME_SUGGESTION_TRIGGERS)

    def _is_anime_watch_request(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        if "anime" not in normalized:
            return False
        if any(phrase in normalized for phrase in ["recomienda", "sugerencia", "recomendacion"]):
            return False
        if any(pattern in normalized for pattern in ANIME_RANDOM_PATTERNS):
            return False
        return any(trigger in normalized for trigger in ANIME_WATCH_TRIGGERS)

    def _extract_anime_title(self, user_text: str) -> str:
        match = re.search(r"(?:ver|buscar|pon|reproduce)\s+(?:el\s+)?anime\s+(?:de|del|llamado|titulado)?\s*(.+)", user_text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip().strip(". !?")
        cleaned = extract_focus_text(
            user_text,
            list(ANIME_SUGGESTION_KEYWORDS | ANIME_WATCH_TRIGGERS |
                 {"quiero ver", "quiero", "ver", "anime", "el anime", "ver el"}),
        )
        return cleaned.strip().strip(". !?")

    def _is_fun_fact_request(self, text_lower: str) -> bool:
        normalized = _normalize_command_text(text_lower)
        return any(keyword in normalized for keyword in FUN_FACT_KEYWORDS)

    def _handle_fun_fact_request(self, user_text: str) -> None:
        fact = random.choice(FUN_FACT_RESPONSES)
        response = f"¿Sabías que {fact}? Si quieres otro dato curioso solo dímelo."
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def _handle_reminder_request(self, user_text: str) -> None:
        text_lower = user_text.lower()
        label = _infer_reminder_label(user_text)
        timer_seconds = _extract_timer_duration_seconds(user_text)
        schedule_detection = _detect_spanish_time_expression(user_text)
        wants_calendar = any(keyword in text_lower for keyword in ["calendar", "calendario", "google calendar"])
        wants_timer = any(keyword in text_lower for keyword in ["temporizador", "timer"])
        wants_alarm = any(keyword in text_lower for keyword in ["alarma", "despertador"])
        recordatorio_keywords = {"recordatorio", "recordarme", "recuérdame", "recuerdame"}
        wants_recordatorio = any(keyword in text_lower for keyword in recordatorio_keywords)

        readable_label = label if label != "tu recordatorio" else "lo que me pediste"

        if schedule_detection and (wants_calendar or wants_recordatorio):
            target_dt, rolled = schedule_detection
            event_title = label if label != "tu recordatorio" else "Recordatorio con Miau"
            link = build_google_calendar_event_link(event_title, target_dt, description=user_text)
            opened = launch_browser(link)
            response = (
                f"Abrí Google Calendar con el evento '{event_title}'"
                f" para {target_dt.strftime('%d/%m a las %H:%M')}" + ("." if opened else "")
            )
            if not opened:
                response += f" Completa o ajusta el evento aquí: {link}"
            if rolled:
                response += " (Moví la fecha al siguiente momento disponible)."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return

        if wants_calendar:
            response = "Para crear el evento en Google Calendar necesito la fecha y la hora exacta."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return

        if timer_seconds > 0 and (wants_timer or not schedule_detection):
            self._schedule_local_reminder(timer_seconds, label)
            duration_text = _format_duration_spanish(timer_seconds)
            response = (
                f"Temporizador configurado por {duration_text} para {readable_label}."
                " Te avisaré cuando termine."
            )
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return

        if schedule_detection:
            target_dt, rolled = schedule_detection
            delta = (target_dt - datetime.datetime.now()).total_seconds()
            if delta < 10:
                response = "Necesito que la hora del recordatorio sea al menos con unos segundos de anticipación."
            else:
                self._schedule_local_reminder(delta, label)
                day_phrase = _describe_schedule_day(target_dt)
                response = (
                    f"Perfecto, te avisaré {day_phrase} a las {target_dt.strftime('%H:%M')}"
                    f" sobre {readable_label}."
                )
                if rolled:
                    response += " Ajusté la hora para el siguiente momento posible."
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            return

        if wants_alarm or wants_timer or "recordatorio" in text_lower:
            response = "Necesito que me digas la hora exacta o en cuántos minutos quieres que te avise."
        else:
            response = (
                "Puedo ayudarte con alarmas, temporizadores o eventos."
                " Dime la hora específica o el intervalo, por favor."
            )
        self.emotion_state.register_assistant_message(response)
        self._emit(response)

    def handle_text(
        self,
        user_text: str,
        reply_context: Optional[str] = None,
        image_insights: Optional[List[str]] = None,
    ) -> None:
        augmented_text = user_text
        if reply_context:
            snippet = reply_context.strip()
            if len(snippet) > 240:
                snippet = snippet[:240] + "…"
            augmented_text = f"Estoy respondiendo a: \"{snippet}\".\n{augmented_text}"
        if image_insights:
            for idx, insight in enumerate(image_insights, 1):
                augmented_text += f"\n\n[Contexto visual {idx}: {insight}]"
        self._process_input(augmented_text)

    def _process_input(self, user_text: str) -> None:
        text_lower = user_text.lower()
        normalized_text = _normalize_command_text(user_text)
        self.emotion_state.register_user_message(user_text)
        route_intent = detect_route_intent(text_lower)
        greeting_detected = any(keyword in text_lower for keyword in GREETING_KEYWORDS)
        action_keywords = [
            "busca",
            "investiga",
            "reproduce",
            "pon",
            "documento",
            "idea",
            "recomienda",
            "canción",
            "cancion",
            "anime",
            "ruta",
            "como llegar",
            "envia",
            "envía",
            "manda",
            "mandar",
            "whatsapp",
        ]
        exit_markers = ["salir", "cerrar", "terminar", "adios", "adiós", "hasta luego"]
        if any(marker in text_lower for marker in exit_markers):
            farewell = "Hasta pronto, cuídate." if self.emotion_state.current != "alegre" else "Hasta luego, fue agradable conversar contigo." 
            self._emit(farewell)
            self.keep_running = False
            self._remember_interaction(user_text, "farewell", ["despedida"])
            return
        if self._is_memory_query(text_lower):
            self._handle_memory_query(user_text)
            self._remember_interaction(user_text, "memory", self._intent_tags("memory"))
            return
        if any(phrase in text_lower for phrase in ["qué hora", "dime la hora", "hora actual", "la hora"]):
            self._handle_time_query()
            self._remember_interaction(user_text, "time", self._intent_tags("time"))
            return
        date_markers = [
            "qué día",
            "que dia",
            "que dia es",
            "que dia es hoy",
            "fecha de hoy",
            "dime la fecha",
            "día actual",
            "dia actual",
            "en que dia",
            "en qué dia",
            "en que dia estoy",
            "en qué día estoy",
            "que dia estamos",
        ]
        if any(marker in text_lower for marker in date_markers):
            self._handle_date_query()
            self._remember_interaction(user_text, "date", self._intent_tags("date"))
            return
        location_markers = [
            "donde estas",
            "dónde estás",
            "en donde estas",
            "en dónde estás",
            "donde estamos",
            "en donde estamos",
            "cual es tu ubicacion",
            "cuál es tu ubicación",
            "dime tu ubicacion",
            "dime tu ubicación",
        ]
        if any(marker in text_lower for marker in location_markers):
            self._handle_location_query()
            self._remember_interaction(user_text, "location", ["ubicacion"])
            return
        if self._is_identity_question(text_lower):
            self._handle_identity_question()
            self._remember_interaction(user_text, "identity", ["identidad"])
            return
        if self._is_compliment_request(text_lower):
            self._handle_compliment_request()
            self._remember_interaction(user_text, "compliment", self._intent_tags("compliment"))
            return
        if self._is_capability_request(text_lower):
            self._handle_capability_request()
            self._remember_interaction(user_text, "capabilities", self._intent_tags("capabilities"))
            return
        if self._is_creator_question(text_lower):
            self._handle_creator_question()
            self._remember_interaction(user_text, "creator", self._intent_tags("creator"))
            return
        if self._is_project_evaluation_question(text_lower):
            self._handle_project_evaluation()
            self._remember_interaction(user_text, "project_evaluation", self._intent_tags("project_evaluation"))
            return
        knowledge_entry = self._match_general_knowledge_entry(user_text)
        if knowledge_entry:
            self._handle_general_knowledge(knowledge_entry)
            self._remember_interaction(user_text, "general_knowledge", self._intent_tags("general_knowledge"))
            return
        curated_entries = detect_curated_game_entries(text_lower)
        if curated_entries:
            response = format_curated_game_guide(user_text, curated_entries)
            self.emotion_state.register_assistant_message(response)
            self._emit(response)
            self._remember_interaction(user_text, "curated_game_guide", ["videojuego", "guia"])
            return
        if self._is_recipe_request(text_lower):
            self._handle_recipe_request(user_text)
            self._remember_interaction(user_text, "recipe", self._intent_tags("recipe"))
            return
        if self._is_hardware_request(text_lower):
            self._handle_hardware_request(user_text)
            self._remember_interaction(user_text, "hardware", self._intent_tags("hardware"))
            return
        if self._is_goty_question(text_lower):
            self._handle_goty_question(user_text)
            self._remember_interaction(user_text, "goty", self._intent_tags("goty"))
            return
        if self._is_voice_mode_command(normalized_text):
            self._handle_mode_switch(user_text)
            self._remember_interaction(user_text, "mode_switch", ["modo"])
            return
        if self._is_emotion_boost_request(text_lower):
            self._handle_emotion_boost_request()
            self._remember_interaction(user_text, "emotion", self._intent_tags("emotion"))
            return
        if any(word in text_lower for word in ["cómo te sientes", "como te sientes", "estado emocional", "estado de ánimo", "estado animico"]):
            self._handle_emotion_request()
            self._remember_interaction(user_text, "emotion", self._intent_tags("emotion"))
            return
        if route_intent:
            self._handle_route_request(user_text)
            self._remember_interaction(user_text, "route", self._intent_tags("route"))
            return
        if any(keyword in text_lower for keyword in REMINDER_KEYWORDS):
            self._handle_reminder_request(user_text)
            self._remember_interaction(user_text, "reminder", self._intent_tags("reminder"))
            return
        if self._is_whatsapp_request(text_lower):
            self._handle_whatsapp_request(user_text)
            self._remember_interaction(user_text, "whatsapp_message", self._intent_tags("whatsapp_message"))
            return
        if any(word in text_lower for word in ["reproduce", "pon", "play", "escuchar", "escucha", "quiero oír", "quiero escuchar", "ponme", "en youtube"]):
            self._handle_music_playback_request(user_text)
            self._remember_interaction(user_text, "music_playback", self._intent_tags("music_playback"))
            return
        if any(word in text_lower for word in ["música", "musica", "canción", "cancion", "melodía", "melodia", "playlist"]):
            self._handle_music_request(user_text)
            self._remember_interaction(user_text, "music_recommendation", self._intent_tags("music_recommendation"))
            return
        if any(
            phrase in text_lower
            for phrase in [
                "quiero enseñarte",
                "quiero mostrarte",
                "te quiero enseñar",
                "te quiero mostrar",
                "abre la cam",
                "abre la cámara",
                "abre la camara",
                "usa la cámara",
                "usa la camara",
                "ver mi cámara",
                "ver mi camara",
                "muestra la cámara",
                "muestra la camara",
            ]
        ):
            self._handle_camera_request()
            self._remember_interaction(user_text, "camera", self._intent_tags("camera"))
            return
        if self._is_fun_fact_request(text_lower):
            self._handle_fun_fact_request(user_text)
            self._remember_interaction(user_text, "fun_fact", ["curiosidades"])
            return
        if self._is_anime_suggestion_request(text_lower):
            self._handle_anime_suggestion_request(user_text)
            self._remember_interaction(user_text, "anime_suggestion", self._intent_tags("anime_suggestion"))
            return
        if self._is_anime_watch_request(text_lower):
            self._handle_anime_watch_request(user_text)
            self._remember_interaction(user_text, "anime_watch", self._intent_tags("anime_watch"))
            return
        if any(keyword in text_lower for keyword in OPINION_KEYWORDS):
            self._handle_opinion_request(user_text)
            self._remember_interaction(user_text, "opinion", self._intent_tags("opinion"))
            return
        if any(word in text_lower for word in ["video", "vídeo", "youtube", "película", "pelicula", "serie", "tráiler", "trailer"]):
            self._handle_video_request(user_text)
            self._remember_interaction(user_text, "video", self._intent_tags("video"))
            return
        if any(word in text_lower for word in ["busca", "buscar", "investiga", "encuentra", "investigación", "investigacion", "investigar"]):
            self._handle_web_search(user_text)
            self._remember_interaction(user_text, "web_search", self._intent_tags("web_search"))
            return
        if self._is_document_request(text_lower):
            self._handle_document_request(user_text)
            self._remember_interaction(user_text, "document", self._intent_tags("document"))
            return
        if self._is_suggestion_request(text_lower):
            self._handle_suggestion_request(user_text)
            self._remember_interaction(user_text, "suggestion", self._intent_tags("suggestion"))
            return
        if greeting_detected and not any(word in text_lower for word in action_keywords):
            self._handle_greeting(user_text)
            self._remember_interaction(user_text, "greeting", self._intent_tags("greeting"))
            return
        predicted_intent = self.intent_predictor.predict(user_text, {"route": route_intent})
        intent_handlers: Dict[str, Callable[..., None]] = {
            "greeting": self._handle_greeting,
            "web_search": self._handle_web_search,
            "music_recommendation": self._handle_music_request,
            "music_playback": self._handle_music_playback_request,
            "video": self._handle_video_request,
            "document": self._handle_document_request,
            "suggestion": self._handle_suggestion_request,
            "opinion": self._handle_opinion_request,
            "anime_suggestion": self._handle_anime_suggestion_request,
            "anime_watch": self._handle_anime_watch_request,
            "route": self._handle_route_request,
            "camera": lambda _: self._handle_camera_request(),
            "mode_switch": self._handle_mode_switch,
            "whatsapp_message": self._handle_whatsapp_request,
            "reminder": self._handle_reminder_request,
            "memory": self._handle_memory_query,
            "capabilities": lambda _: self._handle_capability_request(),
            "project_evaluation": lambda _: self._handle_project_evaluation(),
            "goty": lambda prompt: self._handle_goty_question(prompt),
            "general_knowledge": lambda prompt: self._handle_general_knowledge(
                self._match_general_knowledge_entry(prompt)
                or {"answer": "Necesito más contexto para darte el dato que buscas.", "category": None}
            ),
        }
        if predicted_intent in {"time", "date", "emotion"}:
            if predicted_intent == "time":
                self._handle_time_query()
                return
            if predicted_intent == "date":
                self._handle_date_query()
                return
            if predicted_intent == "emotion":
                self._handle_emotion_request()
                return
        handler = intent_handlers.get(predicted_intent)
        if predicted_intent == "document" and not self._is_document_request(text_lower):
            handler = None
        if handler:
            if predicted_intent in {"camera"}:
                handler(None)
            else:
                handler(user_text)
            self._remember_interaction(user_text, predicted_intent, self._intent_tags(predicted_intent))
            return
        memory_context = self.memory.recall(user_text, limit=3)
        response = self.brain.generate_reply(user_text, memory_context=memory_context)
        self._emit(response)
        self._remember_interaction(user_text, "general", ["conversacion"])


class ChatGUI:
    def __init__(self) -> None:
        if not GUI_AVAILABLE or tk is None or ttk is None:
            raise RuntimeError("Tkinter no está disponible en este entorno.")
        self.root = tk.Tk()
        self.root.title("Miau - Asistente Virtual-Los puffs")
        self.root.geometry("780x620")
        self.root.minsize(560, 480)
        self._configure_style()

        self.chat_body_font = tkfont.Font(family="Segoe UI", size=11)
        self.chat_context_font = tkfont.Font(family="Segoe UI", size=9, slant="italic")
        self.chat_label_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.chat_wrap_width = 500

        chat_container = ttk.Frame(self.root, style="ChatContainer.TFrame", padding=18)
        chat_container.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=(20, 12))
        chat_container.columnconfigure(0, weight=1)
        chat_container.rowconfigure(0, weight=1)
        self.chat_canvas = tk.Canvas(
            chat_container,
            bg=self.palette["card"],
            highlightthickness=0,
            bd=0,
        )
        self.chat_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        scrollbar = ttk.Scrollbar(chat_container, command=self.chat_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        self.chat_inner = tk.Frame(self.chat_canvas, bg=self.palette["card"])
        self.chat_window = self.chat_canvas.create_window((0, 0), window=self.chat_inner, anchor="nw")
        self.chat_inner.bind(
            "<Configure>",
            lambda event: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")),
        )
        self.chat_canvas.bind("<Configure>", self._sync_chat_width)

        input_panel = RoundedPanel(self.root, self.palette, radius=28, padding=18)
        input_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        input_panel.inner.columnconfigure(0, weight=1)
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_panel.inner, textvariable=self.input_var, style="Miau.TEntry")
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<Return>", self._on_enter_pressed)
        self.input_entry.bind("<Shift-Return>", lambda event: None)
        self.send_button = ttk.Button(input_panel.inner, text="Enviar", command=self._send_message, style="Accent.TButton")
        self.send_button.grid(row=0, column=1, sticky="e")

        meta_panel = RoundedPanel(self.root, self.palette, radius=24, padding=16)
        meta_panel.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        meta_panel.inner.columnconfigure(0, weight=1)
        meta_panel.inner.columnconfigure(1, weight=1)

        self.reply_info_var = tk.StringVar(value="Sin respuesta enfocada.")
        reply_label = ttk.Label(meta_panel.inner, textvariable=self.reply_info_var, style="Panel.TLabel")
        reply_label.grid(row=0, column=0, sticky="w")
        self.clear_reply_button = ttk.Button(
            meta_panel.inner,
            text="Cancelar respuesta",
            command=self._clear_reply,
            state="disabled",
            style="Miau.TButton",
        )
        self.clear_reply_button.grid(row=0, column=1, sticky="e", padx=(10, 0))

        attachment_panel = RoundedPanel(self.root, self.palette, radius=24, padding=16)
        attachment_panel.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        attachment_panel.inner.columnconfigure(0, weight=1)
        self.attachment_var = tk.StringVar(value="Sin imagen adjunta.")
        attachment_label = ttk.Label(attachment_panel.inner, textvariable=self.attachment_var, style="Panel.TLabel")
        attachment_label.grid(row=0, column=0, sticky="w")
        attach_buttons = ttk.Frame(attachment_panel.inner, style="Panel.TFrame")
        attach_buttons.grid(row=0, column=1, sticky="e")
        self.attach_button = ttk.Button(attach_buttons, text="Adjuntar imagen", command=self._attach_image, style="Miau.TButton")
        self.attach_button.grid(row=0, column=0)
        self.clear_attachment_button = ttk.Button(
            attach_buttons,
            text="Quitar",
            command=self._clear_attachment,
            state="disabled",
            style="Miau.TButton",
        )
        self.clear_attachment_button.grid(row=0, column=1, padx=(8, 0))

        self.status_var = tk.StringVar(value="Listo para conversar.")
        status_panel = RoundedPanel(self.root, self.palette, radius=22, padding=14)
        status_panel.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        status_label = ttk.Label(status_panel.inner, textvariable=self.status_var, style="StatusValue.TLabel")
        status_label.grid(row=0, column=0, sticky="w")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.assistant = AssistantCore(voice_enabled=True)
        self.assistant.mode = "chat"
        self.assistant.set_output_handler(self._handle_assistant_output)
        # Timer UI hook: show timers scheduled by the assistant
        try:
            self.assistant.set_timer_created_callback(self._on_timer_created)
        except Exception:
            pass
        self.timer_window = None
        self._timer_widgets: Dict[_TimerRecord, Dict[str, Any]] = {}
        self.processing = False
        self.message_counter = 0
        self.message_metadata: List[Dict[str, str]] = []
        self.reply_target: Optional[Dict[str, str]] = None
        self.pending_image_path: Optional[str] = None
        self.voice_interface: Optional[VoiceInterface] = None
        self.voice_listening = False
        self.voice_thread: Optional[threading.Thread] = None
        self.voice_stop_event = threading.Event()
        self.selected_mic_index: Optional[int] = None
        self._append_message("Miau", "Hola, soy Miau. Aquí podemos conversar con comodidad.", animate=True)

    def _configure_style(self) -> None:
        if not ttk:
            return
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.palette = {
            "bg": "#030712",
            "card": "#0f172a",
            "panel": "#101a2d",
            "button": "#1f2c44",
            "button_hover": "#2c3c58",
            "accent": "#4ade80",
            "text_primary": "#f1f5f9",
            "text_muted": "#9fb3c8",
            "bubble_user": "#1d4ed8",
            "bubble_user_text": "#f8fafc",
            "bubble_assistant": "#17233d",
            "bubble_assistant_text": "#e2e8f0",
            "bubble_shadow": "#020817",
            "label_user": "#bfdbfe",
            "label_assistant": "#94a3b8",
            "context_text": "#93adc5",
            "panel_shadow": "#020c1e",
        }

        style.configure("TFrame", background=self.palette["bg"])
        style.configure("Card.TFrame", background=self.palette["card"])
        style.configure("Panel.TFrame", background=self.palette["panel"])
        style.configure("ChatContainer.TFrame", background=self.palette["card"])
        style.configure("StatusCard.TFrame", background=self.palette["panel"])

        style.configure("TLabel", background=self.palette["card"], foreground=self.palette["text_primary"], font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=self.palette["panel"], foreground=self.palette["text_primary"], font=("Segoe UI", 10))
        style.configure("Status.TLabel", background=self.palette["panel"], foreground=self.palette["text_muted"], font=("Segoe UI", 9, "italic"))
        style.configure(
            "StatusValue.TLabel",
            background=self.palette["panel"],
            foreground=self.palette["text_primary"],
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "Miau.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 10),
            background=self.palette["button"],
            foreground=self.palette["text_primary"],
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "Miau.TButton",
            background=[("active", self.palette["button_hover"]), ("pressed", self.palette["button_hover"]), ("disabled", "#1a2438")],
            foreground=[("disabled", "#5f6f86")],
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 10),
            background=self.palette["accent"],
            foreground="#052e16",
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#34d399"), ("pressed", "#22c55e"), ("disabled", "#1a2438")],
            foreground=[("disabled", "#3f4d63")],
        )

        entry_bg = "#0b172b"
        style.configure(
            "Miau.TEntry",
            fieldbackground=entry_bg,
            foreground=self.palette["text_primary"],
            bordercolor=self.palette["button"],
            insertcolor=self.palette["text_primary"],
            padding=10,
            relief="flat",
        )
        style.map(
            "Miau.TEntry",
            fieldbackground=[("focus", "#102342")],
        )

        style.configure(
            "Vertical.TScrollbar",
            background=self.palette["button"],
            troughcolor=self.palette["card"],
            gripcount=0,
            bordercolor=self.palette["card"],
            lightcolor=self.palette["card"],
            darkcolor=self.palette["card"],
        )

        self.root.configure(bg=self.palette["bg"])

    def _append_message(self, speaker: str, text: str, context: Optional[str] = None, animate: bool = False) -> None:
        align = "right" if speaker == "Tú" else "left"
        bubble = ChatBubble(
            self.chat_inner,
            speaker=speaker,
            text=text,
            context=context,
            align=align,
            palette=self.palette,
            fonts={
                "body": self.chat_body_font,
                "context": self.chat_context_font,
                "label": self.chat_label_font,
            },
            wrap_width=self.chat_wrap_width,
            animate=animate,
        )
        padx = (80, 18) if align == "left" else (18, 80)
        bubble.pack(anchor="e" if align == "right" else "w", pady=8, padx=padx, fill="x")
        meta = {"speaker": speaker, "text": text.strip()}
        bubble.bind("<Double-Button-1>", lambda event, data=meta: self._prepare_reply(data))
        bubble.canvas.bind("<Double-Button-1>", lambda event, data=meta: self._prepare_reply(data))
        self.message_metadata.append({"widget": bubble, **meta})
        self.message_counter += 1
        self._scroll_to_bottom()

    def _handle_assistant_output(self, text: str) -> None:
        if not self.root:
            return
        normalized = _normalize_command_text(text)

        def _update():
            self._append_message("Miau", text, animate=True)
            if self.voice_listening and self.assistant.mode != "voz":
                self.assistant.mode = "voz"
            if "modo voz activado" in normalized and not self.voice_listening:
                self._start_voice_session()
            elif any(
                phrase in normalized
                for phrase in [
                    "modo chat activado",
                    "modo voz desactivado",
                    "modo voz apagado",
                ]
            ) and self.voice_listening:
                self._stop_voice_session(notify=False)

        self.root.after(0, _update)

    def _sync_chat_width(self, event: Any) -> None:
        if hasattr(self, "chat_canvas") and hasattr(self, "chat_window"):
            try:
                self.chat_canvas.itemconfigure(self.chat_window, width=event.width)
            except Exception:
                pass

    def _scroll_to_bottom(self) -> None:
        if not hasattr(self, "chat_canvas"):
            return
        self.root.after(25, lambda: self.chat_canvas.yview_moveto(1.0))

    def _ensure_timer_window(self) -> None:
        if self.timer_window and tk.Toplevel.winfo_exists(self.timer_window):
            return
        self.timer_window = tk.Toplevel(self.root)
        self.timer_window.title("Temporizadores")
        self.timer_window.geometry("360x240")
        self.timer_frame = ttk.Frame(self.timer_window)
        self.timer_frame.pack(fill="both", expand=True, padx=8, pady=8)

    def _on_timer_created(self, record: object) -> None:
        # Called from assistant thread; schedule GUI update on main thread
        if not self.root:
            return
        def _create():
            try:
                self._ensure_timer_window()
                # create widget row for this timer
                frame = ttk.Frame(self.timer_frame)
                frame.pack(fill="x", pady=4)
                label = ttk.Label(frame, text=record.label)
                label.pack(side="left")
                remaining_var = tk.StringVar(value=_format_timer_display(record.remaining_seconds()))
                rem_label = ttk.Label(frame, textvariable=remaining_var)
                rem_label.pack(side="left", padx=(8, 8))
                pause_btn = ttk.Button(frame, text="Pausar", width=8, command=lambda: self._pause_timer(record))
                pause_btn.pack(side="right", padx=(4, 0))
                stop_btn = ttk.Button(frame, text="Detener", width=8, command=lambda: self._stop_timer(record))
                stop_btn.pack(side="right")
                self._timer_widgets[record] = {
                    "frame": frame,
                    "remaining_var": remaining_var,
                    "pause_btn": pause_btn,
                    "stop_btn": stop_btn,
                    "paused": False,
                }
                # start update loop
                def _update_loop():
                    if record not in self._timer_widgets:
                        return
                    rem = record.remaining_seconds()
                    self._timer_widgets[record]["remaining_var"].set(_format_timer_display(rem))
                    if rem <= 0:
                        self._timer_widgets[record]["remaining_var"].set("Finalizado")
                        # remove buttons
                        try:
                            self._timer_widgets[record]["pause_btn"].configure(state="disabled")
                            self._timer_widgets[record]["stop_btn"].configure(state="disabled")
                        except Exception:
                            pass
                        return
                    self.root.after(500, _update_loop)
                _update_loop()
            except Exception as exc:
                debug_log(f"Error al crear widget de temporizador: {exc}")
        self.root.after(0, _create)

    def _pause_timer(self, record: object) -> None:
        try:
            if hasattr(record, "pause"):
                record.pause()
            widget = self._timer_widgets.get(record)
            if widget:
                widget["pause_btn"].configure(text="Reanudar", command=lambda: self._resume_timer(record))
        except Exception as exc:
            debug_log(f"Error pausando temporizador: {exc}")

    def _resume_timer(self, record: object) -> None:
        try:
            if hasattr(record, "resume"):
                record.resume()
            widget = self._timer_widgets.get(record)
            if widget:
                widget["pause_btn"].configure(text="Pausar", command=lambda: self._pause_timer(record))
        except Exception as exc:
            debug_log(f"Error reanudando temporizador: {exc}")

    def _stop_timer(self, record: object) -> None:
        try:
            if hasattr(record, "cancel"):
                record.cancel()
            widget = self._timer_widgets.pop(record, None)
            if widget:
                try:
                    widget["frame"].destroy()
                except Exception:
                    pass
        except Exception as exc:
            debug_log(f"Error deteniendo temporizador: {exc}")

    def _set_processing(self, value: bool) -> None:
        self.processing = value
        if value:
            self.send_button.state(["disabled"])
            self.input_entry.configure(state="disabled")
        else:
            self.send_button.state(["!disabled"])
            self.input_entry.configure(state="normal")
        if not value:
            self.input_entry.focus_set()
        if value:
            self.status_var.set("Miau está pensando...")
        else:
            idle_status = "Modo voz activo: esperando dictado." if self.voice_listening else "Listo para conversar."
            self.status_var.set(idle_status)

    def _prepare_reply(self, metadata: Dict[str, str]) -> None:
        self.reply_target = metadata
        snippet = metadata.get("text", "")
        if len(snippet) > 80:
            snippet = snippet[:80] + "…"
        self.reply_info_var.set(f"Respondiendo a {metadata.get('speaker', 'mensaje')}: '{snippet}'")
        self.clear_reply_button.state(["!disabled"])

    def _clear_reply(self) -> None:
        self.reply_target = None
        self.reply_info_var.set("Sin respuesta enfocada.")
        self.clear_reply_button.state(["disabled"])

    def _attach_image(self) -> None:
        if filedialog is None:
            messagebox.showerror("Error", "Tkinter no puede abrir el explorador en este entorno.")
            return
        file_path = filedialog.askopenfilename(
            title="Selecciona una imagen",
            filetypes=[(
                "Imágenes",
                "*.png *.jpg *.jpeg *.bmp *.gif *.webp"
            )],
        )
        if not file_path:
            return
        self.pending_image_path = file_path
        self.attachment_var.set(f"Imagen adjunta: {os.path.basename(file_path)}")
        self.clear_attachment_button.state(["!disabled"])

    def _clear_attachment(self) -> None:
        self.pending_image_path = None
        self.attachment_var.set("Sin imagen adjunta.")
        self.clear_attachment_button.state(["disabled"])

    def _on_enter_pressed(self, event) -> str:
        self._send_message()
        return "break"

    def _send_message(self) -> None:
        if self.processing:
            return
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        if self._handle_voice_mode_command(text):
            self._clear_reply()
            self._clear_attachment()
            return
        reply_snapshot = self.reply_target
        attachment_snapshot = self.pending_image_path
        self._dispatch_user_message(text, reply_snapshot, attachment_snapshot, origin="texto")
        self._clear_reply()
        self._clear_attachment()

    def _dispatch_user_message(
        self,
        text: str,
        reply_snapshot: Optional[Dict[str, str]],
        attachment_path: Optional[str],
        origin: str,
    ) -> None:
        if not text:
            return
        if self.processing:
            if origin == "voz":
                self._append_message("Sistema", "Termino esta respuesta y sigo escuchando.")
            return
        context_note_parts: List[str] = []
        if reply_snapshot:
            snippet = reply_snapshot.get("text", "")
            if len(snippet) > 60:
                snippet = snippet[:60] + "…"
            context_note_parts.append(f"respuesta a {reply_snapshot.get('speaker', 'mensaje')}: '{snippet}'")
        if attachment_path:
            context_note_parts.append(f"imagen adjunta: {os.path.basename(attachment_path)}")
        if origin == "voz":
            context_note_parts.append("dictado por voz")
        context_note = " | ".join(context_note_parts) if context_note_parts else None
        self._append_message("Tú", text, context=context_note)
        self._set_processing(True)
        thread = threading.Thread(
            target=self._process_in_background,
            args=(text, reply_snapshot, attachment_path),
            daemon=True,
        )
        thread.start()

    def _handle_voice_mode_command(self, text: str) -> bool:
        normalized = _normalize_command_text(text)
        candidate = _voice_command_candidate_from_normalized(normalized)
        if candidate in VOICE_MODE_DEACTIVATE_PATTERNS:
            self._stop_voice_session()
            return True
        if candidate in VOICE_MODE_ACTIVATE_PATTERNS:
            self._start_voice_session()
            return True
        return False

    def _start_voice_session(self) -> None:
        if self.voice_listening:
            self._append_message("Sistema", "Ya estoy escuchando por voz; puedes dictar tu mensaje.")
            return
        if not microphone_available():
            self._append_message("Sistema", "No detecto un micrófono disponible para activar la voz.")
            return

        try:
            mics = sr.Microphone.list_microphone_names()
        except OSError:
            mics = []

        target_index = self.selected_mic_index
        if len(mics) > 1:
            target_index = self._ask_user_for_microphone(mics)
            if target_index is None:
                self._append_message("Sistema", "Selección de micrófono cancelada.")
                return
        elif len(mics) == 1:
            target_index = 0
        else:
            target_index = None
        self.selected_mic_index = target_index

        if self.voice_interface is None:
            self.voice_interface = VoiceInterface(device_index=target_index)
        else:
            self.voice_interface.set_device(target_index)

        self.voice_stop_event.clear()
        self.voice_listening = True
        self.assistant.mode = "voz"
        self.status_var.set("Modo voz activo: esperando dictado...")
        self._append_message(
            "Sistema",
            "Modo voz activado. Habla cuando quieras y di 'detén la voz' si deseas volver al teclado.",
        )
        self.voice_thread = threading.Thread(target=self._voice_listen_loop, daemon=True)
        self.voice_thread.start()

    def _ask_user_for_microphone(self, mics: List[str]) -> Optional[int]:
        # Create a custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Seleccionar Micrófono")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        lbl = ttk.Label(dialog, text="Elige tu dispositivo de entrada:", padding=10)
        lbl.pack(fill="x")
        
        default_index = self.selected_mic_index if self.selected_mic_index is not None else 0
        selected = tk.IntVar(value=default_index)
        
        canvas = tk.Canvas(dialog, bg="#0d1117", highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        for i, mic_name in enumerate(mics):
            rb = ttk.Radiobutton(scrollable_frame, text=f"{i}: {mic_name}", variable=selected, value=i)
            rb.pack(anchor="w", padx=5, pady=2)
            
        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill="x")
        
        result = {"index": None}
        
        def on_ok():
            result["index"] = selected.get()
            dialog.destroy()
            
        def on_cancel():
            dialog.destroy()
            
        ok_btn = ttk.Button(btn_frame, text="Aceptar", command=on_ok)
        ok_btn.pack(side="right", padx=5)
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=on_cancel)
        cancel_btn.pack(side="right")
        
        self.root.wait_window(dialog)
        return result["index"]

    def _stop_voice_session(self, notify: bool = True) -> None:
        if not self.voice_listening:
            if notify:
                self._append_message("Sistema", "La voz ya estaba desactivada.")
            return
        self.voice_listening = False
        self.voice_stop_event.set()
        self.assistant.mode = "chat"
        self.status_var.set("Listo para conversar.")
        if notify:
            self._append_message("Sistema", "Modo voz desactivado, volvemos al chat escrito.")

    def _voice_listen_loop(self) -> None:
        if not self.voice_interface:
            return
        while not self.voice_stop_event.is_set():
            transcription = self.voice_interface.listen()
            if self.voice_stop_event.is_set() or not self.voice_listening:
                break
            if transcription:
                text = transcription.strip()
                if text:
                    self.root.after(0, lambda t=text: self._handle_voice_transcription(t))
            else:
                if not self.voice_listening:
                    break
        self.voice_stop_event.clear()
        if not self.voice_listening:
            self.assistant.mode = "chat"

    def _handle_voice_transcription(self, text: str) -> None:
        if self._handle_voice_mode_command(text):
            return
        self._dispatch_user_message(text, None, None, origin="voz")

    def _process_in_background(
        self,
        text: str,
        reply_snapshot: Optional[Dict[str, str]],
        attachment_path: Optional[str],
    ) -> None:
        try:
            image_insights: Optional[List[str]] = None
            if attachment_path:
                success, insight = analyze_image_file(attachment_path)
                if success:
                    description = (
                        f"Analicé la imagen {os.path.basename(attachment_path)}: {insight}"
                    )
                    image_insights = [description]
                else:
                    image_insights = [f"No pude analizar la imagen adjunta: {insight}"]
            self.assistant.handle_text(
                text,
                reply_context=reply_snapshot.get("text") if reply_snapshot else None,
                image_insights=image_insights,
            )
        except Exception as exc:
            debug_log(f"Error en la interfaz gráfica: {exc}")
            if messagebox is not None:
                self.root.after(0, lambda: messagebox.showerror("Error", str(exc)))
            else:
                self.root.after(0, lambda: self._append_message("Sistema", f"Ocurrió un error: {exc}"))
        finally:
            self.root.after(0, lambda: self._set_processing(False))
            if not self.assistant.keep_running:
                self.root.after(500, self.root.destroy)

    def _on_close(self) -> None:
        if self.voice_listening:
            self._stop_voice_session(notify=False)
        self.assistant.keep_running = False
        try:
            self.assistant.shutdown()
        except Exception:
            pass
        self.root.destroy()

    def run(self) -> None:
        self.input_entry.focus_set()
        self.root.mainloop()


def select_mode(initial_input: Optional[str] = None) -> str:
    candidates = {"voz", "chat"}
    if initial_input:
        low = initial_input.strip().lower()
        for candidate in candidates:
            if candidate in low:
                return candidate
    while True:
        choice = input("¿Prefieres modo 'voz' o 'chat'? ").strip().lower()
        if choice in candidates:
            return choice
        print("No entendí la elección, escribe 'voz' o 'chat'.")


def should_launch_gui() -> bool:
    if not GUI_AVAILABLE:
        return False
    arg_set = {arg.lower() for arg in sys.argv[1:]}
    if "--cli" in arg_set or "-c" in arg_set:
        return False
    if "--gui" in arg_set or "-g" in arg_set:
        return True
    env_pref = os.getenv("AGENTE_UI")
    if env_pref:
        env_pref = env_pref.lower()
        if env_pref in {"cli", "terminal", "texto"}:
            return False
        if env_pref in {"gui", "ventana", "chat"}:
            return True
    return True


def run_cli_assistant() -> None:
    preset = os.getenv("AGENTE_MODE")
    if preset and preset.lower() in {"voz", "chat"}:
        mode = preset.lower()
    else:
        try:
            mode = select_mode()
        except (EOFError, KeyboardInterrupt):
            mode = "chat"
    voice_available = engine is not None and microphone_available()
    assistant = AssistantCore(voice_enabled=voice_available)
    assistant.mode = mode if mode == "chat" or voice_available else "chat"
    assistant.run()


if __name__ == "__main__":
    if should_launch_gui():
        try:
            gui = ChatGUI()
            gui.run()
        except RuntimeError as exc:
            print(f"No pude iniciar la interfaz gráfica: {exc}. Abriendo modo consolap, mi...")
            run_cli_assistant()
    else:
        run_cli_assistant()
