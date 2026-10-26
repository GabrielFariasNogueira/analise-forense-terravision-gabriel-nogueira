"""
Trabalho Multidisciplinar - Computação Gráfica & Ciência de Dados
Professora: Angélica Neckel
Estudante: Gabriel Farias Nogueira
Tema 7: Regiões Polares e Calotas de Gelo (Reflexão Visual e Textura)
"""

def carregar_camada_satelite(lista_altitudes):
    """
    Simula a seleção de nível de detalhe (Level of Detail - LoD) de renderização
    geoespacial com base na altitude da câmera virtual.
    """
    print("--- INICIANDO PROCESSAMENTO DE NÍVEL DE DETALHE (LoD) ---")
    
    for idx, altitude in enumerate(lista_altitudes, start=1):
        print(f"\n[Captura {idx}] Altitude atual: {altitude}m")
        
        # Altitude maior que 10.000 metros: Baixa Resolução
        if altitude > 10000:
            print("  -> Status: Carregando camada de BAIXA RESOLUÇÃO.")
            print("  -> Renderizando: Mosaico global da Terra e continentes polarizados.")
            
        # Altitude entre 1.000 e 10.000 metros: Média Resolução
        elif 1000 <= altitude <= 10000:
            print("  -> Status: Carregando camada de MÉDIA RESOLUÇÃO.")
            print("  -> Renderizando: Mosaico regional de calotas polares, plataformas de gelo e grandes geleiras.")
            
        # Altitude menor que 1.000 metros: Alta Resolução
        else:
            print("  -> Status: Carregando camada de ALTA RESOLUÇÃO.")
            print("  -> Renderizando: Detalhes de textura do gelo, ranhuras glaciares, fendas e ajuste de reflexão de luz/albedo.")

# --- BATERIA DE TESTES ---
if __name__ == "__main__":
    # Lista com 5 altitudes simulando a aproximação da câmera virtual em metros
    altitudes_teste = [35000, 12000, 8500, 3200, 450]
    
    # Execução da função
    carregar_camada_satelite(altitudes_teste)