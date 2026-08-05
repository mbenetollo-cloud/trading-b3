# -*- coding: utf-8 -*-
"""
COLETAR DADOS FUNDAMENTAIS - TRADING B3
========================================
Coleta dados fundamentalistas via yfinance para scoring.
Campos: crescmiento_lucro, crescimento_receita, margem_liquida,
        fcf, divida_ebitda, liquidez_corrente, roe, pl, pvp, dy, market_cap
"""

import json
import yfinance as yf
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / 'data'

def coletar_fundamental(ticker: str) -> dict:
    """Coleta dados fundamentalistas de uma acao"""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        
        # Dados basicos
        fundamental = {
            'ticker': ticker,
            'nome': info.get('shortName', ''),
            'preco_atual': info.get('currentPrice') or info.get('regularMarketPrice'),
            'setor': info.get('sector', ''),
            'market_cap': info.get('marketCap'),
            'data_coleta': datetime.now().isoformat(),
            
            # Score Fundamental (35 pts)
            'crescimento_lucro': info.get('earningsGrowth'),  # 15 pts
            'margem_liquida': info.get('profitMargins'),      # 10 pts
            'divida_ebitda': info.get('debtToEquity'),        # 10 pts (proxy)
            
            # Score Valuation (25 pts)
            'crescimento_receita': info.get('revenueGrowth'),  # 10 pts
            'fcf': info.get('freeCashflow'),                   # 10 pts
            'liquidez_corrente': info.get('currentRatio'),     # 5 pts
            
            # Campos legados (manter compatibilidade)
            'roe': info.get('returnOnEquity'),
            'roic': info.get('returnOnCapital'),
            'pl': info.get('trailingPE'),
            'pvp': info.get('priceToBook'),
            'dy': info.get('dividendYield', 0) if info.get('dividendYield') else 0,
        }
        
        return fundamental
        
    except Exception as e:
        print(f"  Erro ao coletar {ticker}: {e}")
        return None


def main():
    """Funcao principal"""
    print("=" * 60)
    print("COLETANDO DADOS FUNDAMENTAIS")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
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
    tickers = [f"{t}.SA" for t in tickers]
    
    fundamentais = {}
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] Coletando {ticker}...")
        fund = coletar_fundamental(ticker)
        if fund:
            fundamentais[ticker] = fund
            print(f"  OK: {fund['nome']}")
        else:
            print(f"  FALHOU")
    
    # Salva fundamentais.json
    output_file = OUTPUT_DIR / 'fundamentais.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fundamentais, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print(f"CONCLUIDO! {len(fundamentais)} fundamentais salvos em {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
