"""Utility to build the curated recipe dataset with >300 entries.

Regenerates data/curated_recipes.json deterministically so the assistant can
answer cooking prompts without hitting external APIs.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "curated_recipes.json"

random.seed(42)

CUISINES = [
    {
        "name": "mexicana",
        "slug": "mex",
        "aliases": ["mexico", "yucatan", "sonora"],
        "spice_mix": "achiote, comino tostado y paprika ahumada",
        "aromatics": "ajo picado y cebolla blanca",
        "acid": "jugo de limon",
        "sauce": "salsa verde tatemada",
        "garnish": "cilantro picado y rabanos fileteados",
        "crunch": "pepitas tostadas",
        "base_options": ["tacos", "bowl_cereal", "cazuela_ligera", "ensalada_templada"],
    },
    {
        "name": "mediterranea",
        "slug": "med",
        "aliases": ["grecia", "levantina", "med"],
        "spice_mix": "zaatar casero con oregano y sumac",
        "aromatics": "ajo rostizado y chalotas",
        "acid": "limon amarillo",
        "sauce": "labneh con aceite de oliva",
        "garnish": "perejil, pepita de granada y aceite extra virgen",
        "crunch": "almendras tostadas",
        "base_options": ["bowl_cereal", "wrap_integral", "sopa_ligera", "ensalada_templada"],
    },
    {
        "name": "asiatica",
        "slug": "asia",
        "aliases": ["fusion asiatica", "seul", "tokio"],
        "spice_mix": "jengibre rallado, salsa de soya ligera y gochugaru",
        "aromatics": "ajo, cebollin y aceite de sesamo",
        "acid": "vinagre de arroz",
        "sauce": "miso ligero con miel",
        "garnish": "ajonjoli tostado y pepino encurtido",
        "crunch": "cacahuate tostado",
        "base_options": ["salteado_wok", "bowl_cereal", "curry_express", "sopa_ligera"],
    },
    {
        "name": "peruana",
        "slug": "peru",
        "aliases": ["andina", "nikkei", "lima"],
        "spice_mix": "aji amarillo, comino y huacatay",
        "aromatics": "ajo, cebolla roja y culantro",
        "acid": "limon sutil",
        "sauce": "leche de tigre cremosa",
        "garnish": "cancha serrana y brotes tiernos",
        "crunch": "maiz chulpe",
        "base_options": ["cazuela_ligera", "bowl_cereal", "salteado_wok", "sopa_ligera"],
    },
    {
        "name": "arabe",
        "slug": "arab",
        "aliases": ["medio oriente", "levant"],
        "spice_mix": "baharat, canela y cardamomo",
        "aromatics": "ajo, cebolla caramelo y menta",
        "acid": "limon con sumac",
        "sauce": "tahini con yogurt",
        "garnish": "perejil, pepitas y aceite de oliva",
        "crunch": "garbanzos crujientes",
        "base_options": ["wrap_integral", "bowl_cereal", "cazuela_ligera", "ensalada_templada"],
    },
    {
        "name": "india",
        "slug": "india",
        "aliases": ["masala", "delhi"],
        "spice_mix": "garam masala, curcuma y cilantro en polvo",
        "aromatics": "ajo, jengibre y cebolla dorada",
        "acid": "yogurt natural",
        "sauce": "pure de tomate especiado",
        "garnish": "cilantro, coco rallado y ghee",
        "crunch": "lentejas crujientes",
        "base_options": ["curry_express", "bowl_cereal", "sopa_ligera", "cazuela_ligera"],
    },
    {
        "name": "caribena",
        "slug": "caribe",
        "aliases": ["caribe", "tropical"],
        "spice_mix": "achiote, pimienta dulce y allspice",
        "aromatics": "ajo, cebolla morada y pimiento",
        "acid": "naranja agria",
        "sauce": "aderezo de coco y lima",
        "garnish": "hierbabuena y coco tostado",
        "crunch": "platanitos horneados",
        "base_options": ["tacos", "bowl_cereal", "ensalada_templada", "curry_express"],
    },
    {
        "name": "veg_fusion",
        "slug": "veg",
        "aliases": ["plant based", "verde"],
        "spice_mix": "miso blanco, citricos y pimienta rosa",
        "aromatics": "ajo asado y poro",
        "acid": "vinagre de sidra",
        "sauce": "crema de anacardo y limon",
        "garnish": "brotes, semillas y aceite de aguacate",
        "crunch": "quinoa inflada",
        "base_options": ["bowl_cereal", "ensalada_templada", "wrap_integral", "pasta_onepot"],
    },
]

BASE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "tacos": {
        "title": "tacos de plancha",
        "slug": "tacos",
        "alias": "tacos caseros",
        "carb": "tortillas de maiz",
        "carb_amount": "8 tortillas",
        "veg": "pimientos tricolor, calabacin y cebolla morada",
        "veg_ratio": "2 tazas",
        "equipment": "un sarten de hierro",
        "fat": "aceite de aguacate",
        "technique_line": "saltea a fuego alto",
        "liquid": "chorro de caldo ligero",
        "finish": "rellena cada tortilla y dobla para atrapar los jugos",
        "side": "ensalada crujiente de nopal",
        "meal_type": "cena",
        "base_time": 25,
        "difficulty": "media",
        "equipment_tag": "sarten",
        "servings": 3,
    },
    "bowl_cereal": {
        "title": "bowl integral",
        "slug": "grain_bowl",
        "alias": "bowl templado",
        "carb": "quinoa y farro cocidos",
        "carb_amount": "2 tazas",
        "veg": "espinaca baby, pepino y zanahoria en listones",
        "veg_ratio": "3 tazas",
        "equipment": "una olla amplia",
        "fat": "aceite de oliva",
        "technique_line": "saltea suave y desglasa",
        "liquid": "chorro de caldo vegetal",
        "finish": "arma tazones por capas",
        "side": "gajos de limon asado",
        "meal_type": "comida",
        "base_time": 28,
        "difficulty": "media",
        "equipment_tag": "olla",
        "servings": 4,
    },
    "salteado_wok": {
        "title": "salteado crujiente",
        "slug": "stir_fry",
        "alias": "wok rapido",
        "carb": "fideos de arroz o soba",
        "carb_amount": "300 g",
        "veg": "brocoli, zanahoria y edamame",
        "veg_ratio": "3 tazas",
        "equipment": "un wok caliente",
        "fat": "aceite de sesamo",
        "technique_line": "saltea por tandas",
        "liquid": "salmuera ligera de soya",
        "finish": "mezcla con los fideos y saltea 1 minuto",
        "side": "pepino encurtido",
        "meal_type": "comida",
        "base_time": 22,
        "difficulty": "facil",
        "equipment_tag": "wok",
        "servings": 3,
    },
    "wrap_integral": {
        "title": "wrap tibio",
        "slug": "wrap",
        "alias": "rollo integral",
        "carb": "pan pita integral o tortillas de trigo",
        "carb_amount": "4 piezas",
        "veg": "lechuga romana, pepino, jitomate y col rallada",
        "veg_ratio": "3 tazas",
        "equipment": "plancha o sarten antiadherente",
        "fat": "aceite de oliva",
        "technique_line": "dora los rellenos y calienta el pan",
        "liquid": "cucharada de aderezo ligero",
        "finish": "rellena, enrolla y sella en la plancha",
        "side": "ensalada de hierbas",
        "meal_type": "comida ligera",
        "base_time": 20,
        "difficulty": "facil",
        "equipment_tag": "plancha",
        "servings": 2,
    },
    "sopa_ligera": {
        "title": "sopa dorada",
        "slug": "sopa",
        "alias": "caldo nutritivo",
        "carb": "granos de elote o arroz jazmin",
        "carb_amount": "1 taza",
        "veg": "apio, zanahoria y poro",
        "veg_ratio": "2 tazas",
        "equipment": "olla profunda",
        "fat": "ghee o aceite de oliva",
        "technique_line": "sofrie y desglasa",
        "liquid": "caldo casero",
        "finish": "sirve caliente con topping fresco",
        "side": "tostadas horneadas",
        "meal_type": "comida",
        "base_time": 30,
        "difficulty": "media",
        "equipment_tag": "olla",
        "servings": 4,
    },
    "curry_express": {
        "title": "curry express",
        "slug": "curry",
        "alias": "guiso especiado",
        "carb": "arroz basmati o coliflor rallada",
        "carb_amount": "2 tazas",
        "veg": "calabacin, chicharo y cebolla",
        "veg_ratio": "2.5 tazas",
        "equipment": "cacerola profunda",
        "fat": "aceite de coco",
        "technique_line": "sofrie las especias hasta perfumar",
        "liquid": "leche de coco ligera",
        "finish": "espesa y sirve con el arroz",
        "side": "pickles rapidos",
        "meal_type": "cena",
        "base_time": 26,
        "difficulty": "media",
        "equipment_tag": "olla",
        "servings": 3,
    },
    "ensalada_templada": {
        "title": "ensalada templada",
        "slug": "ensalada",
        "alias": "ensalada tibia",
        "carb": "mix de hojas baby y granos",
        "carb_amount": "3 tazas",
        "veg": "betabel asado, pepino y brocoli",
        "veg_ratio": "3 tazas",
        "equipment": "charola y sarten",
        "fat": "aceite de oliva",
        "technique_line": "asa las verduras y saltea el acabado",
        "liquid": "vinagreta de citricos",
        "finish": "monta en capas y baña con la vinagreta",
        "side": "pan de masa madre",
        "meal_type": "comida ligera",
        "base_time": 24,
        "difficulty": "facil",
        "equipment_tag": "horno",
        "servings": 3,
    },
    "pasta_onepot": {
        "title": "pasta one-pot",
        "slug": "pasta",
        "alias": "pasta cremosa",
        "carb": "pasta corta integral",
        "carb_amount": "320 g",
        "veg": "col rizada, tomate cherry y ajo",
        "veg_ratio": "2.5 tazas",
        "equipment": "olla ancha",
        "fat": "aceite de oliva",
        "technique_line": "dora y cuece en la misma olla",
        "liquid": "caldo vegetal concentrado",
        "finish": "reduce hasta que la salsa se adhiera",
        "side": "ensalada verde",
        "meal_type": "cena",
        "base_time": 27,
        "difficulty": "media",
        "equipment_tag": "olla",
        "servings": 4,
    },
    "cazuela_ligera": {
        "title": "cazuela ligera",
        "slug": "cazuela",
        "alias": "guiso al horno",
        "carb": "camote en cubos y garbanzo",
        "carb_amount": "3 tazas",
        "veg": "espinaca, jitomate y cebolla",
        "veg_ratio": "3 tazas",
        "equipment": "cazuela u olla apta para horno",
        "fat": "aceite de oliva",
        "technique_line": "sella en estufa y termina en horno",
        "liquid": "caldo espeso con especias",
        "finish": "gratina ligero y sirve en la misma cazuela",
        "side": "ensalada de hojas amargas",
        "meal_type": "comida",
        "base_time": 35,
        "difficulty": "media",
        "equipment_tag": "horno",
        "servings": 4,
    },
}

PROTEINS: List[Dict[str, str]] = [
    {
        "name": "pollo",
        "slug": "pollo",
        "display": "pollo al limon",
        "cut": "en tiras delgadas",
        "quantity": "450 g",
        "prep": "seca las tiras de pollo y marina con aceite, sal y pimienta",
        "diet": "tradicional",
        "aliases": ["pollo salteado", "tiras de pollo"],
        "lean_swap": "pavo magro",
        "texture_hint": "queda dorado por fuera y jugoso por dentro",
        "tags": ["pollo", "ave", "alto_proteina"],
    },
    {
        "name": "res",
        "slug": "res",
        "display": "res magra",
        "cut": "en laminas finas",
        "quantity": "400 g",
        "prep": "mezcla la res con salsa de soya ligera y maicena",
        "diet": "tradicional",
        "aliases": ["carne de res", "res salteada"],
        "lean_swap": "solomillo de cerdo",
        "texture_hint": "se dora rapido sin secarse",
        "tags": ["res", "carne_roja", "alto_proteina"],
    },
    {
        "name": "cerdo",
        "slug": "cerdo",
        "display": "lomo de cerdo",
        "cut": "en cubos",
        "quantity": "420 g",
        "prep": "marina con ajo, comino y miel",
        "diet": "tradicional",
        "aliases": ["cerdo glaseado", "lomo de cerdo"],
        "lean_swap": "pollo deshebrado",
        "texture_hint": "queda caramelizado",
        "tags": ["cerdo", "proteina_media"],
    },
    {
        "name": "garbanzos",
        "slug": "garbanzo",
        "display": "garbanzos crujientes",
        "cut": "escurridos",
        "quantity": "2 tazas",
        "prep": "seca los garbanzos y mezcla con aceite y pimenton",
        "diet": "vegana",
        "aliases": ["garbanzos al horno", "proteina vegetal garbanzo"],
        "lean_swap": "lentejas",
        "texture_hint": "quedan crujientes por fuera",
        "tags": ["garbanzos", "vegana", "plant_based"],
    },
    {
        "name": "lentejas",
        "slug": "lenteja",
        "display": "lentejas especiadas",
        "cut": "cocidas",
        "quantity": "2 tazas",
        "prep": "hierve las lentejas con laurel y escurre",
        "diet": "vegana",
        "aliases": ["lentejas guisadas", "proteina vegetal lenteja"],
        "lean_swap": "garbanzos",
        "texture_hint": "se integran cremosa mente",
        "tags": ["lentejas", "vegana", "plant_based"],
    },
    {
        "name": "tofu",
        "slug": "tofu",
        "display": "tofu firme",
        "cut": "en cubos grandes",
        "quantity": "400 g",
        "prep": "prensa el tofu y marina con salsa tamari",
        "diet": "vegana",
        "aliases": ["tofu dorado", "cubos de tofu"],
        "lean_swap": "tempeh",
        "texture_hint": "queda crujiente por fuera",
        "tags": ["tofu", "vegana", "plant_based", "alto_proteina"],
    },
    {
        "name": "salmon",
        "slug": "salmon",
        "display": "salmon sellado",
        "cut": "en cubos",
        "quantity": "380 g",
        "prep": "retira la piel y marina con miel y mostaza",
        "diet": "pescetariana",
        "aliases": ["salmon al sarten", "cubos de salmon"],
        "lean_swap": "trucha",
        "texture_hint": "queda dorado y mantequilloso",
        "tags": ["salmon", "pescado", "omega"],
    },
    {
        "name": "camarones",
        "slug": "camaron",
        "display": "camarones salteados",
        "cut": "limpios",
        "quantity": "450 g",
        "prep": "marina con ajo, limon y paprika",
        "diet": "pescetariana",
        "aliases": ["camarones picantes", "salteado de camaron"],
        "lean_swap": "calamar",
        "texture_hint": "se cocinan en minutos",
        "tags": ["camarones", "mariscos"],
    },
    {
        "name": "hongos",
        "slug": "hongos",
        "display": "hongos portobello",
        "cut": "en laminas gruesas",
        "quantity": "450 g",
        "prep": "marina con salsa de soya, balsamico y ajo",
        "diet": "vegana",
        "aliases": ["portobello asado", "hongos a la parrilla"],
        "lean_swap": "setas king oyster",
        "texture_hint": " toman textura carnosa",
        "tags": ["hongos", "vegana", "plant_based"],
    },
    {
        "name": "coliflor",
        "slug": "coliflor",
        "display": "coliflor rostizada",
        "cut": "en floretes",
        "quantity": "1 coliflor",
        "prep": "mezcla con aceite y especias",
        "diet": "vegana",
        "aliases": ["coliflor al horno", "floretes especiados"],
        "lean_swap": "brocoli",
        "texture_hint": "queda caramelizada",
        "tags": ["coliflor", "vegana", "plant_based", "bajo_carb"],
    },
]

MEAL_KEYWORDS = {
    "desayuno": "desayuno",
    "comida": "comida",
    "almuerzo": "comida",
    "cena": "cena",
    "snack": "snack",
    "meriendas": "snack",
}


def _slugify(text: str) -> str:
    return text.lower().replace(" ", "_").replace("-", "_")


def build_recipe(index: int, cuisine: Dict[str, str], base_key: str, protein: Dict[str, str]) -> Dict[str, object]:
    base = BASE_TEMPLATES[base_key]
    name = f"{base['title']} de {protein['display']} estilo {cuisine['name']}"
    recipe_id = f"recipe_{index:03d}_{cuisine['slug']}_{base['slug']}_{protein['slug']}"
    alias_tokens = {
        name.lower(),
        f"{base['alias']} {protein['name']}",
        f"{protein['name']} {cuisine['name']}",
        f"{base['alias']} {cuisine['name']}",
        f"{protein['display']} {base['title']}",
    }
    alias_tokens.update({f"{token} {base['slug']}" for token in cuisine['aliases']})
    alias_tokens.update({f"{base['title']} {token}" for token in protein['aliases']})
    aliases = sorted({alias.strip() for alias in alias_tokens if len(alias.strip().split()) >= 2})

    time_minutes = base["base_time"]
    servings = base["servings"]
    tags = set(
        [
            cuisine["name"],
            cuisine["slug"],
            base["slug"],
            protein["name"],
            protein["diet"],
            base["meal_type"],
            base["equipment_tag"],
        ]
    )
    tags.update(protein["tags"])
    tags.update(alias.replace(" ", "_") for alias in cuisine["aliases"])
    tags.update(alias.replace(" ", "_") for alias in protein["aliases"])
    tag_list = sorted(tags)

    ingredients = [
        f"{protein['quantity']} de {protein['name']} {protein['cut']}",
        f"{base['carb_amount']} de {base['carb']}",
        f"{base['veg_ratio']} de {base['veg']}",
        f"Mezcla de especias: {cuisine['spice_mix']}",
        f"Base aromatica: {cuisine['aromatics']}",
        f"Toque acido: {cuisine['acid']}",
        f"Salsa final: {cuisine['sauce']}",
        f"Crunch controlado: {cuisine['crunch']}",
        f"Garnish: {cuisine['garnish']}",
    ]
    if base.get("liquid"):
        ingredients.append(f"Liquido: {base['liquid']}")

    steps = [
        f"Marina la proteina: {protein['prep']} y espolvorea {cuisine['spice_mix']} con un toque de {cuisine['acid']}.",
        f"Sella en {base['equipment']}: agrega {base['fat']} y {base['technique_line']} junto con {cuisine['aromatics']} hasta que {protein['texture_hint']}.",
        f"Integra las verduras: suma {base['veg']} y convierte la mezcla en {base['alias']} usando {base.get('liquid', 'sus propios jugos')}.",
        f"Monta y sirve: {base['finish']}, agrega {cuisine['sauce']}, {cuisine['garnish']} y acompana con {base['side']}.",
    ]

    tips = [
        f"Puedes cambiar {protein['name']} por {protein['lean_swap']} sin alterar tiempos.",
        f"Agrega {cuisine['crunch']} justo antes de servir para mantener textura y {cuisine['acid']} si deseas mas frescura.",
    ]

    detail = {
        "id": recipe_id,
        "name": name,
        "aliases": aliases,
        "meal_type": base["meal_type"],
        "cuisine": cuisine["name"],
        "protein": protein["name"],
        "diet": protein["diet"],
        "difficulty": base["difficulty"],
        "time_minutes": time_minutes,
        "servings": servings,
        "ingredients": ingredients,
        "steps": steps,
        "tips": tips,
        "tags": tag_list,
        "equipment": base["equipment_tag"],
    }
    return detail


def build_dataset(target_count: int = 320) -> List[Dict[str, object]]:
    recipes: List[Dict[str, object]] = []
    index = 1
    for cuisine in CUISINES:
        for base_key in cuisine["base_options"]:
            for protein in PROTEINS:
                recipes.append(build_recipe(index, cuisine, base_key, protein))
                index += 1
                if index > target_count:
                    return recipes
    return recipes


def main() -> None:
    recipes = build_dataset()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as fh:
        json.dump(recipes, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {len(recipes)} recipes to {DATA_PATH}")


if __name__ == "__main__":
    main()
