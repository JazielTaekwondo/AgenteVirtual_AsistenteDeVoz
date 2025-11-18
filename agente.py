import datetime
import os
import re
import sys
import threading
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog

    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    tk = None  # type: ignore[assignment]
    ttk = None  # type: ignore[assignment]
    messagebox = None  # type: ignore[assignment]

try:
    import cv2  # type: ignore[import-not-found]
except ImportError:
    cv2 = None  # type: ignore[assignment]

try:
    import numpy as np  # type: ignore[import-not-found]
except ImportError:
    np = None  # type: ignore[assignment]
import requests
import speech_recognition as sr
from openai import OpenAI
import pyttsx3


# Configuración flexible del modelo de lenguaje (OpenAI por defecto, OpenRouter como respaldo)
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_OPENROUTER_MODEL = "openrouter/auto"
DEFAULT_OPENROUTER_FALLBACK = "meta-llama/llama-3.1-8b-instruct:free"
FALLBACK_ROUTER_KEY = "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"
PIPED_INSTANCES = [
    "https://piped.video",
    "https://pipedapi.kavin.rocks",
    "https://piped.uk",
    "https://watch.leptons.xyz",
]

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
    }


def _describe_scene_from_metrics(metrics: List[Dict[str, float]]) -> str:
    if not metrics:
        return "No pude analizar la escena con suficiente información."
    avg_brightness = sum(item["brightness"] for item in metrics) / len(metrics)
    avg_saturation = sum(item["saturation"] for item in metrics) / len(metrics)
    avg_hue = sum(item["hue"] for item in metrics) / len(metrics)
    avg_edges = sum(item["edge_density"] for item in metrics) / len(metrics)
    max_faces = int(max(item["faces"] for item in metrics))

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

    return f"Percibo {light_desc} {color_desc}. {texture_desc} {faces_desc}"


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
    description = _describe_scene_from_metrics(collected_metrics)
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
    description = _describe_scene_from_metrics([metrics])
    height, width = image.shape[:2]
    return True, f"{description} Resolución aproximada: {width}x{height} píxeles."


