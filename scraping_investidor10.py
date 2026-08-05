#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COLETA DE DIVIDENDOS - Yahoo Finance
======================================
Coleta informações de dividendos via yfinance
Fonte: Yahoo Finance (via yfinance)
"""

import json
from pathlib import Path
from datetime import datetime
import yfinance as yf

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

def coletar_dividendos():
    """Coleta informações de dividendos via yfinance"""
    print("=" * 60)
    print("COLETA DE DIVIDENDOS - Yahoo Finance")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    calendario = {}
    
    for i, ticker in enumerate(ACOES_IBRX100, 1):
        print(f"[{i:2d}/99] {ticker}...", end=" ", flush=True)
        
        try:
            ticker_yf = f"{ticker}.SA"
            stock = yf.Ticker(ticker_yf)
            
            # Obter dividendos
            dividends = stock.dividends
            
            if dividends is not None and len(dividends) > 0:
                # Último dividendo
                ultimo_div = dividends.iloc[-1]
                data_div = dividends.index[-1]
                
                # Próximo dividendo (se disponível)
                proximo_div = None
                if len(dividends) > 1:
                    proximo_div = dividends.index[-2] if len(dividends) > 1 else None
                
                calendario[ticker] = {
                    'ultimo_dividendo': float(ultimo_div),
                    'data_ultimo_dividendo': data_div.strftime('%Y-%m-%d'),
                    'total_dividendos_ano': len(dividends),
                    'fonte': 'yfinance'
                }
                print(f"DY: R${ultimo_div:.2f} ({data_div.strftime('%d/%m/%Y')})")
            else:
                print("Sem dividendos")
        
        except Exception as e:
            print(f"Erro: {e}")
            continue
    
    print()
    print(f"Total de ativos com dividendos: {len(calendario)}")
    
    return calendario

def main():
    """Função principal"""
    calendario = coletar_dividendos()
    
    # Salva calendario_dividendos.json
    output_file = DATA_DIR / 'calendario_dividendos.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(calendario, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print(f"Calendário salvo em: {output_file}")
    print("=" * 60)

if __name__ == '__main__':
    main()
