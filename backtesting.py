#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTESTING - SISTEMA IBrX100
==============================
Simula o desempenho histórico do sistema de seleção de ações.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import yfinance as yf

# Caminhos
DATA_DIR = Path(__file__).parent / 'data'
OUTPUT_DIR = Path(__file__).parent

# Lista oficial IBrX100
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

def baixar_historico(ticker, meses=6):
    """Baixa histórico de preços"""
    try:
        ticker_yf = f"{ticker}.SA"
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=meses * 30)
        
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
            precos.append({'data': data.strftime('%Y-%m-%d'), 'preco': close})
        
        return precos
    except Exception as e:
        print(f"    Erro ao baixar {ticker}: {e}")
        return []

def calcular_rsl(precos, periodo=14):
    """Calcula RSL"""
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
    """Calcula Média Móvel"""
    if len(precos) < periodo:
        return None
    return sum(precos[-periodo:]) / periodo

def simular_carteira(precos_historico, data_inicio, dias=20):
    """Simula carteira por N dias"""
    # Encontra índice da data de início
    idx_inicio = None
    for i, p in enumerate(precos_historico):
        if p['data'] >= data_inicio:
            idx_inicio = i
            break
    
    if idx_inicio is None or idx_inicio + dias >= len(precos_historico):
        return None
    
    preco_inicio = precos_historico[idx_inicio]['preco']
    preco_fim = precos_historico[idx_inicio + dias]['preco']
    
    retorno = (preco_fim - preco_inicio) / preco_inicio * 100
    return retorno

def main():
    """Função principal de backtesting"""
    print("=" * 70)
    print("BACKTESTING - SISTEMA IBrX100")
    print("=" * 70)
    print(f"Data: {datetime.now()}")
    print(f"Período: 6 meses (últimos 180 dias)")
    print(f"Simulação: Compra segura por 20 dias úteis")
    print("=" * 70)
    print()
    
    # Carrega fundamentais
    fundamentais_file = OUTPUT_DIR / 'data' / 'fundamentais.json'
    with open(fundamentais_file, 'r', encoding='utf-8') as f:
        fundamentais = json.load(f)
    
    # Filtro de exclusão
    acoes_filtradas = []
    for ticker in ACOES_IBRX100:
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
    
    print(f"Ações após filtro: {len(acoes_filtradas)}")
    print()
    
    # Baixa histórico de todos os ativos filtrados
    print("Baixando histórico de preços (6 meses)...")
    historico = {}
    for i, ticker in enumerate(acoes_filtradas, 1):
        print(f"   [{i:2d}/{len(acoes_filtradas)}] {ticker}...", end=" ", flush=True)
        dados = baixar_historico(ticker, meses=6)
        if dados:
            historico[ticker] = dados
            print(f"OK ({len(dados)} dias)")
        else:
            print("SEM DADOS")
    
    print()
    print(f"Histórico carregado: {len(historico)} ativos")
    print()
    
    # Simulações para diferentes pontos de entrada
    print("=" * 70)
    print("SIMULAÇÕES DE COMPRA (20 dias úteis = ~1 mês)")
    print("=" * 70)
    
    # Ponto de entrada 1: 3 meses atrás
    data_entrada_1 = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    print(f"\nEntrada: {data_entrada_1} (3 meses atrás)")
    print("-" * 70)
    
    retornos_1 = []
    for ticker, dados in historico.items():
        retorno = simular_carteira(dados, data_entrada_1, dias=20)
        if retorno is not None:
            retornos_1.append((ticker, retorno))
    
    retornos_1.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Ativo':<10} {'Retorno':>10} {'Status':>15}")
    print("-" * 40)
    for ticker, retorno in retornos_1[:10]:
        status = "WIN" if retorno > 0 else "LOSS"
        print(f"{ticker:<10} {retorno:>+9.2f}% {status}")
    
    # Ponto de entrada 2: 2 meses atrás
    data_entrada_2 = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    print(f"\nEntrada: {data_entrada_2} (2 meses atrás)")
    print("-" * 70)
    
    retornos_2 = []
    for ticker, dados in historico.items():
        retorno = simular_carteira(dados, data_entrada_2, dias=20)
        if retorno is not None:
            retornos_2.append((ticker, retorno))
    
    retornos_2.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Ativo':<10} {'Retorno':>10} {'Status':>15}")
    print("-" * 40)
    for ticker, retorno in retornos_2[:10]:
        status = "WIN" if retorno > 0 else "LOSS"
        print(f"{ticker:<10} {retorno:>+9.2f}% {status}")
    
    # Ponto de entrada 3: 1 mês atrás
    data_entrada_3 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    print(f"\nEntrada: {data_entrada_3} (1 mês atrás)")
    print("-" * 70)
    
    retornos_3 = []
    for ticker, dados in historico.items():
        retorno = simular_carteira(dados, data_entrada_3, dias=20)
        if retorno is not None:
            retornos_3.append((ticker, retorno))
    
    retornos_3.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Ativo':<10} {'Retorno':>10} {'Status':>15}")
    print("-" * 40)
    for ticker, retorno in retornos_3[:10]:
        status = "WIN" if retorno > 0 else "LOSS"
        print(f"{ticker:<10} {retorno:>+9.2f}% {status}")
    
    # Resumo geral
    print()
    print("=" * 70)
    print("RESUMO GERAL")
    print("=" * 70)
    
    todos_retornos = retornos_1 + retornos_2 + retornos_3
    if todos_retornos:
        retornos_valores = [r[1] for r in todos_retornos]
        positivos = sum(1 for r in retornos_valores if r > 0)
        negativos = sum(1 for r in retornos_valores if r <= 0)
        
        print(f"Total de simulações: {len(todos_retornos)}")
        print(f"Retornos positivos: {positivos} ({positivos/len(todos_retornos)*100:.1f}%)")
        print(f"Retornos negativos: {negativos} ({negativos/len(todos_retornos)*100:.1f}%)")
        print(f"Retorno médio: {sum(retornos_valores)/len(retornos_valores):+.2f}%")
        print(f"Melhor retorno: {max(retornos_valores):+.2f}%")
        print(f"Pior retorno: {min(retornos_valores):+.2f}%")
    
    # Salva resultados
    resultados = {
        'data_execucao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'simulacoes': {
            'entrada_1': {'data': data_entrada_1, 'resultados': [(t, r) for t, r in retornos_1[:10]]},
            'entrada_2': {'data': data_entrada_2, 'resultados': [(t, r) for t, r in retornos_2[:10]]},
            'entrada_3': {'data': data_entrada_3, 'resultados': [(t, r) for t, r in retornos_3[:10]]}
        },
        'resumo': {
            'total': len(todos_retornos),
            'positivos': positivos if todos_retornos else 0,
            'negativos': negativos if todos_retornos else 0,
            'retorno_medio': sum(retornos_valores)/len(retornos_valores) if todos_retornos else 0
        }
    }
    
    with open(OUTPUT_DIR / 'data' / 'backtest_resultados.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"Resultados salvos em: data/backtest_resultados.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