def query_llm(messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
    target_model = model or LLM_MODEL
    try:
        if "openai.com" in LLM_BASE_URL:
            response = client.responses.create(
                model=target_model,
                input=[{"role": message["role"], "content": message["content"]} for message in messages],
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )
            chunks: List[str] = []
            for item in getattr(response, "output", []) or []:
                if getattr(item, "type", None) != "message":
                    continue
                message = getattr(item, "message", None)
                if not message:
                    continue
                for content in getattr(message, "content", []) or []:
                    if getattr(content, "type", None) == "text":
                        chunks.append(getattr(content, "text", ""))
            return " ".join(chunks).strip() if chunks else ""
        completion = client.chat.completions.create(
            model=target_model,
            messages=messages,
            max_tokens=MAX_OUTPUT_TOKENS,
        )
        return completion.choices[0].message.content.strip()
    except Exception as exc:
        error_text = str(exc)
        debug_log(f"Error en la solicitud al modelo: {error_text}")
        if "Insufficient credits" in error_text or "requires more credits" in error_text:
            return (
                "No tengo crédito disponible en el modelo configurado."
                " Revisa tu cuenta de OpenRouter u OpenAI para agregar saldo o proporciona otra clave."
            )
        if "No endpoints found" in error_text and "openrouter" in LLM_BASE_URL:
            if target_model != LLM_FALLBACK_MODEL and LLM_FALLBACK_MODEL:
                debug_log(f"Intentando modelo alternativo: {LLM_FALLBACK_MODEL}")
                try:
                    completion = client.chat.completions.create(
                        model=LLM_FALLBACK_MODEL,
                        messages=messages,
                        max_tokens=MAX_OUTPUT_TOKENS,
                    )
                    return completion.choices[0].message.content.strip()
                except Exception as fallback_exc:
                    debug_log(f"Error también con el modelo alternativo: {fallback_exc}")
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


def fetch_web_snippets(query: str, limit: int = 5) -> List[Dict[str, str]]:
    try:
        params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1, "ia": "web"}
        response = requests.get("https://api.duckduckgo.com/", params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
        results: List[Dict[str, str]] = []
        abstract = payload.get("AbstractText") or payload.get("Abstract")
        abstract_url = payload.get("AbstractURL")
        abstract_source = payload.get("AbstractSource")
        if abstract and abstract_url:
            results.append(
                {
                    "title": abstract_source or "Resumen",
                    "snippet": abstract,
                    "url": abstract_url,
                }
            )
        for topic in payload.get("RelatedTopics", []):
            if isinstance(topic, dict) and topic.get("Text") and topic.get("FirstURL"):
                results.append(
                    {
                        "title": topic.get("Text").split(" - ")[0][:80],
                        "snippet": topic["Text"],
                        "url": topic["FirstURL"],
                    }
                )
                if len(results) >= limit:
                    break
            elif isinstance(topic, dict) and topic.get("Topics"):
                for sub in topic.get("Topics", []):
                    if sub.get("Text") and sub.get("FirstURL"):
                        results.append(
                            {
                                "title": sub.get("Text").split(" - ")[0][:80],
                                "snippet": sub["Text"],
                                "url": sub["FirstURL"],
                            }
                        )
                        if len(results) >= limit:
                            break
                if len(results) >= limit:
                    break
        return results[:limit]
    except Exception as exc:
        debug_log(f"Error durante la búsqueda web: {exc}")
        return []


def summarize_web_research(query: str, limit: int = 5) -> Tuple[str, List[str]]:
    snippets = fetch_web_snippets(query, limit)
    if not snippets:
        return "", []
    context_lines = []
    for idx, item in enumerate(snippets, 1):
        context_lines.append(
            f"{idx}. Fuente: {item['url']}\nFragmento: {item['snippet'][:300]}"
        )
    context_block = "\n\n".join(context_lines)
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente que sintetiza resultados de investigación en la web."
                " Proporciona una respuesta breve y clara en español basada únicamente en la evidencia dada."
                " Si hay incertidumbre, aclárala."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Consulta: {query}\n\nInformación recopilada:\n{context_block}\n\n"
                "Redacta un resumen conciso (máximo 4 frases) que responda la consulta."
            ),
        },
    ]
    summary = query_llm(messages)
    if summary.strip():
        return summary.strip(), [item["url"] for item in snippets]
    return "", [item["url"] for item in snippets]


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


def open_youtube_video(query: str) -> Optional[str]:
    matches = search_youtube(query, limit=1, filter_music=True)
    if not matches:
        video_id = fetch_first_youtube_video_id(query)
        if video_id:
            url = f"https://youtu.be/{video_id}"
            try:
                opened = webbrowser.open(url)
                if opened:
                    return f"{query} - {url}"
            except Exception as exc:
                debug_log(f"Error al abrir YouTube directo: {exc}")
        return open_youtube_search_page(query)
    video = matches[0]
    try:
        opened = webbrowser.open(video["url"])
        if opened:
            return video["summary"]
    except Exception as exc:
        debug_log(f"Error al abrir YouTube: {exc}")
    return None


def open_google_maps_route(destination: str, origin: Optional[str] = None) -> bool:
    if not destination:
        return False
    params = {"api": "1", "destination": destination}
    if origin:
        params["origin"] = origin
    query = urllib.parse.urlencode(params)
    url = f"https://www.google.com/maps/dir/?{query}"
    try:
        opened = webbrowser.open(url, new=2)
        if not opened and os.name == "nt":
            try:
                os.startfile(url)  # type: ignore[attr-defined]
                opened = True
            except Exception as sub_exc:
                debug_log(f"Fallback startfile para Google Maps falló: {sub_exc}")
        return opened
    except Exception as exc:
        debug_log(f"Error al abrir Google Maps: {exc}")
        if os.name == "nt":
            try:
                os.startfile(url)  # type: ignore[attr-defined]
                return True
            except Exception as sub_exc:
                debug_log(f"Intento secundario de abrir Google Maps falló: {sub_exc}")
        return False


