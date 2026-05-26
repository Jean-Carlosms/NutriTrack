# Relatorio Fase 6

## Objetivo da fase

Implementar autenticacao local simples e opcional para proteger dados pessoais do usuario, mantendo o uso local simples e sem adicionar dependencias Python novas.

## Arquivos criados

- `app/services/auth_service.py`
- `app/templates/login.html`
- `scripts/generate_password_hash.py`
- `tests/test_auth.py`
- `RELATORIO_FASE_6.md`

## Arquivos alterados

- `.env.example`
- `README.md`
- `TODO.md`
- `LESSONS.md`
- `app/__init__.py`
- `app/routes.py`
- `app/templates/base.html`
- `app/static/css/style.css`
- `tests/test_app.py`

## Autenticacao implementada

- `/login` com formulario simples.
- `/logout` limpando a sessao.
- Protecao condicional de rotas principais quando auth esta habilitada.
- Modo sem autenticacao preservado por padrao.
- Redirecionamento para `next` interno apos login.
- Protecao contra open redirect ignorando destinos externos.
- Arquivos estaticos continuam acessiveis.

## Variaveis de ambiente adicionadas

- `NUTRITRACK_AUTH_ENABLED=false`
- `NUTRITRACK_USERNAME=admin`
- `NUTRITRACK_PASSWORD_HASH=`

## Hash de senha

Script criado:

```bash
python scripts/generate_password_hash.py "minha_senha"
```

Saida:

```text
NUTRITRACK_PASSWORD_HASH=<hash>
```

## Testes adicionados

- Auth desabilitada permite acessar dashboard.
- Auth habilitada redireciona dashboard para login.
- `/login` continua acessivel.
- Login valido autentica.
- Login invalido nao autentica.
- Logout limpa sessao.
- CSVs ficam protegidos quando auth esta ligada.
- Arquivos estaticos nao sao protegidos.
- `next` interno funciona.
- `next` externo e ignorado.

## Resultado do pytest

Comando:

```bash
python -m pytest
```

Resultado:

```text
59 passed
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

Auth habilitada:

- `/`: redireciona para `/login`
- `/login`: 200
- Login valido: permite acessar dashboard
- `/logout`: encerra sessao e redireciona para login

## Limitacoes restantes

- Autenticacao e local, simples e opcional.
- Nao ha recuperacao de senha.
- Nao ha controle multiusuario.
- Nao ha limitacao de tentativas de login.
- Nao ha migracoes formais de banco.

## Recomendacoes para Fase 7

- Implementar heuristicas de tendencia de peso.
- Detectar possivel plato com base em janela de medidas.
- Cruzar tendencia com aderencia semanal e consistencia de registros.
- Manter linguagem educativa e nao medica.
