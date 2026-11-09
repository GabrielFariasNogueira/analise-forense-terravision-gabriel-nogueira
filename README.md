#
Análise Forense: TerraVision × Google Earth
### Tema 7 – Regiões Polares e Calotas de Gelo (Reflexão Visual e Textura)

| | |
|---|---|
| **Instituição** | Colégio Estadual Rodolpho Zaninelli |
| **Curso** | Técnico em Desenvolvimento de Sistemas – Turma 3ºD |
| **Disciplina** | Computação Gráfica e Ciência de Dados |
| **Professora** | Angélica Neckel |
| **Estudante** | Gabriel Farias Nogueira |
| **Estudo de caso** | Disputa de patentes do TerraVision contra o Google Earth, retratada na minissérie *Batalha Bilionária: O Caso Google Earth* (Netflix, 2021) |

---

## 1. Contexto do caso

### 1.1 A minissérie

*Batalha Bilionária: O Caso Google Earth* (título original: *Billion Dollar Code*) é uma minissérie alemã de quatro episódios, dirigida por Robert Thalheim e lançada na Netflix em outubro de 2021. A história é baseada em fatos reais, mas dramatizada: os personagens são em parte ficcionais ou inspirados em pessoas reais. Por exemplo, Carsten Schlüter é parcialmente baseado no pioneiro da arte computacional Joachim Sauter (1959–2021), um dos fundadores da ART+COM.

A narrativa alterna duas linhas do tempo:

- **Anos 1990, em Berlim:** logo após a reunificação alemã, jovens programadores e artistas da cena hacker e de arte experimental criam o TerraVision, um software que permite "voar" sobre um modelo digital da Terra. A série mostra a busca por financiamento (como as reuniões com a Deutsche Telekom) e o idealismo da época, em contraste com o Vale do Silício que surgia.
- **Anos 2010, no tribunal:** os criadores processam o Google, alegando que o Google Earth usa a mesma ideia que eles inventaram e patentearam.

Em resumo, a série trata de uma pergunta central: **quem inventou a forma de navegar pela Terra inteira em um computador, e uma patente consegue provar isso?**

### 1.2 O que realmente aconteceu

| Ano | Fato |
|---|---|
| 1994 a 1996 | A ART+COM, de Berlim, desenvolve o **TerraVision**, uma representação virtual e em rede da Terra. A primeira implementação rodava em computadores SGI Onyx, os mais potentes da época para processamento gráfico. |
| 2004 | O Google compra a Keyhole, empresa cujo software dá origem ao Google Earth. |
| 2006 a 2007 | A ART+COM entra em contato com o Google. Michael Jones, então diretor de tecnologia do Google Earth, visita a empresa para discutir licenciamento ou compra da patente. A ART+COM recusa o valor oferecido e encerra as conversas em dezembro de 2007. |
| 2010 | Com a patente reemitida, a ART+COM avisa o Google de que o Google Earth pode precisar de licença. |
| Fev. 2014 | A **ART+COM Innovationpool** processa o Google em um tribunal federal de Delaware (EUA), pedindo cerca de US$ 100 milhões, por violação da patente **US RE44.550** ("Método e dispositivo para representação pictórica de dados espaciais"). |
| Mai. 2016 | Um júri decide a favor do Google: a patente foi considerada inválida por já ter sido antecipada por tecnologia anterior (*prior art*). |
| Out. 2017 | O Tribunal de Apelações do Circuito Federal dos EUA mantém a decisão, e o caso termina com a derrota da ART+COM. |

Um ponto que reforça o argumento da ART+COM: Michael Jones e Brian McClendon, executivos ligados ao Google Earth, trabalharam na SGI na época em que o TerraVision era desenvolvido, e McClendon também trabalhou na Keyhole. A defesa do Google, porém, sustentou que a patente descrevia algo que já existia antes, apoiando-se em um sistema anterior (o "SRI TerraVision", de outra instituição, sem relação com o da ART+COM, apesar do nome parecido).

> **Observação:** não confundir com outra disputa, anterior e distinta: *Skyline Software Systems* contra a Keyhole e o Google (2004 a 2008), que também tratava de visualização 3D da Terra, mas terminou em acordo. O caso da minissérie é o da ART+COM.

