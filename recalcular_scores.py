#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recalcula scores com momentum real"""

import json
import config

# Carrega dados
with open('data/fundamentais.json', 'r', encoding='utf-8') as f:
    fundamentais = json.load(f)

with open('data/momentums.json', 'r') as f:
    momentums = json.load(f)

resultados = []

for ticker_short in ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3']:
    ticker = ticker_short + '.SA'
    fund = fundamentais[ticker]
    mom = momentums[ticker_short]
    
    print(f"\n{ticker_short}:")
    
    # SCORE FUNDAMENTAL (0-100)
    score_fund_pontos = 0
    
    roe = fund.get('roe')
    if roe and roe >= config.ROE_MINIMO:
        score_fund_pontos += 10
        print(f"  ROE: {roe:.1%} +10")
    
    roic = fund.get('roic')
    if roic and roic >= config.ROIC_MINIMO:
        score_fund_pontos += 10
    
    divida = fund.get('divida_ebitda')
    if divida and divida <= config.DIVIDA_LIQUIDA_EBITDA_MAX:
        score_fund_pontos += 10
        print(f"  Divida: {divida:.1f} +10")
    
    score_fund_normalizado = (score_fund_pontos / 30) * 100
    
    # SCORE VALUATION (0-100)
    score_val = 0
    pl = fund.get('pl')
    if pl and config.PL_MINIMO <= pl <= config.PL_MAXIMO:
        score_val += 12
        print(f"  P/L: {pl:.1f} +12")
    
    pvp = fund.get('pvp')
    if pvp and 0 < pvp <= config.PVP_MAXIMO:
        score_val += 13
        print(f"  P/VP: {pvp:.2f} +13")
    
    score_val_100 = (score_val / 25) * 100
    
    # SCORE DIVIDENDOS (0-100)
    score_div = 0
    dy = fund.get('dy')
    if dy and dy >= config.DY_MINIMO:
        score_div = 10
        print(f"  DY: {dy:.1f}% +10")
    
    score_div_100 = (score_div / 10) * 100
    
    # SCORE MOMENTUM (0-100)
    score_mom_100 = (mom / 35) * 100
    print(f"  Momentum: {mom}/35")
    
    # SCORE COMPOSTO
    score_composto = (
        score_fund_normalizado * config.PESOS['fundamental'] / 100 +
        score_mom_100 * config.PESOS['momentum'] / 100 +
        score_val_100 * config.PESOS['valuation'] / 100 +
        score_div_100 * config.PESOS['dividendos'] / 100
    )
    
    resultado = {
        'ticker': ticker_short,
        'nome': fund.get('nome'),
        'preco': fund.get('preco_atual'),
        'setor': fund.get('setor'),
        'roe': roe,
        'pl': pl,
        'pvp': pvp,
        'dy': dy,
        'score_fundamental': round(score_fund_normalizado, 1),
        'score_momentum': mom,
        'score_valuation': score_val,
        'score_dividendos': score_div,
        'score_composto': round(score_composto, 1)
    }
    
    resultados.append(resultado)
    print(f"  SCORE FINAL: {score_composto:.1f}")

# Ordena por score
resultados.sort(key=lambda x: x['score_composto'], reverse=True)

# Salva
with open('data/scores.json', 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print("RANKING FINAL COM MOMENTUM REAL:")
print("=" * 60)
for i, r in enumerate(resultados, 1):
    print(f"{i}. {r['ticker']}: {r['score_composto']}")
print("=" * 60)