def open_google_search(query: str) -> Optional[str]:
    if not query:
        return None
    url = "https://www.google.com/search?" + urllib.parse.urlencode({"q": query})
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
        try:
            if webbrowser.open(url):
                return url
        except Exception as exc:
            debug_log(f"Error al abrir AnimeFLV ({url}): {exc}")
            continue
    return None


def open_youtube_search_page(query: str) -> Optional[str]:
    if not query:
        return None
    url = "https://www.youtube.com/results?" + urllib.parse.urlencode({"search_query": query})
    try:
        success = webbrowser.open(url)
        return f"busqué {query} en YouTube" if success else None
    except Exception as exc:
        debug_log(f"Error al abrir la búsqueda de YouTube: {exc}")
        return None


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
}
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
    "https://www.animeflv.net/browse?q={query}",
    "https://www3.animeflv.net/browse?q={query}",
    "https://www.animeflv.re/search?q={query}",
]


def detect_route_intent(text: str) -> bool:
    lowered = text.lower()
    if any(keyword in lowered for keyword in ROUTE_KEYWORDS):
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
            " Adapta tu tono al estado emocional indicado, manteniendo empatía y claridad."
            f" Estado emocional actual: {self.emotion_state.current} con intensidad {self.emotion_state.intensity:.2f}."
            " Responde en español, con frases fluidas y sin usar formato markdown, listas explícitas ni código."
            " Cuando corresponda, ofrece consejos concretos."
        )

    def generate_reply(self, user_message: str) -> str:
        system_message = {"role": "system", "content": self._system_prompt()}
        messages = [system_message]
        messages.extend(limit_history(self.history, self.max_history))
        messages.append({"role": "user", "content": user_message})
        response = query_llm(messages, model=self.model)
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": response})
        self.history = limit_history(self.history, self.max_history)
        self.emotion_state.register_assistant_message(response)
        return response


def microphone_available() -> bool:
    try:
        return bool(sr.Microphone.list_microphone_names())
    except OSError:
        return False


