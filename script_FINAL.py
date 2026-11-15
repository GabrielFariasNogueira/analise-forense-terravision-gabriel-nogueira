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
LIMITE_PROCEDURAL = 200
MINIMO_ALTITUDES = 5

# Paleta Minimalista & Fosca (Slate / Obsidian)
COR_FUNDO = "#090d14"
COR_CARTAO = "#111722"
COR_ELEVADO = "#192231"
COR_BORDA = "#222e42"
COR_CIANO = "#38bdf8"
COR_VERDE = "#34d399"
COR_AMBAR = "#fbbf24"
COR_ROXO = "#a78bfa"
COR_TEXTO = "#f8fafc"
COR_MUTED = "#7c8ba1"


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


def aplicar_cantos_arredondados(img, raio=22):
    """Aplica máscara suavizada (anti-aliased) com cantos arredondados na imagem."""
    escala = 4  # Supersampling 4x para bordas perfeitamente lisas sem serrilhado
    w, h = img.size
    mascara = Image.new("L", (w * escala, h * escala), 0)
    draw = ImageDraw.Draw(mascara)
    draw.rounded_rectangle((0, 0, w * escala, h * escala), radius=raio * escala, fill=255)
    mascara = mascara.resize((w, h), Image.Resampling.LANCZOS)

    fundo = Image.new("RGB", (w, h), COR_FUNDO)
    fundo.paste(img, (0, 0), mascara)
    return fundo


