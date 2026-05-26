# Relatorio Fase 8

## Objetivo da fase

Persistir relatorios semanais gerados no SQLite, permitir consultar historico, evitar duplicacao por semana, exportar relatorios persistidos em CSV e manter compatibilidade com o relatorio semanal dinamico atual.

## Arquivos criados

- `app/services/report_service.py`
- `app/templates/weekly_reports_history.html`
- `app/templates/weekly_report_saved.html`
- `tests/test_report_service.py`
- `tests/test_weekly_reports_routes.py`
- `RELATORIO_FASE_8.md`

## Arquivos alterados

- `app/database.py`
- `app/routes.py`
- `app/services/export_service.py`
- `app/templates/base.html`
- `app/templates/weekly_report.html`
- `app/templates/exports.html`
- `README.md`
- `TODO.md`
- `LESSONS.md`

## Tabela criada/evoluida

Tabela:

```text
weekly_reports
```

Campos principais:

- `id`
- `week_start`
- `week_end`
- `created_at`
- `updated_at`
- `weight_start`
- `weight_end`
- `weight_delta`
- `avg_calories`
- `avg_protein`
- `avg_carbs`
- `avg_fat`
- `waist_delta`
- `adherence_score`
- `trend_status`
- `weekly_weight_delta`
- `moving_average_latest`
- `plateau_detected`
- `recommendation`
- `notes`

Foi adicionado indice unico em `week_start` para evitar duplicidade por semana.

## Rotas adicionadas

- `POST /weekly-report/save`
- `POST /weekly-report/overwrite`
- `GET /weekly-reports`
- `GET /weekly-reports/<int:report_id>`
- `POST /weekly-reports/<int:report_id>/delete`
- `GET /exports/weekly-reports-history.csv`

## Interface adicionada

- Botao para salvar relatorio semanal.
- Aviso quando ja existe relatorio salvo para a semana.
- Botao para atualizar/sobrescrever relatorio salvo.
- Tela de historico de relatorios.
- Tela de visualizacao de snapshot salvo.
- Botao de exportacao CSV do historico em `/exports`.

## Testes adicionados

- Criacao segura da tabela `weekly_reports`.
- Salvamento de relatorio semanal.
- Bloqueio de duplicidade por `week_start`.
- Sobrescrita de relatorio existente.
- Listagem de historico.
- Visualizacao de relatorio salvo.
- Exclusao de relatorio salvo.
- Exportacao CSV do historico.
- Rota `/weekly-reports`.
- Rota `/weekly-report/save`.
- Protecao por auth nas novas rotas.
- Garantia de que `/weekly-report` dinamico continua funcionando.

## Resultado do pytest

Comando:

```bash
python -m pytest
```

Resultado:

```text
85 passed
```

## Resultado dos smoke tests

Auth desabilitada:

- `/`: 200
- `/profile`: 200
- `/foods`: 200
- `/meals`: 200
- `/measurements`: 200
- `/weekly-report`: 200
- `/weekly-reports`: 200
- `/exports`: 200
- `/exports/weekly-reports-history.csv`: 200

Auth habilitada:

- novas rotas de relatorios salvos redirecionam para `/login` quando nao autenticado.
- apos login valido, `/weekly-reports` retorna 200.

## Limitacoes restantes

- Ainda nao ha migracoes formais de banco.
- Snapshots nao atualizam automaticamente quando dados antigos mudam.
- Ainda nao ha comparacao visual entre varios relatorios salvos.
- Exportacao Excel ainda nao foi implementada.

## Recomendacoes para proxima fase

- Fase 9: adicionar migracoes formais de banco.
- Preparar uma rotina segura para atualizar bancos locais existentes.
- Documentar versao de schema.
- Cobrir migracoes com testes.
