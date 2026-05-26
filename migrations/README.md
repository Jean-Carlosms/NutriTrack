# NutriTrack migrations

Esta pasta contem migracoes SQL simples para SQLite.

Regras do projeto:

- Arquivos devem seguir o padrao `NNN_nome_descritivo.sql`.
- Cada versao deve ser unica.
- Migrações devem ser idempotentes sempre que possivel.
- Nunca escreva migracao destrutiva sem backup previo e revisao manual.
- Seeds de dados ficticios ficam fora das migracoes.

Comandos:

```bash
python scripts/db_status.py
python scripts/db_migrate.py
```
