# Relatorio Fase 2

## Resumo

Foi realizada uma revisao tecnica do MVP NutriTrack com foco em seguranca basica, validacao de formularios, robustez dos servicos, usabilidade inicial, testes e documentacao para preparacao do projeto para versionamento.

## Arquivos alterados

- `.gitignore`
- `README.md`
- `TODO.md`
- `LESSONS.md`
- `app/__init__.py`
- `app/database.py`
- `app/routes.py`
- `app/services/calorie_service.py`
- `app/services/macro_service.py`
- `app/services/bodyfat_service.py`
- `app/services/adherence_service.py`
- `app/services/progress_service.py`
- `app/templates/base.html`
- `app/templates/dashboard.html`
- `app/templates/profile.html`
- `app/templates/foods.html`
- `app/templates/meals.html`
- `app/templates/measurements.html`
- `app/static/js/charts.js`
- `tests/test_adherence_service.py`
- `tests/test_bodyfat_service.py`
- `tests/test_calorie_service.py`
- `tests/test_macro_service.py`

## Arquivos criados

- `.env.example`
- `tests/test_app.py`
- `tests/test_progress_service.py`
- `RELATORIO_FASE_2.md`

## Problemas encontrados

- `SECRET_KEY` estava fixa no codigo.
- Formularios convertiam valores diretamente, permitindo excecoes com entradas invalidas.
- Servicos aceitavam alguns valores zero ou negativos que poderiam gerar resultados incorretos ou divisao por zero.
- `.gitignore` nao cobria `.coverage` e `htmlcov/`.
- Dashboard e graficos assumiam dados suficientes.
- Nao havia teste de criacao da aplicacao Flask.
- Nao havia comando claro para recriar o banco local.

## Correcoes aplicadas

- `SECRET_KEY` passou a usar variavel de ambiente com fallback apenas para desenvolvimento.
- Criado `.env.example`.
- Adicionados comandos `flask --app app.py init-db` e `flask --app app.py reset-db`.
- Banco passou a ativar `PRAGMA foreign_keys = ON`.
- Adicionado suporte a SQLite em memoria para testes Flask.
- Formularios de perfil, alimentos, refeicoes e medidas receberam validacoes basicas.
- Mensagens amigaveis sao exibidas via `flash`.
- Inputs numericos receberam limites `min`.
- Menu principal agora indica a pagina ativa.
- Tabelas receberam estados vazios.
- Graficos deixam de renderizar quando a serie nao tem dados uteis.
- Servicos passaram a rejeitar pesos, alturas, metas e objetivos invalidos.
- Testes foram expandidos para casos de borda.

## Testes executados

```bash
python -m pytest
```

Resultado:

```text
27 passed
```

## Smoke test

Rotas verificadas:

- `/`
- `/profile`
- `/foods`
- `/meals`
- `/measurements`

Resultado esperado e validado por teste automatizado:

```text
200 OK
```

## Limitacoes restantes

- Bootstrap e Chart.js ainda usam CDN.
- Nao ha autenticacao.
- O MVP suporta apenas um perfil local.
- Nao ha migracoes formais de banco.
- Edicao/exclusao de medidas ainda nao foi implementada.
- Edicao de itens de refeicao ainda nao foi implementada.
- Relatorios semanais ainda nao sao persistidos automaticamente.

## Proximos passos recomendados

- Fase 3: melhorar UX de formularios, estados vazios e fluxos de edicao.
- Fase 4: adicionar exportacao CSV/Excel.
- Fase 5: tornar Bootstrap e Chart.js assets locais para uso offline completo.
- Fase 6: preparar configuracoes de deploy.
- Fase 7: explorar machine learning para tendencia de peso e deteccao de plato.
