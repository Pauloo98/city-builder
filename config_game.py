# config_game.py
# Catálogo, custos, ícones e parâmetros de balanceamento

# ===== Catálogo de construções =====
CATALOG = {
    # Residencial
    "Casa":         {"w":1, "h":1, "tile":"residential", "category":"Residencial"},
    "Condomínio":   {"w":3, "h":1, "tile":"residential", "category":"Residencial"},
    # Comercial
    "Loja":         {"w":1, "h":1, "tile":"commercial",  "category":"Comercial"},
    "Fazenda":      {"w":2, "h":2, "tile":"farm",        "category":"Comercial"},
    # Industrial
    "Fábrica":      {"w":1, "h":1, "tile":"industrial",  "category":"Industrial"},
    "Usina":        {"w":1, "h":1, "tile":"utility",     "category":"Industrial"},
    "ETA (Água)":   {"w":2, "h":2, "tile":"water_plant", "category":"Industrial"},
    # Serviços
    "Universidade": {"w":3, "h":2, "tile":"university",  "category":"Serviços"},
    "Parque":       {"w":1, "h":1, "tile":"park",        "category":"Serviços"},
    "Prefeitura":   {"w":3, "h":2, "tile":"city_hall",   "category":"Serviços"},
    "Banco Central":{"w":3, "h":2, "tile":"central_bank","category":"Serviços", "requires":["Prefeitura"]},
    "Delegacia":    {"w":2, "h":2, "tile":"police",      "category":"Serviços"},
    "Hospital":     {"w":2, "h":2, "tile":"hospital",    "category":"Serviços"},
    "Rua":          {"w":1, "h":1, "tile":"road",        "category":"Serviços"},
    # Penalidade dinâmica (não aparece no menu)
    "Favela":       {"w":1, "h":1, "tile":"blight",      "category":"Serviços"},
}

BUILD_EFFECTS = {
    "Casa":          {"money": -100},
    "Condomínio":    {"money": -280},
    "Loja":          {"money": -200},
    "Fazenda":       {"money": -220},
    "Fábrica":       {"money": -300, "happiness": -2, "traffic": +2},
    "Usina":         {"money": -350},
    "ETA (Água)":    {"money": -380},
    "Universidade":  {"money": -500, "happiness": +2},
    "Parque":        {"money": -120, "happiness": +2},
    "Prefeitura":    {"money": -800},
    "Banco Central": {"money": -2000},
    "Delegacia":     {"money": -450},
    "Hospital":      {"money": -600},
    "Rua":           {"money": -20, "traffic": +1},
}

CATEGORY_MENU = [
    ("Residencial", "cat_res"),
    ("Comercial",   "cat_com"),
    ("Industrial",  "cat_ind"),
    ("Serviços",    "cat_srv"),
]

SUBMENU_ITEMS = {
    "cat_res": ["Casa", "Condomínio"],
    "cat_com": ["Loja", "Fazenda"],
    "cat_ind": ["Fábrica", "Usina", "ETA (Água)"],
    "cat_srv": ["Prefeitura", "Banco Central", "Universidade", "Delegacia", "Hospital", "Rua", "Parque"],
}

UI_ITEM_ICON = {
    "Casa": "casa",
    "Condomínio": "condominio",
    "Loja": "loja",
    "Fazenda": "farm",
    "Fábrica": "fabrica",
    "Usina": "usina",
    "ETA (Água)": "water_plant",
    "Universidade": "services",
    "Parque": "parque",
    "Prefeitura": "city_hall",
    "Banco Central": "central_bank",
    "Delegacia": "police",
    "Hospital": "hospital",
    "Rua": "road",
}

# ===== Balanceamento =====
BASE_UNIT_VALUE = 2.0
MIN_WITHDRAW_THRESHOLD = 50.0
WITHDRAW_COOLDOWN_S = 30
PARTICIPATION_ADULT = 0.70
PARTICIPATION_ELDER = 0.10

JOBS_PER = {"commercial": 4, "industrial": 8, "farm": 3}
CAP_PER  = {"commercial": 200, "industrial": 300, "farm": 120}

PROD_POWER_PER = {"utility": 40}
PROD_WATER_PER = {"water_plant": 40}

CONS_POWER_PER_DAY = {
    "residential": 0.4, "commercial": 0.6, "industrial": 1.5, "farm": 0.4,
    "university": 1.0, "park": 0.0, "city_hall": 0.4, "central_bank": 0.6,
    "police": 0.6, "hospital": 1.2,
}
CONS_WATER_PER_DAY = {
    "residential": 0.6, "commercial": 0.3, "industrial": 0.8, "farm": 1.2,
    "university": 0.7, "park": 0.1, "city_hall": 0.2, "central_bank": 0.3,
    "police": 0.3, "hospital": 1.0,
}

ROAD_ONEOFF_POWER = 0.05
ROAD_ONEOFF_WATER = 0.05
ONEOFF_DECAY_PER_HOUR = 0.5

UPKEEP_PER_MIN = {
    "road": lambda roads: (roads // 10) * 1,
    "central_bank": 2,
    "university": 1,
    "police": 1,
    "hospital": 1,
    "water_plant": 1,
}

TOOLTIPS = {
    "money":      "Dinheiro.",
    "people":     "População total.",
    "smile":      "Felicidade geral (passe o mouse para ver fatores).",
    "inflation":  "Inflação (impacta o saque).",
    "literacy":   "Alfabetização (aumenta lucro de comércios/serviços).",
    "crime":      "Criminalidade (reduz faturamento; Delegacia reduz).",
    "health":     "Saúde da população (Hospital melhora).",
    "datetime":   "Data/horário do jogo.",
    "bolt":       "Energia (capacidade vs consumo).",
    "water":      "Água (capacidade vs consumo).",
    "withdraw":   "Sacar receita acumulada (mínimo, cooldown, inflação).",
    "auto_tax":   "Saque automático diário (−2% de eficiência).",
    "pause":      "Pausar/Retomar.",
}
