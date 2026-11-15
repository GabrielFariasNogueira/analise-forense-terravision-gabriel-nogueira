"""
Análise Forense TerraVision x Google Earth
Tema 7 - Regiões Polares e Calotas de Gelo (Reflexão Visual e Textura)

Instituição: Colégio Estadual Rodolpho Zaninelli
Curso: Técnico em Desenvolvimento de Sistemas | Turma: 3ºD
Disciplina: Computação Gráfica e Ciência de Dados
Professora: Angélica Neckel
Estudante: Gabriel Farias Nogueira
"""

import os
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter
    PIL_DISPONIVEL = True
except ImportError:
    PIL_DISPONIVEL = False

# Limites de altitude (em metros) exigidos pelo trabalho
LIMITE_BAIXA = 10000
LIMITE_ALTA = 1000
MINIMO_ALTITUDES = 5


def carregar_camada_satelite(lista_altitudes):
    """
    Função obrigatória do trabalho: recebe no mínimo 5 altitudes (metros)
    e classifica cada uma usando Level of Detail (LoD).
    """
    if not isinstance(lista_altitudes, (list, tuple)):
        raise TypeError("A entrada deve ser uma lista de altitudes.")
    if len(lista_altitudes) < MINIMO_ALTITUDES:
        raise ValueError(f"Informe no mínimo {MINIMO_ALTITUDES} altitudes.")

    camadas = []
    for altitude in lista_altitudes:
        if altitude < 0:
            raise ValueError(f"Altitude inválida: {altitude} m.")

        if altitude > LIMITE_BAIXA:
            nivel = "Baixa Resolução"
            descricao = "Mosaico geral da Terra (visão global, polos como manchas brancas)"
            ajuste_albedo = False
        elif altitude >= LIMITE_ALTA:
            nivel = "Média Resolução"
            descricao = "Mosaico regional de calotas polares e geleiras"
            ajuste_albedo = False
        else:
            nivel = "Alta Resolução"
            descricao = "Detalhes finos de textura do gelo: ranhuras, fendas e ajuste de albedo"
            ajuste_albedo = True

        camadas.append({
            "altitude_m": altitude,
            "nivel": nivel,
            "descricao": descricao,
            "ajuste_albedo": ajuste_albedo,
        })
        print(f"Altitude: {altitude:>7} m | {nivel} -> {descricao}")

    return camadas


class AbaRegiaoPolar(tk.Frame):
    """Componente visual independente para cada aba (Polo Sul ou Groenlândia)."""

    def __init__(self, parent, nome_regiao, prefixo_arquivo, descricoes_camadas):
        super().__init__(parent, bg="#121212")
        self.nome_regiao = nome_regiao
        self.prefixo_arquivo = prefixo_arquivo
        self.descricoes_camadas = descricoes_camadas
        self.imagens_carregadas = []
        self.pasta_base = os.path.dirname(os.path.abspath(__file__))

        if not PIL_DISPONIVEL:
            tk.Label(
                self,
                text="Biblioteca 'pillow' não instalada.\nRode 'pip install pillow' no terminal.",
                fg="#ffcc00", bg="#121212", font=("Arial", 12), pady=80
            ).pack()
            return

        # Carrega as 7 camadas renomeadas (ex: polo_sul_1.jpg a polo_sul_7.jpg)
        for i in range(1, 8):
            img_encontrada = None
            for ext in (".jpg", ".png", ".jpeg"):
                caminho = os.path.join(self.pasta_base, f"{prefixo_arquivo}_{i}{ext}")
                if os.path.exists(caminho):
                    img_encontrada = Image.open(caminho).convert("RGB").resize((840, 460), Image.Resampling.LANCZOS)
                    break
            self.imagens_carregadas.append(img_encontrada)

        # Painel do Mapa
        self.lbl_mapa = tk.Label(self, bg="#0a0a0a", bd=2, relief="sunken", width=840, height=460)
        self.lbl_mapa.pack(padx=15, pady=(12, 6))

        # Painel de Telemetria Forense
        self.lbl_status = tk.Label(
            self, text="", fg="white", bg="#1e1e1e",
            font=("Consolas", 10), justify="left", padx=15, pady=10, width=96
        )
        self.lbl_status.pack(pady=6)

        # Controle Deslizante de Altitude (Zoom)
        frame_ctrl = tk.Frame(self, bg="#121212")
        frame_ctrl.pack(pady=8, fill="x", padx=30)

        tk.Label(
            frame_ctrl, text="Altitude da Câmera (Zoom):",
            fg="#00d4ff", bg="#121212", font=("Arial", 10, "bold")
        ).pack(side="left")

        self.slider = tk.Scale(
            frame_ctrl, from_=200, to=35000, orient="horizontal",
            length=540, bg="#121212", fg="white", troughcolor="#2c2c2c",
            highlightthickness=0, command=self.atualizar_camada
        )
        self.slider.set(35000)
        self.slider.pack(side="right")

        self.atualizar_camada(35000)

    def aplicar_melhoria_forense(self, img, altitude):
        """Realça relevo, fendas glaciares e corrige o estouro de branco (Efeito Albedo)."""
        img_proc = img.copy()
        img_proc = img_proc.filter(ImageFilter.UnsharpMask(radius=1.8, percent=135, threshold=3))

        if altitude > LIMITE_BAIXA:
            img_proc = ImageEnhance.Contrast(img_proc).enhance(1.08)
        elif altitude >= LIMITE_ALTA:
            img_proc = ImageEnhance.Contrast(img_proc).enhance(1.18)
            img_proc = ImageEnhance.Brightness(img_proc).enhance(0.95)
        else:
            img_proc = ImageEnhance.Contrast(img_proc).enhance(1.32)
            img_proc = ImageEnhance.Brightness(img_proc).enhance(0.88)
            img_proc = ImageEnhance.Color(img_proc).enhance(1.12)

        return img_proc

    def atualizar_camada(self, valor):
        altitude = int(valor)

        if altitude > 22000:
            idx = 0
        elif altitude > 10000:
            idx = 1
        elif altitude > 6500:
            idx = 2
        elif altitude > 3500:
            idx = 3
        elif altitude >= 1000:
            idx = 4
        elif altitude > 550:
            idx = 5
        else:
            idx = 6

        if altitude > LIMITE_BAIXA:
            nivel = "BAIXA RESOLUÇÃO (> 10.000 m)"
            albedo_txt = "Desativado (visão orbital — alta reflexão atmosférica)"
        elif altitude >= LIMITE_ALTA:
            nivel = "MÉDIA RESOLUÇÃO (1.000 m a 10.000 m)"
            albedo_txt = "Moderado (destaque de costura/stitching e borda costeira)"
        else:
            nivel = "ALTA RESOLUÇÃO (< 1.000 m)"
            albedo_txt = "ATIVADO (Redução de brilho + realce de relevo e fendas)"

        img_base = self.imagens_carregadas[idx]

        if img_base is None:
            self.lbl_mapa.config(
                image="",
                text=f"[{self.nome_regiao} — Camada {idx + 1}/7 aguardando '{self.prefixo_arquivo}_{idx + 1}.jpg']\n"
                     f"Salve as imagens desta região na mesma pasta do script.py",
                fg="#888888", font=("Arial", 12)
            )
        else:
            img_final = self.aplicar_melhoria_forense(img_base, altitude)
            self.foto_tk = ImageTk.PhotoImage(img_final)
            self.lbl_mapa.config(image=self.foto_tk, text="")

        self.lbl_status.config(
            text=f"REGIÃO: {self.nome_regiao.upper()}  |  ALTITUDE: {altitude} m  |  CAMADA {idx + 1}/7: {nivel}\n"
                 f"CENA: {self.descricoes_camadas[idx]}\n"
                 f"PROCESSAMENTO FORENSE (ALBEDO/RELEVO): {albedo_txt}"
        )


