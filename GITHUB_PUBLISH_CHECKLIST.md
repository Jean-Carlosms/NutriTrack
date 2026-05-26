# GitHub Publish Checklist

## Antes de publicar

- [ ] Rodar `python -m pytest`.
- [ ] Rodar `python scripts/db_status.py`.
- [ ] Rodar `python scripts/db_migrate.py`, se houver migracoes pendentes.
- [ ] Rodar novamente `python scripts/db_status.py`.
- [ ] Conferir `.gitignore`.
- [ ] Confirmar que `instance/` nao sera versionado.
- [ ] Confirmar que `.env` nao sera versionado.
- [ ] Confirmar que `.env.example` existe e nao contem segredo real.
- [ ] Confirmar que `*.db`, `*.sqlite`, `*.sqlite3` e backups nao serao versionados.
- [ ] Confirmar que `app/static/vendor/` sera versionado para modo offline.
- [ ] Confirmar que `migrations/` sera versionado.
- [ ] Confirmar que `tests/` sera versionado.
- [ ] Confirmar que o README esta atualizado.
- [ ] Conferir arquivos de relatorio e release.

## Comandos Git sugeridos

Nao execute estes comandos automaticamente sem revisao final.

```bash
git init
git branch -M main
git status
git add .gitignore .env.example README.md TODO.md LESSONS.md RELEASE_NOTES.md GITHUB_PUBLISH_CHECKLIST.md PORTFOLIO_SUMMARY.md RELATORIO_FASE_*.md app migrations scripts tests requirements.txt
git status
git commit -m "feat: release NutriTrack local MVP"
git remote add origin <URL_DO_REPOSITORIO>
git push -u origin main
```

## Conferencia manual depois do `git add`

- [ ] `git status` nao mostra `instance/`.
- [ ] `git status` nao mostra `.env`.
- [ ] `git status` nao mostra arquivos `.db`.
- [ ] `git status` nao mostra backups.
- [ ] `git status` mostra `app/static/vendor/`.
- [ ] `git status` mostra `migrations/`.
- [ ] `git status` mostra `tests/`.
