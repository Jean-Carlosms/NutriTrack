# Release Notes - NutriTrack v0.1.0-local

## Resumo

NutriTrack e uma aplicacao web local para acompanhamento de dieta, calorias, macronutrientes, medidas corporais, evolucao fisica e aderencia semanal.

Esta release consolida o MVP local com Flask, SQLite, assets offline, autenticacao opcional, exportacoes CSV, backups e migracoes simples de banco.

## Principais funcionalidades

- Cadastro de perfil local.
- CRUD de alimentos.
- Registro de refeicoes e itens de refeicao.
- CRUD de medidas corporais.
- Dashboard com cards, graficos e estados vazios.
- Relatorio semanal dinamico.
- Relatorios semanais persistidos como snapshots.
- Historico de relatorios salvos.
- Exportacoes CSV.
- Backup local do SQLite.
- Modo offline com Bootstrap e Chart.js locais.
- Autenticacao local opcional por variavel de ambiente.
- Analise educativa de tendencia de peso, media movel e possivel plato.
- Sistema proprio de migracoes SQLite.
- Testes automatizados com Pytest.

## Incluido na release

- Codigo Flask em `app/`.
- Regras de negocio em `app/services/`.
- Templates HTML em `app/templates/`.
- Assets locais em `app/static/`.
- Migracoes SQL em `migrations/`.
- Scripts auxiliares em `scripts/`.
- Testes em `tests/`.
- Documentacao de uso, release, checklist e portfolio.

## Limitacoes conhecidas

- Projeto local e single-user.
- Autenticacao simples, voltada a uso pessoal/local.
- Sem deploy configurado.
- Sem exportacao Excel.
- Sem multiplos usuarios.
- Migracoes sao simples e nao possuem rollback automatico.
- Calculos corporais e recomendacoes sao estimativas educacionais.

## Como instalar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Como rodar

```bash
python app.py
```

Acesse:

```text
http://127.0.0.1:5000
```

## Como rodar testes

```bash
python -m pytest
```

## Como aplicar migracoes

Ver status:

```bash
python scripts/db_status.py
```

Aplicar pendentes:

```bash
python scripts/db_migrate.py
```

Antes de aplicar migracoes pendentes em banco existente, o script tenta criar backup local.

## Autenticacao opcional

Por padrao, a autenticacao pode ficar desligada:

```powershell
$env:NUTRITRACK_AUTH_ENABLED="false"
```

Para habilitar:

```powershell
$env:NUTRITRACK_AUTH_ENABLED="true"
$env:NUTRITRACK_USERNAME="admin"
$env:NUTRITRACK_PASSWORD_HASH="<hash-gerado>"
```

Gerar hash:

```bash
python scripts/generate_password_hash.py "minha_senha"
```

Nao salve senha pura em arquivos do projeto.

## Aviso educacional de saude

NutriTrack tem finalidade educacional e de organizacao pessoal. Calculos, estimativas e recomendacoes nao substituem nutricionista, medico ou profissional de saude.

## Aviso sobre dados pessoais locais

O banco SQLite, backups e exportacoes CSV podem conter dados pessoais relacionados a saude. Mantenha `instance/`, `.env`, bancos e backups fora do versionamento e compartilhe arquivos exportados com cuidado.