class MiniGoogleEarthApp:
    """Janela principal com navegação por abas (Polo Sul e Groenlândia)."""

    def __init__(self, root):
        self.root = root
        self.root.title("TerraVision vs. Google Earth — Análise Forense LoD (Tema 7: Regiões Polares)")
        self.root.configure(bg="#121212")

        tk.Label(
            root,
            text="SIMULADOR DE RENDERIZAÇÃO GEOESPACIAL (LoD) — TEMA 7: REGIÕES POLARES",
            fg="#00d4ff", bg="#121212", font=("Arial", 13, "bold"), pady=8
        ).pack()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#121212", borderwidth=0)
        style.configure("TNotebook.Tab", background="#252526", foreground="white", padding=[18, 6], font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#007acc")], foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- ABA 1: POLO SUL (ANTÁRTIDA) ---
        descricoes_polo_sul = [
            "Visão Orbital Global — Cobertura de nuvens e calota polar vista do espaço",
            "Contorno Continental da Antártida — Artefatos de costura (stitching) visíveis no gelo",
            "Plataforma Costeira (Terra de Wilkes) — Contraste Figura-Fundo entre gelo e oceano",
            "Aproximação Regional (Casey Station) — Afloramentos rochosos e borda da geleira",
            "Zona de Fratura Costeira — Início do desprendimento de blocos de gelo no mar",
            "Detalhe Glacial (AB Dobrowolski Polar Station) — Fendas e mosaico de gelo fragmentado",
            "Zoom Máximo (Ilha Mill) — Alta definição de blocos de gelo flutuantes e relevo de textura",
        ]
        aba_sul = AbaRegiaoPolar(self.notebook, "Polo Sul (Antártida)", "polo_sul", descricoes_polo_sul)
        self.notebook.add(aba_sul, text="  ❄️ Polo Sul (Antártida)  ")

        # --- ABA 2: GROENLÂNDIA ---
        descricoes_groenlandia = [
            "Visão Orbital Global — Ártico e Groenlândia vistos do espaço",
            "Contorno Continental da Groenlândia — Calota de gelo e estreitos oceânicos",
            "Plataforma Costeira — Fiordes glaciares e contraste gelo/oceano",
            "Aproximação Regional — Línguas glaciares e vales nevados",
            "Zona de Fratura — Icebergs e frentes de geleiras em degelo",
            "Detalhe Glacial — Ranhuras profundas e relevo da superfície gelada",
            "Zoom Máximo — Textura fina de fendas e ajuste local de Albedo",
        ]
        aba_groenlandia = AbaRegiaoPolar(self.notebook, "Groenlândia", "groenlandia", descricoes_groenlandia)
        self.notebook.add(aba_groenlandia, text="  🧊 Groenlândia  ")


if __name__ == "__main__":
    print("=== EXECUÇÃO DA FUNÇÃO OBRIGATÓRIA (LoD) ===")
    carregar_camada_satelite([35000, 12000, 8500, 3200, 450])

    janela = tk.Tk()
    app = MiniGoogleEarthApp(janela)
    janela.mainloop()
