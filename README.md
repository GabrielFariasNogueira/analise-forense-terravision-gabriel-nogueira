# Análise Forense TerraVision / Google Earth - Regiões Polares e Calotas de Gelo

**Estudante:** Gabriel Farias Nogueira  
**Turma:** 3°D - Desenvolvimento de Sistemas  
**Disciplina:** Computação Gráfica & Ciência de Dados  
**Professora:** Angélica Neckel  
**Tema Designado:** Tema 7 - Regiões Polares e Calotas de Gelo (Reflexão Visual e Textura)  

---

## 1. Descrição do Projeto
Este repositório contém o estudo de caso e a análise analítica forense baseada na disputa de patentes entre o TerraVision (ART+COM) e o Google Earth, aplicando conceitos de Ciência de Dados (filtragem por Level of Detail) e Computação Gráfica / UX/UI no mapeamento de áreas de calotas polares.

---

## 2. Processamento e Tratamento de Imagem (Sensoriamento Remoto)
Ao renderizar regiões cobertas por gelo e neve, os algoritmos de visualização espacial enfrentam desafios específicos:

- **Reflexão da Luz e Efeito Albedo:** A neve e o gelo refletem grande parte da radiação solar, causando alta taxa de albedo. Isso gera imagens superexpostas ou estouradas ("glare"), onde se perdem as sombras e os relevos superficiais.
- **Falta de Contraste:** Em extensões contínuas de gelo, há ausência de pontos de referência visuais (landmarks) e baixo contraste tonal. Isso dificulta o algoritmo de *stitching* (costura de fotos de satélite) em identificar pontos de correspondência para alinhar os mosaicos.
- **Uniformização de Cor e Textura:** Para evitar descontinuidades visuais bruscas entre imagens obtidas por satélites em momentos diferentes (com ângulos solares e coberturas de nuvens distintas), o software aplica correções de exposição e equalização de histograma.

---

## 3. Design de Interface e Leis da Gestalt
Na interface do Google Earth / TerraVision, o design orienta a navegação intuitiva através das seguintes leis:

1. **Lei da Figura-Fundo:**
   - *Aplicação:* A massa de gelo polar brilhante atua como "Figura" destacada sobre o azul denso do oceano ("Fundo"). Essa separação de contraste permite que o usuário identifique instantaneamente os limites territoriais das plataformas de gelo, mesmo em altitudes elevadas.
2. **Lei da Continuidade:**
   - *Aplicação:* As fissuras, rachaduras no gelo e linhas de costa congeladas orientam o olhar do usuário. Ao aproximar o zoom, o algoritmo transiciona suavemente entre os níveis de resolução (LoD), mantendo o fluxo contínuo das linhas do relevo polar sem saltos visuais abruptos.

---

## 4. Evidência Mapeada (Captura de Tela)
![Calota Polar - Google Earth](link_da_sua_imagem_aqui.png)
*(Insira aqui o print do Google Earth mostrando uma região polar ou geleira)*

---

## 5. Histórico de Commits
- `feat: adiciona algoritmo de Level of Detail em script.py`
- `docs: adiciona analise de imagem e Gestalt no README.md`
