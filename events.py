# events.py — dilemas/eventos aleatórios

import random
from dataclasses import dataclass
from typing import Callable, Dict

@dataclass
class Event:
    title: str
    desc: str
    options: Dict[str, Callable]  # {"A": func(state), "B": func(state)}

def get_random_event(state) -> Event:
    """
    state: objeto com atributos .money, .happiness, .inflation, .traffic
    """
    def a1(s):
        """Ignorar (morador irritado)"""
        s.happiness = max(0, s.happiness - 8)

    def b1(s):
        """Tentar conter preços (campanha)"""
        s.money = max(0, s.money - 300)
        s.inflation = max(0, s.inflation - 3)

    def a2(s):
        """Aprovar expansão industrial"""
        s.money += 200
        s.inflation += 2

    def b2(s):
        """Negar e focar bem-estar"""
        s.happiness = min(100, s.happiness + 5)

    def a3(s):
        """Ignorar trânsito"""
        s.happiness = max(0, s.happiness - 6)
        s.traffic = min(100, s.traffic + 8)

    def b3(s):
        """Investir emergencialmente"""
        s.money = max(0, s.money - 500)
        s.traffic = max(0, s.traffic - 10)

    pool = [
        Event(
            "Inflação preocupa moradores",
            "“Os preços estão subindo demais!”",
            {"A": a1, "B": b1}
        ),
        Event(
            "Proposta de expansão industrial",
            "Um grupo quer ampliar fábricas rapidamente.",
            {"A": a2, "B": b2}
        ),
        Event(
            "Colapso do Trânsito",
            "Engarrafamentos aumentaram nas últimas semanas.",
            {"A": a3, "B": b3}
        ),
    ]
    return random.choice(pool)
