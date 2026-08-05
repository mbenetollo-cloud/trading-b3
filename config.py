# -*- coding: utf-8 -*-
"""
CONFIGURACAO DO SISTEMA DE TRADING B3
======================================
TODO PARAMETRO PODE SER ALTERADO AQUI PARA FACIL ACESSO.
Autor: mbene
Data: 2026-08-04
Ultima otimizacao: Backtesting 01/2025 a 06/2026
"""

# ============================================================
# INDEX
# ============================================================
INDICE = 'IBRX100'  # IBOV ou IBrX100

# ============================================================
# PESOS DO SCORE (soma = 100%)
# ============================================================
PESOS = {
    'fundamental': 30,    # Peso do fundamental (trimestral)
    'momentum': 35,       # Peso do momentum (diário)
    'valuation': 25,      # Peso do valuation (diário)
    'dividendos': 10      # Peso dos dividendos (diário)
}

# ============================================================
# INDICADORES FUNDAMENTAIS (trimestrais)
# ============================================================
ROE_MINIMO = 0.10        # ROE mínimo (10%)
ROIC_MINIMO = 0.08       # ROIC mínimo (8%)
DIVIDA_LIQUIDA_EBITDA_MAX = 3.0  # Endividamento máximo

# ============================================================
# INDICADORES DE MOMENTO (diários)
# ============================================================
RSL_PERIODOS = 10        # Período do RSL (OTIMIZADO: 10 > 14)
MM_CURTA = 50            # Média móvel curta
MM_LONGA = 200           # Média móvel longa

# ============================================================
# INDICADORES DE VALOR (diários)
# ============================================================
PL_MAXIMO = 20           # P/L máximo
PL_MINIMO = 3            # P/L mínimo
PVP_MAXIMO = 3           # P/VP máximo

# ============================================================
# DIVIDENDOS
# ============================================================
DY_MINIMO = 2.0          # Dividend Yield mínimo (2%) - OTIMIZADO

# ============================================================
# FILTROS
# ============================================================
SCORE_MINIMO = 50        # Score mínimo para compra
VOLUME_MINIMO = 1000000  # Volume mínimo diário

# ============================================================
# GESTAO DE RISCO
# ============================================================
STOP_LOSS = 0.06         # Stop loss (6%) - OTIMIZADO
TAKE_PROFIT = 0.25       # Take profit (25%) - OTIMIZADO
TRAILING_STOP = 0.05     # Trailing stop (5%) - OTIMIZADO
MAX_POSICOES = 5         # Máximo de posições simultâneas
MAX_POR_POSICAO = 0.05   # Máximo 5% por posição (conservador)

# ============================================================
# CAPITAL
# ============================================================
CAPITAL_INICIAL = 10000  # R$ 10.000
# Capital cresce com retornos + aportes

# ============================================================
# FONTES DE DADOS
# ============================================================
FONTE_PRINCIPAL = 'OpenFinance'  # Fonte principal
FONTE_FALLBACK = 'yfinance'      # Fallback

# ============================================================
# ATUALIZACAO
# ============================================================
FREQ_ATUALIZACAO_DIARIA = True
FREQ_ATUALIZACAO_TRIMESTRAL = True

# ============================================================
# LANDING PAGE
# ============================================================
PASTA_OUTPUT = 'output'
ARQUIVO_LANDING_PAGE = 'index.html'

# ============================================================
# BACKTEST
# ============================================================
PERIODO_BACKTEST = '2025-01-01'
