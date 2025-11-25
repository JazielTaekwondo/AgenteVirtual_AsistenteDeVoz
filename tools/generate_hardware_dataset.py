"""Generate the curated hardware build dataset (>2,000 combos, 2015-2025).

This utility expands the assistant's knowledge with deterministic desktop and
laptop configurations covering Intel, AMD, NVIDIA, AMD Radeon e Intel Arc
combinations. Running this script writes data/curated_hardware_builds.json.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Sequence

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "curated_hardware_builds.json"

random.seed(20251121)

PERF_LEVEL = {"entry": 1, "mid": 2, "upper": 3, "enthusiast": 4}

DESKTOP_CPUS: List[Dict[str, object]] = [
    {"name": "Intel Core i5-6600K", "brand": "intel", "socket": "LGA1151", "level": PERF_LEVEL["entry"], "year": 2015, "series": "Skylake", "cores": "4C/4T"},
    {"name": "Intel Core i7-7700K", "brand": "intel", "socket": "LGA1151", "level": PERF_LEVEL["mid"], "year": 2017, "series": "Kaby Lake", "cores": "4C/8T"},
    {"name": "Intel Core i7-8700K", "brand": "intel", "socket": "LGA1151", "level": PERF_LEVEL["mid"], "year": 2017, "series": "Coffee Lake", "cores": "6C/12T"},
    {"name": "Intel Core i9-9900K", "brand": "intel", "socket": "LGA1151", "level": PERF_LEVEL["upper"], "year": 2018, "series": "Coffee Lake Refresh", "cores": "8C/16T"},
    {"name": "Intel Core i9-10900K", "brand": "intel", "socket": "LGA1200", "level": PERF_LEVEL["upper"], "year": 2020, "series": "Comet Lake", "cores": "10C/20T"},
    {"name": "Intel Core i7-11700K", "brand": "intel", "socket": "LGA1200", "level": PERF_LEVEL["mid"], "year": 2021, "series": "Rocket Lake", "cores": "8C/16T"},
    {"name": "Intel Core i5-12600K", "brand": "intel", "socket": "LGA1700", "level": PERF_LEVEL["mid"], "year": 2021, "series": "Alder Lake", "cores": "10C (6P+4E)"},
    {"name": "Intel Core i7-13700K", "brand": "intel", "socket": "LGA1700", "level": PERF_LEVEL["upper"], "year": 2022, "series": "Raptor Lake", "cores": "16C (8P+8E)"},
    {"name": "Intel Core i9-14900K", "brand": "intel", "socket": "LGA1700", "level": PERF_LEVEL["enthusiast"], "year": 2023, "series": "Raptor Lake Refresh", "cores": "24C (8P+16E)"},
    {"name": "Intel Core Ultra 9 285K", "brand": "intel", "socket": "LGA1851", "level": PERF_LEVEL["enthusiast"], "year": 2024, "series": "Meteor Lake-S", "cores": "24C (8P+16E)"},
    {"name": "AMD Ryzen 5 1600", "brand": "amd", "socket": "AM4", "level": PERF_LEVEL["entry"], "year": 2017, "series": "Zen", "cores": "6C/12T"},
    {"name": "AMD Ryzen 7 2700X", "brand": "amd", "socket": "AM4", "level": PERF_LEVEL["mid"], "year": 2018, "series": "Zen+", "cores": "8C/16T"},
    {"name": "AMD Ryzen 5 3600", "brand": "amd", "socket": "AM4", "level": PERF_LEVEL["mid"], "year": 2019, "series": "Zen 2", "cores": "6C/12T"},
    {"name": "AMD Ryzen 7 5800X", "brand": "amd", "socket": "AM4", "level": PERF_LEVEL["upper"], "year": 2020, "series": "Zen 3", "cores": "8C/16T"},
    {"name": "AMD Ryzen 9 5900X", "brand": "amd", "socket": "AM4", "level": PERF_LEVEL["upper"], "year": 2020, "series": "Zen 3", "cores": "12C/24T"},
    {"name": "AMD Ryzen 5 7600", "brand": "amd", "socket": "AM5", "level": PERF_LEVEL["mid"], "year": 2023, "series": "Zen 4", "cores": "6C/12T"},
    {"name": "AMD Ryzen 7 7800X3D", "brand": "amd", "socket": "AM5", "level": PERF_LEVEL["upper"], "year": 2023, "series": "Zen 4", "cores": "8C/16T"},
    {"name": "AMD Ryzen 9 7950X3D", "brand": "amd", "socket": "AM5", "level": PERF_LEVEL["enthusiast"], "year": 2023, "series": "Zen 4", "cores": "16C/32T"},
    {"name": "AMD Ryzen 9 9950X", "brand": "amd", "socket": "AM5", "level": PERF_LEVEL["enthusiast"], "year": 2024, "series": "Zen 5", "cores": "16C/32T"},
]

DESKTOP_GPUS: List[Dict[str, object]] = [
    {"name": "NVIDIA GeForce GTX 970", "brand": "nvidia", "level": PERF_LEVEL["entry"], "year": 2014, "vram": "4 GB", "power": 170, "family": "Maxwell"},
    {"name": "NVIDIA GeForce GTX 1070", "brand": "nvidia", "level": PERF_LEVEL["mid"], "year": 2016, "vram": "8 GB", "power": 180, "family": "Pascal"},
    {"name": "NVIDIA GeForce GTX 1660 Super", "brand": "nvidia", "level": PERF_LEVEL["entry"], "year": 2019, "vram": "6 GB", "power": 125, "family": "Turing"},
    {"name": "NVIDIA GeForce RTX 2060", "brand": "nvidia", "level": PERF_LEVEL["mid"], "year": 2019, "vram": "6 GB", "power": 160, "family": "Turing"},
    {"name": "NVIDIA GeForce RTX 3060", "brand": "nvidia", "level": PERF_LEVEL["mid"], "year": 2021, "vram": "12 GB", "power": 170, "family": "Ampere"},
    {"name": "NVIDIA GeForce RTX 3070", "brand": "nvidia", "level": PERF_LEVEL["upper"], "year": 2020, "vram": "8 GB", "power": 220, "family": "Ampere"},
    {"name": "NVIDIA GeForce RTX 3080", "brand": "nvidia", "level": PERF_LEVEL["upper"], "year": 2020, "vram": "10 GB", "power": 320, "family": "Ampere"},
    {"name": "NVIDIA GeForce RTX 4070", "brand": "nvidia", "level": PERF_LEVEL["upper"], "year": 2023, "vram": "12 GB", "power": 200, "family": "Ada"},
    {"name": "NVIDIA GeForce RTX 4080 Super", "brand": "nvidia", "level": PERF_LEVEL["enthusiast"], "year": 2024, "vram": "16 GB", "power": 320, "family": "Ada"},
    {"name": "NVIDIA GeForce RTX 4090", "brand": "nvidia", "level": PERF_LEVEL["enthusiast"], "year": 2022, "vram": "24 GB", "power": 450, "family": "Ada"},
    {"name": "NVIDIA GeForce RTX 5080", "brand": "nvidia", "level": PERF_LEVEL["enthusiast"], "year": 2025, "vram": "18 GB", "power": 360, "family": "Blackwell"},
    {"name": "AMD Radeon RX 480", "brand": "amd", "level": PERF_LEVEL["entry"], "year": 2016, "vram": "8 GB", "power": 150, "family": "Polaris"},
    {"name": "AMD Radeon RX 580", "brand": "amd", "level": PERF_LEVEL["entry"], "year": 2017, "vram": "8 GB", "power": 185, "family": "Polaris"},
    {"name": "AMD Radeon RX 5700 XT", "brand": "amd", "level": PERF_LEVEL["mid"], "year": 2019, "vram": "8 GB", "power": 225, "family": "Navi 10"},
    {"name": "AMD Radeon RX 6700 XT", "brand": "amd", "level": PERF_LEVEL["mid"], "year": 2021, "vram": "12 GB", "power": 230, "family": "RDNA 2"},
    {"name": "AMD Radeon RX 7900 XT", "brand": "amd", "level": PERF_LEVEL["upper"], "year": 2022, "vram": "20 GB", "power": 315, "family": "RDNA 3"},
    {"name": "AMD Radeon RX 7900 XTX", "brand": "amd", "level": PERF_LEVEL["enthusiast"], "year": 2022, "vram": "24 GB", "power": 355, "family": "RDNA 3"},
    {"name": "AMD Radeon RX 8800 XT", "brand": "amd", "level": PERF_LEVEL["enthusiast"], "year": 2024, "vram": "20 GB", "power": 320, "family": "RDNA 4"},
    {"name": "Intel Arc A580", "brand": "intel_arc", "level": PERF_LEVEL["entry"], "year": 2023, "vram": "8 GB", "power": 185, "family": "Alchemist"},
    {"name": "Intel Arc A770", "brand": "intel_arc", "level": PERF_LEVEL["mid"], "year": 2022, "vram": "16 GB", "power": 225, "family": "Alchemist"},
    {"name": "Intel Arc B770", "brand": "intel_arc", "level": PERF_LEVEL["upper"], "year": 2025, "vram": "18 GB", "power": 260, "family": "Battlemage"},
]

LAPTOP_CPUS: List[Dict[str, object]] = [
    {"name": "Intel Core i7-7700HQ", "brand": "intel", "level": PERF_LEVEL["entry"], "year": 2017, "series": "Kaby Lake", "cores": "4C/8T"},
    {"name": "Intel Core i7-9750H", "brand": "intel", "level": PERF_LEVEL["mid"], "year": 2019, "series": "Coffee Lake", "cores": "6C/12T"},
    {"name": "Intel Core i7-10750H", "brand": "intel", "level": PERF_LEVEL["mid"], "year": 2020, "series": "Comet Lake", "cores": "6C/12T"},
    {"name": "Intel Core i9-11900H", "brand": "intel", "level": PERF_LEVEL["upper"], "year": 2021, "series": "Tiger Lake", "cores": "8C/16T"},
    {"name": "Intel Core i9-12900H", "brand": "intel", "level": PERF_LEVEL["upper"], "year": 2022, "series": "Alder Lake", "cores": "14C (6P+8E)"},
    {"name": "Intel Core i9-13980HX", "brand": "intel", "level": PERF_LEVEL["enthusiast"], "year": 2023, "series": "Raptor Lake", "cores": "24C (8P+16E)"},
    {"name": "Intel Core Ultra 9 185H", "brand": "intel", "level": PERF_LEVEL["enthusiast"], "year": 2024, "series": "Meteor Lake", "cores": "22C"},
    {"name": "AMD Ryzen 7 4800H", "brand": "amd", "level": PERF_LEVEL["mid"], "year": 2020, "series": "Zen 2", "cores": "8C/16T"},
    {"name": "AMD Ryzen 9 5900HX", "brand": "amd", "level": PERF_LEVEL["upper"], "year": 2021, "series": "Zen 3", "cores": "8C/16T"},
    {"name": "AMD Ryzen 7 6800HS", "brand": "amd", "level": PERF_LEVEL["mid"], "year": 2022, "series": "Zen 3+", "cores": "8C/16T"},
    {"name": "AMD Ryzen 9 7940HS", "brand": "amd", "level": PERF_LEVEL["upper"], "year": 2023, "series": "Zen 4", "cores": "8C/16T"},
    {"name": "AMD Ryzen AI 9 HX 370", "brand": "amd", "level": PERF_LEVEL["enthusiast"], "year": 2024, "series": "Zen 5C", "cores": "12C"},
]

LAPTOP_GPUS: List[Dict[str, object]] = [
    {"name": "NVIDIA GTX 1650 Laptop", "brand": "nvidia", "level": PERF_LEVEL["entry"], "year": 2019, "vram": "4 GB", "family": "Turing"},
    {"name": "NVIDIA RTX 2060 Laptop", "brand": "nvidia", "level": PERF_LEVEL["mid"], "year": 2020, "vram": "6 GB", "family": "Turing"},
    {"name": "NVIDIA RTX 3060 Laptop", "brand": "nvidia", "level": PERF_LEVEL["mid"], "year": 2021, "vram": "6 GB", "family": "Ampere"},
    {"name": "NVIDIA RTX 3070 Ti Laptop", "brand": "nvidia", "level": PERF_LEVEL["upper"], "year": 2022, "vram": "8 GB", "family": "Ampere"},
    {"name": "NVIDIA RTX 4070 Laptop", "brand": "nvidia", "level": PERF_LEVEL["upper"], "year": 2023, "vram": "8 GB", "family": "Ada"},
    {"name": "NVIDIA RTX 4080 Laptop", "brand": "nvidia", "level": PERF_LEVEL["enthusiast"], "year": 2023, "vram": "12 GB", "family": "Ada"},
    {"name": "NVIDIA RTX 5090M", "brand": "nvidia", "level": PERF_LEVEL["enthusiast"], "year": 2025, "vram": "16 GB", "family": "Blackwell"},
    {"name": "AMD Radeon RX 6600M", "brand": "amd", "level": PERF_LEVEL["mid"], "year": 2021, "vram": "8 GB", "family": "RDNA 2"},
    {"name": "AMD Radeon RX 7600M XT", "brand": "amd", "level": PERF_LEVEL["upper"], "year": 2023, "vram": "8 GB", "family": "RDNA 3"},
    {"name": "AMD Radeon 780M iGPU", "brand": "amd", "level": PERF_LEVEL["entry"], "year": 2023, "vram": "UMA", "family": "RDNA 3"},
    {"name": "Intel Arc A370M", "brand": "intel_arc", "level": PERF_LEVEL["entry"], "year": 2022, "vram": "4 GB", "family": "Alchemist"},
    {"name": "Intel Arc A730M", "brand": "intel_arc", "level": PERF_LEVEL["mid"], "year": 2023, "vram": "12 GB", "family": "Alchemist"},
    {"name": "Intel Arc B580M", "brand": "intel_arc", "level": PERF_LEVEL["upper"], "year": 2025, "vram": "12 GB", "family": "Battlemage"},
]

STORAGE_PRESETS = [
    ["1 TB NVMe Gen3", "2 TB HDD"],
    ["1 TB NVMe Gen4"],
    ["2 TB NVMe Gen4", "4 TB SATA SSD"],
    ["1 TB NVMe Gen5", "2 TB NVMe Gen4"],
]

DESKTOP_PROFILES = [
    {
        "tag": "gaming_1080p",
        "label": "Gaming 1080p",
        "min_cpu": PERF_LEVEL["entry"],
        "min_gpu": PERF_LEVEL["entry"],
        "ram": "16 GB DDR4-3600",
        "storage_choice": [0, 1],
        "psu_floor": 600,
        "cooling": "torre de aire 160 mm",
        "use_cases": ["gaming", "streaming_entry"],
        "budget": "budget_entry",
        "resolution": "1080p 144 Hz",
    },
    {
        "tag": "gaming_1440p",
        "label": "Gaming 1440p",
        "min_cpu": PERF_LEVEL["mid"],
        "min_gpu": PERF_LEVEL["mid"],
        "ram": "32 GB DDR5-6000",
        "storage_choice": [1, 2],
        "psu_floor": 700,
        "cooling": "AIO 240 mm",
        "use_cases": ["gaming", "streaming", "creator_light"],
        "budget": "mid_high",
        "resolution": "1440p 165 Hz",
    },
    {
        "tag": "gaming_4k",
        "label": "Gaming 4K",
        "min_cpu": PERF_LEVEL["upper"],
        "min_gpu": PERF_LEVEL["upper"],
        "ram": "32 GB DDR5-6400",
        "storage_choice": [2, 3],
        "psu_floor": 850,
        "cooling": "AIO 360 mm",
        "use_cases": ["gaming", "streaming", "capture 4K"],
        "budget": "enthusiast",
        "resolution": "4K 120 Hz",
    },
    {
        "tag": "creator",
        "label": "Creator 4K",
        "min_cpu": PERF_LEVEL["mid"],
        "min_gpu": PERF_LEVEL["mid"],
        "ram": "64 GB DDR5-6000",
        "storage_choice": [2, 3],
        "psu_floor": 800,
        "cooling": "AIO 280 mm",
        "use_cases": ["edicion_video", "render", "color_grading"],
        "budget": "mid_high",
        "resolution": "Dual 4K",
    },
    {
        "tag": "ai_workstation",
        "label": "IA/Compute",
        "min_cpu": PERF_LEVEL["upper"],
        "min_gpu": PERF_LEVEL["enthusiast"],
        "ram": "96 GB DDR5-6400",
        "storage_choice": [3],
        "psu_floor": 1000,
        "cooling": "custom loop",
        "use_cases": ["ai_training", "simulacion"],
        "budget": "workstation",
        "resolution": "Multi-monitor",
    },
]

LAPTOP_PROFILES = [
    {
        "tag": "ultrabook",
        "label": "Ultrabook productivo",
        "min_cpu": PERF_LEVEL["entry"],
        "min_gpu": PERF_LEVEL["entry"],
        "ram": "16 GB LPDDR5",
        "storage": "1 TB NVMe Gen4",
        "display": "14\" 1920x1200 100% sRGB",
        "battery": "70 Wh",
        "weight": "1.3 kg",
        "use_cases": ["productividad", "movilidad"],
        "budget": "premium_light",
    },
    {
        "tag": "creator_laptop",
        "label": "Laptop creador 16\"",
        "min_cpu": PERF_LEVEL["mid"],
        "min_gpu": PERF_LEVEL["mid"],
        "ram": "32 GB LPDDR5X",
        "storage": "2 TB NVMe Gen4",
        "display": "16\" 2560x1600 Mini LED",
        "battery": "99 Wh",
        "weight": "2.1 kg",
        "use_cases": ["edicion_video", "fotografia"],
        "budget": "mid_high",
    },
    {
        "tag": "gaming_laptop",
        "label": "Laptop gaming 240 Hz",
        "min_cpu": PERF_LEVEL["mid"],
        "min_gpu": PERF_LEVEL["mid"],
        "ram": "32 GB DDR5",
        "storage": "1 TB NVMe Gen4",
        "display": "16\" 2560x1600 240 Hz",
        "battery": "90 Wh",
        "weight": "2.4 kg",
        "use_cases": ["gaming", "streaming"],
        "budget": "mid_high",
    },
    {
        "tag": "workstation_laptop",
        "label": "Workstation móvil",
        "min_cpu": PERF_LEVEL["upper"],
        "min_gpu": PERF_LEVEL["upper"],
        "ram": "64 GB DDR5",
        "storage": "4 TB NVMe Gen4",
        "display": "17\" 3840x2400 HDR",
        "battery": "99 Wh",
        "weight": "2.8 kg",
        "use_cases": ["cad", "simulacion", "ai_inference"],
        "budget": "workstation",
    },
]

MOTHERBOARDS = {
    "LGA1151": ["ASUS Z270-A", "MSI Z390 Tomahawk", "Gigabyte Z370 Aorus"],
    "LGA1200": ["ASUS Z490-E", "MSI MPG Z590", "Gigabyte Z590 Vision"],
    "LGA1700": ["ASUS TUF B760-PLUS", "MSI Z790 Carbon", "Gigabyte Z790 Aero G"],
    "LGA1851": ["ASUS Z890 ProArt", "MSI Z890 ACE", "Gigabyte Z890 Aorus Master"],
    "AM4": ["MSI B450 Tomahawk", "ASUS X570 TUF", "Gigabyte B550 Aorus Pro"],
    "AM5": ["ASUS B650E-F", "MSI X670E Carbon", "Gigabyte B650 Aorus Elite"],
}

CASES = ["NZXT H5 Flow", "Fractal North", "Corsair 4000D Airflow", "Lian Li O11 Air Mini", "Hyte Y70 Touch"]
COOLING_NOTES = {
    "torre de aire 160 mm": "Noctua NH-D15 o similar",
    "AIO 240 mm": "Corsair H100i Elite",
    "AIO 280 mm": "NZXT Kraken 280",
    "AIO 360 mm": "Lian Li Galahad 360",
    "custom loop": "Loop CPU+GPU con radiador 360+240",
}

DISPLAY_PORTS = [
    "HDMI 2.1 + 2x DisplayPort 1.4a",
    "2x DisplayPort 2.1 + USB-C alt mode",
    "HDMI 2.1 + USB4",
]

PORT_OPTIONS = [
    "2x USB-C 4, 2x USB-A 3.2, HDMI 2.1, SD Express",
    "2x Thunderbolt 4, 2x USB-A, RJ45, HDMI 2.1",
    "USB4 + USB-A + Mini DisplayPort + HDMI",
]

CHASSIS = ["aluminio CNC", "magnesio reforzado", "polimero con refuerzo de fibra"]


def _pick_motherboard(socket: str) -> str:
    options = MOTHERBOARDS.get(socket, ["OEM board"])
    return random.choice(options)


def _pick_storage(profile: Dict[str, object]) -> List[str]:
    choices = profile["storage_choice"] if "storage_choice" in profile else [0]
    idx = random.choice(choices)
    return STORAGE_PRESETS[idx]


def _build_aliases(prefix: str, cpu: str, gpu: str, tag: str, year: int) -> List[str]:
    base = [
        f"{prefix} {tag} {cpu.lower()}",
        f"{prefix} {gpu.lower()}",
        f"{prefix} {year}",
        f"build {cpu.lower()} {gpu.lower()}",
    ]
    return sorted({alias.replace("  ", " ").strip() for alias in base})


def _desktop_entry(idx: int, cpu: Dict[str, object], gpu: Dict[str, object], profile: Dict[str, object]) -> Dict[str, object]:
    storage = _pick_storage(profile)
    release_year = max(int(cpu["year"]), int(gpu["year"]))
    psu = max(profile["psu_floor"], int(gpu["power"]) + 250)
    motherboard = _pick_motherboard(cpu["socket"])
    case = random.choice(CASES)
    cooling_name = profile["cooling"]
    cooling_detail = COOLING_NOTES.get(cooling_name, cooling_name)
    components = [
        f"CPU: {cpu['name']} ({cpu['cores']}, {cpu['series']})",
        f"GPU: {gpu['name']} {gpu['vram']}",
        f"Motherboard: {motherboard}",
        f"RAM: {profile['ram']}",
        f"Storage: {', '.join(storage)}",
        f"PSU: {psu}W 80+ Gold",
        f"Cooling: {cooling_detail}",
        f"Case: {case} con flujo optimizado",
    ]
    title = f"PC {profile['label']} {gpu['name']} + {cpu['name']}"
    tags = {
        "desktop",
        profile["tag"],
        profile["budget"],
        cpu["brand"],
        cpu["socket"].lower(),
        gpu["brand"],
        gpu["family"].lower().replace(" ", "_"),
        f"{release_year}",
    }
    if gpu["brand"].startswith("intel"):
        tags.add("intel_arc")
    if "RTX" in gpu["name"]:
        tags.add("rtx")
    if "RX" in gpu["name"]:
        tags.add("radeon")
    tags.add(profile["resolution"].split()[0].lower())
    summary = (
        f"Pensado para {profile['label']} con estabilidad en {profile['resolution']} y margen térmico gracias a {cooling_name}. "
        "Incluye ruta de actualización hacia futuras GPU PCIe 5.0 y soporte para DDR5 de mayor frecuencia."
    )
    entry = {
        "id": f"desktop_{idx:04d}",
        "type": "desktop",
        "title": title,
        "release_window": release_year,
        "cpu": cpu["name"],
        "gpu": gpu["name"],
        "ram": profile["ram"],
        "storage": storage,
        "motherboard": motherboard,
        "psu": f"{psu}W 80+ Gold",
        "cooling": cooling_name,
        "case": case,
        "use_cases": profile["use_cases"],
        "resolution": profile["resolution"],
        "budget_tier": profile["budget"],
        "components": components,
        "summary": summary,
        "aliases": _build_aliases("pc", cpu["name"], gpu["name"], profile["tag"], release_year),
        "tags": sorted(tags),
        "recommended_os": "Windows 11 Pro",
    }
    return entry


def _laptop_entry(idx: int, cpu: Dict[str, object], gpu: Dict[str, object], profile: Dict[str, object]) -> Dict[str, object]:
    release_year = max(int(cpu["year"]), int(gpu["year"]))
    components = [
        f"CPU: {cpu['name']} ({cpu['cores']})",
        f"GPU: {gpu['name']} {gpu['vram']}",
        f"RAM: {profile['ram']}",
        f"Storage: {profile['storage']}",
        f"Display: {profile['display']}",
        f"Puertos: {random.choice(PORT_OPTIONS)}",
        f"Chasis: {random.choice(CHASSIS)}",
        f"Red: Wi-Fi 7 + BT 5.4",
    ]
    tags = {
        "laptop",
        profile["tag"],
        profile["budget"],
        cpu["brand"],
        gpu["brand"],
        f"{release_year}",
    }
    if "Arc" in gpu["name"]:
        tags.add("intel_arc")
    if "RTX" in gpu["name"]:
        tags.add("rtx")
    title = f"{profile['label']} {gpu['name']} + {cpu['name']}"
    summary = (
        f"Portátil enfocada en {', '.join(profile['use_cases'])} con pantalla {profile['display']} y batería {profile['battery']}. "
        "Incluye modo silencioso y perfiles de ventilación para prolongar la vida útil."
    )
    entry = {
        "id": f"laptop_{idx:04d}",
        "type": "laptop",
        "title": title,
        "release_window": release_year,
        "cpu": cpu["name"],
        "gpu": gpu["name"],
        "ram": profile["ram"],
        "storage": profile["storage"],
        "display": profile["display"],
        "battery": profile["battery"],
        "weight": profile["weight"],
        "use_cases": profile["use_cases"],
        "budget_tier": profile["budget"],
        "components": components,
        "summary": summary,
        "aliases": _build_aliases("laptop", cpu["name"], gpu["name"], profile["tag"], release_year),
        "tags": sorted(tags),
        "recommended_os": "Windows 11 Pro",
    }
    return entry


def generate_dataset(target_desktops: int = 1400, target_laptops: int = 900) -> List[Dict[str, object]]:
    dataset: List[Dict[str, object]] = []
    desktop_idx = 1
    laptop_idx = 1

    for profile in DESKTOP_PROFILES:
        for cpu in DESKTOP_CPUS:
            if cpu["level"] < profile["min_cpu"]:
                continue
            for gpu in DESKTOP_GPUS:
                if gpu["level"] < profile["min_gpu"]:
                    continue
                entry = _desktop_entry(desktop_idx, cpu, gpu, profile)
                dataset.append(entry)
                desktop_idx += 1
                if desktop_idx > target_desktops:
                    break
            if desktop_idx > target_desktops:
                break
        if desktop_idx > target_desktops:
            break

    for profile in LAPTOP_PROFILES:
        for cpu in LAPTOP_CPUS:
            if cpu["level"] < profile["min_cpu"]:
                continue
            for gpu in LAPTOP_GPUS:
                if gpu["level"] < profile["min_gpu"]:
                    continue
                entry = _laptop_entry(laptop_idx, cpu, gpu, profile)
                dataset.append(entry)
                laptop_idx += 1
                if laptop_idx > target_laptops:
                    break
            if laptop_idx > target_laptops:
                break
        if laptop_idx > target_laptops:
            break

    # If loops exited early (due to thresholds), broaden selection by relaxing filters.
    while desktop_idx <= target_desktops:
        cpu = random.choice(DESKTOP_CPUS)
        gpu = random.choice(DESKTOP_GPUS)
        profile = random.choice(DESKTOP_PROFILES)
        entry = _desktop_entry(desktop_idx, cpu, gpu, profile)
        dataset.append(entry)
        desktop_idx += 1

    while laptop_idx <= target_laptops:
        cpu = random.choice(LAPTOP_CPUS)
        gpu = random.choice(LAPTOP_GPUS)
        profile = random.choice(LAPTOP_PROFILES)
        entry = _laptop_entry(laptop_idx, cpu, gpu, profile)
        dataset.append(entry)
        laptop_idx += 1

    return dataset


def main() -> None:
    dataset = generate_dataset()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as fh:
        json.dump(dataset, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {len(dataset)} hardware combinations to {DATA_PATH}")


if __name__ == "__main__":
    main()
