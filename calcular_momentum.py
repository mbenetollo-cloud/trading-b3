#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calcula momentum real de todas as acoes"""

import json
import config
from pathlib import Path

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
    """Calcula score de momentum (0-30 pontos)"""
    # Carrega precos
    data_dir = Path(__file__).parent / 'data'
    arquivo = data_dir / f'{ticker}.json'
    
    if not arquivo.exists():
        print(f"    Arquivo nao encontrado: {arquivo}")
        return 0  # Sem dados = sem score
    
    with open(arquivo, 'r') as f:
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
    
    # MM50 vs MM200 (0-10 pontos)
    mm50 = calcular_mm(precos, 50)
    mm200 = calcular_mm(precos, 200)
    preco_atual = precos[-1]
    
    if mm50 and mm200:
        if preco_atual > mm50 > mm200:  # Tendencia de alta forte
            score += 10
            print(f"    MM50: {mm50:.2f} | MM200: {mm200:.2f} | Preco: {preco_atual:.2f} (alta forte) +10")
        elif preco_atual > mm50:  # Acima da MM50
            score += 7
            print(f"    MM50: {mm50:.2f} | Preco: {preco_atual:.2f} (acima MM50) +7")
        elif preco_atual > mm200:  # Acima da MM200
            score += 4
            print(f"    MM200: {mm200:.2f} | Preco: {preco_atual:.2f} (acima MM200) +4")
        else:
            print(f"    MM50: {mm50:.2f} | MM200: {mm200:.2f} | Preco: {preco_atual:.2f} (abaixo) +0")
    elif mm50:
        if preco_atual > mm50:
            score += 7
            print(f"    MM50: {mm50:.2f} | Preco: {preco_atual:.2f} (acima MM50) +7")
        else:
            print(f"    MM50: {mm50:.2f} | Preco: {preco_atual:.2f} (abaixo) +0")
    
    return score

# Carrega lista de tickers do IBrX100 (lista oficial B3)
data_dir = Path(__file__).parent / 'data'

# Lista oficial IBrX100 - B3 Carteira do Dia 03/08/2026
ACOES = [
    'ALOS3', 'ABEV3', 'ANIM3', 'ASAI3', 'AURE3', 'AXIA3', 'AZZA3',
    'B3SA3', 'BBSE3', 'BBDC3', 'BBDC4', 'BRAP4', 'SAUD3', 'BBAS3',
    'BRKM5', 'BRAV3', 'BPAC11', 'CXSE3', 'CBAV3', 'CEAB3', 'CMIG4',
    'COGN3', 'CSMG3', 'CPLE3', 'CSAN3', 'CPFE3', 'CMIN3', 'CURY3',
    'CVCB3', 'CYRE3', 'DIRR3', 'ECOR3', 'EMBJ3', 'ENGI11', 'ENEV3',
    'EGIE3', 'EQTL3', 'EZTC3', 'FLRY3', 'GGBR4', 'GOAU4', 'GGPS3',
    'GMAT3', 'HAPV3', 'HYPE3', 'IGTI11', 'INTB3', 'IRBR3', 'ISAE4',
    'ITSA4', 'ITUB3', 'ITUB4', 'JHSF3', 'KLBN11', 'RENT3', 'LREN3',
    'MGLU3', 'POMO4', 'MBRF3', 'BEEF3', 'MOTV3', 'MDNE3', 'MOVI3',
    'MRVE3', 'MULT3', 'NATU3', 'ORVR3', 'PETR3', 'PETR4', 'RECV3',
    'AUAU3', 'PSSA3', 'PRIO3', 'RADL3', 'RAPT4', 'RDOR3', 'RAIL3',
    'SBSP3', 'SAPR11', 'SANB11', 'SMTO3', 'CSNA3', 'SIMH3', 'SLCE3',
    'SMFT3', 'SUZB3', 'TAEE11', 'VIVT3', 'TEND3', 'TIMS3', 'TOTS3',
    'UGPA3', 'USIM5', 'VALE3', 'VAMO3', 'VBBR3', 'VIVA3', 'WEGE3', 'YDUQ3'
]

print("=" * 60)
print("CALCULANDO MOMENTUM REAL - TODAS AS ACOES (30 pontos)")
print("=" * 60)

momentums = {}
for ticker in ACOES:
    print(f"\n{ticker}:")
    mom = calcular_momentum(ticker)
    momentums[ticker] = mom
    print(f"  SCORE MOMENTUM: {mom}/30")

print("\n" + "=" * 60)
print("MOMENTUMS:")
print("=" * 60)
for ticker, mom in sorted(momentums.items(), key=lambda x: x[1], reverse=True):
    print(f"  {ticker}: {mom}/30")

# Salva
with open(data_dir / 'momentums.json', 'w') as f:
    json.dump(momentums, f, indent=2)

print("\nSalvo em data/momentums.json")
