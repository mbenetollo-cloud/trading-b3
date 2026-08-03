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
            'dy': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
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
    
    # Carrega lista de tickers do IBrX100
    # (por enquanto usa lista fixa, depois podemos integrar com B3)
    tickers = [
        'PETR4.SA', 'PETR3.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA',
        'ABEV3.SA', 'BBAS3.SA', 'RENT3.SA', 'WEGE3.SA', 'SUZB3.SA',
        'JBSS3.SA', 'RADL3.SA', 'RDOR3.SA', 'NTCO3.SA', 'HYPE3.SA',
        'CMIG4.SA', 'ITSA4.SA', 'BBSE3.SA', 'BPAC11.SA', 'ELET3.SA',
        'CSAN3.SA', 'FLRY3.SA', 'RAIL3.SA', 'UFGA3.SA', 'TOTS3.SA',
        'EQTL3.SA', 'VIVT3.SA', 'KLBN11.SA', 'CYRE3.SA', 'LREN3.SA',
        'MGLU3.SA', 'COGN3.SA', 'HAPV3.SA', 'ASAI3.SA', 'AMER3.SA',
        'GOAU4.SA', 'CSNA3.SA', 'USIM5.SA', 'BRKM5.SA', 'CAML3.SA',
        'SLCE3.SA', 'IRBR3.SA', 'CVCB3.SA', 'LWSA3.SA', 'MOVI3.SA',
        'MULT3.SA', 'BEEF3.SA', 'EZTC3.SA', 'YDUQ3.SA', 'ENEV3.SA',
        'PRIO3.SA', 'BBDC3.SA', 'ALPA4.SA', 'B3SA3.SA', 'BRPR3.SA',
        'KNRI11.SA', 'TAEE11.SA', 'VIVT3.SA', 'SBSP3.SA', 'CEMB3.SA'
    ]
    
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
