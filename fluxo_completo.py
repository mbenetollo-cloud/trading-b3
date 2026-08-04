#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILTRO SEMANAL - FLUXO COMPLETO
================================
1. IBrX100 (100 ações)
2. Filtro de exclusão (lucro/patrimônio/FCF negativos)
3. Score Fundamentalista (35 pts): Cresc.Lucro(15) + Margem(10) + Divida(10)
4. Score Valuation (25 pts): Cresc.Receita(10) + FCF(10) + Liquidez(5)
5. Top 30
6. Liquidez
7. Top 20
8. Momentum (30 pts) + Dividendos (10 pts)
9. Top 10 Compras
"""

import json
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

# Config
ROE_MINIMO = 0.10
PL_MAXIMO = 20
PL_MINIMO = 3
PVP_MAXIMO = 3
DY_MINIMO = 0.02
SCORE_MINIMO = 50
VOLUME_MINIMO = 1000000

# Caminhos
DATA_DIR = Path(__file__).parent / 'data'
OUTPUT_DIR = Path(__file__).parent

def obter_acoes_ibrx100():
    """Obtém ações do IBrX100 - Lista oficial B3 (03/08/2026)
    
    Fonte: https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-amplos/indice-brasil-100-ibrx-100-composicao-da-carteira.htm
    """
    # Lista oficial IBrX100 - B3 Carteira do Dia 03/08/2026
    tickers = [
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
    
    # Adiciona .SA para cada ticker
    codigos = [f"{t}.SA" for t in tickers]
    
    print(f"Obtidas {len(codigos)} ações do IBrX100 (lista oficial B3)")
    return codigos

def calcular_score_fundamental(fund):
    """Calcula score fundamental (0-35 pontos)
    
    Critérios:
    - Crescimento Lucro 5 anos (15 pts): earningsGrowth >= 0
    - Margem Líquida (10 pts): profitMargins >= 0.10
    - Dívida/EBITDA (10 pts): debtToEquity <= 150 (proxy)
    """
    score = 0
    
    # Crescimento Lucro (15 pts)
    cresc_lucro = fund.get('crescimento_lucro')
    if cresc_lucro is not None and cresc_lucro >= 0:
        score += 15
    
    # Margem Líquida (10 pts)
    margem = fund.get('margem_liquida')
    if margem is not None and margem >= 0.10:
        score += 10
    
    # Dívida/EBITDA (10 pts) - usa debtToEquity como proxy
    divida = fund.get('divida_ebitda')
    if divida is not None and divida <= 150:
        score += 10
    
    return score

def calcular_score_valuation(fund):
    """Calcula score valuation (0-25 pontos)
    
    Critérios:
    - Crescimento Receita 5 anos (10 pts): revenueGrowth >= 0
    - Fluxo de Caixa Livre (10 pts): freeCashflow > 0
    - Liquidez Corrente (5 pts): currentRatio >= 1.0
    """
    score = 0
    
    # Crescimento Receita (10 pts)
    cresc_receita = fund.get('crescimento_receita')
    if cresc_receita is not None and cresc_receita >= 0:
        score += 10
    
    # Fluxo de Caixa Livre (10 pts)
    fcf = fund.get('fcf')
    if fcf is not None and fcf > 0:
        score += 10
    
    # Liquidez Corrente (5 pts)
    liquidez = fund.get('liquidez_corrente')
    if liquidez is not None and liquidez >= 1.0:
        score += 5
    
    return score

def calcular_score_dividendos(fund):
    """Calcula score dividendos (0-10 pontos)"""
    dy = fund.get('dy')
    if dy and dy >= DY_MINIMO:
        return 10
    return 0

def calcular_score_momentum(ticker):
    """Calcula score momentum (0-30 pontos) e retorna dados de MM"""
    # Carrega dados de momentum
    momentums_file = OUTPUT_DIR / 'data' / 'momentums.json'
    mm50 = 0
    mm200 = 0
    
    if momentums_file.exists():
        with open(momentums_file, 'r', encoding='utf-8') as f:
            momentums = json.load(f)
        
        ticker_short = ticker.replace('.SA', '')
        if ticker_short in momentums:
            score = momentums[ticker_short]
            
            # Carrega dados de preço para calcular MM
            dados_file = OUTPUT_DIR / 'data' / f'{ticker_short}.json'
            if dados_file.exists():
                with open(dados_file, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                precos = [d['close'] for d in dados]
                if len(precos) >= 50:
                    mm50 = sum(precos[-50:]) / 50
                if len(precos) >= 200:
                    mm200 = sum(precos[-200:]) / 200
            return score, mm50, mm200
    
    return 0, mm50, mm200  # Sem dados = 0 pts

def filtrar_liquidez(acoes, fundamentais):
    """Filtra por liquidez (volume mínimo)"""
    acoes_liquidas = []
    for ticker in acoes:
        fund = fundamentais.get(ticker, {})
        # Volume mínimo: R$ 1.000.000 por dia
        # Estimativa: market_cap * 0.001 (0.1% do market cap)
        market_cap = fund.get('market_cap', 0)
        if market_cap and market_cap * 0.001 >= VOLUME_MINIMO:
            acoes_liquidas.append(ticker)
    return acoes_liquidas

def main():
    """Função principal"""
    print("=" * 60)
    print("FILTRO SEMANAL - FLUXO COMPLETO")
    print("=" * 60)
    print(f"Data: {datetime.now()}")
    print()
    
    # 1. Obtém ações do IBrX100
    print("1. Obtendo ações do IBrX100...")
    acoes_ibrx = obter_acoes_ibrx100()
    print(f"   Total: {len(acoes_ibrx)} ações")
    print()
    
    # 2. Carrega fundamentais
    print("2. Carregando fundamentais...")
    fundamentais_file = OUTPUT_DIR / 'data' / 'fundamentais.json'
    with open(fundamentais_file, 'r', encoding='utf-8') as f:
        fundamentais = json.load(f)
    print(f"   Total: {len(fundamentais)} ações com fundamentais")
    print()
    
    # 3. Filtro de exclusão
    print("3. Aplicando filtro de exclusão...")
    acoes_filtradas = []
    for ticker in acoes_ibrx:
        fund = fundamentais.get(ticker, {})
        
        # Exclui se lucro negativo
        roe = fund.get('roe')
        if roe and roe < 0:
            continue
        
        # Exclui se patrimônio negativo
        pvp = fund.get('pvp')
        if pvp and pvp < 0:
            continue
        
        # Exclui se FCF negativo
        fcf = fund.get('fcf')
        if fcf and fcf < 0:
            continue
        
        acoes_filtradas.append(ticker)
    
    print(f"   Excluídas: {len(acoes_ibrx) - len(acoes_filtradas)} ações")
    print(f"   Restantes: {len(acoes_filtradas)} ações")
    print()
    
    # 4. Score Fundamentalista
    print("4. Calculando score fundamentalista...")
    scores_fund = []
    for ticker in acoes_filtradas:
        fund = fundamentais.get(ticker, {})
        score = calcular_score_fundamental(fund)
        scores_fund.append((ticker, score))
    
    # Ordena por score
    scores_fund.sort(key=lambda x: x[1], reverse=True)
    print(f"   Top 5:")
    for i, (ticker, score) in enumerate(scores_fund[:5], 1):
        print(f"   {i}. {ticker}: {score}/35")
    print()
    
    # 5. Score Valuation
    print("5. Calculando score valuation...")
    scores_val = []
    for ticker, score_fund in scores_fund:
        fund = fundamentais.get(ticker, {})
        score_val = calcular_score_valuation(fund)
        score_total = score_fund + score_val
        scores_val.append((ticker, score_total, score_fund, score_val))
    
    # Ordena por score total
    scores_val.sort(key=lambda x: x[1], reverse=True)
    print(f"   Top 5:")
    for i, (ticker, total, fund, val) in enumerate(scores_val[:5], 1):
        print(f"   {i}. {ticker}: {total}/60 (F:{fund} V:{val})")
    print()
    
    # 6. Top 30
    print("6. Selecionando Top 30...")
    top_30 = [t for t, _, _, _ in scores_val[:30]]
    print(f"   Top 30: {len(top_30)} ações")
    print()
    
    # 7. Liquidez
    print("7. Aplicando filtro de liquidez...")
    acoes_liquidas = filtrar_liquidez(top_30, fundamentais)
    print(f"   Liquidas: {len(acoes_liquidas)} ações")
    print()
    
    # 8. Top 20
    print("8. Selecionando Top 20...")
    top_20 = acoes_liquidas[:20]
    print(f"   Top 20: {len(top_20)} ações")
    print()
    
    # 9. RSL + Tendência
    print("9. Calculando RSL + Tendência...")
    scores_momentum = []
    for ticker in top_20:
        score_mom, mm50, mm200 = calcular_score_momentum(ticker)
        fund = fundamentais.get(ticker, {})
        score_fund = calcular_score_fundamental(fund)
        score_val = calcular_score_valuation(fund)
        score_div = calcular_score_dividendos(fund)
        score_total = score_fund + score_val + score_div + score_mom
        scores_momentum.append({
            'ticker': ticker,
            'score_fundamental': score_fund,
            'score_valuation': score_val,
            'score_dividendos': score_div,
            'score_momentum': score_mom,
            'score_composto': score_total,
            'preco_atual': fund.get('preco_atual'),
            'mm50': mm50,
            'mm200': mm200,
            'euforia': 'False'
        })
    
    # Ordena por score total
    scores_momentum.sort(key=lambda x: x['score_composto'], reverse=True)
    print(f"   Top 5:")
    for i, s in enumerate(scores_momentum[:5], 1):
        print(f"   {i}. {s['ticker']}: {s['score_composto']}/100 (F:{s['score_fundamental']} V:{s['score_valuation']} D:{s['score_dividendos']} M:{s['score_momentum']})")
    print()
    
    # 10. Top 10 Compras - Mantem todos mas adiciona alerta se MM50 < MM200
    print("10. Selecionando Top 10 Compras...")
    for s in scores_momentum:
        mm50 = s.get('mm50', 0)
        mm200 = s.get('mm200', 0)
        if mm50 and mm200:
            # Calcula diferenca percentual
            diff = abs(mm50 - mm200) / mm200
            if mm50 > mm200:
                s['mm50_status'] = 'SIM'
            elif diff <= 0.05:  # MM50 esta proxima do MM200 (ate 5%)
                s['mm50_status'] = 'ATENCAO'
            else:
                s['mm50_status'] = 'NAO'
        elif mm50:
            s['mm50_status'] = 'SIM'
        else:
            s['mm50_status'] = 'SEM DADOS'
    
    top_10 = scores_momentum[:10]
    print(f"    Top 10: {len(top_10)} ações")
    print()
    
    # Salva resultados
    with open(OUTPUT_DIR / 'data' / 'scores.json', 'w', encoding='utf-8') as f:
        json.dump(scores_momentum, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print("RANKING FINAL - TOP 10 COMPRAS:")
    print("=" * 60)
    for i, s in enumerate(top_10, 1):
        print(f"{i}. {s['ticker']}: {s['score_composto']}/100")
        print(f"   F:{s['score_fundamental']} V:{s['score_valuation']} D:{s['score_dividendos']} M:{s['score_momentum']}")
    print("=" * 60)
    print(f"Scores salvos em {OUTPUT_DIR / 'data' / 'scores.json'}")

if __name__ == "__main__":
    main()
