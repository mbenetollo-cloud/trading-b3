#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILTRO SEMANAL - FLUXO COMPLETO (OTIMIZADO)
============================================
Fase 1: Fundamental + Valuation -> Top 30
Fase 2: RSL (20 dias uteis) -> Top 10
Fase 3: MM50, MM200, Euforia (220 dias uteis) -> apenas Top 10

Economia: ~85% menos chamadas a API Yahoo Finance
Uso de DIAS UTEIS (nao corridos) para precisao nos indicadores
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import yfinance as yf

# Config
DY_MINIMO = 0.02
VOLUME_MINIMO = 1000000

# Caminhos
DATA_DIR = Path(__file__).parent / 'data'
OUTPUT_DIR = Path(__file__).parent

# Lista oficial IBrX100 - B3 Carteira do Dia 03/08/2026
ACOES_IBRX100 = [
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

# ─────────────────────────────────────────────────────────
# FUNCOES DE SCORING (usam fundamentais.json - sem API)
# ─────────────────────────────────────────────────────────

def calcular_score_fundamental(fund):
    """Score fundamental (0-35 pts): Cresc.Lucro(15) + Margem(10) + Divida(10)"""
    score = 0
    if fund.get('crescimento_lucro') is not None and fund['crescimento_lucro'] >= 0:
        score += 15
    if fund.get('margem_liquida') is not None and fund['margem_liquida'] >= 0.10:
        score += 10
    if fund.get('divida_ebitda') is not None and fund['divida_ebitda'] <= 150:
        score += 10
    return score

def calcular_score_valuation(fund):
    """Score valuation (0-25 pts): Cresc.Receita(10) + FCF(10) + Liquidez(5)"""
    score = 0
    if fund.get('crescimento_receita') is not None and fund['crescimento_receita'] >= 0:
        score += 10
    if fund.get('fcf') is not None and fund['fcf'] > 0:
        score += 10
    if fund.get('liquidez_corrente') is not None and fund['liquidez_corrente'] >= 1.0:
        score += 5
    return score

def calcular_score_dividendos(fund):
    """Score dividendos (0-10 pts)"""
    dy = fund.get('dy')
    if dy and dy >= DY_MINIMO:
        return 10
    return 0

# ─────────────────────────────────────────────────────────
# FUNCOES DE DADOS (usam yfinance - chamadas API)
# ─────────────────────────────────────────────────────────

def baixar_precos(ticker, dias_uteis=30):
    """Baixa precos historicos de um ticker via yfinance
    
    Args:
        ticker: Ticker da acao (ex: 'PETR4')
        dias_uteis: Numero de DIAS UTEIS desejados (nao corridos)
                    Conversao: ~1.4x dias corridos (considerando fins de semana)
                    Ex: 200 dias uteis = ~280 dias corridos
    """
    try:
        ticker_yf = f"{ticker}.SA"
        # Converte dias uteis para corridos (multiplica por 1.4 para compensar fins de semana)
        dias_corridos = int(dias_uteis * 1.4) + 30  # +30 margem para feriados
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias_corridos)
        
        dados = yf.download(
            ticker_yf,
            start=data_inicio.strftime('%Y-%m-%d'),
            progress=False
        )
        
        if dados.empty:
            return []
        
        precos = []
        for data, row in dados.iterrows():
            try:
                close = float(row['Close'].iloc[0]) if hasattr(row['Close'], 'iloc') else float(row['Close'])
            except:
                close = float(row['Close'])
            precos.append(close)
        
        return precos
    except Exception as e:
        print(f"    Erro ao baixar {ticker}: {e}")
        return []

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

def filtrar_liquidez(acoes, fundamentais):
    """Filtra por liquidez (volume minimo estimado)"""
    acoes_liquidas = []
    for ticker in acoes:
        fund = fundamentais.get(f"{ticker}.SA", {})
        market_cap = fund.get('market_cap', 0)
        if market_cap and market_cap * 0.001 >= VOLUME_MINIMO:
            acoes_liquidas.append(ticker)
    return acoes_liquidas

# ─────────────────────────────────────────────────────────
# FLUXO PRINCIPAL
# ─────────────────────────────────────────────────────────

