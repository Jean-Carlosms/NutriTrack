# TODO

## Fase 1: MVP inicial concluido

- Estrutura Flask criada.
- SQLite local inicializado.
- Servicos de calculo separados.
- Templates principais criados.
- Dashboard, alimentos, refeicoes, medidas e relatorio semanal implementados.
- Testes iniciais criados.

## Fase 2: hardening tecnico concluido

- `SECRET_KEY` via variavel de ambiente.
- `.env.example` criado.
- `.gitignore` ajustado.
- Validacoes basicas no backend.
- Comandos `init-db` e `reset-db`.
- Testes de borda nos servicos.
- Relatorio da fase criado.

## Fase 3: melhorias de UX concluida

- Estados vazios do dashboard refinados.
- CRUD de medidas corporais implementado.
- Edicao e exclusao de itens de refeicao implementadas.
- CRUD de alimentos revisado com bloqueio de exclusao quando houver uso em refeicoes.
- Relatorio semanal aceita selecao de semana.
- Testes de fluxos POST e CRUD adicionados.

## Fase 4: exportacao CSV e backup concluida

- Exportacao CSV de alimentos.
- Exportacao CSV de refeicoes por periodo.
- Exportacao CSV de itens de refeicao por periodo.
- Exportacao CSV de medidas por periodo.
- Exportacao CSV de resumo semanal.
- Backup local do banco SQLite em `instance/backups`.
- Testes de exportacao e backup adicionados.

## Fase 5: versao offline completa com assets locais concluida

- Bootstrap 5.3.3 adicionado em `app/static/vendor`.
- Chart.js 4.4.3 adicionado em `app/static/vendor`.
- Dependencia de CDN removida dos templates.
- `VENDOR_ASSETS.md` criado com versoes e fontes.
- Testes adicionados para bloquear referencias externas nos templates.

## Fase 6: autenticacao local simples concluida

- Autenticacao opcional via `NUTRITRACK_AUTH_ENABLED`.
- Login e logout implementados.
- Senha configurada por hash, sem senha pura no codigo.
- Script `scripts/generate_password_hash.py` criado.
- Rotas principais e exportacoes protegidas quando auth esta ligada.
- Testes de login, logout, rotas protegidas e `next` seguro adicionados.

## Fase 7: heuristicas de tendencia de peso e plato concluida

- `trend_service.py` criado.
- Media movel simples implementada.
- Tendencia de peso implementada.
- Deteccao simples de possivel plato implementada.
- Dashboard e relatorio semanal atualizados.
- Testes de heuristicas e telas adicionados.

## Fase 8: persistencia de relatorios semanais concluida

- Tabela `weekly_reports` evoluida com campos de snapshot.
- Salvamento de relatorio semanal implementado.
- Sobrescrita de relatorio existente por semana implementada.
- Historico em `/weekly-reports` criado.
- Visualizacao de snapshot salvo criada.
- Exclusao de snapshot salvo implementada.
- Exportacao CSV do historico implementada.

## Fase 9: migracoes formais de banco concluida

- Pasta `migrations/` criada com SQL versionado.
- Tabela `schema_migrations` criada para controle.
- `migration_service.py` criado.
- `init_db` passou a aplicar migracoes pendentes.
- Seed de dados ficticios separado de schema.
- Scripts `db_status.py` e `db_migrate.py` criados.
- Testes de migracao e scripts adicionados.

## Fase 10: preparacao para GitHub concluida

- `.gitignore` revisado para proteger ambientes, caches, bancos, backups e arquivos sensiveis.
- Busca por possiveis secrets, senhas, bancos e dados pessoais em arquivos versionaveis executada.
- `RELEASE_NOTES.md` criado.
- `GITHUB_PUBLISH_CHECKLIST.md` criado.
- `PORTFOLIO_SUMMARY.md` criado.
- README atualizado para apresentacao no GitHub.
- Comandos Git sugeridos documentados, sem execucao automatica.

## Fase 11: documentacao visual para GitHub concluida

- Pasta `docs/images/` criada para screenshots.
- Guia `docs/SCREENSHOTS_GUIDE.md` criado.
- README atualizado com secao "Screenshots".
- `PORTFOLIO_SUMMARY.md` atualizado com secao de apresentacao visual.
- `RELATORIO_FASE_11.md` criado.

## Fase 12: deploy opcional

- Configurar variaveis de ambiente.
- Adicionar suporte a banco externo.
- Avaliar PostgreSQL.
- Criar pipeline de testes.
- Configurar logs adequados.

## Fase 13: comparacao visual entre relatorios salvos

- Comparar snapshots semanais lado a lado.
- Criar graficos de evolucao entre relatorios persistidos.
- Exportar comparativo em CSV.

## Fase 14: exportacao Excel opcional

- Avaliar necessidade real de `.xlsx`.
- Evitar Pandas/openpyxl enquanto CSV atender bem.

## Fase 15: multiplos usuarios opcional

- Avaliar se o MVP ainda deve permanecer single-user.
- Projetar isolamento de dados por usuario.
- Reavaliar autenticacao e modelo de sessao.
