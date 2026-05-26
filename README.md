# NutriTrack

[Status: MVP local] [Release: v0.1.0-local] [Tests: 94 passed] [Offline: Bootstrap + Chart.js locais]

NutriTrack e uma aplicacao web local para acompanhamento de dieta, calorias, macronutrientes, medidas corporais e evolucao fisica.

O projeto foi criado como um MVP simples e evolutivo, com regras de negocio em `app/services`, rotas Flask enxutas, banco SQLite local e testes automatizados para calculos e fluxos principais.

## Visao geral

O NutriTrack foi preparado para uso local e versionamento no GitHub. O banco SQLite, backups, `.env`, caches e dados pessoais ficam fora do versionamento; codigo, testes, migracoes e assets offline devem ser versionados.

## Objetivo

Oferecer uma base local para registrar perfil, alimentos, refeicoes e medidas corporais, acompanhando metas caloricas, macros, progresso fisico e aderencia semanal.

## Stack

- Python
- Flask
- SQLite
- HTML/CSS
- Bootstrap 5.3.3 local
- Chart.js 4.4.3 local
- Pytest

Pandas pode ser adicionado futuramente para importacao, exportacao e analises, mas nao e necessario para o MVP atual.

## Arquitetura

- `app/routes.py`: rotas Flask e composicao das telas.
- `app/database.py`: conexao SQLite, inicializacao, migracoes e seed demo.
- `app/services/`: regras de negocio, calculos, relatorios, exportacao, backup, auth, tendencia e migracoes.
- `app/templates/`: templates HTML.
- `app/static/`: CSS, JS e bibliotecas locais de vendor.
- `migrations/`: SQL versionado do schema.
- `scripts/`: utilitarios operacionais.
- `tests/`: testes unitarios e de fluxo.

## Funcionalidades atuais

- Cadastro de perfil unico local.
- Calculo de TMB pela formula Mifflin-St Jeor.
- Calculo de gasto energetico diario total.
- Meta calorica por objetivo.
- Sugestao de macronutrientes.
- CRUD de alimentos.
- Registro de refeicoes por data e tipo.
- Edicao de quantidade e exclusao de itens de refeicao.
- Calculo proporcional de calorias e macros por quantidade consumida.
- CRUD de medidas corporais.
- Estimativas educacionais de IMC, relacao cintura/altura e percentual de gordura pelo metodo da Marinha dos EUA.
- Dashboard com cards, score semanal, variacao de peso e graficos.
- Analise de tendencia de peso, media movel e possivel plato com heuristicas simples.
- Estados vazios amigaveis no dashboard, tabelas e graficos.
- Relatorio semanal por semana selecionada.
- Relatorios semanais persistidos como snapshots historicos.
- Exportacoes CSV de alimentos, refeicoes, itens de refeicao, medidas e relatorio semanal.
- Backup local simples do banco SQLite.
- Autenticacao local simples e opcional por variavel de ambiente.
- Migracoes formais simples para SQLite, sem dependencias externas.
- Validacoes basicas de formularios.
- Comandos CLI para inicializar ou recriar o banco.

## Limitacoes do MVP

- Autenticacao local e simples, opcional e voltada a uso individual.
- Um unico perfil local.
- Migracoes atuais sao SQL simples e nao substituem uma ferramenta robusta para cenarios maiores.
- Relatorios semanais salvos sao snapshots e nao atualizam automaticamente quando dados antigos mudam.
- Exportacao Excel ainda nao foi implementada.
- Calculos corporais sao estimativas educacionais.
- Analise de tendencia e plato usa heuristicas simples, nao diagnostico.
- Nao ha deploy configurado nesta release.

## Como instalar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuracao

Defina uma chave secreta propria no ambiente antes de rodar em uma sessao local:

```powershell
$env:SECRET_KEY="uma-chave-local-segura"
```

O arquivo `.env.example` mostra as variaveis esperadas para documentacao. O projeto nao adiciona `python-dotenv` nesta fase para evitar dependencia extra; se um `.env` real for usado futuramente, ele nao deve ser versionado.

