#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calcula scores reais das 5 acoes"""

import json
import config

# Carrega fundamentais
with open('data/fundamentais.json', 'r', encoding='utf-8') as f:
    fundamentais = json.load(f)

resultados = []

for ticker, fund in fundamentais.items():
    print(f"Calculando score de {ticker}...")
    
    # SCORE FUNDAMENTAL (0-100)
    score_fund_pontos = 0
    total_fund = 30
    
    # ROE (10 pts)
    roe = fund.get('roe')
    if roe and roe >= config.ROE_MINIMO:
        score_fund_pontos += 10
        print(f"  ROE: {roe:.1%} (>= {config.ROE_MINIMO:.0%}) +10")
    elif roe:
        print(f"  ROE: {roe:.1%} (< {config.ROE_MINIMO:.0%}) +0")
    
    # ROIC (10 pts) - nao disponivel no yfinance
    roic = fund.get('roic')
    if roic and roic >= config.ROIC_MINIMO:
        score_fund_pontos += 10
        print(f"  ROIC: {roic:.1%} +10")
    else:
        print(f"  ROIC: N/A +0")
    
    # Divida/EBITDA (10 pts)
    divida = fund.get('divida_ebitda')
    if divida and divida <= config.DIVIDA_LIQUIDA_EBITDA_MAX:
        score_fund_pontos += 10
        print(f"  Divida/EBITDA: {divida:.1f} (<= {config.DIVIDA_LIQUIDA_EBITDA_MAX}) +10")
    elif divida:
        print(f"  Divida/EBITDA: {divida:.1f} (> {config.DIVIDA_LIQUIDA_EBITDA_MAX}) +0")
    else:
        print(f"  Divida/EBITDA: N/A +0")
    
    score_fund_normalizado = (score_fund_pontos / total_fund) * 100
    
    # SCORE VALUATION (0-25)
    score_val = 0
    
    # P/L (12 pts)
    pl = fund.get('pl')
    if pl and config.PL_MINIMO <= pl <= config.PL_MAXIMO:
        score_val += 12
        print(f"  P/L: {pl:.1f} (entre {config.PL_MINIMO}-{config.PL_MAXIMO}) +12")
    elif pl:
        print(f"  P/L: {pl:.1f} (fora da faixa) +0")
    
    # P/VP (13 pts)
    pvp = fund.get('pvp')
    if pvp and 0 < pvp <= config.PVP_MAXIMO:
        score_val += 13
        print(f"  P/VP: {pvp:.2f} (<= {config.PVP_MAXIMO}) +13")
    elif pvp:
        print(f"  P/VP: {pvp:.2f} (> {config.PVP_MAXIMO}) +0")
    
    # SCORE DIVIDENDOS (0-10)
    score_div = 0
    dy = fund.get('dy')
    if dy and dy >= config.DY_MINIMO:
        score_div = 10
        print(f"  DY: {dy:.1f}% (>= {config.DY_MINIMO:.0%}) +10")
    elif dy:
        print(f"  DY: {dy:.1f}% (< {config.DY_MINIMO:.0%}) +0")
    
    # SCORE MOMENTUM (0-35) - Precisa de dados historicos
    # Por enquanto, usa valor medio
    score_mom = 25  # Medio
    print(f"  Momentum: {score_mom} (simulado)")
    
    # SCORE COMPOSTO (normalizado para 0-100)
    # Cada pilar ja esta em escala 0-100 (ou convertido)
    score_fund_100 = score_fund_normalizado  # Ja 0-100
    score_mom_100 = (score_mom / 35) * 100   # Converte 0-35 para 0-100
    score_val_100 = (score_val / 25) * 100   # Converte 0-25 para 0-100
    score_div_100 = (score_div / 10) * 100   # Converte 0-10 para 0-100
    
    score_composto = (
        score_fund_100 * config.PESOS['fundamental'] / 100 +
        score_mom_100 * config.PESOS['momentum'] / 100 +
        score_val_100 * config.PESOS['valuation'] / 100 +
        score_div_100 * config.PESOS['dividendos'] / 100
    )
    
    resultado = {
        'ticker': ticker,
        'nome': fund.get('nome'),
        'preco': fund.get('preco_atual'),
        'setor': fund.get('setor'),
        'roe': roe,
        'pl': pl,
        'pvp': pvp,
        'dy': dy,
        'score_fundamental': round(score_fund_normalizado, 1),
        'score_momentum': score_mom,
        'score_valuation': score_val,
        'score_dividendos': score_div,
        'score_composto': round(score_composto, 1)
    }
    
    resultados.append(resultado)
    print(f"  SCORE TOTAL: {score_composto:.1f}")
    print()

# Ordena por score
resultados.sort(key=lambda x: x['score_composto'], reverse=True)

# Salva
with open('data/scores.json', 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print("=" * 60)
print("RANKING FINAL:")
print("=" * 60)
for i, r in enumerate(resultados, 1):
    print(f"{i}. {r['ticker']}: {r['score_composto']}")
print("=" * 60)
print("Scores salvos em data/scores.json")
