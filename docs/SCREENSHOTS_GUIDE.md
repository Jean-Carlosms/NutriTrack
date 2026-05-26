# Guia de screenshots do NutriTrack

Este guia documenta as capturas recomendadas para melhorar a apresentacao visual do projeto no GitHub.

## Preparacao

1. Instale dependencias e rode o app localmente:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

2. Acesse:

```text
http://127.0.0.1:5000
```

3. Use dados ficticios. Nao capture dados reais de saude, nome real, e-mail, banco, caminhos locais sensiveis ou tokens.

4. Antes de capturar, prefira uma janela em torno de 1366x768 ou 1440x900. Para telas muito largas, corte apenas a regiao relevante.

## Checklist de arquivos esperados

Salve as imagens em `docs/images/` com estes nomes:

- `dashboard.png`
- `profile.png`
- `foods.png`
- `meals.png`
- `measurements.png`
- `weekly-report.png`
- `weekly-reports-history.png`
- `exports.png`
- `login.png`

## Telas recomendadas

### Dashboard

Arquivo:

```text
docs/images/dashboard.png
```

Capturar:

- Cards de peso, meta, macros e score semanal.
- Graficos de peso, cintura, calorias ou macros.
- Secao "Analise de Tendencia".

### Perfil

Arquivo:

```text
docs/images/profile.png
```

Capturar:

- Formulario de perfil preenchido com dados ficticios.
- Resultado de meta calorica/macros, se exibido.

### Alimentos

Arquivo:

```text
docs/images/foods.png
```

Capturar:

- Formulario de cadastro ou edicao.
- Tabela com alimentos ficticios.
- Acoes de editar/excluir, se estiverem visiveis.

### Refeicoes

Arquivo:

```text
docs/images/meals.png
```

Capturar:

- Formulario de registro de refeicao.
- Itens registrados com quantidade.
- Edicao inline de quantidade.

### Medidas corporais

Arquivo:

```text
docs/images/measurements.png
```

Capturar:

- Formulario ou tabela de medidas.
- Dados ficticios suficientes para mostrar historico.

### Relatorio semanal

Arquivo:

```text
docs/images/weekly-report.png
```

Capturar:

- Semana selecionada.
- Medias nutricionais.
- Score de aderencia.
- Tendencia, possivel plato e recomendacao educativa.
- Botoes de salvar/atualizar relatorio, se aplicavel.

### Historico de relatorios

Arquivo:

```text
docs/images/weekly-reports-history.png
```

Capturar:

- Lista de snapshots semanais salvos.
- Colunas de semana, peso, media calorica, score e tendencia.
- Acoes de visualizar/excluir, se estiverem visiveis.

### Exportacoes

Arquivo:

```text
docs/images/exports.png
```

Capturar:

- Cards/botoes de exportacao CSV.
- Filtros de data.
- Botao de backup local.

### Login

Arquivo:

```text
docs/images/login.png
```

Capturar somente se `NUTRITRACK_AUTH_ENABLED=true`.

Capturar:

- Tela limpa de login.
- Nao mostrar senha preenchida.
- Nao mostrar hash, token ou variaveis de ambiente.

## Recomendacoes para GitHub

- Use PNG para melhor compatibilidade.
- Comprima as imagens se ficarem grandes demais.
- Prefira dados ficticios consistentes.
- Evite capturar a barra do navegador se ela revelar caminhos, usuarios ou informacoes pessoais.
- Atualize o README somente depois que os arquivos reais forem adicionados.

## Observacao

O README ja referencia os caminhos esperados das imagens. Enquanto os PNGs nao forem adicionados, o GitHub pode mostrar links de imagem quebrados. Isso e esperado ate a captura final ser feita.