### 1.3 Por que este caso interessa à Computação Gráfica

A patente da ART+COM descreve, de forma geral, um método "do grosso ao fino" (*coarse-to-fine*) para solicitar, armazenar e exibir dados geográficos em múltiplas resoluções. Na prática, é o princípio do **Level of Detail (LoD)**: carregar primeiro uma imagem de baixa resolução e, conforme o usuário se aproxima, buscar camadas mais detalhadas.

É exatamente isso que o `script.py` deste repositório simula. Para um perito computacional, entender essa lógica é essencial para comparar duas tecnologias: duas aplicações podem parecer visualmente idênticas na tela e, mesmo assim, não haver violação, já que a patente protege um método específico, e não o resultado visual.

---

## 2. O código

O arquivo `script.py` implementa a função `carregar_camada_satelite(lista_altitudes)`, que exige no mínimo 5 altitudes (em metros) e escolhe o nível de detalhe com `if/elif/else`:

| Altitude da câmera | Nível | Conteúdo carregado |
|---|---|---|
| > 10.000 m | Baixa resolução | Mosaico geral da Terra |
| 1.000 m a 10.000 m | Média resolução | Mosaico regional de calotas polares e geleiras |
| < 1.000 m | Alta resolução | Textura fina do gelo (ranhuras, fendas) e ajuste de albedo |

### Como executar

```bash
python script.py
```

A bateria de testes usa a lista `[35000, 12000, 8500, 3200, 450]`, e a saída esperada é: baixa, baixa, média, média e alta resolução, nessa ordem.

---

## 3. Tratamento de Imagem: desafios de renderização polar

### 3.1 Albedo e brilho excessivo

**Albedo** é a fração da luz solar que uma superfície reflete. Neve e gelo recentes refletem cerca de 80% a 90% da luz, enquanto o oceano aberto e o solo escuro refletem muito menos. Isso gera problemas na renderização:

- **Estouro de brancos (clipping):** os pixels do gelo chegam ao valor máximo (255) e a informação de textura se perde. Ranhuras e fendas "somem" em um branco chapado.
- **Faixa dinâmica extrema:** uma mesma cena tem gelo muito claro e água ou rochas escuras, e o sensor não captura bem os dois extremos juntos.
- **Reflexão especular:** em gelo liso ou com água de degelo, o brilho do sol pode aparecer como mancha, confundindo o relevo real com reflexo.

**Soluções típicas:** correção gama, *tone mapping*, redução de exposição em áreas muito claras e normalização radiométrica entre cenas. No `script.py`, isso é representado pela flag `ajuste_albedo`, ativada apenas no nível de alta resolução, onde a textura precisa ser preservada.

### 3.2 Baixo contraste no gelo

Em áreas de gelo contínuo, a imagem tem poucas variações de tom. Gelo, neve e nuvens finas podem ficar quase idênticos, o que dificulta enxergar fendas, sastrugi (ondulações causadas pelo vento) e limites de geleiras.

**Soluções típicas:** equalização de histograma adaptativa (**CLAHE**), realce de bordas, uso de bandas espectrais além da visível (infravermelho) e filtros de nitidez aplicados com cuidado para não amplificar ruído.

### 3.3 Stitching (costura) de mosaicos

Montar o mosaico polar a partir de milhares de fotos de satélite tem dificuldades próprias:

1. **Poucos pontos de referência:** algoritmos de alinhamento (SIFT, ORB) dependem de pontos de interesse. Em extensões de gelo homogêneo, quase não há, e o alinhamento falha ou desliza.
2. **Datas e iluminação diferentes:** fotos tiradas em dias distintos, com o sol baixo típico dos polos, geram sombras longas e tons diferentes entre imagens vizinhas, deixando "emendas" visíveis.
3. **Distorção de projeção:** nos polos os meridianos convergem. Em projeções como a Mercator, a região polar é esticada ao extremo, então é preciso usar projeção apropriada (como a estereográfica polar) ou reprojetar as imagens.
4. **Mudanças no terreno:** o gelo se move e se transforma, então duas imagens da "mesma" área podem não coincidir.
5. **Nuvens e neblina:** cobertura frequente exige seleção das melhores cenas e remoção de nuvens.

