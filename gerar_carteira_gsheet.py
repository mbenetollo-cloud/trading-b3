#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera dados para Google Sheets - Carteira IBrX100
"""

import json
from datetime import datetime

# Carrega scoring
with open('D:\\Meus APP\\ibrx100_system\\output\\data\\scores.json', 'r', encoding='utf-8') as f:
    scores = json.load(f)

top10 = scores[:10]

nomes = {
    "FLRY3.SA": "Fleury",
    "ABEV3.SA": "Ambev",
    "PETR3.SA": "Petrobras PN",
    "PETR4.SA": "Petrobras ON",
    "HYPE3.SA": "Hypera",
    "EZTC3.SA": "Eztec",
    "MULT3.SA": "Multiplan",
    "B3SA3.SA": "B3",
    "TOTS3.SA": "TOTVS",
    "LREN3.SA": "Lojas Renner"
}

# Gera CSV para importar no Google Sheets
csv_lines = []

# Header
csv_lines.append("Rank,Ticker,Nome,Score,Fundamental,Valuation,Momentum,Dividendos,Data Entrada,Preco Entrada,Quantidade,Custo Total,Preco Atual,Valor Atual,Lucro/Prejuizo,Retorno %")

# Dados
for i, stock in enumerate(top10):
    ticker = stock['ticker'].replace('.SA', '')
    row = [
        i+1,
        ticker,
        nomes.get(stock['ticker'], ''),
        stock['score_composto'],
        stock['score_fundamental'],
        stock['score_valuation'],
        stock['score_momentum'],
        stock['score_dividendos'],
        datetime.now().strftime("%d/%m/%Y"),
        stock['preco_atual'],
        0,  # Quantidade (usuario preenche)
        f'=J{i+2}*K{i+2}',  # Custo Total
        f'=IFERROR(GOOGLEFINANCE("BVMF:{ticker}","price"),{stock["preco_atual"]})',  # Preco Atual
        f'=K{i+2}*M{i+2}',  # Valor Atual
        f'=N{i+2}-L{i+2}',  # Lucro/Prejuizo
        f'=IFERROR(O{i+2}/L{i+2},0)'  # Retorno %
    ]
    csv_lines.append(','.join(str(x) for x in row))

# Salva CSV
csv_path = 'D:\\Meus APP\\ibrx100_system\\carteira_ibrx100.csv'
with open(csv_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(csv_lines))

print("CSV gerado:", csv_path)
print()
print("=== INSTRUCOES PARA GOOGLE SHEETS ===")
print()
print("1. Acesse: https://sheets.google.com")
print("2. Clique em 'Arquivo' > 'Importar' > 'Fazer upload'")
print("3. Selecione o arquivo: carteira_ibrx100.csv")
print("4. Escolha: 'Separador: virgula'")
print("5. Clique em 'Importar'")
print()
print("6. Na coluna K (Quantidade), preencha o numero de acoes")
print("7. As formulas GOOGLEFINANCE vao atualizar automaticamente")
print()
print("=== TOP 10 INCLUIDOS ===")
for i, stock in enumerate(top10):
    ticker = stock['ticker'].replace('.SA', '')
    print(f"  {i+1}. {ticker} - Score: {stock['score_composto']}")