class VoiceInterface:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.calibrated = False

    def listen(self, timeout: int = 5, phrase_time_limit: int = 15) -> Optional[str]:
        if not microphone_available():
            print("No hay micrófono disponible.")
            return None
        with sr.Microphone() as source:
            if not self.calibrated:
                print("Ajustando ruido ambiental, mantente en silencio...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.calibrated = True
            print("Escuchando...")
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                print("Reconociendo...")
                text = self.recognizer.recognize_google(audio, language="es-ES")
                print(f"Tú (voz): {text}")
                return text
            except sr.WaitTimeoutError:
                print("No se detectó voz a tiempo.")
            except sr.UnknownValueError:
                print("No entendí lo que dijiste, intenta otra vez.")
            except sr.RequestError as exc:
                print(f"Error con el servicio de reconocimiento de voz: {exc}")
        return None


class AssistantCore:
    def __init__(self, voice_enabled: bool = True) -> None:
        self.emotion_state = EmotionState()
        self.brain = AssistantBrain(self.emotion_state)
        self.voice_interface = VoiceInterface() if voice_enabled else None
        self.voice_enabled = voice_enabled and engine is not None
        self.mode = "voz" if self.voice_enabled else "chat"
        self.keep_running = True
        self.output_handler: Optional[Callable[[str], None]] = None

    def _emit(self, text: str) -> None:
        if self.output_handler:
            try:
                self.output_handler(text)
                return
            except Exception as exc:
                debug_log(f"Error en output_handler: {exc}")
        if self.voice_enabled and self.mode == "voz":
            speak(text)
        else:
            print(f"Asistente: {text}")

    def set_output_handler(self, handler: Optional[Callable[[str], None]]) -> None:
        self.output_handler = handler

    def _format_list(self, title: str, items: List[str]) -> str:
        if not items:
            return f"No encontré resultados al buscar {title.lower()}."
        if len(items) == 1:
            return f"Puedes probar {items[0]}."
        joined = "; ".join(items[:-1]) + f" y {items[-1]}" if len(items) > 1 else items[0]
        return f"Te sugiero {joined}."

    def _handle_music_request(self, user_text: str) -> None:
        focus = extract_focus_text(user_text, ["recomienda", "música", "musica", "canción", "cancion", "melodía", "melodia", "song"])
        if not focus:
            focus = f"música {self.emotion_state.current}"
        query = clean_music_query(focus)
        results = fetch_music_recommendations(query)
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
        playback_summary = open_youtube_video(focus)
        if playback_summary:
            if playback_summary.lower().startswith("busqué"):
                response = f"Abrí YouTube y {playback_summary}."
            else:
                response = f"Abrí YouTube con {playback_summary}."
        else:
            suggestions = [entry["summary"] for entry in search_youtube(focus, limit=3, filter_music=True)]
            if suggestions:
                response = "No pude iniciar la reproducción directa, pero " + self._format_list("música", suggestions)
            else:
                fallback_msg = open_youtube_search_page(focus)
                if fallback_msg:
                    response = f"Abrí YouTube y {fallback_msg}."
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
        summary, sources = summarize_web_research(focus)
        if summary:
            if sources:
                top_sources = "; ".join(sources[:3])
                response = f"Según lo que encontré en línea, {summary} Fuentes consultadas: {top_sources}."
            else:
                response = summary
        else:
            results = perform_web_search(focus)
            response = self._format_list("información", results)
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
            response = self.brain.generate_reply(user_text)
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
        removal_terms = list(ANIME_SUGGESTION_KEYWORDS | ANIME_SUGGESTION_TRIGGERS)
        focus = extract_focus_text(user_text, removal_terms)
        if not focus:
            focus = "animes populares recientes"
        results = fetch_anime_recommendations(focus)
        if results:
            response = self._format_list("animes", results)
        else:
            response = "No encontré recomendaciones confiables ahora mismo, intenta con otro título o género."
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
        opened = open_google_maps_route(destination, origin=origin)
        if opened:
            response = (
                f"Abrí Google Maps con la ruta hacia {destination}" + (f" desde {origin}" if origin else "") + "."
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

    def _handle_mode_switch(self, user_text: str) -> None:
        target_mode = "voz" if "voz" in user_text.lower() else "chat"
        if target_mode == self.mode:
            self._emit(f"Ya estoy en modo {self.mode}.")
            return
        if target_mode == "voz" and not self.voice_enabled:
            self._emit("No puedo activar la voz porque el motor TTS o el micrófono no están disponibles.")
            return
        self.mode = target_mode
        self._emit(f"Modo {self.mode} activado.")

    def _handle_emotion_request(self) -> None:
        response = f"Mi estado emocional actual es {self.emotion_state.describe()}."
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
        if "anime" not in text_lower and "animes" not in text_lower:
            return False
        return any(trigger in text_lower for trigger in ANIME_SUGGESTION_TRIGGERS)

    def _is_anime_watch_request(self, text_lower: str) -> bool:
        if "anime" not in text_lower:
            return False
        if any(phrase in text_lower for phrase in ["recomienda", "sugerencia", "recomendación", "recomendacion"]):
            return False
        return any(trigger in text_lower for trigger in ANIME_WATCH_TRIGGERS)

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
        self.emotion_state.register_user_message(user_text)
        route_intent = detect_route_intent(text_lower)
        exit_markers = ["salir", "cerrar", "terminar", "adios", "adiós", "hasta luego"]
        if any(marker in text_lower for marker in exit_markers):
            farewell = "Hasta pronto, cuídate." if self.emotion_state.current != "alegre" else "Hasta luego, fue agradable conversar contigo." 
            self._emit(farewell)
            self.keep_running = False
            return
        if any(phrase in text_lower for phrase in ["qué hora", "dime la hora", "hora actual", "la hora"]):
            self._handle_time_query()
            return
        if any(phrase in text_lower for phrase in ["qué día", "fecha de hoy", "dime la fecha", "día actual", "dia actual"]):
            self._handle_date_query()
            return
        if "modo" in text_lower and ("voz" in text_lower or "chat" in text_lower):
            self._handle_mode_switch(user_text)
            return
        if any(word in text_lower for word in ["cómo te sientes", "como te sientes", "estado emocional", "cómo estás", "como estas"]):
            self._handle_emotion_request()
            return
        if route_intent:
            self._handle_route_request(user_text)
            return
        if any(word in text_lower for word in ["reproduce", "pon", "play", "escuchar", "escucha", "quiero oír", "quiero escuchar", "ponme", "en youtube"]):
            self._handle_music_playback_request(user_text)
            return
        if any(word in text_lower for word in ["música", "musica", "canción", "cancion", "melodía", "melodia", "playlist"]):
            self._handle_music_request(user_text)
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
            return
        if self._is_anime_watch_request(text_lower):
            self._handle_anime_watch_request(user_text)
            return
        if self._is_anime_suggestion_request(text_lower):
            self._handle_anime_suggestion_request(user_text)
            return
        if any(word in text_lower for word in ["video", "vídeo", "youtube", "ver", "película", "pelicula", "serie"]):
            self._handle_video_request(user_text)
            return
        if any(word in text_lower for word in ["busca", "buscar", "investiga", "encuentra", "investigación", "investigacion", "investigar"]):
            self._handle_web_search(user_text)
            return
        if self._is_document_request(text_lower):
            self._handle_document_request(user_text)
            return
        if self._is_suggestion_request(text_lower):
            self._handle_suggestion_request(user_text)
            return
        response = self.brain.generate_reply(user_text)
        self._emit(response)


class ChatGUI:
    def __init__(self) -> None:
        if not GUI_AVAILABLE or tk is None or ttk is None:
            raise RuntimeError("Tkinter no está disponible en este entorno.")
        self.root = tk.Tk()
        self.root.title("Miau - Asistente Emocional")
        self.root.geometry("780x620")
        self.root.minsize(560, 480)
        self._configure_style()

        self.chat_display = tk.Text(
            self.root,
            wrap="word",
            state="disabled",
            bg="#0d1117",
            fg="#e6edf3",
            padx=12,
            pady=12,
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 11),
            spacing3=6,
            insertbackground="#e6edf3",
        )
        scrollbar = ttk.Scrollbar(self.root, command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=scrollbar.set)
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=(20, 0), pady=(20, 10))
        scrollbar.grid(row=0, column=1, sticky="ns", pady=(20, 10), padx=(0, 20))
        self.chat_display.tag_configure("user", foreground="#7ee787", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_configure("assistant", foreground="#58a6ff", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_configure("body", foreground="#e6edf3", font=("Segoe UI", 11))
        self.chat_display.tag_configure("context", foreground="#8b949e", font=("Segoe UI", 10, "italic"))

        input_frame = ttk.Frame(self.root)
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        input_frame.columnconfigure(0, weight=1)
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var)
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<Return>", self._on_enter_pressed)
        self.input_entry.bind("<Shift-Return>", lambda event: None)
        self.send_button = ttk.Button(input_frame, text="Enviar", command=self._send_message)
        self.send_button.grid(row=0, column=1, sticky="e")

        meta_frame = ttk.Frame(self.root)
        meta_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        meta_frame.columnconfigure(0, weight=1)
        meta_frame.columnconfigure(1, weight=1)

        self.reply_info_var = tk.StringVar(value="Sin respuesta enfocada.")
        reply_label = ttk.Label(meta_frame, textvariable=self.reply_info_var, style="Status.TLabel")
        reply_label.grid(row=0, column=0, sticky="w")
        self.clear_reply_button = ttk.Button(meta_frame, text="Cancelar respuesta", command=self._clear_reply, state="disabled")
        self.clear_reply_button.grid(row=0, column=1, sticky="e", padx=(10, 0))

        attachment_frame = ttk.Frame(self.root)
        attachment_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        attachment_frame.columnconfigure(0, weight=1)
        self.attachment_var = tk.StringVar(value="Sin imagen adjunta.")
        attachment_label = ttk.Label(attachment_frame, textvariable=self.attachment_var, style="Status.TLabel")
        attachment_label.grid(row=0, column=0, sticky="w")
        attach_buttons = ttk.Frame(attachment_frame)
        attach_buttons.grid(row=0, column=1, sticky="e")
        self.attach_button = ttk.Button(attach_buttons, text="Adjuntar imagen", command=self._attach_image)
        self.attach_button.grid(row=0, column=0)
        self.clear_attachment_button = ttk.Button(
            attach_buttons,
            text="Quitar",
            command=self._clear_attachment,
            state="disabled",
        )
        self.clear_attachment_button.grid(row=0, column=1, padx=(8, 0))

        self.status_var = tk.StringVar(value="Listo para conversar.")
        status_label = ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel")
        status_label.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.assistant = AssistantCore(voice_enabled=False)
        self.assistant.mode = "chat"
        self.assistant.set_output_handler(self._handle_assistant_output)
        self.processing = False
        self.message_counter = 0
        self.message_metadata: List[Dict[str, str]] = []
        self.reply_target: Optional[Dict[str, str]] = None
        self.pending_image_path: Optional[str] = None
        self._append_message("Miau", "Hola, soy SolaChat. Aquí podemos conversar con comodidad.")

    def _configure_style(self) -> None:
        if not ttk:
            return
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#010409")
        style.configure("TLabel", background="#010409", foreground="#e6edf3", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", relief="flat")
        style.configure("Status.TLabel", foreground="#8b949e")
        self.root.configure(bg="#010409")

    def _append_message(self, speaker: str, text: str, context: Optional[str] = None) -> None:
        self.chat_display.configure(state="normal")
        tag = "assistant" if speaker != "Tú" else "user"
        message_id = f"msg_{self.message_counter}"
        start_index = self.chat_display.index("end-1c")
        self.chat_display.insert("end", f"{speaker}: ", tag)
        self.chat_display.insert("end", f"{text.strip()}\n", "body")
        if context:
            self.chat_display.insert("end", f"   ↳ {context}\n", "context")
        end_index = self.chat_display.index("end-1c")
        self.chat_display.tag_add(message_id, start_index, end_index)
        self.chat_display.tag_bind(
            message_id,
            "<Double-Button-1>",
            lambda event, meta={"speaker": speaker, "text": text.strip()}: self._prepare_reply(meta),
        )
        self.message_metadata.append({"id": message_id, "speaker": speaker, "text": text.strip()})
        self.message_counter += 1
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _handle_assistant_output(self, text: str) -> None:
        if not self.root:
            return
        self.root.after(0, lambda: self._append_message("Miau", text))

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
        self.status_var.set("Miau está pensando..." if value else "Listo para conversar.")

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
        reply_snapshot = self.reply_target
        attachment_snapshot = self.pending_image_path
        context_note_parts: List[str] = []
        if reply_snapshot:
            snippet = reply_snapshot.get("text", "")
            if len(snippet) > 60:
                snippet = snippet[:60] + "…"
            context_note_parts.append(f"respuesta a {reply_snapshot.get('speaker', 'mensaje')}: '{snippet}'")
        if attachment_snapshot:
            context_note_parts.append(f"imagen adjunta: {os.path.basename(attachment_snapshot)}")
        context_note = " | ".join(context_note_parts) if context_note_parts else None
        self._append_message("Tú", text, context=context_note)
        self._clear_reply()
        self._clear_attachment()
        self._set_processing(True)
        thread = threading.Thread(
            target=self._process_in_background,
            args=(text, reply_snapshot, attachment_snapshot),
            daemon=True,
        )
        thread.start()

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
                image_insights = [insight]
                if not success:
                    self.root.after(
                        0,
                        lambda: self._append_message(
                            "Sistema",
                            f"No pude analizar la imagen adjunta: {insight}",
                        ),
                    )
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
        self.assistant.keep_running = False
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
            print(f"No pude iniciar la interfaz gráfica: {exc}. Abriendo modo consola, mi...")
            run_cli_assistant()
    else:
        run_cli_assistant()