**Soluções típicas:** correção radiométrica antes da junção, linhas de corte (*seamlines*) em regiões de baixo contraste e mesclagem em múltiplas bandas (*multi-band blending*, com pirâmides de Laplace) para suavizar as transições.

---

## 4. Design e Gestalt na UI ao aproximar o zoom no gelo polar

### 4.1 Lei da Figura-Fundo

A mente separa uma cena em um elemento em destaque (**figura**) e o restante (**fundo**).

- **No mapa:** em zoom intermediário, a calota ou geleira é a figura e o oceano escuro é o fundo. O forte contraste claro/escuro ajuda a identificar o limite do gelo.
- **O risco:** em zoom alto, gelo contra neve ou nuvem tem pouco contraste, e a figura se confunde com o fundo. O ajuste de albedo e contraste do `script.py` tem justamente a função de recuperar essa separação.
- **Na interface:** rótulos, ícones e painéis devem ter fundo semitransparente escuro ou contorno, pois texto branco sobre gelo branco fica ilegível. O elemento de UI precisa ser a figura, e o mapa, o fundo.

### 4.2 Lei da Continuidade

Percebemos elementos alinhados como parte de uma linha contínua, e o olhar tende a seguir curvas e direções sem interrupções bruscas.

- **No mapa:** fendas, ranhuras e bordas de geleiras formam trajetórias que o olho segue. Se o stitching falha e uma fenda aparece "cortada" na emenda entre dois tiles, a continuidade é quebrada e o usuário percebe um defeito.
- **Na navegação:** a transição entre níveis de LoD deve ser suave (*fade* ou interpolação), sem "saltos" que mudem de repente o aspecto do gelo. Zoom e rotação também devem seguir trajetórias contínuas, para o usuário não perder a referência de onde está. Essa fluidez é justamente o que a ART+COM destacava no TerraVision: uma navegação contínua por um volume enorme de dados.

---

## 5. Evidência Mapeada

> Captura de tela do Google Earth mostrando a calota polar em zoom, com a textura do gelo visível.

<img width="892" height="639" alt="print-polar-longe" src="https://github.com/user-attachments/assets/753a1966-f449-4db9-b7f8-23f99dc0c68a" />

<img width="666" height="781" alt="Captura de tela 2026-11-09 095032" src="https://github.com/user-attachments/assets/159a1c2d-c7e7-47c4-8cd0-375e960ef652" />


---

## 6. Estrutura do repositório

```
analise-forense-terravision-gabriel-nogueira/
├── script.py
├── README.md
└── print-polar.png
```

---

## 7. Conclusão

O caso TerraVision × Google Earth mostra que, em tecnologia, parecer igual não é o mesmo que ser igual: a Justiça americana concluiu que a patente da ART+COM não se sustentava, embora as duas interfaces sejam visualmente parecidas. O LoD, ideia central da disputa, resolve ao mesmo tempo um problema técnico (não carregar a Terra inteira de uma vez) e um problema de percepção (o que o usuário vê em cada altitude precisa ser legível). Nas regiões polares, albedo alto, baixo contraste e dificuldade de costura exigem tratamento específico de imagem, e os princípios de Figura-Fundo e Continuidade orientam como apresentar o resultado na interface.

---

## Referências

- *Batalha Bilionária: O Caso Google Earth* (*Billion Dollar Code*), minissérie, Netflix, 2021.
- Olhar Digital. "Batalha Bilionária: disputa judicial sobre o Google Earth inspira série da Netflix", 07/10/2021.
- Goethe-Institut. "Batalha bilionária: o caso Google Earth" (sobre a minissérie e a inspiração em Joachim Sauter).
- IPWatchdog. "CAFC affirms invalidity of geographic map visualization patent asserted against Google Earth", 25/10/2017.
- IPWatchdog. "Billion Dollar Code brings to life the nasty patent battle over Google Earth", 25/01/2022.
- United States Court of Appeals for the Federal Circuit. *ART+COM Innovationpool GmbH v. Google LLC*, nº 2017-1016, 20/10/2017.
- The Daily Dot. "German firm says Google infringed on its patent when it made Google Earth", 23/02/2014.
- Wikipedia. "Terravision (computer program)".
- Documentação de OpenCV sobre CLAHE e stitching; NSIDC (National Snow and Ice Data Center), sobre albedo e dados de gelo.