Opcionalmente, scripts e testes podem apontar para outro banco:

```powershell
$env:NUTRITRACK_DATABASE="C:\caminho\para\nutritrack.db"
```

## Autenticacao local opcional

Por padrao, a autenticacao pode ficar desabilitada para manter o uso local simples:

```powershell
$env:NUTRITRACK_AUTH_ENABLED="false"
```

Para habilitar:

```powershell
$env:NUTRITRACK_AUTH_ENABLED="true"
$env:NUTRITRACK_USERNAME="admin"
$env:NUTRITRACK_PASSWORD_HASH="hash-gerado"
```

Gere o hash da senha com:

```bash
python scripts/generate_password_hash.py "minha_senha"
```

A saida tera o formato:

```text
NUTRITRACK_PASSWORD_HASH=<hash>
```

Variaveis:

- `NUTRITRACK_AUTH_ENABLED`: `true` ou `false`.
- `NUTRITRACK_USERNAME`: usuario local.
- `NUTRITRACK_PASSWORD_HASH`: hash da senha, nunca a senha pura.

Esta autenticacao e simples e pensada para uso local em computador pessoal. Nao e uma solucao corporativa robusta.

## Como rodar

```bash
python app.py
```

Acesse:

```text
http://127.0.0.1:5000
```

O banco SQLite e criado automaticamente em `instance/nutritrack.db` na primeira execucao.

## Banco de dados

Inicializar banco:

```bash
flask --app app.py init-db
```

Recriar banco local com dados ficticios:

```bash
flask --app app.py reset-db
```

A pasta `instance/` e ignorada pelo Git para evitar versionamento do banco local.

## Migracoes de banco

A partir da Fase 9, o schema e controlado por arquivos SQL em `migrations/` e pela tabela `schema_migrations`.

Ver status:

```bash
python scripts/db_status.py
```

Aplicar migracoes pendentes:

```bash
python scripts/db_migrate.py
```

Antes de aplicar migracoes pendentes no banco local existente, o script tenta criar um backup em `instance/backups/`.

Migracao e seed sao coisas diferentes:

- Migracoes criam ou evoluem tabelas, indices e constraints.
- Seed adiciona dados ficticios de desenvolvimento/demo quando as tabelas estao vazias.

Antes de migrar um banco real com dados importantes, crie backup e revise as migracoes pendentes. As migracoes deste MVP sao simples, idempotentes quando possivel, e pensadas para SQLite local.

## Exportacoes CSV

Acesse:

```text
http://127.0.0.1:5000/exports
```

Exportacoes disponiveis:

- `foods.csv`: alimentos cadastrados.
- `meals.csv`: refeicoes por periodo.
- `meal-items.csv`: itens de refeicao por periodo com macros proporcionais.
- `measurements.csv`: medidas corporais por periodo.
- `weekly-report.csv`: resumo semanal.
- `weekly-reports-history.csv`: historico de relatorios semanais salvos.

As rotas aceitam filtros simples por query string quando aplicavel:

```text
/exports/meals.csv?start_date=2026-05-01&end_date=2026-05-31
/exports/weekly-report.csv?week_start=2026-05-25
```

Os arquivos CSV podem conter dados pessoais relacionados a saude. Guarde e compartilhe esses arquivos com cuidado.

## Relatorios semanais persistidos

O relatorio em `/weekly-report` continua sendo calculado dinamicamente a partir dos registros atuais.

Agora tambem e possivel salvar um snapshot semanal:

- Abra `/weekly-report`.
- Escolha a semana desejada.
- Clique em "Salvar relatorio da semana".
- Se ja existir snapshot para a semana, use "Atualizar relatorio salvo" para sobrescrever.

Historico:

```text
/weekly-reports
```

O historico mostra semana, data de criacao, peso inicial/final, variacao, media calorica, score e tendencia. Snapshots salvos nao mudam automaticamente se voce editar refeicoes ou medidas depois.

Exportacao CSV do historico:

```text
/exports/weekly-reports-history.csv
```

Relatorios salvos podem conter dados pessoais relacionados a saude. Trate esses arquivos com cuidado.

