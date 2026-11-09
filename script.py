"""
Análise Forense TerraVision x Google Earth
Tema 7 - Regiões Polares e Calotas de Gelo (Reflexão Visual e Textura)

Instituição: Colégio Estadual Rodolpho Zaninelli
Curso: Técnico em Desenvolvimento de Sistemas | Turma: 3ºD
Disciplina: Computação Gráfica e Ciência de Dados
Professora: Angélica Neckel
Estudante: Gabriel Farias Nogueira

Simula o Level of Detail (LoD): quanto menor a altitude da câmera,
maior o nível de detalhe das texturas carregadas.
"""

# Limites de altitude (em metros) que separam os níveis de detalhe
LIMITE_BAIXA = 10000   # acima disso: baixa resolução
LIMITE_ALTA = 1000     # abaixo disso: alta resolução
MINIMO_ALTITUDES = 5   # exigência do trabalho


def carregar_camada_satelite(lista_altitudes):
    """
    Recebe uma lista com no mínimo 5 altitudes (metros) e decide qual
    camada de textura carregar para cada uma, usando LoD.

    Retorna uma lista de dicionários com os resultados.
    """
    # --- Validação de entrada ---
    if not isinstance(lista_altitudes, (list, tuple)):
        raise TypeError("A entrada deve ser uma lista de altitudes.")
    if len(lista_altitudes) < MINIMO_ALTITUDES:
        raise ValueError(
            f"Informe no mínimo {MINIMO_ALTITUDES} altitudes "
            f"(recebido: {len(lista_altitudes)})."
        )

    camadas = []

    for altitude in lista_altitudes:
        if altitude < 0:
            raise ValueError(f"Altitude inválida: {altitude} m.")

        # --- Level of Detail (LoD) ---
        if altitude > LIMITE_BAIXA:
            nivel = "Baixa Resolução"
            descricao = "Mosaico geral da Terra (visão global, polos como manchas brancas)"
            ajuste_albedo = False
        elif altitude >= LIMITE_ALTA:  # de 1.000 m a 10.000 m
            nivel = "Média Resolução"
            descricao = "Mosaico regional de calotas polares e geleiras"
            ajuste_albedo = False
        else:  # menor que 1.000 m
            nivel = "Alta Resolução"
            descricao = (
                "Detalhes finos de textura do gelo: ranhuras, fendas, "
                "com ajuste de reflexão de luz (albedo)"
            )
            ajuste_albedo = True

        camadas.append({
            "altitude_m": altitude,
            "nivel": nivel,
            "descricao": descricao,
            "ajuste_albedo": ajuste_albedo,
        })

        # --- Saída no console ---
        print(f"Altitude: {altitude:>7} m | {nivel}")
        print(f"   -> {descricao}")
        if ajuste_albedo:
            print("   -> Albedo: reduzir brilho e aumentar contraste local "
                  "para evitar estouro de brancos")

    return camadas


# --- Bateria de testes ---
if __name__ == "__main__":
    print("=== TESTE: carregar_camada_satelite ===\n")
    resultado = carregar_camada_satelite([35000, 12000, 8500, 3200, 450])

    print("\n=== RESUMO ===")
    for item in resultado:
        print(f"{item['altitude_m']:>7} m -> {item['nivel']}")
