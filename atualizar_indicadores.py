#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATUALIZAÇÃO DIÁRIA DE INDICADORES
==================================
Baixa preços e calcula MM50, MM200, RSL, Euforia
Execução: diária (8h ou 18h)
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
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

# ─────────────────────────────────────────────────────────
# FUNÇÕES DE CÁLCULO
# ─────────────────────────────────────────────────────────

def baixar_precos(ticker, dias_uteis=220):
    """Baixa preços históricos via yfinance"""
    try:
        ticker_yf = f"{ticker}.SA"
        # Converte dias úteis para corridos
        dias_corridos = int(dias_uteis * 1.4) + 30
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias_corridos)
        
        dados = yf.download(
            ticker_yf,
            start=data_inicio.strftime('%Y-%m-%d'),
            progress=False
        )
        
        if dados.empty:
            return [], []
        
        precos = []
        datas = []
        for data, row in dados.iterrows():
            try:
                close = float(row['Close'].iloc[0]) if hasattr(row['Close'], 'iloc') else float(row['Close'])
            except:
                close = float(row['Close'])
            precos.append(close)
            datas.append(data.strftime('%Y-%m-%d'))
        
        return precos, datas
    except Exception as e:
        print(f"    Erro ao baixar {ticker}: {e}")
        return [], []

def calcular_mm(precos, periodo):
    """Calcula Média Móvel"""
    if len(precos) < periodo:
        return None
    return sum(precos[-periodo:]) / periodo

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

def calcular_indicadores(ticker):
    """Calcula todos os indicadores de um ticker"""
    precos, datas = baixar_precos(ticker, dias_uteis=220)
    
    if not precos:
        return None
    
    # Preço atual
    preco_atual = precos[-1]
    
    # MM50 e MM200
    mm50 = calcular_mm(precos, 50)
    mm200 = calcular_mm(precos, 200)
    
    # RSL
    rsl = calcular_rsl(precos, 14)
    
    # MM50 Status e Euforia
    mm50_status = "SEM DADOS"
    euforia = False
    
    if mm50 and mm200:
        diff = abs(mm50 - mm200) / mm200
        
        # Euforia (gap > 15%)
        if mm50 > mm200 and diff > 0.15:
            euforia = True
        
        # Status
        if diff <= 0.05:
            mm50_status = "ATENCAO"
        elif mm50 > mm200:
            mm50_status = "SIM"
        else:
            mm50_status = "NAO"
    
    return {
        'ticker': ticker,
        'preco_atual': round(preco_atual, 2),
        'mm50': round(mm50, 2) if mm50 else 0,
        'mm200': round(mm200, 2) if mm200 else 0,
        'mm50_status': mm50_status,
        'euforia': euforia,
        'rsl': round(rsl, 4),
        'data_atualizacao': datetime.now().isoformat()
    }

# ─────────────────────────────────────────────────────────
# FLUXO PRINCIPAL
# ─────────────────────────────────────────────────────────

def main():
    """Função principal"""
    print("=" * 60)
    print("ATUALIZAÇÃO DIÁRIA DE INDICADORES")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    indicadores = {}
    
    for i, ticker in enumerate(ACOES_IBRX100, 1):
        print(f"[{i:2d}/99] {ticker}...", end=" ", flush=True)
        
        indicador = calcular_indicadores(ticker)
        if indicador:
            indicadores[ticker] = indicador
            status = indicador['mm50_status']
            euph = " [EUFORIA]" if indicador['euforia'] else ""
            print(f"RSL={indicador['rsl']:.4f} MM50={indicador['mm50']:.2f} MM200={indicador['mm200']:.2f} -> {status}{euph}")
        else:
            print("SEM DADOS")
    
    # Salva indicadores.json
    output_file = DATA_DIR / 'indicadores.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(indicadores, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print(f"Indicadores salvos em: {output_file}")
    print(f"Total: {len(indicadores)} ativos atualizados")
    print("=" * 60)
    
    # Estatísticas
    sim_count = sum(1 for i in indicadores.values() if i['mm50_status'] == 'SIM')
    nao_count = sum(1 for i in indicadores.values() if i['mm50_status'] == 'NAO')
    atencao_count = sum(1 for i in indicadores.values() if i['mm50_status'] == 'ATENCAO')
    euphoria_count = sum(1 for i in indicadores.values() if i['euforia'])
    
    print()
    print("ESTATÍSTICAS:")
    print(f"  SIM (tendência alta): {sim_count}")
    print(f"  NAO (tendência baixa): {nao_count}")
    print(f"  ATENCAO (indefinido): {atencao_count}")
    print(f"  EUFORIA (gap > 15%): {euphoria_count}")

    # ─── AUTO-COMMIT ───
    print()
    print("=" * 60)
    print("COMMIT AUTOMÁTICO...")
    print("=" * 60)
    
    import subprocess
    try:
        subprocess.run(['git', 'add', 'data/indicadores.json'], 
                      cwd=OUTPUT_DIR, capture_output=True, check=True)
        
        data_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        msg = f"update: Indicadores {data_str}"
        result = subprocess.run(['git', 'commit', '-m', msg], 
                               cwd=OUTPUT_DIR, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   Commit realizado com sucesso!")
            result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                   cwd=OUTPUT_DIR, capture_output=True, text=True)
            if result.returncode == 0:
                print("   Push realizado com sucesso!")
            else:
                print(f"   Erro no push: {result.stderr}")
        else:
            print("   Nenhuma alteração para commitar")
    except Exception as e:
        print(f"   Erro no auto-commit: {e}")

if __name__ == '__main__':
    main()