## Backup local

Na pagina `/exports`, use o botao "Criar backup local" para copiar o SQLite atual para:

```text
instance/backups/
```

O nome do arquivo segue o padrao:

```text
nutritrack_YYYYMMDD_HHMMSS.db
```

O app mostra apenas o nome do arquivo criado, nao o caminho absoluto do sistema. A pasta `instance/` continua ignorada pelo Git, incluindo backups.

## Analise de tendencia e plato

O dashboard e o relatorio semanal exibem uma analise educativa baseada nas medidas e registros existentes.

Indicadores:

- Tendencia atual do peso: reduzindo, aumentando, estavel ou dados insuficientes.
- Variacao aproximada no periodo.
- Media movel simples do peso, usando ate 7 registros.
- Possivel plato quando ha pelo menos 14 dias de medidas e variacao de peso menor ou igual a 0.3 kg.
- Recomendacao educativa cruzando tendencia, aderencia e calorias medias.

Dados necessarios:

- Pelo menos 2 medidas para tendencia basica.
- Pelo menos 14 dias de medidas para avaliar possivel plato.
- Registros de refeicoes e perfil cadastrado para comparar calorias medias com a meta.

Limitacoes:

- As regras sao heuristicas transparentes e simples.
- Nao ha machine learning pesado.
- Nao substitui nutricionista, medico ou profissional de saude.

## Modo offline/local

Bootstrap e Chart.js foram movidos para `app/static/vendor`, removendo a dependencia de CDN nas telas do MVP.

Assets locais:

- Bootstrap 5.3.3
  - `app/static/vendor/bootstrap/css/bootstrap.min.css`
  - `app/static/vendor/bootstrap/js/bootstrap.bundle.min.js`
- Chart.js 4.4.3
  - `app/static/vendor/chartjs/chart.umd.min.js`

As versoes e fontes estao documentadas em `app/static/vendor/VENDOR_ASSETS.md`.

Para rodar sem internet:

```bash
python app.py
```

Depois acesse `http://127.0.0.1:5000`. Layout, componentes Bootstrap e graficos do dashboard passam a carregar de arquivos locais.

## Como executar os testes

```bash
python -m pytest
```

Resultado atual validado:

```text
94 passed
```

## Estrutura de pastas

```text
.
|-- app.py
|-- requirements.txt
|-- README.md
|-- TODO.md
|-- LESSONS.md
|-- RELATORIO_FASE_2.md
|-- RELATORIO_FASE_3.md
|-- RELATORIO_FASE_4.md
|-- RELATORIO_FASE_5.md
|-- RELATORIO_FASE_6.md
|-- RELATORIO_FASE_7.md
|-- RELATORIO_FASE_8.md
|-- RELATORIO_FASE_9.md
|-- RELATORIO_FASE_10.md
|-- RELEASE_NOTES.md
|-- GITHUB_PUBLISH_CHECKLIST.md
|-- PORTFOLIO_SUMMARY.md
|-- migrations/
|-- scripts/
|-- app/
|   |-- __init__.py
|   |-- database.py
|   |-- models.py
|   |-- routes.py
|   |-- services/
|   |-- templates/
|   `-- static/
`-- tests/
```

## Preparacao para GitHub

Antes de publicar, revise:

- `.gitignore`
- `GITHUB_PUBLISH_CHECKLIST.md`
- `RELEASE_NOTES.md`
- `PORTFOLIO_SUMMARY.md`

Nao versione:

- `.env`
- `instance/`
- bancos SQLite reais
- backups
- caches
- dados pessoais de saude

Versione:

- `app/`
- `migrations/`
- `scripts/`
- `tests/`
- `app/static/vendor/`
- documentacao e relatorios de fase

## Aviso educacional

Este projeto tem finalidade educacional e de organizacao pessoal. As estimativas e calculos nao substituem nutricionista, medico ou qualquer profissional de saude.

## Proximos passos

- Fase 11: deploy opcional.
- Fase 12: exportacao Excel opcional.
- Fase 13: comparacao visual entre relatorios salvos.
- Fase 14: multiplos usuarios opcional.
