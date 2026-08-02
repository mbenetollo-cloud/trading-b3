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

# Lista de acoes do IBOV para baixar dados
ACOES_IBOV = [
    'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA',
    'BBAS3.SA', 'RENT3.SA', 'WEGE3.SA', 'SUZB3.SA', 'JBSS3.SA'
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
    print(f"Acoes: {len(ACOES_IBOV)}")
    print("=" * 60)
    print()
    
    for ticker in ACOES_IBOV:
        # Baixa dados
        dados = baixar_dados_acao(ticker, dias=250)
        
        if dados:
            # Salva em JSON
            salvar_json(ticker, dados)
        
        print()
    
    print("=" * 60)
    print("CONCLUIDO!")
    print("=" * 60)
    print(f"Arquivos salvos na pasta: data/")
    print("Abra o index.html no navegador para ver graficos reais!")


if __name__ == "__main__":
    main()
