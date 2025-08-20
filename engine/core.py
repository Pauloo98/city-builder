import random
import time
import sys

# ==========================
# CONFIGURAÇÕES BÁSICAS
# ==========================
GRID_SIZE = 20
DAYS_IN_MONTH = 30
MONTHS_IN_YEAR = 12

# ==========================
# CLASSES DO JOGO
# ==========================

class GameTime:
    def __init__(self):
        self.day = 1
        self.month = 1
        self.year = 1
        self.hour = 8
        self.paused = False
        self.speed = 1

    def tick(self):
        if self.paused:
            return
        self.hour += self.speed
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
        while self.day > DAYS_IN_MONTH:
            self.day = 1
            self.month += 1
        while self.month > MONTHS_IN_YEAR:
            self.month = 1
            self.year += 1

    def date_str(self):
        return f"{self.day:02d}/{self.month:02d}/{self.year} - {self.hour:02d}:00"


class City:
    def __init__(self):
        self.money = 1000
        self.happiness = 70
        self.inflation_pressure = 0
        self.unemployment = 10
        self.education = 0
        self.industrialization = 0
        self.transport = {"traffic": 0, "public": False, "taxi": False, "bike": False}
        self.grid = [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.time = GameTime()
        self.dilemmas = []
        self.monthly_report_due = False

    def show_stats(self):
        print("\n=== STATUS DA CIDADE ===")
        print(f"Data: {self.time.date_str()}")
        print(f"Dinheiro: ${self.money}")
        print(f"Felicidade: {self.happiness}")
        print(f"Inflação: {self.inflation_pressure}%")
        print(f"Desemprego: {self.unemployment}%")
        print(f"Educação: {self.education}")
        print(f"Industrialização: {self.industrialization}")
        print(f"Trânsito: {self.transport['traffic']}")
        print("==========================\n")

    def show_grid(self):
        print("\n=== MAPA DA CIDADE ===")
        for row in self.grid:
            print(" ".join(row))
        print("======================\n")

    def collect_income(self):
        income = 100 + self.industrialization * 10
        self.money += income
        self.happiness -= 5
        self.inflation_pressure += 2
        print(f"💰 Receita coletada: ${income}. Felicidade -5, inflação +2")

        if self.industrialization > 20 and random.random() < 0.1:
            print("🔥 Um incêndio ocorreu! Felicidade -80")
            self.happiness -= 80

    def invest_education(self):
        if self.money >= 200:
            self.money -= 200
            self.education += 5
            print("📚 Educação aumentada em +5 pontos!")
        else:
            print("Dinheiro insuficiente!")

    def apply_policies(self, action):
        if action == "centralbank":
            self.inflation_pressure = max(0, self.inflation_pressure - 5)
            print("🏦 Banco Central atuou, inflação -5")
        elif action == "subsidies":
            if self.money >= 300:
                self.money -= 300
                self.happiness += 5
                print("🏭 Subsídios pagos. Felicidade +5, custo $300")
        elif action == "imports":
            if self.money >= 200:
                self.money -= 200
                self.inflation_pressure = max(0, self.inflation_pressure - 10)
                print("🚢 Importações baratearam preços. Inflação -10, custo $200")
        elif action == "exports":
            self.money += 400
            self.inflation_pressure += 5
            print("📦 Exportações feitas. Dinheiro +400, Inflação +5")

    def build(self, category, symbol, x, y, size=1):
        if x + size > GRID_SIZE or y + size > GRID_SIZE:
            print("❌ Espaço insuficiente para essa construção!")
            return
        for i in range(size):
            for j in range(size):
                if self.grid[y+i][x+j] != ".":
                    print("❌ Espaço já ocupado!")
                    return
        for i in range(size):
            for j in range(size):
                self.grid[y+i][x+j] = symbol
        print(f"✅ {category} construído em ({x},{y}) tamanho {size}x{size}")

    def update_transport(self):
        if self.transport["traffic"] > 50:
            self.happiness -= 5
            print("🚦 Trânsito caótico: Felicidade -5")
        if self.transport["public"]:
            self.transport["traffic"] = max(0, self.transport["traffic"] - 10)

    def monthly_report(self):
        print("\n📊 === RELATÓRIO MENSAL ===")
        print(f"Dinheiro: {self.money}")
        print(f"Felicidade: {self.happiness}")
        print(f"Inflação: {self.inflation_pressure}")
        print(f"Educação: {self.education}")
        print(f"Industrialização: {self.industrialization}")
        print("===========================\n")

    def random_dilemma(self):
        dilemmas = [
            ("Um morador reclama da inflação, o que você faz?",
             {"A": ("Ignorar", lambda self: setattr(self, "happiness", self.happiness - 10)),
              "B": ("Tentar controlar", lambda self: setattr(self, "inflation_pressure", max(0, self.inflation_pressure - 5)))}),
            ("Uma fábrica quer abrir sem licença ambiental. Aprovar?",
             {"A": ("Aprovar", lambda self: setattr(self, "industrialization", self.industrialization + 5)),
              "B": ("Negar", lambda self: setattr(self, "happiness", self.happiness + 5))})
        ]
        return random.choice(dilemmas)

    def seasonal_effects(self):
        season = (self.time.month % 12) // 3
        if season == 0:  # Verão
            if random.random() < 0.1:
                print("🔥 Incêndio sazonal! Felicidade -20")
                self.happiness -= 20
        elif season == 1:  # Outono
            pass
        elif season == 2:  # Inverno
            if random.random() < 0.1:
                print("🤒 Epidemia de gripe no inverno! Felicidade -15")
                self.happiness -= 15
        elif season == 3:  # Primavera
            if self.time.month == 12:
                print("🎄 Natal! Mais consumo, indústria +5, desemprego -2")
                self.industrialization += 5
                self.unemployment = max(0, self.unemployment - 2)


# ==========================
# LOOP PRINCIPAL
# ==========================

def main():
    city = City()

    print("=== Bem-vindo ao City Builder ===")
    print("Digite 'help' para comandos.\n")

    while True:
        cmd = input("> ").strip().lower()
        if cmd == "quit":
            print("Saindo do jogo...")
            break
        elif cmd == "help":
            print("Comandos: stats, city, collect, invest, policy <tipo>, build <cat> <x> <y>, reports, time pause/play, speed <n>")
        elif cmd == "stats":
            city.show_stats()
        elif cmd == "city":
            city.show_grid()
        elif cmd == "collect":
            city.collect_income()
        elif cmd == "invest":
            city.invest_education()
        elif cmd.startswith("policy"):
            _, action = cmd.split()
            city.apply_policies(action)
        elif cmd.startswith("build"):
            parts = cmd.split()
            if len(parts) >= 4:
                _, cat, x, y = parts[:4]
                size = 1
                if cat == "condominio": size = 3
                if cat in ("aeroporto", "porto"): size = 5
                if cat == "universidade": size = 3
                city.build(cat, cat[0].upper(), int(x), int(y), size)
        elif cmd == "reports":
            city.monthly_report()
        elif cmd.startswith("time"):
            _, action = cmd.split()
            if action == "pause":
                city.time.paused = True
            elif action == "play":
                city.time.paused = False
        elif cmd.startswith("speed"):
            _, s = cmd.split()
            city.time.speed = int(s)
        elif cmd == "next":
            city.time.tick()
            if city.time.day == 1:
                city.monthly_report()
                city.seasonal_effects()
            if random.random() < 0.05:
                q, choices = city.random_dilemma()
                print("\n❓ DILEMA:", q)
                for k, v in choices.items():
                    print(f"{k}: {v[0]}")
                choice = input("Sua escolha: ").upper()
                if choice in choices:
                    choices[choice][1](city)
        else:
            print("Comando inválido. Digite 'help'.")

if __name__ == "__main__":
    main()