def gerar_textura_procedural_gelo(largura, altura, semente=42):
    """Gera mapa procedural de micro-fendas e granulação glacial (< 200 m)."""
    rng = random.Random(semente)
    ruido_fino = Image.effect_noise((largura, altura), 36).convert("L")
    ruido_macro = Image.effect_noise((largura // 4, altura // 4), 52).convert("L")
    ruido_macro = ruido_macro.resize((largura, altura), Image.Resampling.BICUBIC)
    mapa_altura = Image.blend(ruido_macro, ruido_fino, 0.45)

    draw = ImageDraw.Draw(mapa_altura)
    for _ in range(48):
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

    return mapa_altura.filter(ImageFilter.GaussianBlur(0.8)).convert("RGB")


class BotaoPilula(tk.Canvas):
    """Botão arredondado minimalista desenhado vetorialmente."""

    def __init__(self, parent, texto, comando, largura=118, altura=30, bg_cor=COR_ELEVADO, fg_cor=COR_TEXTO):
        super().__init__(parent, width=largura, height=altura, bg=COR_CARTAO, highlightthickness=0, cursor="hand2")
        self.comando = comando
        self.bg_cor = bg_cor
        self.hover_cor = "#243147"
        self.fg_cor = fg_cor
        self.texto = texto
        self.largura = largura
        self.altura = altura

        self._desenhar(self.bg_cor)
        self.bind("<Enter>", lambda e: self._desenhar(self.hover_cor))
        self.bind("<Leave>", lambda e: self._desenhar(self.bg_cor))
        self.bind("<Button-1>", lambda e: self.comando())

    def _desenhar(self, cor):
        self.delete("all")
        r = self.altura // 2
        w, h = self.largura - 1, self.altura - 1
        # Forma de pílula arredondada
        self.create_oval(1, 1, 1 + 2 * r, h, fill=cor, outline="")
        self.create_oval(w - 2 * r, 1, w, h, fill=cor, outline="")
        self.create_rectangle(1 + r, 1, w - r, h, fill=cor, outline="")
        self.create_text(self.largura // 2, self.altura // 2, text=self.texto, fill=self.fg_cor, font=("Segoe UI", 8, "bold"))


class SliderArredondado(tk.Canvas):
    """Barra deslizante minimalista e arredondada para controle suave de altitude."""

    def __init__(self, parent, ao_mudar, largura=810, altura=28):
        super().__init__(parent, width=largura, height=altura, bg=COR_CARTAO, highlightthickness=0, cursor="hand2")
        self.ao_mudar = ao_mudar
        self.largura = largura
        self.altura = altura
        self.valor = 0.0  # 0.0 a 1.0
        self.margem = 14

        self.bind("<Button-1>", self._interagir)
        self.bind("<B1-Motion>", self._interagir)
        self._desenhar()

    def definir_valor(self, t):
        self.valor = max(0.0, min(1.0, float(t)))
        self._desenhar()

    def _interagir(self, event):
        util = self.largura - 2 * self.margem
        t = (event.x - self.margem) / max(1, util)
        self.definir_valor(t)
        self.ao_mudar(self.valor)

    def _desenhar(self):
        self.delete("all")
        cy = self.altura // 2
        x0 = self.margem
        x1 = self.largura - self.margem
        xp = x0 + int((x1 - x0) * self.valor)

        # Trilho de fundo arredondado
        self.create_line(x0, cy, x1, cy, fill=COR_ELEVADO, width=6, capstyle="round")
        # Trilho ativo (ciano)
        if xp > x0:
            self.create_line(x0, cy, xp, cy, fill=COR_CIANO, width=6, capstyle="round")
        # Pegador circular minimalista
        self.create_oval(xp - 8, cy - 8, xp + 8, cy + 8, fill=COR_TEXTO, outline=COR_CIANO, width=2)


class CartaoArredondado(tk.Canvas):
    """Container com cantos arredondados suaves para agrupar informações."""

    def __init__(self, parent, largura, altura, raio=18, bg_cartao=COR_CARTAO, borda=COR_BORDA):
        super().__init__(parent, width=largura, height=altura, bg=COR_FUNDO, highlightthickness=0)
        self._desenhar_fundo(largura, altura, raio, bg_cartao, borda)

    def _desenhar_fundo(self, w, h, r, cor, borda):
        pts = [
            r, 1, w - r, 1, w - 1, 1, w - 1, r,
            w - 1, h - r, w - 1, h - 1, w - r, h - 1,
            r, h - 1, 1, h - 1, 1, h - r, 1, r, 1, 1
        ]
        self.create_polygon(pts, smooth=True, fill=cor, outline=borda, width=1)


class AbaRegiaoPolar(tk.Frame):
    """Aba minimalista com viewport arredondado, zoom fluido e telemetria limpa."""

    LIMITES_CAMADAS = [35000, 22000, 10000, 6500, 3500, 1000, 550, 200]

    def __init__(self, parent, nome_regiao, subtitulo_geo, prefixos_arquivos, descricoes_camadas, semente_procedural=42):
        super().__init__(parent, bg=COR_FUNDO)
        self.nome_regiao = nome_regiao
        self.subtitulo_geo = subtitulo_geo
        self.prefixos_arquivos = prefixos_arquivos
        self.descricoes_camadas = descricoes_camadas
        self.imagens_carregadas = []
        self.largura_tela = 840
        self.altura_tela = 430
        self.pasta_base = os.path.dirname(os.path.abspath(__file__))

        self.altitude_atual = 35000.0
        self.altitude_alvo = 35000.0
        self.animacao_ativa = False
        self.albedo_ativo = True

        if not PIL_DISPONIVEL:
            tk.Label(
                self, text="Instale a biblioteca Pillow: pip install pillow",
                fg=COR_AMBAR, bg=COR_FUNDO, font=("Segoe UI", 11), pady=80
            ).pack()
            return

        for i in range(1, 8):
            img_encontrada = None
            for prefixo in prefixos_arquivos:
                for ext in (".jpg", ".png", ".jpeg"):
                    caminho = os.path.join(self.pasta_base, f"{prefixo}{i}{ext}")
                    if os.path.exists(caminho):
                        img = Image.open(caminho).convert("RGB").resize(
                            (self.largura_tela, self.altura_tela), Image.Resampling.LANCZOS
                        )
                        img_encontrada = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))
                        break
                if img_encontrada is not None:
                    break
            self.imagens_carregadas.append(img_encontrada)

        self.mapa_procedural = gerar_textura_procedural_gelo(
            self.largura_tela, self.altura_tela, semente=semente_procedural
        )

        self._construir_interface()
        self.renderizar_quadro(35000)

    def _construir_interface(self):
        # 1. VIEWPORT ARREDONDADO
        self.canvas = tk.Canvas(
            self, width=self.largura_tela, height=self.altura_tela,
            bg=COR_FUNDO, highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=(12, 8))

        self.canvas.bind("<MouseWheel>", self._ao_rolar_mouse)
        self.canvas.bind("<Button-4>", lambda e: self._ajustar_zoom_relativo(0.82))
        self.canvas.bind("<Button-5>", lambda e: self._ajustar_zoom_relativo(1.22))

        # 2. CARTÃO MINIMALISTA UNIFICADO (TELEMETRIA + CONTROLES)
        card = CartaoArredondado(self, largura=self.largura_tela, altura=148, raio=22)
        card.pack(padx=20, pady=(0, 14))

        interno = tk.Frame(card, bg=COR_CARTAO)
        card.create_window(self.largura_tela // 2, 74, window=interno, width=self.largura_tela - 28, height=132)

        # Linha Superior: Status limpo e minimalista
        topo_info = tk.Frame(interno, bg=COR_CARTAO)
        topo_info.pack(fill="x", pady=(2, 2))

        self.lbl_nivel = tk.Label(
            topo_info, text="● BAIXA RESOLUÇÃO", bg=COR_CARTAO, fg=COR_CIANO,
            font=("Segoe UI", 9, "bold")
        )
        self.lbl_nivel.pack(side="left")

        self.lbl_altitude = tk.Label(
            topo_info, text="35.000 m", bg=COR_CARTAO, fg=COR_TEXTO,
            font=("Segoe UI", 11, "bold"), padx=12
        )
        self.lbl_altitude.pack(side="left")

        self.lbl_camada = tk.Label(
            topo_info, text="Camada 1/7  •  1.00x", bg=COR_CARTAO, fg=COR_MUTED,
            font=("Segoe UI", 9)
        )
        self.lbl_camada.pack(side="right")

        # Descrição única em uma linha limpa
        self.lbl_descricao = tk.Label(
            interno, text="", bg=COR_CARTAO, fg=COR_MUTED,
            font=("Segoe UI", 9), anchor="w"
        )
        self.lbl_descricao.pack(fill="x", pady=(0, 4))

        # Slider Arredondado Minimalista
        self.slider = SliderArredondado(interno, ao_mudar=self._ao_mover_slider, largura=self.largura_tela - 32, altura=26)
        self.slider.pack(pady=(2, 6))

        # Barra Inferior: Voo Rápido + Alternador de Albedo em pílulas arredondadas
        barra_acoes = tk.Frame(interno, bg=COR_CARTAO)
        barra_acoes.pack(fill="x")

        presets = [
            ("Órbita", 35000),
            ("Continental", 15000),
            ("Regional", 5000),
            ("Alta Res.", 600),
            ("Procedural", 50),
        ]
        for nome_btn, alt_dest in presets:
            btn = BotaoPilula(
                barra_acoes, texto=nome_btn,
                comando=lambda a=alt_dest: self.voar_para_altitude(a),
                largura=92, altura=28
            )
            btn.pack(side="left", padx=(0, 6))

        self.btn_albedo = BotaoPilula(
            barra_acoes, texto="Albedo: ON",
            comando=self._alternar_albedo,
            largura=104, altura=28, bg_cor="#163229", fg_cor=COR_VERDE
        )
        self.btn_albedo.pack(side="right")

    def _alternar_albedo(self):
        self.albedo_ativo = not self.albedo_ativo
        if self.albedo_ativo:
            self.btn_albedo.texto = "Albedo: ON"
            self.btn_albedo.bg_cor = "#163229"
            self.btn_albedo.fg_cor = COR_VERDE
        else:
            self.btn_albedo.texto = "Albedo: OFF"
            self.btn_albedo.bg_cor = COR_ELEVADO
            self.btn_albedo.fg_cor = COR_MUTED
        self.btn_albedo._desenhar(self.btn_albedo.bg_cor)
        self.renderizar_quadro(int(round(self.altitude_atual)))

    # --- CONVERSÃO EXPONENCIAL PARA ZOOM FLUIDO ---
    def _slider_para_altitude(self, t):
        t = max(0.0, min(1.0, float(t)))
        alt = 35000.0 * ((10.0 / 35000.0) ** t)
        return max(10, min(35000, int(round(alt))))

    def _altitude_para_slider(self, altitude):
        alt = max(10.0, min(35000.0, float(altitude)))
        return math.log(alt / 35000.0) / math.log(10.0 / 35000.0)

    def _ao_mover_slider(self, t):
        alt = self._slider_para_altitude(t)
        self.altitude_atual = float(alt)
        self.altitude_alvo = float(alt)
        self.renderizar_quadro(alt)

    def _ao_rolar_mouse(self, event):
        fator = 0.80 if event.delta > 0 else 1.25
        self._ajustar_zoom_relativo(fator)

    def _ajustar_zoom_relativo(self, fator):
        nova_alt = max(10, min(35000, int(self.altitude_alvo * fator)))
        self.voar_para_altitude(nova_alt)

    def voar_para_altitude(self, destino):
        self.altitude_alvo = float(max(10, min(35000, destino)))
        if not self.animacao_ativa:
            self.animacao_ativa = True
            self._passo_animacao()

    def _passo_animacao(self):
        diff = self.altitude_alvo - self.altitude_atual
        if abs(diff) < 1.5:
            self.altitude_atual = self.altitude_alvo
            self.slider.definir_valor(self._altitude_para_slider(self.altitude_atual))
            self.renderizar_quadro(int(round(self.altitude_atual)))
            self.animacao_ativa = False
            return

        self.altitude_atual += diff * 0.22
        alt_int = int(round(self.altitude_atual))
        self.slider.definir_valor(self._altitude_para_slider(self.altitude_atual))
        self.renderizar_quadro(alt_int)
        self.after(16, self._passo_animacao)

    def _recortar_zoom_continuo(self, img, fator_zoom):
        if fator_zoom <= 1.001:
            return img
        nw = max(40, int(self.largura_tela / fator_zoom))
        nh = max(40, int(self.altura_tela / fator_zoom))
        left = (self.largura_tela - nw) // 2
        top = (self.altura_tela - nh) // 2
        return img.crop((left, top, left + nw, top + nh)).resize(
            (self.largura_tela, self.altura_tela), Image.Resampling.BILINEAR
        )

    def processar_imagem(self, img_base, altitude, fator_zoom_camada):
        img_proc = self._recortar_zoom_continuo(img_base, fator_zoom_camada)

        if altitude < LIMITE_PROCEDURAL:
            progresso = (LIMITE_PROCEDURAL - altitude) / (LIMITE_PROCEDURAL - 10)
            intensidade_procedural = min(0.42, 0.10 + progresso * 0.32)
            img_proc = Image.blend(img_proc, self.mapa_procedural, intensidade_procedural)
            img_proc = img_proc.filter(ImageFilter.UnsharpMask(radius=1.8, percent=150, threshold=2))

        if self.albedo_ativo:
            if altitude > LIMITE_BAIXA:
                img_proc = ImageEnhance.Contrast(img_proc).enhance(1.06)
            elif altitude >= LIMITE_ALTA:
                img_proc = ImageEnhance.Contrast(img_proc).enhance(1.18)
                img_proc = ImageEnhance.Brightness(img_proc).enhance(0.95)
            else:
                img_proc = ImageEnhance.Contrast(img_proc).enhance(1.32)
                img_proc = ImageEnhance.Brightness(img_proc).enhance(0.88)
                img_proc = ImageEnhance.Color(img_proc).enhance(1.12)

        return aplicar_cantos_arredondados(img_proc, raio=22)

    def renderizar_quadro(self, altitude):
        limites = self.LIMITES_CAMADAS
        if altitude >= LIMITE_PROCEDURAL:
            idx_img = 6
            fator_zoom = 1.0
            for i in range(7):
                teto = limites[i]
                piso = limites[i + 1]
                if altitude >= piso or i == 6:
                    idx_img = i
                    progresso_faixa = max(0.0, min(1.0, (teto - altitude) / max(1, (teto - piso))))
                    fator_zoom = 1.0 + (progresso_faixa * 0.36)
                    break
            idx_desc = idx_img
        else:
            idx_img = 6
            idx_desc = 7
            progresso_proc = (LIMITE_PROCEDURAL - altitude) / (LIMITE_PROCEDURAL - 10)
            fator_zoom = 1.36 + (progresso_proc * 1.64)

        if altitude > LIMITE_BAIXA:
            nivel_txt = "●  BAIXA RESOLUÇÃO"
            cor_badge = COR_CIANO
        elif altitude >= LIMITE_ALTA:
            nivel_txt = "●  MÉDIA RESOLUÇÃO"
            cor_badge = COR_AMBAR
        elif altitude >= LIMITE_PROCEDURAL:
            nivel_txt = "●  ALTA RESOLUÇÃO"
            cor_badge = COR_VERDE
        else:
            nivel_txt = "●  SÍNTESE PROCEDURAL"
            cor_badge = COR_ROXO

        self.lbl_nivel.config(text=nivel_txt, fg=cor_badge)
        self.lbl_altitude.config(text=f"{altitude:,} m".replace(",", "."))
        camada_str = "Procedural" if altitude < LIMITE_PROCEDURAL else f"Camada {idx_img + 1}/7"
        self.lbl_camada.config(text=f"{camada_str}  •  {fator_zoom:.2f}x")
        self.lbl_descricao.config(text=self.descricoes_camadas[idx_desc])

        self.canvas.delete("all")
        img_base = self.imagens_carregadas[idx_img]

        if img_base is None:
            exemplo_nome = f"{self.prefixos_arquivos[0]}{idx_img + 1}.jpg"
            self.canvas.create_text(
                self.largura_tela // 2, self.altura_tela // 2,
                text=f"Aguardando '{exemplo_nome}' na pasta do script",
                fill=COR_MUTED, font=("Segoe UI", 11)
            )
        else:
            img_final = self.processar_imagem(img_base, altitude, fator_zoom)
            self.foto_tk = ImageTk.PhotoImage(img_final)
            self.canvas.create_image(0, 0, anchor="nw", image=self.foto_tk)

            # Mira minimalista central
            cx, cy = self.largura_tela // 2, self.altura_tela // 2
            self.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, outline=COR_CIANO, width=1)

            # Tag discreta de localização no canto inferior esquerdo
            self.canvas.create_text(
                20, self.altura_tela - 18, anchor="w",
                text=self.subtitulo_geo, fill=COR_TEXTO, font=("Segoe UI", 9, "bold")
            )


class MiniGoogleEarthApp:
    """Janela principal minimalista e arredondada."""

    def __init__(self, root):
        self.root = root
        self.root.title("TerraVision × Google Earth — LoD Regiões Polares")
        self.root.configure(bg=COR_FUNDO)
        self.root.resizable(False, False)

        # Barra superior minimalista
        topo = tk.Frame(root, bg=COR_FUNDO)
        topo.pack(fill="x", padx=22, pady=(14, 4))

        tk.Label(
            topo, text="TerraVision × Google Earth",
            fg=COR_TEXTO, bg=COR_FUNDO, font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        tk.Label(
            topo, text="Tema 7 • Regiões Polares (LoD & Albedo)",
            fg=COR_MUTED, bg=COR_FUNDO, font=("Segoe UI", 9)
        ).pack(side="right", pady=(4, 0))

        # Abas limpas sem bordas pesadas
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=COR_FUNDO, foreground=COR_MUTED,
            padding=[18, 8], font=("Segoe UI", 10, "bold"), borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COR_CARTAO)],
            foreground=[("selected", COR_CIANO)]
        )

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        descricoes_polo_sul = [
            "Visão orbital global — cobertura de nuvens e calota polar vista do espaço",
            "Contorno continental da Antártida — artefatos de costura (stitching) no gelo",
            "Plataforma costeira (Terra de Wilkes) — contraste entre gelo e oceano",
            "Aproximação regional (Casey Station) — afloramentos rochosos e borda glacial",
            "Zona de fratura costeira — desprendimento de blocos de gelo no mar",
            "Detalhe glacial (AB Dobrowolski) — fendas e mosaico de gelo fragmentado",
            "Zoom máximo satélite (Ilha Mill) — blocos flutuantes e relevo costeiro",
            "Síntese procedural (< 200 m) — micro-fendas e granulação geradas em tempo real",
        ]
        aba_sul = AbaRegiaoPolar(
            self.notebook,
            nome_regiao="Polo Sul",
            subtitulo_geo="Antártida • Terra de Wilkes",
            prefixos_arquivos=["polo_sul_", "polo_sul"],
            descricoes_camadas=descricoes_polo_sul,
            semente_procedural=42
        )
        self.notebook.add(aba_sul, text="  ❄️ Polo Sul  ")

        descricoes_groenlandia = [
            "Visão orbital regional — Groenlândia, Arquipélago Ártico e Islândia",
            "Contorno continental — Mar de Baffin, Islândia e calota central de gelo",
            "Costa Leste (Summit Camp a Ittoqqortoormiit) — costura triangular de satélite",
            "Rede de fiordes (Myggbukta, Traill Øer e Mestersvig) — rocha, gelo e mar",
            "Aproximação glacial (Traill Øer / Mestersvig) — línguas de gelo nos vales",
            "Detalhe topográfico (Ymer Øer) — relevo montanhoso exposto e faixa de mosaico",
            "Zoom máximo satélite (Costa Ártica) — geleira de vale e gelo marinho fragmentado",
            "Síntese procedural (< 200 m) — micro-fendas e relevo rochoso gerados em tempo real",
        ]
        aba_groenlandia = AbaRegiaoPolar(
            self.notebook,
            nome_regiao="Groenlândia",
            subtitulo_geo="Groenlândia • Costa Leste",
            prefixos_arquivos=["gro", "groenlandia_", "groenlandia"],
            descricoes_camadas=descricoes_groenlandia,
            semente_procedural=99
        )
        self.notebook.add(aba_groenlandia, text="  🧊 Groenlândia  ")


if __name__ == "__main__":
    print("=== EXECUÇÃO DA FUNÇÃO OBRIGATÓRIA (LoD) ===")
    carregar_camada_satelite([35000, 12000, 8500, 3200, 450])

    janela = tk.Tk()
    app = MiniGoogleEarthApp(janela)
    janela.mainloop()
