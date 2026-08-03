#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera scores.json para landing page no formato antigo:
- Fundamental: 35 pontos (max)
- Valuation: 25 pontos (max)
- Dividendos: 10 pontos (max)
- Momentum: 35 pontos (max)
- Total: 100 pontos (max)
"""

import json
from pathlib import Path

# Config
ROE_MINIMO = 0.10
ROIC_MINIMO = 0.08
DIVIDA_LIQUIDA_EBITDA_MAX = 3.0
PL_MAXIMO = 20
PL_MINIMO = 3
PVP_MAXIMO = 3
DY_MINIMO = 0.02

# Caminhos
DATA_DIR = Path(__file__).parent / 'data'

# Carrega fundamentais
with open(DATA_DIR / 'fundamentais.json', 'r', encoding='utf-8') as f:
    fundamentais = json.load(f)

# Carrega momentums
momentums = {}
momentums_file = DATA_DIR / 'momentums.json'
if momentums_file.exists():
    with open(momentums_file, 'r', encoding='utf-8') as f:
        momentums = json.load(f)
    print(f"Carregados {len(momentums)} momentums")
else:
    print("Arquivo momentums.json nao encontrado")

resultados = []

for ticker, fund in fundamentais.items():
    print(f"\nCalculando score de {ticker}...")
    
    # SCORE FUNDAMENTAL (0-35 pontos)
    score_fund = 0
    
    # ROE (10 pts)
    roe = fund.get('roe')
    if roe and roe >= ROE_MINIMO:
        score_fund += 10
        print(f"  ROE: {roe:.1%} (>= {ROE_MINIMO:.0%}) +10")
    elif roe:
        print(f"  ROE: {roe:.1%} (< {ROE_MINIMO:.0%}) +0")
    
    # ROIC (10 pts) - nao disponivel no yfinance
    roic = fund.get('roic')
    if roic and roic >= ROIC_MINIMO:
        score_fund += 10
        print(f"  ROIC: {roic:.1%} +10")
    else:
        print(f"  ROIC: N/A +0")
    
    # Divida/EBITDA (10 pts)
    divida = fund.get('divida_ebitda')
    if divida and divida <= DIVIDA_LIQUIDA_EBITDA_MAX:
        score_fund += 10
        print(f"  Divida/EBITDA: {divida:.1f} (<= {DIVIDA_LIQUIDA_EBITDA_MAX}) +10")
    elif divida:
        print(f"  Divida/EBITDA: {divida:.1f} (> {DIVIDA_LIQUIDA_EBITDA_MAX}) +0")
    else:
        print(f"  Divida/EBITDA: N/A +0")
    
    # SCORE VALUATION (0-25 pontos)
    score_val = 0
    
    # P/L (12 pts)
    pl = fund.get('pl')
    if pl and PL_MINIMO <= pl <= PL_MAXIMO:
        score_val += 12
        print(f"  P/L: {pl:.1f} (entre {PL_MINIMO}-{PL_MAXIMO}) +12")
    elif pl:
        print(f"  P/L: {pl:.1f} (fora da faixa) +0")
    
    # P/VP (13 pts)
    pvp = fund.get('pvp')
    if pvp and 0 < pvp <= PVP_MAXIMO:
        score_val += 13
        print(f"  P/VP: {pvp:.2f} (<= {PVP_MAXIMO}) +13")
    elif pvp:
        print(f"  P/VP: {pvp:.2f} (> {PVP_MAXIMO}) +0")
    
    # SCORE DIVIDENDOS (0-10 pontos)
    score_div = 0
    dy = fund.get('dy')
    if dy and dy >= DY_MINIMO:
        score_div = 10
        print(f"  DY: {dy:.1f}% (>= {DY_MINIMO:.0%}) +10")
    elif dy:
        print(f"  DY: {dy:.1f}% (< {DY_MINIMO:.0%}) +0")
    
    # SCORE MOMENTUM (0-35 pontos)
    ticker_short = ticker.replace('.SA', '')
    if ticker_short in momentums:
        score_mom = momentums[ticker_short]
        print(f"  Momentum: {score_mom}/35 (real)")
    else:
        score_mom = 15  # Medio padrao
        print(f"  Momentum: {score_mom}/35 (padrao)")
    
    # SCORE COMPOSTO (soma direta: 35 + 25 + 10 + 35 = 105 max)
    score_composto = score_fund + score_val + score_div + score_mom
    
    resultado = {
        'ticker': ticker,
        'nome': fund.get('nome'),
        'preco': fund.get('preco_atual'),
        'preco_atual': fund.get('preco_atual'),
        'setor': fund.get('setor'),
        'roe': roe,
        'pl': pl,
        'pvp': pvp,
        'dy': dy,
        'score_fundamental': score_fund,
        'score_momentum': score_mom,
        'score_valuation': score_val,
        'score_dividendos': score_div,
        'score_liquidez': 100,
        'score_composto': score_composto,
        'euforia': 'False',
        'detalhes_euforia': {
            'euforia': 'False',
            'preco_atual': fund.get('preco_atual'),
            'mm52': 0,
            'percentual_acima': 0,
            'limite': 25
        }
    }
    
    resultados.append(resultado)
    print(f"  SCORE TOTAL: {score_composto}")

# Ordena por score
resultados.sort(key=lambda x: x['score_composto'], reverse=True)

# Salva
with open(DATA_DIR / 'scores.json', 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print("RANKING FINAL:")
print("=" * 60)
for i, r in enumerate(resultados[:20], 1):
    print(f"{i}. {r['ticker']}: {r['score_composto']} (F:{r['score_fundamental']} V:{r['score_valuation']} D:{r['score_dividendos']} M:{r['score_momentum']})")
print("=" * 60)
print(f"Total: {len(resultados)} acoes")
print("Scores salvos em data/scores.json")
