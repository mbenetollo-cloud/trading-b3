# CHECKLIST DE COMMITS - SISTEMA IBrX100

## Regra de Ouro
**TODA alteração DEVE ser comitada imediatamente!**

## Checklist Antes de Sair

- [ ] Todos os scripts modificados foram comitados?
- [ ] Todos os dados atualizados foram comitados?
- [ ] Documentação foi atualizada?
- [ ] Resultados de testes foram salvos?
- [ ] Configurações foram documentadas?

## O que Comitar

### Scripts
- [ ] fluxo_completo.py
- [ ] baixar_dados.py
- [ ] calcular_momentum.py
- [ ] coletar_fundamentais.py
- [ ] backtesting*.py
- [ ] config.py

### Dados
- [ ] data/scores.json
- [ ] data/fundamentais.json
- [ ] data/momentums.json
- [ ] data/backtest_*.json

### Documentação
- [ ] INVENTARIO_MUDANCAS.md
- [ ] BACKTESTING_RESULTADOS.md
- [ ] Obsidian vault (*.md)

## Commits Recomendados

```
feat: [descrição da funcionalidade]
fix: [descrição da correção]
docs: [descrição da documentação]
update: [descrição da atualização]
```

## Exemplo de Fluxo

1. Faz alteração
2. Testa
3. **COMITA IMEDIATAMENTE**
4. Documenta
5. **COMITA DOCUMENTAÇÃO**
6. Push para GitHub

---

* Criado: 04/08/2026
* Última atualização: 04/08/2026
