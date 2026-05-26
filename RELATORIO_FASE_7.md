# Relatorio Fase 7

## Objetivo da fase

Implementar analise simples de tendencia de peso, media movel, deteccao de possivel plato e recomendacoes educativas usando heuristicas transparentes, sem machine learning pesado e sem novas dependencias.

## Arquivos criados

- `app/services/trend_service.py`
- `tests/test_trend_service.py`
- `RELATORIO_FASE_7.md`

## Arquivos alterados

- `app/routes.py`
- `app/templates/dashboard.html`
- `app/templates/weekly_report.html`
- `app/static/js/charts.js`
- `tests/test_app.py`
- `README.md`
- `TODO.md`
- `LESSONS.md`

## Heuristicas implementadas

- Media movel simples do peso com janela de ate 7 registros.
- Tendencia de peso com classificacao:
  - `reduzindo`
  - `aumentando`
  - `estavel`
  - `dados insuficientes`
- Variacao aproximada semanal.
- Possivel plato quando ha pelo menos 14 dias de medidas e variacao absoluta menor ou igual a 0.3 kg.
- Analise educativa cruzando calorias medias, meta calorica, aderencia e tendencia de peso.

## Telas alteradas

- Dashboard:
  - nova secao "Analise de Tendencia"
  - tendencia atual
  - variacao no periodo
  - media movel atual
  - possivel plato
  - recomendacao educativa
  - grafico de peso com linha de media movel
- Relatorio semanal:
  - tendencia semanal
  - variacao semanal aproximada
  - media movel
  - possivel plato
  - recomendacao educativa

## Testes adicionados

- Sem medidas.
- Uma medida apenas.
- Duas medidas com reducao.
- Duas medidas com aumento.
- Peso estavel.
- Calculo de media movel.
- Plato detectado.
- Plato nao detectado.
- Dados insuficientes para plato.
- Recomendacao com dados insuficientes.
- Recomendacao para baixa aderencia.
- Recomendacao para possivel reavaliacao de meta.
- Dashboard com poucos dados.
- Dashboard com dados suficientes.
- Relatorio semanal com analise de tendencia.

## Resultado do pytest

Comando:

```bash
python -m pytest
```

Resultado:

```text
75 passed
```

## Resultado dos smoke tests

Auth desabilitada:

- `/`: 200
- `/profile`: 200
- `/foods`: 200
- `/meals`: 200
- `/measurements`: 200
- `/weekly-report`: 200
- `/exports`: 200

Auth habilitada continua coberta por testes especificos.

## Limitacoes restantes

- Heuristicas dependem da qualidade e frequencia dos registros.
- Possivel plato e apenas uma leitura educativa.
- Nao ha machine learning ou predicao estatistica avancada.
- Relatorios semanais ainda nao sao persistidos historicamente.

## Recomendacoes para proxima fase

- Fase 8: persistir relatorios semanais gerados.
- Permitir comparar relatorios historicos.
- Evitar duplicidade por semana.
- Preparar migracoes formais se a persistencia exigir mudancas no schema.
