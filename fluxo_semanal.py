#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FLUXO SEMANAL - FUNDAMENTAIS
=============================
Calcula fundamentais quando empresa publica resultados
Execução: sexta 18h ou quando empresa divulga

Fonte de dados: Investidor10 (calendário)
"""

import json
from pathlib import Path
from datetime import datetime
import yfinance as yf

# Config
DY_MINIMO = 2.0  # 2% mínimo para score de dividendos

# Caminhos
DATA_DIR = Path(__file__).parent / 'data'
OUTPUT_DIR = Path(__file__).parent

# Lista oficial IBrX100 - B3 Carteira do Dia 04/08/2026
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
# FUNÇÕES DE SCORING (usam fundamentais.json - sem API)
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
# VERIFICAÇÃO DE CALENDÁRIO
# ─────────────────────────────────────────────────────────

def verificar_calendario(ticker):
    """Verifica se ativo tem calendário no Investidor10"""
    calendario_file = DATA_DIR / 'calendario_dividendos.json'
    
    if not calendario_file.exists():
        return None
    
    with open(calendario_file, 'r', encoding='utf-8') as f:
        calendario = json.load(f)
    
    return calendario.get(ticker)

def verificar_freshness(ticker, fundamentais):
    """Verifica se fundamental está atualizado"""
    hoje = datetime.now()
    
    # Verificar se tem calendário
    calendario = verificar_calendario(ticker)
    if calendario:
        data_divulgacao = calendario.get('data_com')
        if data_divulgacao:
            try:
                data = datetime.strptime(data_divulgacao, '%Y-%m-%d')
                dias_desde_divulgacao = (hoje - data).days
                if dias_desde_divulgacao <= 30:
                    return "ATUALIZADO"
            except:
                pass
    
    # Fallback: verificar data de coleta dos fundamentais
    fund = fundamentais.get(f"{ticker}.SA", {})
    data_coleta = fund.get('data_coleta')
    if data_coleta:
        try:
            data = datetime.fromisoformat(data_coleta)
            dias_desde_coleta = (hoje - data).days
            if dias_desde_coleta <= 90:
                return "ATUALIZADO"
        except:
            pass
    
    return "DESATUALIZADO"

# ─────────────────────────────────────────────────────────
# FLUXO PRINCIPAL
# ─────────────────────────────────────────────────────────

def main():
    """Função principal - Fluxo semanal de fundamentais"""
    print("=" * 60)
    print("FLUXO SEMANAL - FUNDAMENTAIS")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # 1. Carrega fundamentais
    print("1. Carregando fundamentais...")
    fundamentais_file = OUTPUT_DIR / 'data' / 'fundamentais.json'
    
    if not fundamentais_file.exists():
        print("   ERRO: Arquivo fundamentais.json não encontrado!")
        print("   Execute primeiro: python coletar_fundamentais.py")
        return
    
    with open(fundamentais_file, 'r', encoding='utf-8') as f:
        fundamentais = json.load(f)
    print(f"   Total: {len(fundamentais)} ações com fundamentais")
    
    # 2. Verificar freshness por ativo
    print("2. Verificando freshness dos fundamentais...")
    ativos_desatualizados = []
    for ticker in ACOES_IBRX100:
        status = verificar_freshness(ticker, fundamentais)
        if status == "DESATUALIZADO":
            ativos_desatualizados.append(ticker)
    
    print(f"   Atualizados: {len(ACOES_IBRX100) - len(ativos_desatualizados)}")
    print(f"   Desatualizados: {len(ativos_desatualizados)}")
    
    # 3. Calcular scores fundamentais
    print("3. Calculando scores fundamentais...")
    scores = []
    for ticker in ACOES_IBRX100:
        fund = fundamentais.get(f"{ticker}.SA", {})
        
        # Filtro de exclusão
        roe = fund.get('roe')
        pvp = fund.get('pvp')
        fcf = fund.get('fcf')
        
        if roe and roe < 0:
            continue
        if pvp and pvp < 0:
            continue
        if fcf and fcf < 0:
            continue
        
        score_fund = calcular_score_fundamental(fund)
        score_val = calcular_score_valuation(fund)
        score_div = calcular_score_dividendos(fund)
        score_total = score_fund + score_val + score_div
        
        scores.append({
            'ticker': ticker,
            'score_fundamental': score_fund,
            'score_valuation': score_val,
            'score_dividendos': score_div,
            'score_semanal': score_total,
            'freshness': verificar_freshness(ticker, fundamentais)
        })
    
    # Ordena por score
    scores.sort(key=lambda x: x['score_semanal'], reverse=True)
    
    print("\n   Top 10:")
    for i, s in enumerate(scores[:10], 1):
        print(f"   {i}. {s['ticker']}: {s['score_semanal']}/70 (F:{s['score_fundamental']} V:{s['score_valuation']} D:{s['score_dividendos']})")
    
    # 4. Salvar scores semanais
    output_file = DATA_DIR / 'scores_semanais.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print(f"Scores semanais salvos em: {output_file}")
    print("=" * 60)
    
    # 5. Estatísticas
    print()
    print("ESTATÍSTICAS:")
    print(f"  Total de ativos: {len(scores)}")
    print(f"  Com dividendos (DY >= 2%): {sum(1 for s in scores if s['score_dividendos'] == 10)}")
    print(f"  Atualizados: {sum(1 for s in scores if s['freshness'] == 'ATUALIZADO')}")
    print(f"  Desatualizados: {sum(1 for s in scores if s['freshness'] == 'DESATUALIZADO')}")

if __name__ == "__main__":
    main()
