#!/usr/bin/env python3
import json
with open('output/data/scores.json', 'r', encoding='utf-8') as f:
    scores = json.load(f)
print('Top 10 no scores.json:')
for i, s in enumerate(scores[:10], 1):
    print(f"{i}. {s['ticker']}: {s['score_composto']}")
