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

# Paleta de Cores Moderna (Estilo Estação Espacial / Google Earth Pro)
COR_FUNDO = "#0b0f17"
COR_PAINEL = "#131a26"
COR_BORDA = "#1f2b3e"
COR_CIANO = "#38bdf8"
COR_VERDE = "#34d399"
COR_AMBAR = "#fbbf24"
COR_ROXO = "#a78bfa"
COR_TEXTO = "#f1f5f9"
COR_TEXTO_SUAVE = "#94a3b8"


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

    mapa_altura = mapa_altura.filter(ImageFilter.GaussianBlur(0.8))
    return mapa_altura.convert("RGB")


class AbaRegiaoPolar(tk.Frame):
    """Componente visual com zoom contínuo (interpolado),HUD dinâmico e atalhos rápidos."""

    # Faixas de altitude de cada uma das 7 camadas reais (do topo até 200m)
    LIMITES_CAMADAS = [35000, 22000, 10000, 6500, 3500, 1000, 550, 200]

    def __init__(self, parent, nome_regiao, subtitulo_geo, prefixos_arquivos, descricoes_camadas, semente_procedural=42):
        super().__init__(parent, bg=COR_FUNDO)
        self.nome_regiao = nome_regiao
        self.subtitulo_geo = subtitulo_geo
        self.prefixos_arquivos = prefixos_arquivos
        self.descricoes_camadas = descricoes_camadas
        self.imagens_carregadas = []
        self.largura_tela = 860
        self.altura_tela = 450
        self.pasta_base = os.path.dirname(os.path.abspath(__file__))

        # Variáveis de controle de suavização (inércia) e animação
        self.altitude_atual = 35000.0
        self.altitude_alvo = 35000.0
        self.animacao_ativa = False
        self.albedo_ativo = tk.BooleanVar(value=True)

        if not PIL_DISPONIVEL:
            tk.Label(
                self,
                text="Biblioteca 'pillow' não instalada.\nRode 'pip install pillow' no terminal.",
                fg=COR_AMBAR, bg=COR_FUNDO, font=("Segoe UI", 12, "bold"), pady=80
            ).pack()
            return

        # Pré-carrega e já aplica nitidez base nas 7 camadas para resposta ultrarrápida
        for i in range(1, 8):
            img_encontrada = None
            for prefixo in prefixos_arquivos:
                for ext in (".jpg", ".png", ".jpeg"):
                    caminho = os.path.join(self.pasta_base, f"{prefixo}{i}{ext}")
                    if os.path.exists(caminho):
                        img = Image.open(caminho).convert("RGB").resize(
                            (self.largura_tela, self.altura_tela), Image.Resampling.LANCZOS
                        )
                        img_encontrada = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=125, threshold=3))
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
        # --- CONTAINER SUPERIOR DO VIEWPORT ---
        frame_viewport = tk.Frame(self, bg=COR_BORDA, padx=2, pady=2)
        frame_viewport.pack(padx=16, pady=(10, 6))

        self.canvas = tk.Canvas(
            frame_viewport, width=self.largura_tela, height=self.altura_tela,
            bg="#05070b", highlightthickness=0
        )
        self.canvas.pack()

        # Suporte a zoom fluido com a rodinha do mouse (Scroll Wheel) diretamente no mapa!
        self.canvas.bind("<MouseWheel>", self._ao_rolar_mouse)
        self.canvas.bind("<Button-4>", lambda e: self._ajustar_zoom_relativo(0.82))
        self.canvas.bind("<Button-5>", lambda e: self._ajustar_zoom_relativo(1.22))

        # --- PAINEL DE TELEMETRIA FORENSE (CARDS) ---
        frame_telemetria = tk.Frame(self, bg=COR_PAINEL, highlightbackground=COR_BORDA, highlightthickness=1)
        frame_telemetria.pack(fill="x", padx=16, pady=4)

        # Linha superior de badges técnicos
        linha_badges = tk.Frame(frame_telemetria, bg=COR_PAINEL)
        linha_badges.pack(fill="x", padx=14, pady=(8, 4))

        self.lbl_badge_nivel = tk.Label(
            linha_badges, text="BAIXA RESOLUÇÃO", bg="#1e293b", fg=COR_CIANO,
            font=("Segoe UI", 9, "bold"), padx=10, pady=3
        )
        self.lbl_badge_nivel.pack(side="left")

        self.lbl_altitude = tk.Label(
            linha_badges, text="ALTITUDE: 35.000 m", bg=COR_PAINEL, fg=COR_TEXTO,
            font=("Consolas", 11, "bold"), padx=14
        )
        self.lbl_altitude.pack(side="left")

        self.lbl_camada_info = tk.Label(
            linha_badges, text="CAMADA 1/7  •  ZOOM ÓPTICO: 1.00x", bg=COR_PAINEL, fg=COR_TEXTO_SUAVE,
            font=("Consolas", 10)
        )
        self.lbl_camada_info.pack(side="right")

        # Descrição detalhada da cena
        self.lbl_descricao = tk.Label(
            frame_telemetria, text="", bg=COR_PAINEL, fg=COR_TEXTO,
            font=("Segoe UI", 10), anchor="w", justify="left"
        )
        self.lbl_descricao.pack(fill="x", padx=14, pady=(2, 2))

        self.lbl_albedo_status = tk.Label(
            frame_telemetria, text="", bg=COR_PAINEL, fg=COR_VERDE,
            font=("Consolas", 9), anchor="w", justify="left"
        )
        self.lbl_albedo_status.pack(fill="x", padx=14, pady=(0, 8))

        # --- PAINEL DE CONTROLES INTERATIVOS ---
        frame_controles = tk.Frame(self, bg=COR_PAINEL, highlightbackground=COR_BORDA, highlightthickness=1)
        frame_controles.pack(fill="x", padx=16, pady=(4, 10))

        # Linha 1: Slider não-linear (escala logarítmica para zoom super suave em baixas altitudes!)
        linha_slider = tk.Frame(frame_controles, bg=COR_PAINEL)
        linha_slider.pack(fill="x", padx=14, pady=(8, 4))

        tk.Label(
            linha_slider, text="CONTROLE DE ALTITUDE (Arraste ou use a roda do mouse):",
            fg=COR_CIANO, bg=COR_PAINEL, font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        # Checkbox para ligar/desligar a correção de Albedo em tempo real
        chk_albedo = tk.Checkbutton(
            linha_slider, text="Correção Forense de Albedo / Relevo",
            variable=self.albedo_ativo, command=lambda: self.renderizar_quadro(self.altitude_atual),
            bg=COR_PAINEL, fg=COR_TEXTO, selectcolor="#1e293b",
            activebackground=COR_PAINEL, activeforeground=COR_CIANO,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        chk_albedo.pack(side="right")

        # Slider vai de 0 (35.000m) até 1000 (10m) usando curva exponencial para fluidez total
        self.slider_var = tk.DoubleVar(value=0.0)
        self.slider = tk.Scale(
            frame_controles, from_=0, to=1000, orient="horizontal",
            variable=self.slider_var, showvalue=False,
            bg=COR_PAINEL, fg=COR_TEXTO, troughcolor="#1e293b",
            activebackground=COR_CIANO, highlightthickness=0, bd=0,
            sliderlength=26, width=14, command=self._ao_mover_slider
        )
        self.slider.pack(fill="x", padx=14, pady=(2, 6))

        # Linha 2: Botões de Atalho Rápido (Presets de Altitude com voo suave!)
        linha_botoes = tk.Frame(frame_controles, bg=COR_PAINEL)
        linha_botoes.pack(fill="x", padx=14, pady=(2, 8))

        tk.Label(
            linha_botoes, text="Voo Rápido:", fg=COR_TEXTO_SUAVE,
            bg=COR_PAINEL, font=("Segoe UI", 9)
        ).pack(side="left", padx=(0, 8))

        presets = [
            ("🛰️ Órbita (35 km)", 35000),
            ("🌍 Continental (15 km)", 15000),
            ("🏔️ Regional (5 km)", 5000),
            ("❄️ Alta Res. (600 m)", 600),
            ("🔬 Procedural (50 m)", 50),
        ]
        for texto_btn, alt_destino in presets:
            btn = tk.Button(
                linha_botoes, text=texto_btn,
                command=lambda a=alt_destino: self.voar_para_altitude(a),
                bg="#1e293b", fg=COR_TEXTO, activebackground=COR_CIANO,
                activeforeground="#0b0f17", relief="flat", padx=10, pady=3,
                font=("Segoe UI", 8, "bold"), cursor="hand2"
            )
            btn.pack(side="left", padx=4)

    # --- CONVERSÃO EXPONENCIAL PARA ZOOM FLUIDO ---
    def _slider_para_altitude(self, pos):
        """Converte posição linear do slider (0..1000) em altitude logarítmica (35.000m..10m)."""
        t = max(0.0, min(1.0, float(pos) / 1000.0))
        alt = 35000.0 * ((10.0 / 35000.0) ** t)
        return max(10, min(35000, int(round(alt))))

    def _altitude_para_slider(self, altitude):
        """Converte altitude (35.000m..10m) para posição do slider (0..1000)."""
        alt = max(10.0, min(35000.0, float(altitude)))
        t = math.log(alt / 35000.0) / math.log(10.0 / 35000.0)
        return t * 1000.0

    def _ao_mover_slider(self, valor):
        alt = self._slider_para_altitude(valor)
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
        """Animação suave de voo (easing) entre altitudes."""
        self.altitude_alvo = float(max(10, min(35000, destino)))
        if not self.animacao_ativa:
            self.animacao_ativa = True
            self._passo_animacao()

    def _passo_animacao(self):
        diff = self.altitude_alvo - self.altitude_atual
        if abs(diff) < 1.5:
            self.altitude_atual = self.altitude_alvo
            self.slider_var.set(self._altitude_para_slider(self.altitude_atual))
            self.renderizar_quadro(int(round(self.altitude_atual)))
            self.animacao_ativa = False
            return

        # Interpolação suave (22% da distância por frame a ~60 FPS)
        self.altitude_atual += diff * 0.22
        alt_int = int(round(self.altitude_atual))
        self.slider_var.set(self._altitude_para_slider(self.altitude_atual))
        self.renderizar_quadro(alt_int)
        self.after(16, self._passo_animacao)

    def _recortar_zoom_continuo(self, img, fator_zoom):
        """Aplica zoom óptico progressivo suave dentro da mesma camada antes de trocar para a próxima."""
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
        """
        Combina:
        1. Zoom óptico progressivo dentro de cada camada (eliminando saltos bruscos);
        2. Correção forense de Albedo e realce de relevo;
        3. Síntese procedural de micro-fendas abaixo de 200 m.
        """
        img_proc = self._recortar_zoom_continuo(img_base, fator_zoom_camada)

        if altitude < LIMITE_PROCEDURAL:
            progresso = (LIMITE_PROCEDURAL - altitude) / (LIMITE_PROCEDURAL - 10)
            intensidade_procedural = min(0.42, 0.10 + progresso * 0.32)
            img_proc = Image.blend(img_proc, self.mapa_procedural, intensidade_procedural)
            img_proc = img_proc.filter(ImageFilter.UnsharpMask(radius=1.8, percent=150, threshold=2))

        if self.albedo_ativo.get():
            if altitude > LIMITE_BAIXA:
                img_proc = ImageEnhance.Contrast(img_proc).enhance(1.06)
            elif altitude >= LIMITE_ALTA:
                img_proc = ImageEnhance.Contrast(img_proc).enhance(1.18)
                img_proc = ImageEnhance.Brightness(img_proc).enhance(0.95)
            else:
                img_proc = ImageEnhance.Contrast(img_proc).enhance(1.32)
                img_proc = ImageEnhance.Brightness(img_proc).enhance(0.88)
                img_proc = ImageEnhance.Color(img_proc).enhance(1.12)

        return img_proc

    def renderizar_quadro(self, altitude):
        # Determina qual das 7 camadas usar e calcula o zoom progressivo interno (1.00x a 1.38x)
        limites = self.LIMITES_CAMADAS
        if altitude >= LIMITE_PROCEDURAL:
            idx_img = 6
            fator_zoom = 1.0
            for i in range(7):
                teto = limites[i]
                piso = limites[i + 1]
                if altitude >= piso or i == 6:
                    idx_img = i
                    progresso_faixa = (teto - altitude) / max(1, (teto - piso))
                    progresso_faixa = max(0.0, min(1.0, progresso_faixa))
                    fator_zoom = 1.0 + (progresso_faixa * 0.36)
                    break
            idx_desc = idx_img
        else:
            idx_img = 6
            idx_desc = 7
            progresso_proc = (LIMITE_PROCEDURAL - altitude) / (LIMITE_PROCEDURAL - 10)
            fator_zoom = 1.36 + (progresso_proc * 1.64)  # Vai de 1.36x até 3.00x no modo procedural

        # Atualiza badges e textos
        if altitude > LIMITE_BAIXA:
            nivel_txt = "BAIXA RESOLUÇÃO (> 10.000 m)"
            cor_badge = COR_CIANO
            albedo_txt = "ALBEDO: Passivo (visão orbital — alta reflexão atmosférica e nuvens)"
        elif altitude >= LIMITE_ALTA:
            nivel_txt = "MÉDIA RESOLUÇÃO (1.000 m a 10.000 m)"
            cor_badge = COR_AMBAR
            albedo_txt = "ALBEDO: Moderado (realce de bordas costeiras e artefatos de costura/stitching)"
        elif altitude >= LIMITE_PROCEDURAL:
            nivel_txt = "ALTA RESOLUÇÃO SATÉLITE (200 m a 1.000 m)"
            cor_badge = COR_VERDE
            albedo_txt = "ALBEDO: Correção Ativa (redução de brilho para evitar estouro de branco no gelo)"
        else:
            nivel_txt = "MICRO-ESCALA PROCEDURAL (< 200 m)"
            cor_badge = COR_ROXO
            albedo_txt = "SÍNTESE PROCEDURAL: Ruído fractal + micro-fendas glaciares geradas em tempo real"

        if not self.albedo_ativo.get():
            albedo_txt = "ALBEDO: Desativado pelo usuário (exibindo textura bruta sem correção de luz)"

        self.lbl_badge_nivel.config(text=nivel_txt, fg=cor_badge)
        self.lbl_altitude.config(text=f"ALTITUDE: {altitude:,} m".replace(",", "."))
        camada_str = "PROCEDURAL" if altitude < LIMITE_PROCEDURAL else f"CAMADA {idx_img + 1}/7"
        self.lbl_camada_info.config(text=f"{camada_str}  •  ZOOM INTERPOLADO: {fator_zoom:.2f}x")
        self.lbl_descricao.config(text=f"Cena: {self.descricoes_camadas[idx_desc]}")
        self.lbl_albedo_status.config(text=albedo_txt, fg=cor_badge if self.albedo_ativo.get() else COR_TEXTO_SUAVE)

        # Renderiza no Canvas
        self.canvas.delete("all")
        img_base = self.imagens_carregadas[idx_img]

        if img_base is None:
            exemplo_nome = f"{self.prefixos_arquivos[0]}{idx_img + 1}.jpg"
            self.canvas.create_text(
                self.largura_tela // 2, self.altura_tela // 2,
                text=f"[{self.nome_regiao} — Camada {idx_img + 1}/7 aguardando '{exemplo_nome}']\n"
                     f"Salve as imagens na mesma pasta do script.py",
                fill=COR_TEXTO_SUAVE, font=("Segoe UI", 12), justify="center"
            )
        else:
            img_final = self.processar_imagem(img_base, altitude, fator_zoom)
            self.foto_tk = ImageTk.PhotoImage(img_final)
            self.canvas.create_image(0, 0, anchor="nw", image=self.foto_tk)

            # Mira discreta estilo HUD geoespacial no centro da tela
            cx, cy = self.largura_tela // 2, self.altura_tela // 2
            self.canvas.create_line(cx - 14, cy, cx - 5, cy, fill="#38bdf8", width=1)
            self.canvas.create_line(cx + 5, cy, cx + 14, cy, fill="#38bdf8", width=1)
            self.canvas.create_line(cx, cy - 14, cx, cy - 5, fill="#38bdf8", width=1)
            self.canvas.create_line(cx, cy + 5, cx, cy + 14, fill="#38bdf8", width=1)

            # Coordenadas e região no canto inferior esquerdo do mapa
            self.canvas.create_rectangle(10, self.altura_tela - 32, 370, self.altura_tela - 8, fill="#0b0f17", outline=COR_BORDA)
            self.canvas.create_text(
                18, self.altura_tela - 20, anchor="w",
                text=self.subtitulo_geo, fill=COR_CIANO, font=("Consolas", 9, "bold")
            )


class MiniGoogleEarthApp:
    """Janela principal com design moderno e navegação por abas."""

    def __init__(self, root):
        self.root = root
        self.root.title("TerraVision vs. Google Earth — Análise Forense LoD (Tema 7: Regiões Polares)")
        self.root.configure(bg=COR_FUNDO)
        self.root.resizable(False, False)

        # Cabeçalho estilizado
        header = tk.Frame(root, bg=COR_PAINEL, highlightbackground=COR_BORDA, highlightthickness=1)
        header.pack(fill="x", padx=16, pady=(12, 6))

        tk.Label(
            header,
            text="ANÁLISE FORENSE: TERRAVISION × GOOGLE EARTH",
            fg=COR_CIANO, bg=COR_PAINEL, font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=14, pady=8)

        tk.Label(
            header,
            text="Tema 7: Regiões Polares & Calotas de Gelo (LoD + Albedo + Síntese Procedural)",
            fg=COR_TEXTO_SUAVE, bg=COR_PAINEL, font=("Segoe UI", 9)
        ).pack(side="right", padx=14, pady=8)

        # Estilo personalizado das abas (ttk.Notebook)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background="#161f2e", foreground=COR_TEXTO_SUAVE,
            padding=[22, 8], font=("Segoe UI", 10, "bold"), borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#1e293b")],
            foreground=[("selected", COR_CIANO)]
        )

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        # --- ABA 1: POLO SUL (ANTÁRTIDA) ---
        descricoes_polo_sul = [
            "Visão Orbital Global — Cobertura atmosférica e calota polar vista do espaço",
            "Contorno Continental da Antártida — Artefatos de costura (stitching) visíveis no gelo",
            "Plataforma Costeira (Terra de Wilkes) — Contraste Figura-Fundo entre gelo e oceano",
            "Aproximação Regional (Casey Station) — Afloramentos rochosos e borda da geleira",
            "Zona de Fratura Costeira — Início do desprendimento de blocos de gelo no mar",
            "Detalhe Glacial (AB Dobrowolski Polar Station) — Fendas e mosaico de gelo fragmentado",
            "Zoom Máximo Satélite (Ilha Mill) — Blocos de gelo flutuantes e relevo costeiro",
            "Síntese Procedural (< 200 m) — Micro-fendas glaciares e granulação geradas matematicamente",
        ]
        aba_sul = AbaRegiaoPolar(
            self.notebook,
            nome_regiao="Polo Sul (Antártida)",
            subtitulo_geo="ANTÁRTIDA • 66°17'S 110°31'E (TERRA DE WILKES)",
            prefixos_arquivos=["polo_sul_", "polo_sul"],
            descricoes_camadas=descricoes_polo_sul,
            semente_procedural=42
        )
        self.notebook.add(aba_sul, text="  ❄️  POLO SUL (ANTÁRTIDA)  ")

        # --- ABA 2: GROENLÂNDIA ---
        descricoes_groenlandia = [
            "Visão Orbital Regional — Groenlândia, Arquipélago Ártico e Islândia",
            "Contorno Continental — Mar de Baffin, Islândia e massa central de gelo (Albedo alto)",
            "Costa Leste (Summit Camp a Ittoqqortoormiit) — Artefato triangular de costura (stitching)",
            "Rede de Fiordes (Myggbukta, Traill Øer e Mestersvig) — Contraste entre rocha, gelo e mar",
            "Aproximação Glacial (Traill Øer / Mestersvig) — Línguas de gelo encaixadas nos vales",
            "Detalhe Topográfico (Ymer Øer) — Relevo montanhoso exposto e faixa de mosaico",
            "Zoom Máximo Satélite (Costa Ártica) — Geleira de vale, morainas e gelo marinho fragmentado",
            "Síntese Procedural (< 200 m) — Micro-fendas glaciares e relevo rochoso gerados matematicamente",
        ]
        aba_groenlandia = AbaRegiaoPolar(
            self.notebook,
            nome_regiao="Groenlândia",
            subtitulo_geo="GROENLÂNDIA • 72°14'N 23°55'W (COSTA LESTE)",
            prefixos_arquivos=["gro", "groenlandia_", "groenlandia"],
            descricoes_camadas=descricoes_groenlandia,
            semente_procedural=99
        )
        self.notebook.add(aba_groenlandia, text="  🧊  GROENLÂNDIA  ")


if __name__ == "__main__":
    print("=== EXECUÇÃO DA FUNÇÃO OBRIGATÓRIA (LoD) ===")
    carregar_camada_satelite([35000, 12000, 8500, 3200, 450])

    janela = tk.Tk()
    app = MiniGoogleEarthApp(janela)
    janela.mainloop()
