# NutriTrack - Portfolio Summary

## Nome do projeto

NutriTrack

## Descricao curta em portugues

Aplicacao web local para acompanhamento de dieta, calorias, macronutrientes, medidas corporais, evolucao fisica e aderencia semanal.

## Short description in English

Local web application for tracking diet, calories, macronutrients, body measurements, physical progress and weekly adherence.

## Problema resolvido

NutriTrack organiza registros nutricionais e corporais em um ambiente local, simples e auditavel, evitando planilhas dispersas e mantendo os dados pessoais no computador do usuario.

## Funcionalidades principais

- Perfil local com metas.
- CRUD de alimentos.
- Registro de refeicoes.
- CRUD de medidas corporais.
- Dashboard com graficos.
- Relatorio semanal dinamico.
- Snapshots semanais persistidos.
- Exportacao CSV.
- Backup local do SQLite.
- Autenticacao local opcional.
- Modo offline com assets locais.
- Migracoes SQLite proprias.

## Stack

- Python
- Flask
- SQLite
- HTML/CSS
- Bootstrap local
- Chart.js local
- Pytest

## Diferenciais tecnicos

- Separacao clara entre rotas, banco e services.
- Regras de negocio testadas fora das rotas Flask.
- Sem dependencias pesadas para CSV, backup, migracoes ou heuristicas.
- Assets versionados localmente para uso offline.
- Auth opcional por variavel de ambiente.
- Sistema simples de migracoes com `schema_migrations`.
- Relatorios persistidos como snapshots historicos.

## Arquitetura

- `app/routes.py`: camada web Flask.
- `app/database.py`: conexao SQLite, inicializacao e seed demo.
- `app/services/`: calculos, exportacao, backup, auth, tendencia, relatorios e migracoes.
- `app/templates/`: interface HTML.
- `migrations/`: SQL versionado.
- `scripts/`: comandos auxiliares.
- `tests/`: testes unitarios e de fluxo.

## Testes

Suite com Pytest cobrindo calculos, servicos, rotas principais, autenticacao, exportacoes, relatorios persistidos e migracoes.

Status atual:

```text
94 passed
```

## Seguranca

- `.env` ignorado.
- Banco SQLite e backups ignorados.
- Senha configurada por hash, nao por senha pura.
- Auth local opcional.
- `instance/` fora do versionamento.
- Exportacoes podem conter dados pessoais e devem ser tratadas com cuidado.

## Limitacoes

- MVP local single-user.
- Sem deploy configurado.
- Sem multiplos usuarios.
- Sem exportacao Excel.
- Auth simples, nao corporativa.
- Calculos e recomendacoes sao educacionais.

## Proximos passos

- Deploy opcional.
- Exportacao Excel opcional.
- Comparacao visual entre relatorios salvos.
- Multiplos usuarios opcional.

## Texto sugerido para LinkedIn/GitHub

Desenvolvi o NutriTrack, um MVP web local em Python/Flask para acompanhamento nutricional e evolucao fisica. O projeto usa SQLite, Bootstrap e Chart.js locais para funcionar offline, possui CRUDs completos, dashboard, relatorios semanais, exportacao CSV, backup local, autenticacao opcional, heuristicas de tendencia de peso e um sistema proprio de migracoes SQLite. A arquitetura separa rotas, banco e services, com cobertura automatizada em Pytest.