def main():
    """Funcao principal - Fluxo otimizado em 3 fases"""
    print("=" * 60)
    print("FILTRO SEMANAL - FLUXO COMPLETO (OTIMIZADO)")
    print("=" * 60)
    print(f"Data: {datetime.now()}")
    print()
    
    # ─── FASE 1: Fundamental + Valuation (sem API) ───
    print("=" * 60)
    print("FASE 1: FUNDAMENTAL + VALUATION")
    print("=" * 60)
    
    # 1. Carrega fundamentais (dados locais - sem chamada API)
    print("1. Carregando fundamentais...")
    fundamentais_file = OUTPUT_DIR / 'data' / 'fundamentais.json'
    with open(fundamentais_file, 'r', encoding='utf-8') as f:
        fundamentais = json.load(f)
    print(f"   Total: {len(fundamentais)} acoes com fundamentais")
    
    # 2. Filtro de exclusao
    print("2. Aplicando filtro de exclusao...")
    acoes_filtradas = []
    for ticker in ACOES_IBRX100:
        # Busca com .SA (chave do fundamentais.json)
        fund = fundamentais.get(f"{ticker}.SA", {})
        roe = fund.get('roe')
        pvp = fund.get('pvp')
        fcf = fund.get('fcf')
        
        if roe and roe < 0:
            continue
        if pvp and pvp < 0:
            continue
        if fcf and fcf < 0:
            continue
        
        acoes_filtradas.append(ticker)
    
    print(f"   Excluidas: {len(ACOES_IBRX100) - len(acoes_filtradas)} acoes")
    print(f"   Restantes: {len(acoes_filtradas)} acoes")
    
    # 3. Score Fundamental + Valuation
    print("3. Calculando Fundamental + Valuation...")
    scores = []
    for ticker in acoes_filtradas:
        fund = fundamentais.get(f"{ticker}.SA", {})
        score_fund = calcular_score_fundamental(fund)
        score_val = calcular_score_valuation(fund)
        score_total = score_fund + score_val
        scores.append((ticker, score_total, score_fund, score_val))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    
    print("   Top 10:")
    for i, (ticker, total, fund, val) in enumerate(scores[:10], 1):
        print(f"   {i}. {ticker}: {total}/60 (F:{fund} V:{val})")
    
    # 4. Top 30
    top_30 = [t for t, _, _, _ in scores[:30]]
    print(f"\n   Top 30 selecionados para Fase 2")
    print()
    
    # ─── FASE 2: RSL - dados curtos (30 dias) ───
    print("=" * 60)
    print("FASE 2: MOMENTUM RSL (30 dias de dados)")
    print("=" * 60)
    
    scores_rsl = []
    for i, ticker in enumerate(top_30, 1):
        print(f"   [{i:2d}/30] {ticker}...", end=" ", flush=True)
        
        precos = baixar_precos(ticker, dias_uteis=20)  # 20 dias uteis para RSL 14
        if precos:
            rsl = calcular_rsl(precos, 14)
            if rsl > 1.05:
                score_rsl = 20
            elif rsl > 1.0:
                score_rsl = 15
            elif rsl > 0.95:
                score_rsl = 10
            else:
                score_rsl = 5
            
            fund = fundamentais.get(f"{ticker}.SA", {})
            score_fund = calcular_score_fundamental(fund)
            score_val = calcular_score_valuation(fund)
            score_div = calcular_score_dividendos(fund)
            score_total = score_fund + score_val + score_div + score_rsl
            
            scores_rsl.append({
                'ticker': ticker,
                'score_fundamental': score_fund,
                'score_valuation': score_val,
                'score_dividendos': score_div,
                'score_momentum': score_rsl,
                'score_composto': score_total,
                'preco_atual': fund.get('preco_atual'),
                'rsl': rsl
            })
            print(f"RSL={rsl:.4f} -> {score_rsl}pts")
        else:
            print("SEM DADOS")
    
    # Ordena por score total
    scores_rsl.sort(key=lambda x: x['score_composto'], reverse=True)
    
    print("\n   Top 10 apos RSL:")
    for i, s in enumerate(scores_rsl[:10], 1):
        print(f"   {i}. {s['ticker']}: {s['score_composto']}/100 (M:{s['score_momentum']})")
    
    # Top 10 final
    top_10 = scores_rsl[:10]
    print(f"\n   Top 10 selecionados para Fase 3")
    print()
    
    # ─── FASE 3: MM50, MM200, Euforia (730 dias) ───
    print("=" * 60)
    print("FASE 3: MM50, MM200, EUFORIA (730 dias)")
    print("=" * 60)
    
    for s in top_10:
        ticker = s['ticker']
        print(f"   {ticker}...", end=" ", flush=True)
        
        precos = baixar_precos(ticker, dias_uteis=220)  # 220 dias uteis para MM200
        if precos:
            mm50 = calcular_mm(precos, 50)
            mm200 = calcular_mm(precos, 200)
            
            s['mm50'] = mm50 if mm50 else 0
            s['mm200'] = mm200 if mm200 else 0
            
            # Calcula mm50_status e euforia
            if mm50 and mm200:
                diff = abs(mm50 - mm200) / mm200
                
                # Euforia
                if mm50 > mm200 and diff > 0.15:
                    s['euforia'] = 'True'
                else:
                    s['euforia'] = 'False'
                
                # Status
                if diff <= 0.05:
                    s['mm50_status'] = 'ATENCAO'
                elif mm50 > mm200:
                    s['mm50_status'] = 'SIM'
                else:
                    s['mm50_status'] = 'NAO'
                
                status = s['mm50_status']
                euph = "EUFORIA" if s['euforia'] == 'True' else ""
                print(f"MM50={mm50:.2f} MM200={mm200:.2f} -> {status} {euph}")
            else:
                s['mm50_status'] = 'SEM DADOS'
                s['euforia'] = 'False'
                print("MM50/MM200 indisponivel")
        else:
            s['mm50'] = 0
            s['mm200'] = 0
            s['mm50_status'] = 'SEM DADOS'
            s['euforia'] = 'False'
            print("SEM DADOS")
    
    print()
    
    # ─── RESULTADO FINAL ───
    # Salva todos os scores (top 10 com todos os dados)
    with open(OUTPUT_DIR / 'data' / 'scores.json', 'w', encoding='utf-8') as f:
        json.dump(top_10, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print("RANKING FINAL - TOP 10 COMPRAS:")
    print("=" * 60)
    for i, s in enumerate(top_10, 1):
        mm50 = s.get('mm50', 0)
        mm200 = s.get('mm200', 0)
        diff = f"{((mm50 - mm200) / mm200 * 100):+.1f}%" if mm200 else "N/A"
        euph = " [EUFORIA]" if s.get('euforia') == 'True' else ""
        print(f"{i}. {s['ticker']}: {s['score_composto']}/100 {s['mm50_status']}{euph}")
        print(f"   F:{s['score_fundamental']} V:{s['score_valuation']} D:{s['score_dividendos']} M:{s['score_momentum']}")
        print(f"   Preco: R${s['preco_atual']:.2f} | MM50-MM200: {diff}")
    print("=" * 60)
    print(f"Scores salvos em {OUTPUT_DIR / 'data' / 'scores.json'}")
    
    # ─── AUTO-DEPLOY: Commit e push automatico ───
    print()
    print("=" * 60)
    print("ATUALIZANDO LANDING PAGE...")
    print("=" * 60)
    
    import subprocess
    try:
        # Git add
        subprocess.run(['git', 'add', 'data/scores.json'], 
                      cwd=OUTPUT_DIR, capture_output=True, check=True)
        
        # Git commit
        data_str = datetime.now().strftime('%d/%m/%Y')
        msg = f"update: Scores {data_str} - pipeline otimizado"
        result = subprocess.run(['git', 'commit', '-m', msg], 
                               cwd=OUTPUT_DIR, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   Commit realizado com sucesso!")
            
            # Git push
            result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                   cwd=OUTPUT_DIR, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   Push realizado com sucesso!")
                print("   Landing page sera atualizada em instantes!")
                print("   URL: https://mbenetollo-cloud.github.io/trading-b3/")
            else:
                print(f"   Erro no push: {result.stderr}")
        else:
            print("   Nenhuma alteracao para commitar")
            
    except Exception as e:
        print(f"   Erro ao atualizar landing page: {e}")
        print("   Execute manualmente: git add . && git commit -m 'update' && git push")

if __name__ == "__main__":
    main()
