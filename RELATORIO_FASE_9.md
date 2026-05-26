# RELATORIO FASE 9 - Migracoes SQLite

## Objetivo da fase

Implementar um sistema simples, auditavel e reprodutivel de migracoes formais para SQLite, sem adicionar dependencias externas e sem apagar dados existentes.

## Arquivos criados

- `migrations/001_initial_schema.sql`
- `migrations/002_weekly_reports.sql`
- `migrations/003_indexes.sql`
- `migrations/README.md`
- `app/services/migration_service.py`
- `scripts/db_status.py`
- `scripts/db_migrate.py`
- `tests/test_migration_service.py`
- `RELATORIO_FASE_9.md`

## Arquivos alterados

- `app/__init__.py`
- `app/database.py`
- `.env.example`
- `README.md`
- `TODO.md`
- `LESSONS.md`

## Migrations criadas

- `001_initial_schema`: cria tabelas base de perfil, alimentos, refeicoes, itens de refeicao e medidas.
- `002_weekly_reports`: cria tabela de snapshots semanais persistidos.
- `003_indexes`: cria indice unico por `week_start` em `weekly_reports` e indices auxiliares para consultas por data e relacionamentos.

## Mudancas em database.py

- `init_db()` agora chama o fluxo de migracoes por meio de `create_schema()`.
- `create_schema()` aplica migracoes pendentes via `migration_service`.
- `seed_demo_data()` ficou separado da criacao/evolucao do schema.
- `seed_example_data()` foi mantida como alias de compatibilidade.
- `reset_db()` remove tambem `schema_migrations` para recriar o banco local de forma limpa.
- `ensure_weekly_reports_schema()` foi preservada como compatibilidade para bancos criados em fases anteriores.
- `get_db()` passou a criar a pasta do caminho configurado em `NUTRITRACK_DATABASE`, quando usado.

## Scripts criados

- `python scripts/db_status.py`: mostra total de migracoes, aplicadas, pendentes e status geral.
- `python scripts/db_migrate.py`: aplica migracoes pendentes e cria backup do SQLite local antes de migrar quando o banco existe.

## Testes adicionados

- Criacao da tabela `schema_migrations`.
- Listagem ordenada de migracoes.
- Deteccao de migracoes pendentes.
- Registro de migracao aplicada.
- Garantia de que migracao aplicada nao roda novamente.
- Tratamento de falha de migracao.
- Banco novo recebendo todas as migracoes via `init_db`.
- Preservacao de dados existentes ao rodar `init_db`.
- Execucao basica dos scripts usando banco em memoria.

## Resultado do pytest

Comando executado:

```bash
python -m pytest
```

Resultado:

```text
94 passed
```

## Resultado dos scripts

Comandos executados:

```bash
python scripts/db_status.py
python scripts/db_migrate.py
python scripts/db_status.py
```

Resultado:

- Status inicial: 3 migracoes pendentes.
- `db_migrate`: criou backup `nutritrack_20260526_130345.db`.
- Migracoes aplicadas: `001`, `002`, `003`.
- Status final: 3 aplicadas, 0 pendentes, banco atualizado.

## Smoke tests

Auth desabilitada, com redirects seguidos:

- `/`: 200
- `/profile`: 200
- `/foods`: 200
- `/meals`: 200
- `/measurements`: 200
- `/weekly-report`: 200
- `/weekly-reports`: 200
- `/exports`: 200

Auth habilitada:

- `/weekly-reports` sem login: 302 para `/login?next=/weekly-reports`
- `/login`: 200
- POST `/login` valido: 302
- `/weekly-reports` apos login: 200

## Limitacoes restantes

- As migracoes sao SQL simples e nao possuem rollback automatico por versao.
- O mecanismo atende bem ao MVP local, mas projetos maiores podem exigir ferramenta dedicada.
- A compatibilidade com bancos muito antigos ainda depende de migracoes idempotentes e de verificacoes pontuais no `database.py`.
- Seeds continuam voltadas apenas para desenvolvimento/demo.

## Recomendacoes para proxima fase

- Preparar configuracao de deploy opcional.
- Avaliar exportacao Excel apenas se CSV deixar de atender.
- Planejar suporte a multiplos usuarios somente se o MVP realmente precisar.
- Criar comparacao visual entre relatorios semanais salvos.
