---
tags: #trading #ibrx100 #backtesting #resultados
---

# Backtesting - Resultados e Configuracoes

## Periodo de Teste
- **Inicio:** Janeiro/2025
- **Fim:** Agosto/2026
- **Duracao:** ~1.5 anos (358 dias uteis)

## Ativos Testados
- **Indice:** IBrX100
- **Quantidade:** 99 ativos (lista B3 03/08/2026)
- **Filtro:** Todos os ativos do indice

## Parametros do Sistema

### Entrada
| Parametro | Valor | Descricao |
|-----------|-------|-----------|
| RSL | 14 periodos | Relative Strength Level |
| Condicao RSL | > 1.0 | Tendencia de alta |
| MM50 > MM200 | Sim | Tendencia confirmada |
| Euforia | < 15% | Nao comprar se gap muito alto |

### Saida
| Parametro | Valor | Descricao |
|-----------|-------|-----------|
| Stop Loss | ATR 12 x 1,5 | Baseado em volatilidade |
| Take Profit | 20% | Lucro esperado |
| Trailing Stop | 8% | Protecao de lucro |
| Tendencia | MM50 < MM200 | Saida por reversao |

### Gestao de Risco
| Parametro | Valor | Descricao |
|-----------|-------|-----------|
| Max posicoes | 5 | Simultaneas |
| Max por posicao | 5% | Do capital total |
| Capital inicial | R$ 10.000 | Simulacao |

## Resultados Obtidos

### Retorno Geral
| Metrica | Valor |
|---------|-------|
| Capital inicial | R$ 10.000,00 |
| Capital final | R$ 11.138,92 |
| Lucro total | R$ 1.138,92 |
| Retorno total | +11,39% |
| **Retorno anualizado** | **~7,6%** |

### Operacoes
| Metrica | Valor |
|---------|-------|
| Total de operacoes | 61 |
| Operacoes vencedoras | 24 (39,3%) |
| Operacoes perdedoras | 37 (60,7%) |
| Retorno medio/op | +3,70% |

### Por Motivo de Saida
| Motivo | Ops | Lucro |
|--------|-----|-------|
| TAKE PROFIT | 19 | +R$ 2.182,33 |
| STOP LOSS | 35 | -R$ 1.057,45 |
| TENDENCIA QUEDA | 2 | +R$ 34,88 |
| FIM SIMULACAO | 5 | -R$ 20,84 |

### Melhores Operacoes
| Rank | Ativo | Retorno |
|------|-------|---------|
| 1 | ANIM3 | +31,36% |
| 2 | AURE3 | +22,50% |
| 3 | BBSE3 | +21,55% |

### Piores Operacoes
| Rank | Ativo | Retorno |
|------|-------|---------|
| 1 | AXIA3 | -23,77% |
| 2 | BRKM5 | -14,21% |
| 3 | CURY3 | -8,37% |

## Analise dos Resultados

### Pontos Fortes
- Take Profits geraram +R$ 2.182 (19 operacoes)
- Stop Loss limitou perdas em -R$ 1.057 (35 operacoes)
- Saldo final positivo (+R$ 1.138)

### Pontos de Atencao
- Win Rate de 39,3% (abaixo de 50%)
- Muitos stop losses (35 de 61 operacoes)
- Retorno anualizado (7,6%) abaixo do objetivo (18%)

### Possiveis Melhorias
1. Ajustar periodo do RSL (testar 22 periodos)
2. Modificar multiplicador do ATR (testar 2,0)
3. Adicionar filtros fundamentalistas na entrada
4. Testar diferentes periodos de hold

## Comparacao com Mercado

| Indice | Retorno Anualizado |
|--------|-------------------|
| **Sistema IBrX100** | **~7,6%** |
| IBovespa (referencia) | ~12% (media historica) |
| CDI | ~10,5% (2025) |

## Proximos Passos

1. **Otimizar parametros:** Testar diferentes combinacoes
2. **Estender periodo:** Testar com 2-3 anos de dados
3. **Adicionar filtros:** Considerar fundamentais na entrada
4. **Comparar versoes:** Testar sem filtro de euforia

## Observacoes Importantes

- O backtesting NAO considera custos operacionais (corretagem, emolumentos)
- Resultados passados NAO garantem resultados futuros
- O sistema esta em fase de teste e validacao

---

*Documento gerado em 04/08/2026*
*Version: 1.0*
