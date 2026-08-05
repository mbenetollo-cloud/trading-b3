#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTESTING - VARIACAO DE INDICADORES
======================================
Testa variacoes de:
- Take Profit (15%, 20%, 25%, 30%)
- Trailing Stop (5%, 8%, 10%, 12%)
- RSL Periodos (10, 14, 20, 30)
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

# Parametros fixos (usados como base)
STOP_LOSS_FIXO = 0.06  # 6% (melhor encontrado)
ATR_PERIODOS = 12
ATR_MULTIPLICADOR = 1.5
MAX_POSICOES = 5
MAX_POR_POSICAO = 0.05
CAPITAL_INICIAL = 10000

def baixar_dados_completos(ticker, data_inicio_str='2025-01-01', data_fim_str='2026-06-30'):
    """Baixa dados OHLCV completos"""
    try:
        ticker_yf = f"{ticker}.SA"
        dados = yf.download(
            ticker_yf,
            start=data_inicio_str,
            end=data_fim_str,
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
    except:
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
    
    if len(tr_list) >= periodo:
        return sum(tr_list[-periodo:]) / periodo
    return None

def calcular_rsl(dados, periodo=14):
    """Calcula RSL"""
    if len(dados) < periodo:
        return None
    
    precos = [d['close'] for d in dados[-periodo:]]
    media = sum(precos) / periodo
    preco_atual = dados[-1]['close']
    
    return preco_atual / media if media > 0 else None

def calcular_mm(dados, periodo):
    """Calcula Media Movvel"""
    if len(dados) < periodo:
        return None
    
    precos = [d['close'] for d in dados[-periodo:]]
    return sum(precos) / periodo

def simular_sistema(historico, take_profit, trailing_stop, rsl_periodos):
    """Simula o sistema com parametros especificos"""
    
    dados_ativos = {}
    for ticker in ACOES_IBRX100:
        dados = historico.get(ticker)
        if dados and len(dados) > 50:
            dados_ativos[ticker] = dados
    
    capital = CAPITAL_INICIAL
    posicoes = []
    historico_operacoes = []
    
    todas_datas = set()
    for dados in dados_ativos.values():
        for d in dados:
            todas_datas.add(d['data'])
    
    datas_ordenadas = sorted(todas_datas)
    datas_simulacao = datas_ordenadas[50:]
    
    for data_atual in datas_simulacao:
        # 1. Verifica stops
        posicoes_para_fechar = []
        for pos in posicoes:
            ticker = pos['ticker']
            dados = dados_ativos.get(ticker)
            if not dados:
                continue
            
            preco_atual = None
            for d in dados:
                if d['data'] == data_atual:
                    preco_atual = d['close']
                    break
            
            if preco_atual is None:
                continue
            
            dados_ate_agora = [d for d in dados if d['data'] <= data_atual]
            atr = calcular_atr(dados_ate_agora, ATR_PERIODOS)
            
            # Stop Loss
            stop_loss_fixo_calc = pos['preco_entrada'] * (1 - STOP_LOSS_FIXO)
            stop_loss_atr = None
            if atr is not None:
                stop_loss_atr = pos['preco_entrada'] - (atr * ATR_MULTIPLICADOR)
            
            stop_loss = max(stop_loss_fixo_calc, stop_loss_atr) if stop_loss_atr else stop_loss_fixo_calc
            
            # Take Profit
            take_profit_calc = pos['preco_entrada'] * (1 + take_profit)
            
            # Trailing Stop
            preco_maximo = pos.get('preco_maximo', pos['preco_entrada'])
            if preco_atual > preco_maximo:
                preco_maximo = preco_atual
                pos['preco_maximo'] = preco_maximo
                novo_stop = preco_maximo * (1 - trailing_stop)
                if novo_stop > stop_loss:
                    stop_loss = novo_stop
            
            if preco_atual <= stop_loss:
                posicoes_para_fechar.append((pos, preco_atual, 'STOP LOSS'))
            elif preco_atual >= take_profit_calc:
                posicoes_para_fechar.append((pos, preco_atual, 'TAKE PROFIT'))
        
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
        
        # 2. Verifica novas entradas
        if len(posicoes) < MAX_POSICOES:
            for ticker, dados in dados_ativos.items():
                if len(posicoes) >= MAX_POSICOES:
                    break
                
                if any(p['ticker'] == ticker for p in posicoes):
                    continue
                
                dados_ate_agora = [d for d in dados if d['data'] <= data_atual]
                if len(dados_ate_agora) < 50:
                    continue
                
                rsl = calcular_rsl(dados_ate_agora, rsl_periodos)
                mm50 = calcular_mm(dados_ate_agora, 50)
                mm200 = calcular_mm(dados_ate_agora, 200)
                
                if rsl is None or mm50 is None:
                    continue
                
                condicao_tendencia = True
                tem_euforia = False
                
                if mm200 is not None:
                    condicao_tendencia = mm50 > mm200
                    if mm50 > mm200:
                        gap = (mm50 - mm200) / mm200
                        if gap > 0.15:
                            tem_euforia = True
                
                if rsl > 1.0 and condicao_tendencia and not tem_euforia:
                    preco_atual = None
                    for d in dados:
                        if d['data'] == data_atual:
                            preco_atual = d['close']
                            break
                    
                    if preco_atual is None:
                        continue
                    
                    capital_por_posicao = capital * 0.05
                    qtd_acoes = int(capital_por_posicao / preco_atual)
                    if qtd_acoes < 1:
                        continue
                    
                    posicoes.append({
                        'ticker': ticker,
                        'data_entrada': data_atual,
                        'preco_entrada': preco_atual,
                        'quantidade': qtd_acoes,
                        'capital_investido': qtd_acoes * preco_atual,
                        'preco_maximo': preco_atual
                    })
        
        # 3. Verifica saida por tendencia de queda
        posicoes_para_fechar_tendencia = []
        for pos in posicoes:
            ticker = pos['ticker']
            dados = dados_ativos.get(ticker)
            if not dados:
                continue
            
            dados_ate_agora = [d for d in dados if d['data'] <= data_atual]
            mm50 = calcular_mm(dados_ate_agora, 50)
            mm200 = calcular_mm(dados_ate_agora, 200)
            
            if mm50 is not None and mm200 is not None and mm50 < mm200:
                preco_atual = None
                for d in dados:
                    if d['data'] == data_atual:
                        preco_atual = d['close']
                        break
                
                if preco_atual is not None:
                    posicoes_para_fechar_tendencia.append((pos, preco_atual))
        
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
        dados = dados_ativos.get(pos['ticker'])
        if dados:
            ultimo_preco = dados[-1]['close']
            retorno = (ultimo_preco - pos['preco_entrada']) / pos['preco_entrada']
            lucro = pos['capital_investido'] * retorno
            
            historico_operacoes.append({
                'ticker': pos['ticker'],
                'data_entrada': pos['data_entrada'],
                'data_saida': datas_ordenadas[-1],
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
    print("BACKTESTING - VARIACAO DE INDICADORES")
    print("=" * 70)
    print(f"Data: {datetime.now()}")
    print(f"Periodo: Janeiro/2025 a Junho/2026 (~18 meses)")
    print(f"Stop Loss fixo: 6% (melhor encontrado)")
    print("=" * 70)
    print()
    
    # Baixa historico uma vez so
    print("Baixando historico completo...")
    historico = {}
    for i, ticker in enumerate(ACOES_IBRX100, 1):
        print(f"   [{i:2d}/{len(ACOES_IBRX100)}] {ticker}...", end=" ", flush=True)
        dados = baixar_dados_completos(ticker)
        if dados:
            historico[ticker] = dados
            print(f"OK ({len(dados)} dias)")
        else:
            print("SEM DADOS")
    
    print()
    print(f"Historico carregado: {len(historico)} ativos")
    
    # ============================================
    # TESTE 1: VARIACAO TAKE PROFIT
    # ============================================
    print("\n" + "=" * 70)
    print("TESTE 1: VARIACAO TAKE PROFIT (15%, 20%, 25%, 30%)")
    print("=" * 70)
    
    resultados_tp = []
    for tp in [0.15, 0.20, 0.25, 0.30]:
        print(f"\nTestando Take Profit {tp*100:.0f}%...")
        resultado = simular_sistema(historico, tp, 0.08, 14)
        
        lucro_total = resultado['capital_final'] - resultado['capital_inicial']
        retorno_total = (resultado['capital_final'] / resultado['capital_inicial'] - 1) * 100
        
        ops = resultado['operacoes']
        total_ops = len(ops)
        wins = sum(1 for o in ops if o['retorno'] > 0)
        losses = sum(1 for o in ops if o['retorno'] <= 0)
        
        take_profits = sum(1 for o in ops if o['motivo'] == 'TAKE PROFIT')
        stop_losses = sum(1 for o in ops if o['motivo'] == 'STOP LOSS')
        
        print(f"  Retorno: {retorno_total:+.2f}% | Win Rate: {wins/total_ops*100:.1f}% | TP: {take_profits} | SL: {stop_losses}")
        
        resultados_tp.append({
            'take_profit': tp,
            'retorno_total': retorno_total,
            'win_rate': wins/total_ops*100,
            'take_profits': take_profits,
            'stop_losses': stop_losses
        })
    
    print("\nRESUMO TAKE PROFIT:")
    print(f"{'TP':<8} {'Retorno':<12} {'Win Rate':<12} {'TPs':<8} {'SLs':<8}")
    print("-" * 50)
    for r in resultados_tp:
        print(f"{r['take_profit']*100:.0f}%{'':<6} {r['retorno_total']:+.2f}%{'':<8} {r['win_rate']:.1f}%{'':<8} {r['take_profits']:<8} {r['stop_losses']:<8}")
    
    melhor_tp = max(resultados_tp, key=lambda x: x['retorno_total'])
    print(f"\nMELHOR TP: {melhor_tp['take_profit']*100:.0f}% -> {melhor_tp['retorno_total']:+.2f}%")
    
    # ============================================
    # TESTE 2: VARIACAO TRAILING STOP
    # ============================================
    print("\n" + "=" * 70)
    print("TESTE 2: VARIACAO TRAILING STOP (5%, 8%, 10%, 12%)")
    print("=" * 70)
    
    resultados_ts = []
    for ts in [0.05, 0.08, 0.10, 0.12]:
        print(f"\nTestando Trailing Stop {ts*100:.0f}%...")
        resultado = simular_sistema(historico, 0.20, ts, 14)
        
        lucro_total = resultado['capital_final'] - resultado['capital_inicial']
        retorno_total = (resultado['capital_final'] / resultado['capital_inicial'] - 1) * 100
        
        ops = resultado['operacoes']
        total_ops = len(ops)
        wins = sum(1 for o in ops if o['retorno'] > 0)
        
        take_profits = sum(1 for o in ops if o['motivo'] == 'TAKE PROFIT')
        stop_losses = sum(1 for o in ops if o['motivo'] == 'STOP LOSS')
        
        print(f"  Retorno: {retorno_total:+.2f}% | Win Rate: {wins/total_ops*100:.1f}% | TP: {take_profits} | SL: {stop_losses}")
        
        resultados_ts.append({
            'trailing_stop': ts,
            'retorno_total': retorno_total,
            'win_rate': wins/total_ops*100,
            'take_profits': take_profits,
            'stop_losses': stop_losses
        })
    
    print("\nRESUMO TRAILING STOP:")
    print(f"{'TS':<8} {'Retorno':<12} {'Win Rate':<12} {'TPs':<8} {'SLs':<8}")
    print("-" * 50)
    for r in resultados_ts:
        print(f"{r['trailing_stop']*100:.0f}%{'':<6} {r['retorno_total']:+.2f}%{'':<8} {r['win_rate']:.1f}%{'':<8} {r['take_profits']:<8} {r['stop_losses']:<8}")
    
    melhor_ts = max(resultados_ts, key=lambda x: x['retorno_total'])
    print(f"\nMELHOR TS: {melhor_ts['trailing_stop']*100:.0f}% -> {melhor_ts['retorno_total']:+.2f}%")
    
    # ============================================
    # TESTE 3: VARIACAO RSL PERIODOS
    # ============================================
    print("\n" + "=" * 70)
    print("TESTE 3: VARIACAO RSL PERIODOS (10, 14, 20, 30)")
    print("=" * 70)
    
    resultados_rsl = []
    for rsl in [10, 14, 20, 30]:
        print(f"\nTestando RSL {rsl} periodos...")
        resultado = simular_sistema(historico, 0.20, 0.08, rsl)
        
        lucro_total = resultado['capital_final'] - resultado['capital_inicial']
        retorno_total = (resultado['capital_final'] / resultado['capital_inicial'] - 1) * 100
        
        ops = resultado['operacoes']
        total_ops = len(ops)
        wins = sum(1 for o in ops if o['retorno'] > 0)
        
        take_profits = sum(1 for o in ops if o['motivo'] == 'TAKE PROFIT')
        stop_losses = sum(1 for o in ops if o['motivo'] == 'STOP LOSS')
        
        print(f"  Retorno: {retorno_total:+.2f}% | Win Rate: {wins/total_ops*100:.1f}% | TP: {take_profits} | SL: {stop_losses}")
        
        resultados_rsl.append({
            'rsl_periodos': rsl,
            'retorno_total': retorno_total,
            'win_rate': wins/total_ops*100,
            'take_profits': take_profits,
            'stop_losses': stop_losses
        })
    
    print("\nRESUMO RSL:")
    print(f"{'RSL':<8} {'Retorno':<12} {'Win Rate':<12} {'TPs':<8} {'SLs':<8}")
    print("-" * 50)
    for r in resultados_rsl:
        print(f"{r['rsl_periodos']:<8} {r['retorno_total']:+.2f}%{'':<8} {r['win_rate']:.1f}%{'':<8} {r['take_profits']:<8} {r['stop_losses']:<8}")
    
    melhor_rsl = max(resultados_rsl, key=lambda x: x['retorno_total'])
    print(f"\nMELHOR RSL: {melhor_rsl['rsl_periodos']} periodos -> {melhor_rsl['retorno_total']:+.2f}%")
    
    # ============================================
    # RESUMO FINAL
    # ============================================
    print("\n" + "=" * 70)
    print("RESUMO FINAL - MELHORES PARAMETROS")
    print("=" * 70)
    print(f"Melhor Take Profit:  {melhor_tp['take_profit']*100:.0f}% -> {melhor_tp['retorno_total']:+.2f}%")
    print(f"Melhor Trailing Stop: {melhor_ts['trailing_stop']*100:.0f}% -> {melhor_ts['retorno_total']:+.2f}%")
    print(f"Melhor RSL:          {melhor_rsl['rsl_periodos']} periodos -> {melhor_rsl['retorno_total']:+.2f}%")
    
    # Teste combinacao otima
    print("\n" + "=" * 70)
    print("TESTE COMBINACAO OTIMA")
    print("=" * 70)
    print(f"Testando: TP {melhor_tp['take_profit']*100:.0f}% + TS {melhor_ts['trailing_stop']*100:.0f}% + RSL {melhor_rsl['rsl_periodos']}")
    
    resultado_otimo = simular_sistema(
        historico, 
        melhor_tp['take_profit'], 
        melhor_ts['trailing_stop'], 
        melhor_rsl['rsl_periodos']
    )
    
    retorno_otimo = (resultado_otimo['capital_final'] / resultado_otimo['capital_inicial'] - 1) * 100
    print(f"RESULTADO COMBINACAO OTIMA: {retorno_otimo:+.2f}%")
    
    # Salva todos os resultados
    with open(OUTPUT_DIR / 'data' / 'backtest_variacao_indicadores.json', 'w', encoding='utf-8') as f:
        json.dump({
            'data_execucao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'periodo': '2025-01-01 a 2026-06-30',
            'stop_loss_fixo': 0.06,
            'resultados_take_profit': resultados_tp,
            'resultados_trailing_stop': resultados_ts,
            'resultados_rsl': resultados_rsl,
            'melhor_combinacao': {
                'take_profit': melhor_tp['take_profit'],
                'trailing_stop': melhor_ts['trailing_stop'],
                'rsl_periodos': melhor_rsl['rsl_periodos'],
                'retorno': retorno_otimo
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados salvos em: data/backtest_variacao_indicadores.json")

if __name__ == "__main__":
    main()
