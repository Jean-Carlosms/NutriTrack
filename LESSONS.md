# LESSONS

## Fase 1

- Separar regras de negocio em `services` facilita testes unitarios e reduz acoplamento com Flask.
- SQLite atende bem ao MVP local e permite evoluir depois para migracoes formais.
- Graficos no frontend mantem o backend simples quando os dados ja chegam agregados.
- Calculos corporais devem deixar claro que sao estimativas educacionais.

## Fase 2

- Validacoes simples no backend evitam excecoes de formulario e melhoram a experiencia sem adicionar dependencias.
- Testes de borda sao importantes em calculos nutricionais, especialmente para evitar divisao por zero.
- `SECRET_KEY` deve vir de variavel de ambiente, com fallback apenas para desenvolvimento local.
- Um comando `reset-db` ajuda a recriar ambientes locais de forma previsivel.
- Testes Flask com SQLite em memoria deixam o smoke test mais rapido e isolado.
- CDN e pratico para MVP, mas deve virar tarefa explicita quando o objetivo for uso offline completo.

## Fase 3

- Preservar valores de formulario em erros melhora bastante a usabilidade sem exigir biblioteca extra.
- Estados vazios precisam ser tratados no backend e no template; grafico sem dado nao deve parecer bug.
- CRUD com Flask e SQLite fica simples quando cada rota valida entrada antes de executar SQL.
- Bloquear exclusao de alimento usado em refeicoes preserva historico nutricional.
- Testes de fluxos POST ajudam a proteger comportamentos reais da interface, nao apenas funcoes puras.
- Edicoes inline funcionam bem para quantidades de refeicao, desde que a validacao do backend continue sendo a fonte de verdade.

## Fase 4

- A biblioteca padrao `csv` com `io.StringIO` atende bem a exportacoes simples de MVP.
- `Response` do Flask com `text/csv` e `Content-Disposition` e suficiente para downloads previsiveis.
- Exportacoes devem retornar cabecalho mesmo sem dados, para facilitar uso em planilhas.
- Backup local de SQLite pode ser uma copia simples com timestamp, desde que fique fora do versionamento.
- A interface nao deve mostrar caminhos absolutos do sistema; o nome do arquivo basta para o usuario.
- Testes de arquivos podem usar diretorios temporarios dentro do workspace quando o `%TEMP%` do ambiente esta restrito.

## Fase 5

- Assets locais em Flask devem ser referenciados com `url_for('static', filename=...)` para preservar portabilidade.
- Remover CDN melhora o modo offline e reduz dependencia externa em um app local.
- Versionar arquivos minificados de vendor e aceitavel em um MVP local quando o objetivo e rodar sem internet.
- Documentar versao, fonte e data de inclusao ajuda a atualizar bibliotecas depois sem adivinhacao.
- Testes que varrem templates contra `https://`, `cdn.jsdelivr`, `unpkg` e afins protegem contra regressao para CDN.

## Fase 6

- `session` do Flask e suficiente para autenticacao local simples quando existe `SECRET_KEY` configurada.
- Autenticacao opcional por variavel de ambiente preserva a experiencia simples do MVP.
- Hash de senha com Werkzeug evita senha pura no codigo ou na documentacao local.
- Protecao condicional via `before_request` reduz repeticao de decorators em muitas rotas.
- `next` apos login precisa aceitar apenas caminhos internos para evitar open redirect.
- Arquivos estaticos devem continuar fora da protecao para preservar CSS, JS e assets locais na tela de login.

## Fase 7

- Heuristicas transparentes sao mais adequadas que ML pesado quando ainda ha poucos dados.
- Servicos devem retornar estruturas seguras em caso de dados insuficientes, em vez de quebrar templates.
- Media movel simples pode ser calculada sem dependencias externas usando listas e janelas.
- Deteccao de plato precisa ser apresentada como possibilidade educativa, nao conclusao medica.
- Cruzar aderencia, calorias e peso ajuda a gerar recomendacoes mais uteis sem ser prescritivo.

## Fase 8

- Snapshot persistido e diferente de relatorio calculado em tempo real: ele preserva o contexto do momento em que foi salvo.
- `UNIQUE` por `week_start` evita duplicidade simples de relatorios semanais.
- Evoluir schema sem migracoes formais exige `CREATE TABLE IF NOT EXISTS`, `PRAGMA table_info` e `ALTER TABLE` cuidadoso.
- Manter colunas legadas preenchidas ajuda a nao quebrar bancos criados em fases anteriores.
- Historicos salvos precisam de exportacao propria, separada do relatorio semanal dinamico.

## Fase 9

- Um mecanismo simples de migracoes com `schema_migrations` ja traz rastreabilidade suficiente para um MVP local.
- Migrações idempotentes reduzem risco ao aplicar SQL em bancos criados em fases anteriores.
- Separar schema de seed evita que recriacoes e evolucoes do banco misturem estrutura com dados ficticios.
- Scripts de status e migracao tornam a manutencao mais explicita do que inicializar tudo dentro das rotas.
- Mesmo em SQLite local, backup antes de migrar e um cuidado barato que evita perda acidental de dados.

## Fase 10

- Preparar um projeto para GitHub e tambem revisar o que nao deve ir para o GitHub.
- `.gitignore` precisa cobrir ambiente virtual, caches, bancos SQLite, backups, logs e `.env`, sem esconder codigo, testes, migracoes ou assets offline.
- Busca por termos como `secret`, `token`, `senha`, `hash`, `.db` e caminhos locais ajuda a encontrar riscos antes do primeiro commit.
- Release notes e checklist reduzem chance de publicar arquivos sensiveis por pressa.
- Um resumo de portfolio ajuda a explicar decisoes tecnicas, limites do MVP e proximos passos com clareza.

## Fase 11

- Screenshots ajudam o GitHub a comunicar valor antes mesmo de alguem rodar o projeto.
- Um guia de captura evita imagens inconsistentes e reduz risco de expor dados pessoais.
- Referenciar caminhos previstos no README prepara a vitrine sem criar imagens falsas.
- Capturas devem usar dados ficticios e evitar barra do navegador quando ela revelar usuario, caminho local ou informacao sensivel.
- A tela de dashboard e o relatorio semanal sao as melhores vitrines porque mostram dados, graficos e recomendacoes em uma unica narrativa visual.
