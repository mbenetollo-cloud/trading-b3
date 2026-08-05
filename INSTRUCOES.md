# INSTRUÇÕES DO PROJETO - Trading B3 IBrX100

## Regras Fundamentais
1. NUNCA usar dados de simulação em produção
2. DY deve ser percentual (2.0 = 2%), não decimal (0.02)
3. MM50/MM200 é FILTRO de compra, não apenas componente de score
4. DY_MINIMO = 2.0 (2%)
5. Sempre commitar alterações imediatamente
6. Documentar mudanças no INSTRUCOES.md

## Temporalidade dos Dados
- **Indicadores** (MM50, MM200, RSL, Euforia): Diário/Semanal
- **Fundamentais**: Conforme calendário de publicação (Investidor10)
- **Dividendos**: Conforme calendário de publicação

## Ciclo de Atualização
- Sexta 18h: Nova semana inicia
- Indicadores: Atualização automática (agente)
- Fundamentais: Quando empresa publica resultados

## Convenções
- Lista oficial: 99 ativos IBrX100 (CSV B3)
- Score: Fundamental(35) + Valuation(25) + Momentum(30) + Dividendos(10) = 100
- Filtros: Lucro negativo, Patrimônio negativo, FCF negativo

## Fontes de Dados
- **Yahoo Finance (yfinance)**: Preços, fundamentais, indicadores, dividendos
- *Nota: Investidor10 era fonte planejada mas é JS-rendered, inacessível*

## Histórico de Alterações
- 04/08/2026: Corrigido bug DY, adicionado filtro compra MM50/Euforia
- 04/08/2026: Definida regra temporal (sexta 18h = nova semana)
- 04/08/2026: Separados fluxos semanal e diário
