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
import math
import random
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageDraw
    PIL_DISPONIVEL = True
except ImportError:
    PIL_DISPONIVEL = False

# Limites de altitude (em metros) exigidos pelo trabalho
LIMITE_BAIXA = 10000
LIMITE_ALTA = 1000
LIMITE_PROCEDURAL = 200  # Abaixo de 200m ativa a síntese procedural de micro-relevo
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


def gerar_textura_procedural_gelo(largura, altura, semente=42):
    """
    Gera um mapa procedural de micro-fendas, cristais e granulação glacial
    para simular detalhes em altitudes ultra-baixas (< 200 m).
    """
    rng = random.Random(semente)
    ruido_fino = Image.effect_noise((largura, altura), 38).convert("L")
    ruido_macro = Image.effect_noise((largura // 4, altura // 4), 55).convert("L")
    ruido_macro = ruido_macro.resize((largura, altura), Image.Resampling.BICUBIC)

    mapa_altura = Image.blend(ruido_macro, ruido_fino, 0.45)

    draw = ImageDraw.Draw(mapa_altura)
    for _ in range(45):
        x = rng.randint(0, largura)
        y = rng.randint(0, altura)
        angulo = rng.uniform(-0.6, 0.6) + (math.pi / 4)
        pontos = [(x, y)]
        for _ in range(rng.randint(5, 12)):
            passo = rng.randint(15, 45)
            angulo += rng.uniform(-0.35, 0.35)
            x += int(math.cos(angulo) * passo)
            y += int(math.sin(angulo) * passo)
            pontos.append((x, y))
        draw.line(pontos, fill=rng.randint(25, 75), width=rng.randint(1, 2))

    mapa_altura = mapa_altura.filter(ImageFilter.GaussianBlur(0.8))
    return mapa_altura.convert("RGB")


class AbaPoloSul(tk.Frame):
    """Aba principal do Polo Sul (Antártida) com 7 camadas reais + síntese procedural."""

    def __init__(self, parent):
        super().__init__(parent, bg="#121212")
        self.pasta_base = os.path.dirname(os.path.abspath(__file__))
        self.imagens_carregadas = []
        self.largura_tela = 840
        self.altura_tela = 460

        self.descricoes_camadas = [
            "Visão Orbital Global — Cobertura de nuvens e calota polar vista do espaço",
            "Contorno Continental da Antártida — Artefatos de costura (stitching) visíveis no gelo",
            "Plataforma Costeira (Terra de Wilkes) — Contraste Figura-Fundo entre gelo e oceano",
            "Aproximação Regional (Casey Station) — Afloramentos rochosos e borda da geleira",
            "Zona de Fratura Costeira — Início do desprendimento de blocos de gelo no mar",
            "Detalhe Glacial (AB Dobrowolski Polar Station) — Fendas e mosaico de gelo fragmentado",
            "Zoom Máximo Satélite (Ilha Mill) — Blocos de gelo flutuantes e relevo costeiro",
            "SÍNTESE PROCEDURAL (< 200 m) — Micro-fendas glaciares e granulação geradas matematicamente",
        ]

        if not PIL_DISPONIVEL:
            tk.Label(
                self,
                text="Biblioteca 'pillow' não instalada.\nRode 'pip install pillow' no terminal.",
                fg="#ffcc00", bg="#121212", font=("Arial", 12), pady=80
            ).pack()
            return

        for i in range(1, 8):
            img_encontrada = None
            for ext in (".jpg", ".png", ".jpeg"):
                caminho = os.path.join(self.pasta_base, f"polo_sul_{i}{ext}")
                if os.path.exists(caminho):
                    img_encontrada = Image.open(caminho).convert("RGB").resize(
                        (self.largura_tela, self.altura_tela), Image.Resampling.LANCZOS
                    )
                    break
            self.imagens_carregadas.append(img_encontrada)

        self.mapa_procedural = gerar_textura_procedural_gelo(self.largura_tela, self.altura_tela)

        self.lbl_mapa = tk.Label(self, bg="#0a0a0a", bd=2, relief="sunken", width=self.largura_tela, height=self.altura_tela)
        self.lbl_mapa.pack(padx=15, pady=(12, 6))

        self.lbl_status = tk.Label(
            self, text="", fg="white", bg="#1e1e1e",
            font=("Consolas", 10), justify="left", padx=15, pady=10, width=98
        )
        self.lbl_status.pack(pady=6)

        frame_ctrl = tk.Frame(self, bg="#121212")
        frame_ctrl.pack(pady=8, fill="x", padx=30)

        tk.Label(
            frame_ctrl, text="Altitude da Câmera (Zoom):",
            fg="#00d4ff", bg="#121212", font=("Arial", 10, "bold")
        ).pack(side="left")

        self.slider = tk.Scale(
            frame_ctrl, from_=10, to=35000, orient="horizontal",
            length=540, bg="#121212", fg="white", troughcolor="#2c2c2c",
            highlightthickness=0, command=self.atualizar_camada
        )
        self.slider.set(35000)
        self.slider.pack(side="right")

        self.atualizar_camada(35000)

    def processar_imagem(self, img_base, altitude):
        img_proc = img_base.copy()

        if altitude < LIMITE_PROCEDURAL:
            progresso = (LIMITE_PROCEDURAL - altitude) / (LIMITE_PROCEDURAL - 10)
            escala = 1.0 + (progresso * 1.8)

            nw = int(self.largura_tela / escala)
            nh = int(self.altura_tela / escala)
            left = (self.largura_tela - nw) // 2
            top = (self.altura_tela - nh) // 2

            img_zoom = img_proc.crop((left, top, left + nw, top + nh)).resize(
                (self.largura_tela, self.altura_tela), Image.Resampling.BILINEAR
            )

            intensidade_procedural = min(0.42, 0.12 + progresso * 0.30)
            img_proc = Image.blend(img_zoom, self.mapa_procedural, intensidade_procedural)

            img_proc = img_proc.filter(ImageFilter.UnsharpMask(radius=2.0, percent=160, threshold=2))
            img_proc = ImageEnhance.Contrast(img_proc).enhance(1.38)
            img_proc = ImageEnhance.Brightness(img_proc).enhance(0.86)
            return img_proc

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
            idx_img, idx_desc = 0, 0
        elif altitude > 10000:
            idx_img, idx_desc = 1, 1
        elif altitude > 6500:
            idx_img, idx_desc = 2, 2
        elif altitude > 3500:
            idx_img, idx_desc = 3, 3
        elif altitude >= 1000:
            idx_img, idx_desc = 4, 4
        elif altitude > 550:
            idx_img, idx_desc = 5, 5
        elif altitude >= LIMITE_PROCEDURAL:
            idx_img, idx_desc = 6, 6
        else:
            idx_img, idx_desc = 6, 7

        if altitude > LIMITE_BAIXA:
            nivel = "BAIXA RESOLUÇÃO (> 10.000 m)"
            albedo_txt = "Desativado (visão orbital — alta reflexão atmosférica)"
        elif altitude >= LIMITE_ALTA:
            nivel = "MÉDIA RESOLUÇÃO (1.000 m a 10.000 m)"
            albedo_txt = "Moderado (destaque de costura/stitching e borda costeira)"
        elif altitude >= LIMITE_PROCEDURAL:
            nivel = "ALTA RESOLUÇÃO SATÉLITE (200 m a 1.000 m)"
            albedo_txt = "ATIVADO (Redução de brilho + realce de relevo e fendas)"
        else:
            nivel = "MICRO-ESCALA PROCEDURAL (< 200 m)"
            albedo_txt = "SÍNTESE PROCEDURAL ATIVA (Detail Texturing + Correção Albedo)"

        img_base = self.imagens_carregadas[idx_img]

        if img_base is None:
            self.lbl_mapa.config(
                image="",
                text=f"[Polo Sul — Camada {idx_img + 1}/7 aguardando 'polo_sul_{idx_img + 1}.jpg']\n"
                     f"Salve as imagens na mesma pasta do script.py",
                fg="#888888", font=("Arial", 12)
            )
        else:
            img_final = self.processar_imagem(img_base, altitude)
            self.foto_tk = ImageTk.PhotoImage(img_final)
            self.lbl_mapa.config(image=self.foto_tk, text="")

        camada_label = "PROCEDURAL" if altitude < LIMITE_PROCEDURAL else f"{idx_img + 1}/7"
        self.lbl_status.config(
            text=f"REGIÃO: POLO SUL (ANTÁRTIDA)  |  ALTITUDE: {altitude} m  |  CAMADA {camada_label}: {nivel}\n"
                 f"CENA: {self.descricoes_camadas[idx_desc]}\n"
                 f"MODO DE RENDERIZAÇÃO: {albedo_txt}"
        )


class MiniGoogleEarthApp:
    """Janela principal do simulador."""

    def __init__(self, root):
        self.root = root
        self.root.title("TerraVision vs. Google Earth — Análise Forense LoD (Tema 7: Regiões Polares)")
        self.root.configure(bg="#121212")

        tk.Label(
            root,
            text="SIMULADOR DE RENDERIZAÇÃO GEOESPACIAL (LoD) + SÍNTESE PROCEDURAL",
            fg="#00d4ff", bg="#121212", font=("Arial", 13, "bold"), pady=8
        ).pack()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#121212", borderwidth=0)
        style.configure("TNotebook.Tab", background="#252526", foreground="white", padding=[18, 6], font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#007acc")], foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        aba_sul = AbaPoloSul(self.notebook)
        self.notebook.add(aba_sul, text="  ❄️ Polo Sul (Antártida)  ")


if __name__ == "__main__":
    print("=== EXECUÇÃO DA FUNÇÃO OBRIGATÓRIA (LoD) ===")
    carregar_camada_satelite([35000, 12000, 8500, 3200, 450])

    janela = tk.Tk()
    app = MiniGoogleEarthApp(janela)
    janela.mainloop()
