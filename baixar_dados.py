# -*- coding: utf-8 -*-
"""
BAIXAR DADOS REAIS - TRADING B3
================================
Baixa dados de precos via yfinance e salva em JSON para o grafico.
"""

import json
import os
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

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

def baixar_dados_acao(ticker: str, dias: int = 730) -> list:
    """
    Baixa dados historicos de uma acao.
    
    Args:
        ticker: Ticker da acao (ex: 'PETR4.SA')
        dias: Numero de dias para buscar (padrao: 730 = 2 anos)
    
    Returns:
        Lista de dicionarios com dados de candle
    """
    try:
        print(f"Baixando dados de {ticker}...")
        
        # Calcula data inicio (2 anos para ter dados suficientes para MM200)
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias)
        
        # Baixa dados via yfinance
        dados = yf.download(
            ticker, 
            start=data_inicio.strftime('%Y-%m-%d'),
            progress=False
        )
        
        if dados.empty:
            print(f"  Aviso: Sem dados para {ticker}")
            return []
        
        # Converte para formato do grafico
        candles = []
        for data, row in dados.iterrows():
            # Acessa os valores corretamente (pode ter multi-level columns)
            try:
                open_val = float(row['Open'].iloc[0]) if hasattr(row['Open'], 'iloc') else float(row['Open'])
                high_val = float(row['High'].iloc[0]) if hasattr(row['High'], 'iloc') else float(row['High'])
                low_val = float(row['Low'].iloc[0]) if hasattr(row['Low'], 'iloc') else float(row['Low'])
                close_val = float(row['Close'].iloc[0]) if hasattr(row['Close'], 'iloc') else float(row['Close'])
            except:
                open_val = float(row['Open'])
                high_val = float(row['High'])
                low_val = float(row['Low'])
                close_val = float(row['Close'])
            
            candle = {
                'time': data.strftime('%Y-%m-%d'),
                'open': round(open_val, 2),
                'high': round(high_val, 2),
                'low': round(low_val, 2),
                'close': round(close_val, 2)
            }
            candles.append(candle)
        
        print(f"  OK: {len(candles)} candles baixados")
        return candles
        
    except Exception as e:
        print(f"  Erro ao baixar {ticker}: {e}")
        return []


def salvar_json(ticker: str, dados: list, pasta: str = 'data'):
    """
    Salva dados em arquivo JSON.
    
    Args:
        ticker: Ticker da acao
        dados: Lista de candles
        pasta: Pasta de saida
    """
    # Cria pasta se nao existir
    os.makedirs(pasta, exist_ok=True)
    
    # Nome do arquivo (remove .SA para facilitar)
    nome_arquivo = ticker.replace('.SA', '')
    caminho = os.path.join(pasta, f'{nome_arquivo}.json')
    
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False)
    
    print(f"  Salvo: {caminho}")


def main():
    """Funcao principal."""
    print("=" * 60)
    print("BAIXANDO DADOS REAIS - TRADING B3")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"Acoes: {len(ACOES_IBRX100)}")
    print("=" * 60)
    print()
    
    for ticker in ACOES_IBRX100:
        # Adiciona .SA para tickers brasileiros
        ticker_yf = f"{ticker}.SA"
        
        # Baixa dados (3 anos para ter dados suficientes para MM200)
        dados = baixar_dados_acao(ticker_yf, dias=730)
        
        if dados:
            # Salva em JSON (sem .SA no nome do arquivo)
            salvar_json(ticker, dados)
        
        print()
    
    print("=" * 60)
    print("CONCLUIDO!")
    print("=" * 60)
    print(f"Arquivos salvos na pasta: data/")
    print("Abra o index.html no navegador para ver graficos reais!")


if __name__ == "__main__":
    main()
