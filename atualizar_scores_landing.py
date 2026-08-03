#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza scores.json com campos para landing page"""

import json

# Carrega scores atuais
with open('data/scores.json', 'r', encoding='utf-8') as f:
    scores = json.load(f)

# Atualiza campos para compatibilidade com landing page
for s in scores:
    # Adiciona preco_atual (copiar de preco)
    s['preco_atual'] = s.get('preco', 0)
    
    # Adiciona euforia (calcular ou definir False)
    s['euforia'] = 'False'
    
    # Adiciona score_liquidez (100 por padrao)
    s['score_liquidez'] = 100

# Salva
with open('data/scores.json', 'w', encoding='utf-8') as f:
    json.dump(scores, f, ensure_ascii=False, indent=2)

print('Scores atualizados com campos para landing page')
print('Top 10:')
for i, s in enumerate(scores[:10], 1):
    print(f"{i}. {s['ticker']}: {s['score_composto']}")
