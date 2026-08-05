#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTESTING - SISTEMA IBrX100 (COM REGRAS REAIS)
=================================================
Usa as mesmas regras do sistema de trading:
- RSL 14: > 1 = compra
- Stop Loss: ATR 12 x 1,5
- Take Profit: 20%
- Max 5 posicoes
- Max 5% por posicao
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np

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

# Parametros do sistema (conforme config.py e landing page de 02/08/2026)
RSL_PERIODOS = 14
ATR_PERIODOS = 12
ATR_MULTIPLICADOR = 1.5
TAKE_PROFIT = 0.20  # 20%
STOP_LOSS_FIXO = 0.10  # 10% (fallback se ATR nao disponivel)
TRAILING_STOP = 0.08  # 8%
MAX_POSICOES = 5
MAX_POR_POSICAO = 0.05  # 5% por posicao
CAPITAL_INICIAL = 10000
SCORE_MINIMO = 50

def baixar_dados_completos(ticker, meses=20):
    """Baixa dados OHLCV completos (1.5 anos = ~20 meses)"""
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
            return None
        
        resultado = []
        for data, row in dados.iterrows():
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
            
            resultado.append({
                'data': data.strftime('%Y-%m-%d'),
                'open': open_val,
                'high': high_val,
                'low': low_val,
                'close': close_val
            })
        
        return resultado
    except Exception as e:
        print(f"    Erro ao baixar {ticker}: {e}")
        return None

def calcular_atr(dados, periodo=12):
    """Calcula Average True Range"""
    if len(dados) < periodo + 1:
        return None
    
    tr_list = []
    for i in range(1, len(dados)):
        high = dados[i]['high']
        low = dados[i]['low']
        prev_close = dados[i-1]['close']
        
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        tr_list.append(tr)
    
    # ATR = media dos ultimos 'periodo' TRs
    if len(tr_list) >= periodo:
        atr = sum(tr_list[-periodo:]) / periodo
        return atr
    return None

def calcular_rsl(dados, periodo=14):
    """Calcula RSL (preco / media)"""
    if len(dados) < periodo:
        return None
    
    precos = [d['close'] for d in dados[-periodo:]]
    media = sum(precos) / periodo
    preco_atual = dados[-1]['close']
    
    if media > 0:
        return preco_atual / media
    return None

def calcular_mm(dados, periodo):
    """Calcula Media Movvel"""
    if len(dados) < periodo:
        return None
    
    precos = [d['close'] for d in dados[-periodo:]]
    return sum(precos) / periodo

