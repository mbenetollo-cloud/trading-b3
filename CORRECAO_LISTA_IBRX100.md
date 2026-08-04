---
tags: #trading #ibrx100 #correcao #lista
---

# Correcao da Lista IBrX100 - Ativos Fantasma

## Problema Identificado
Em 03/08/2026 (noite), foi identificado que a lista original do IBrX100 continha **15 ativosfantasma** (nao existentes ou incorretos).

## Fonte da Lista Correta
- **Fonte:** B3 - Carteira do Dia 03/08/2026
- **Download:** CSV oficial da B3
- **URL:** https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-amplos/indice-brasil-100-ibrx-100-composicao-da-carteira.htm

## Ativos Corretos (99 ativos)

### A
- ALOS3, ABEV3, ANIM3, ASAI3, AURE3, AXIA3, AZZA3

### B
- B3SA3, BBSE3, BBDC3, BBDC4, BRAP4, SAUD3, BBAS3
- BRKM5, BRAV3, BPAC11

### C
- CXSE3, CBAV3, CEAB3, CMIG4, COGN3, CSMG3, CPLE3
- CSAN3, CPFE3, CMIN3, CURY3, CVCB3, CYRE3

### D
- DIRR3

### E
- ECOR3, EMBJ3, ENGI11, ENEV3, EGIE3, EQTL3, EZTC3

### F
- FLRY3

### G
- GGBR4, GOAU4, GGPS3, GMAT3

### H
- HAPV3, HYPE3

### I
- IGTI11, INTB3, IRBR3, ISAE4, ITSA4, ITUB3, ITUB4

### J
- JHSF3

### K
- KLBN11

### L
- RENT3, LREN3

### M
- MGLU3, POMO4, MBRF3, BEEF3, MOTV3, MDNE3, MOVI3
- MRVE3, MULT3

### N
- NATU3

### O
- ORVR3

### P
- PETR3, PETR4, RECV3, AUAU3, PSSA3, PRIO3

### R
- RADL3, RAPT4, RDOR3, RAIL3

### S
- SBSP3, SAPR11, SANB11, SMTO3, CSNA3, SIMH3, SLCE3
- SMFT3, SUZB3

### T
- TAEE11, VIVT3, TEND3, TIMS3, TOTS3

### U
- UGPA3, USIM5

### V
- VALE3, VAMO3, VBBR3, VIVA3

### W
- WEGE3

### Y
- YDUQ3

## Total: 99 ativos

## Ativos Removidos (15 - hipoteticos)
*Nota: Os ativos fantasma nao foram documentados individualmente.*
*A lista acima e a versao correta validada.*

## Data da Correcao
- **03/08/2026 (noite):** Identificacao do problema
- **04/08/2026:** Correcao implementada nos scripts

## Scripts Atualizados
- fluxo_completo.py
- baixar_dados.py
- calcular_momentum.py
- coletar_fundamentais.py

## Impacto
- Antes: 114 ativos (15 fantasma)
- Depois: 99 ativos (corretos)
- Reducao: 15 ativos invalidos removidos

---

*Documento gerado em 04/08/2026*
*Validado com lista B3 03/08/2026*
