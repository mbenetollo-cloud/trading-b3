#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calcula momentum real das 5 acoes"""

import json
import config

ACOES = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3']

def calcular_rsl(precos, periodo=14):
    """Calcula Relative Strength Level"""
    if len(precos) < periodo:
        return 1.0
    retornos = []
    for i in range(1, len(precos)):
        ret = (precos[i] - precos[i-1]) / precos[i-1]
        retornos.append(ret)
    ultimos_retornos = retornos[-periodo:]
    retorno_acumulado = 1
    for r in ultimos_retornos:
        retorno_acumulado *= (1 + r)
    return retorno_acumulado

def calcular_mm(precos, periodo):
    """Calcula Media Movel"""
    if len(precos) < periodo:
        return None
    return sum(precos[-periodo:]) / periodo

def calcular_momentum(ticker):
    """Calcula score de momentum (0-35)"""
    # Carrega precos
    with open(f'data/{ticker}.json', 'r') as f:
        dados = json.load(f)
    
    precos = [d['close'] for d in dados]
    
    score = 0
    
    # RSL 14 (0-20 pontos)
    rsl = calcular_rsl(precos, 14)
    if rsl > 1.05:  # Forte alta
        score += 20
        print(f"    RSL 14: {rsl:.4f} (forte alta) +20")
    elif rsl > 1.0:  # Alta
        score += 15
        print(f"    RSL 14: {rsl:.4f} (alta) +15")
    elif rsl > 0.95:  # Estavel
        score += 10
        print(f"    RSL 14: {rsl:.4f} (estavel) +10")
    else:  # Baixa
        score += 5
        print(f"    RSL 14: {rsl:.4f} (baixa) +5")
    
    # MM50 vs MM200 (0-15 pontos)
    mm50 = calcular_mm(precos, 50)
    mm200 = calcular_mm(precos, 200)
    preco_atual = precos[-1]
    
    if mm50 and mm200:
        if preco_atual > mm50 > mm200:  # Tendencia de alta forte
            score += 15
            print(f"    MM50: {mm50:.2f} | MM200: {mm200:.2f} | Preco: {preco_atual:.2f} (alta forte) +15")
        elif preco_atual > mm50:  # Acima da MM50
            score += 10
            print(f"    MM50: {mm50:.2f} | Preco: {preco_atual:.2f} (acima MM50) +10")
        elif preco_atual > mm200:  # Acima da MM200
            score += 5
            print(f"    MM200: {mm200:.2f} | Preco: {preco_atual:.2f} (acima MM200) +5")
        else:
            print(f"    MM50: {mm50:.2f} | MM200: {mm200:.2f} | Preco: {preco_atual:.2f} (abaixo) +0")
    elif mm50:
        if preco_atual > mm50:
            score += 10
            print(f"    MM50: {mm50:.2f} | Preco: {preco_atual:.2f} (acima MM50) +10")
        else:
            print(f"    MM50: {mm50:.2f} | Preco: {preco_atual:.2f} (abaixo) +0")
    
    return score

print("=" * 60)
print("CALCULANDO MOMENTUM REAL")
print("=" * 60)

momentums = {}
for ticker in ACOES:
    print(f"\n{ticker}:")
    mom = calcular_momentum(ticker)
    momentums[ticker] = mom
    print(f"  SCORE MOMENTUM: {mom}/35")

print("\n" + "=" * 60)
print("MOMENTUMS:")
print("=" * 60)
for ticker, mom in sorted(momentums.items(), key=lambda x: x[1], reverse=True):
    print(f"  {ticker}: {mom}/35")

# Salva
with open('data/momentums.json', 'w') as f:
    json.dump(momentums, f, indent=2)

print("\nSalvo em data/momentums.json")