def simular_sistema(historico, fundamentais):
    """Simula o sistema completo com gerenciamento de risco"""
    
    print("Simulando sistema com gerenciamento de risco...")
    print(f"  Capital inicial: R$ {CAPITAL_INICIAL:,.2f}")
    print(f"  Stop Loss: ATR {ATR_PERIODOS} x {ATR_MULTIPLICADOR} (ou {STOP_LOSS_FIXO*100:.0f}% fixo)")
    print(f"  Take Profit: {TAKE_PROFIT*100:.0f}%")
    print(f"  Trailing Stop: {TRAILING_STOP*100:.0f}%")
    print(f"  Max posicoes: {MAX_POSICOES} ({MAX_POR_POSICAO*100:.0f}% cada)")
    print(f"  Score minimo: {SCORE_MINIMO}")
    print()
    
    # Carrega dados de todos os ativos
    dados_ativos = {}
    for ticker in ACOES_IBRX100:
        dados = historico.get(ticker)
        if dados and len(dados) > 50:
            dados_ativos[ticker] = dados
    
    print(f"  Ativos com dados suficientes: {len(dados_ativos)}")
    print()
    
    # Simula dia a dia (ultimos 6 meses)
    capital = CAPITAL_INICIAL
    posicoes = []  # Lista de posicoes abertas
    historico_operacoes = []
    
    # Pega todas as datas disponiveis
    todas_datas = set()
    for dados in dados_ativos.values():
        for d in dados:
            todas_datas.add(d['data'])
    
    datas_ordenadas = sorted(todas_datas)
    
    # Comeca depois de 50 dias (para ter RSL 14 + MM50)
    if len(datas_ordenadas) < 50:
        print("  Dados insuficientes para simulacao")
        return None
    
    datas_simulacao = datas_ordenadas[50:]
    
    print(f"  Dias de simulacao: {len(datas_simulacao)}")
    print()
    
    for data_atual in datas_simulacao:
        # 1. Verifica stops das posicoes abertas
        posicoes_para_fechar = []
        for pos in posicoes:
            ticker = pos['ticker']
            dados = dados_ativos.get(ticker)
            if not dados:
                continue
            
            # Encontra preco atual
            preco_atual = None
            for d in dados:
                if d['data'] == data_atual:
                    preco_atual = d['close']
                    break
            
            if preco_atual is None:
                continue
            
            # Calcula ATR atual
            dados_ate_agora = [d for d in dados if d['data'] <= data_atual]
            atr = calcular_atr(dados_ate_agora, ATR_PERIODOS)
            
            if atr is None:
                continue
            
            # Stop Loss: preco_entrada - (ATR x multiplicador)
            stop_loss = pos['preco_entrada'] - (atr * ATR_MULTIPLICADOR)
            
            # Take Profit: preco_entrada x 1.20
            take_profit = pos['preco_entrada'] * (1 + TAKE_PROFIT)
            
            # Trailing Stop: se preco subiu, ajusta stop para cima
            preco_maximo = pos.get('preco_maximo', pos['preco_entrada'])
            if preco_atual > preco_maximo:
                preco_maximo = preco_atual
                pos['preco_maximo'] = preco_maximo
                # Ajusta stop loss para trailing (preco_maximo - 8%)
                novo_stop = preco_maximo * (1 - TRAILING_STOP)
                if novo_stop > stop_loss:
                    stop_loss = novo_stop
                    pos['stop_loss'] = stop_loss
            
            # Verifica se bateu o stop
            if preco_atual <= stop_loss:
                posicoes_para_fechar.append((pos, preco_atual, 'STOP LOSS'))
            elif preco_atual >= take_profit:
                posicoes_para_fechar.append((pos, preco_atual, 'TAKE PROFIT'))
        
        # Fecha posicoes que bateram o stop
        for pos, preco_saida, motivo in posicoes_para_fechar:
            retorno = (preco_saida - pos['preco_entrada']) / pos['preco_entrada']
            lucro = pos['capital_investido'] * retorno
            
            historico_operacoes.append({
                'ticker': pos['ticker'],
                'data_entrada': pos['data_entrada'],
                'data_saida': data_atual,
                'preco_entrada': pos['preco_entrada'],
                'preco_saida': preco_saida,
                'retorno': retorno,
                'lucro': lucro,
                'motivo': motivo
            })
            
            capital += lucro
            posicoes.remove(pos)
        
        # 2. Verifica novas entradas (se tem espaco)
        if len(posicoes) < MAX_POSICOES:
            for ticker, dados in dados_ativos.items():
                if len(posicoes) >= MAX_POSICOES:
                    break
                
                # Verifica se ja tem posicao aberta
                if any(p['ticker'] == ticker for p in posicoes):
                    continue
                
                # Encontra dados ate a data atual
                dados_ate_agora = [d for d in dados if d['data'] <= data_atual]
                if len(dados_ate_agora) < 50:
                    continue
                
                # Calcula indicadores
                rsl = calcular_rsl(dados_ate_agora, RSL_PERIODOS)
                mm50 = calcular_mm(dados_ate_agora, 50)
                mm200 = calcular_mm(dados_ate_agora, 200)
                
                if rsl is None or mm50 is None:
                    continue
                
                # Condicoes de entrada:
                # 1. RSL > 1 (forca relativa)
                # 2. MM50 > MM200 (se MM200 disponivel)
                # 3. Euforia: NAO comprar se gap > 15%
                condicao_tendencia = True
                tem_euforia = False
                
                if mm200 is not None:
                    condicao_tendencia = mm50 > mm200
                    # Verifica euforia (gap > 15%)
                    if mm50 > mm200:
                        gap = (mm50 - mm200) / mm200
                        if gap > 0.15:
                            tem_euforia = True
                
                # Entra apenas se: RSL forte + tendencia alta + SEM euforia
                if rsl > 1.0 and condicao_tendencia and not tem_euforia:
                    # Encontra preco atual
                    preco_atual = None
                    for d in dados:
                        if d['data'] == data_atual:
                            preco_atual = d['close']
                            break
                    
                    if preco_atual is None:
                        continue
                    
                    # Calcula ATR para stop
                    atr = calcular_atr(dados_ate_agora, ATR_PERIODOS)
                    if atr is None:
                        continue
                    
                    # Capital por posicao (5% do capital total)
                    capital_por_posicao = capital * 0.05
                    
                    # Quantidade de acoes
                    qtd_acoes = int(capital_por_posicao / preco_atual)
                    if qtd_acoes < 1:
                        continue
                    
                    # Abre posicao
                    posicoes.append({
                        'ticker': ticker,
                        'data_entrada': data_atual,
                        'preco_entrada': preco_atual,
                        'quantidade': qtd_acoes,
                        'capital_investido': qtd_acoes * preco_atual,
                        'stop_loss': preco_atual - (atr * ATR_MULTIPLICADOR),
                        'take_profit': preco_atual * (1 + TAKE_PROFIT),
                        'preco_maximo': preco_atual  # Para trailing stop
                    })
        
        # 3. Verifica saida por tendencia de queda
        posicoes_para_fechar_tendencia = []
        for pos in posicoes:
            ticker = pos['ticker']
            dados = dados_ativos.get(ticker)
            if not dados:
                continue
            
            dados_ate_agora = [d for d in dados if d['data'] <= data_atual]
            if len(dados_ate_agora) < 50:
                continue
            
            mm50 = calcular_mm(dados_ate_agora, 50)
            mm200 = calcular_mm(dados_ate_agora, 200)
            
            # Se MM50 caiu abaixo do MM200, tendencia mudou
            if mm50 is not None and mm200 is not None and mm50 < mm200:
                # Encontra preco atual
                preco_atual = None
                for d in dados:
                    if d['data'] == data_atual:
                        preco_atual = d['close']
                        break
                
                if preco_atual:
                    posicoes_para_fechar_tendencia.append((pos, preco_atual))
        
        # Fecha posicoes por tendencia
        for pos, preco_saida in posicoes_para_fechar_tendencia:
            retorno = (preco_saida - pos['preco_entrada']) / pos['preco_entrada']
            lucro = pos['capital_investido'] * retorno
            
            historico_operacoes.append({
                'ticker': pos['ticker'],
                'data_entrada': pos['data_entrada'],
                'data_saida': data_atual,
                'preco_entrada': pos['preco_entrada'],
                'preco_saida': preco_saida,
                'retorno': retorno,
                'lucro': lucro,
                'motivo': 'TENDENCIA QUEDA'
            })
            
            capital += lucro
            posicoes.remove(pos)
    
    # Fecha posicoes restantes
    for pos in posicoes:
        ticker = pos['ticker']
        dados = dados_ativos.get(ticker)
        if dados:
            ultimo_preco = dados[-1]['close']
            retorno = (ultimo_preco - pos['preco_entrada']) / pos['preco_entrada']
            lucro = pos['capital_investido'] * retorno
            
            historico_operacoes.append({
                'ticker': pos['ticker'],
                'data_entrada': pos['data_entrada'],
                'data_saida': dados[-1]['data'],
                'preco_entrada': pos['preco_entrada'],
                'preco_saida': ultimo_preco,
                'retorno': retorno,
                'lucro': lucro,
                'motivo': 'FIM SIMULACAO'
            })
            
            capital += lucro
    
    return {
        'capital_inicial': CAPITAL_INICIAL,
        'capital_final': capital,
        'operacoes': historico_operacoes
    }

