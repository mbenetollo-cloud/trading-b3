#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcula portfolio ideal com R$ 10.000 - Ranking Atualizado 04/08/2026
"""

import json

# Carrega scoring
with open('D:\\Meus APP\ibrx100_system\\output\\data\\scores.json', 'r', encoding='utf-8') as f:
    scores = json.load(f)

# Regra: quando empresa tem ON (3) e PN (4), remove ON e keep PN
on_para_pn = {
    'PETR3': 'PETR4',
    'ITUB3': 'ITUB4',
    'BBDC3': 'BBDC4',
    'GOAU3': 'GOAU4',
    'CSNA3': 'CSNA4',
    'USIM3': 'USIM5',
}

# Coletar tickers para remover (ON quando existe PN)
tickers_para_remover = set()
for stock in scores:
    ticker = stock['ticker'].replace('.SA', '')
    if ticker in on_para_pn:
        tickers_para_remover.add(ticker)

# Filtra scores
scores_filtrados = [s for s in scores if s['ticker'].replace('.SA', '') not in tickers_para_remover]

print("=" * 70)
print("RANKING ATUALIZADO - 04/08/2026 (SEM DUPLICATAS)")
print("=" * 70)
for i, stock in enumerate(scores_filtrados[:10]):
    ticker = stock['ticker'].replace('.SA', '')
    print(f"  {i+1}. {ticker} - Score: {stock['score_composto']}")
print()

# Calcula portfolio
capital_inicial = 10000.00
capital_restante = capital_inicial
compras = []
max_tickers = 4

print("=" * 70)
print("PORTFOLIO SUGERIDO - R$ 10.000 (MAXIMO 4 ACOES)")
print("=" * 70)
print()

print(f"{'Rank':<6} {'Ticker':<10} {'Score':<8} {'Preco':<12} {'Qtd':<8} {'Total':<12} {'% Carteira':<12}")
print("-" * 78)

for i, stock in enumerate(scores_filtrados):
    if len(compras) >= max_tickers:
        break
    
    ticker = stock['ticker'].replace('.SA', '')
    preco = stock['preco_atual']
    score = stock['score_composto']
    custo = preco * 100
    
    if custo <= capital_restante:
        compras.append({
            'rank': i+1,
            'ticker': ticker,
            'score': score,
            'preco': preco,
            'quantidade': 100,
            'custo': custo
        })
        capital_restante -= custo
        qtd = 100
    else:
        qtd_parcial = int(capital_restante / preco)
        if qtd_parcial > 0:
            custo_parcial = preco * qtd_parcial
            compras.append({
                'rank': i+1,
                'ticker': ticker,
                'score': score,
                'preco': preco,
                'quantidade': qtd_parcial,
                'custo': custo_parcial
            })
            capital_restante -= custo_parcial
            qtd = qtd_parcial
        else:
            continue
    
    custo_total = preco * qtd
    pct = (custo_total / (capital_inicial - capital_restante)) * 100
    print(f"{i+1:<6} {ticker:<10} {score:<8} R$ {preco:<10.2f} {qtd:<8} R$ {custo_total:<10.2f} {pct:.1f}%")

print("-" * 78)

# Resumo
total_investido = capital_inicial - capital_restante

print()
print("RESUMO")
print("=" * 70)
print(f"Capital inicial:      R$ {capital_inicial:,.2f}")
print(f"Total investido:      R$ {total_investido:,.2f}")
print(f"Capital restante:     R$ {capital_restante:,.2f}")
print(f"Numero de tickers:    {len(compras)}")
print()

# Verificacao
empresas = [c['ticker'][:4] for c in compras]
if len(empresas) == len(set(empresas)):
    print("OK: Todas sao empresas diferentes!")
else:
    print("AVISO: Ha empresas duplicadas!")

print()
print("Acoes disponiveis mas que nao cabem no capital:")
for i, stock in enumerate(scores_filtrados):
    ticker = stock['ticker'].replace('.SA', '')
    if not any(c['ticker'] == ticker for c in compras):
        preco = stock['preco_atual']
        score = stock['score_composto']
        print(f"  {ticker} (Score: {score}) - R$ {preco*100:,.2f} para 100 acoes")