def main():
    """Funcao principal"""
    print("=" * 70)
    print("BACKTESTING - SISTEMA IBrX100 (COM REGRAS REAIS)")
    print("=" * 70)
    print(f"Data: {datetime.now()}")
    print(f"Periodo: Janeiro/2025 a Agosto/2026 (~1.5 anos)")
    print(f"Parametros:")
    print(f"  - RSL: {RSL_PERIODOS} periodos")
    print(f"  - Stop Loss: ATR {ATR_PERIODOS} x {ATR_MULTIPLICADOR} (ou {STOP_LOSS_FIXO*100:.0f}% fixo)")
    print(f"  - Take Profit: {TAKE_PROFIT*100:.0f}%")
    print(f"  - Trailing Stop: {TRAILING_STOP*100:.0f}%")
    print(f"  - Max posicoes: {MAX_POSICOES} ({MAX_POR_POSICAO*100:.0f}% cada)")
    print(f"  - Score minimo: {SCORE_MINIMO}")
    print(f"  - Capital inicial: R$ {CAPITAL_INICIAL:,.2f}")
    print("=" * 70)
    print()
    
    # Carrega fundamentais
    fundamentais_file = OUTPUT_DIR / 'data' / 'fundamentais.json'
    with open(fundamentais_file, 'r', encoding='utf-8') as f:
        fundamentais = json.load(f)
    
    # Baixa historico completo (1.5 anos = ~20 meses)
    print("Baixando historico completo (Janeiro/2025 a Agosto/2026)...")
    historico = {}
    for i, ticker in enumerate(ACOES_IBRX100, 1):
        print(f"   [{i:2d}/{len(ACOES_IBRX100)}] {ticker}...", end=" ", flush=True)
        dados = baixar_dados_completos(ticker, meses=20)
        if dados:
            historico[ticker] = dados
            print(f"OK ({len(dados)} dias)")
        else:
            print("SEM DADOS")
    
    print()
    print(f"Historico carregado: {len(historico)} ativos")
    print()
    
    # Executa simulacao
    resultado = simular_sistema(historico, fundamentais)
    
    if resultado:
        print()
        print("=" * 70)
        print("RESULTADO DA SIMULACAO")
        print("=" * 70)
        print(f"Capital inicial: R$ {resultado['capital_inicial']:,.2f}")
        print(f"Capital final:   R$ {resultado['capital_final']:,.2f}")
        
        lucro_total = resultado['capital_final'] - resultado['capital_inicial']
        retorno_total = (resultado['capital_final'] / resultado['capital_inicial'] - 1) * 100
        
        print(f"Lucro/Prejuizo:  R$ {lucro_total:,.2f}")
        print(f"Retorno total:   {retorno_total:+.2f}%")
        print()
        
        # Analise das operacoes
        ops = resultado['operacoes']
        if ops:
            total_ops = len(ops)
            wins = sum(1 for o in ops if o['retorno'] > 0)
            losses = sum(1 for o in ops if o['retorno'] <= 0)
            
            print(f"Total de operacoes: {total_ops}")
            print(f"Operacoes vencedoras: {wins} ({wins/total_ops*100:.1f}%)")
            print(f"Operacoes perdedoras: {losses} ({losses/total_ops*100:.1f}%)")
            print()
            
            # Retorno medio
            media_retorno = sum(o['retorno'] for o in ops) / total_ops * 100
            print(f"Retorno medio por operacao: {media_retorno:+.2f}%")
            
            # Melhor e pior operacao
            melhor = max(ops, key=lambda x: x['retorno'])
            pior = min(ops, key=lambda x: x['retorno'])
            
            print(f"Melhor operacao: {melhor['ticker']} ({melhor['retorno']*100:+.2f}%)")
            print(f"Pior operacao:   {pior['ticker']} ({pior['retorno']*100:+.2f}%)")
            print()
            
            # Operacoes por motivo
            motivos = {}
            for o in ops:
                motivo = o['motivo']
                if motivo not in motivos:
                    motivos[motivo] = {'count': 0, 'lucro': 0}
                motivos[motivo]['count'] += 1
                motivos[motivo]['lucro'] += o['lucro']
            
            print("Operacoes por motivo:")
            for motivo, dados in sorted(motivos.items()):
                print(f"  {motivo}: {dados['count']} ops, R$ {dados['lucro']:,.2f}")
            
            # Salva resultados
            with open(OUTPUT_DIR / 'data' / 'backtest_regras_reais.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'data_execucao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'parametros': {
                        'rsl_periodos': RSL_PERIODOS,
                        'atr_periodos': ATR_PERIODOS,
                        'atr_multiplicador': ATR_MULTIPLICADOR,
                        'take_profit': TAKE_PROFIT,
                        'max_posicoes': MAX_POSICOES,
                        'capital_inicial': CAPITAL_INICIAL
                    },
                    'resultado': {
                        'capital_final': resultado['capital_final'],
                        'lucro_total': lucro_total,
                        'retorno_total': retorno_total,
                        'total_operacoes': total_ops,
                        'wins': wins,
                        'losses': losses,
                        'win_rate': wins/total_ops*100
                    },
                    'operacoes': ops
                }, f, ensure_ascii=False, indent=2)
            
            print()
            print("Resultados salvos em: data/backtest_regras_reais.json")
        
        print("=" * 70)

if __name__ == "__main__":
    main()
