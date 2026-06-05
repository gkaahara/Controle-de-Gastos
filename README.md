# Controle de Gastos

App desktop para controle de gastos compartilhados entre moradores.
Interface web local (Flask), dados em JSON, exportável como .exe.

## Requisitos

- Python 3.13+
- Windows (para o .exe)

## Setup

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Executar (desenvolvimento)

```bat
.venv\Scripts\activate
python app.py
```

Acessar http://127.0.0.1:5000

## Executar (produção — duplo clique)

```bat
python app/runner.py
```

Abre o navegador automaticamente em http://127.0.0.1:5000.
Dados salvos em `data/` ao lado do script.

## Build .exe

```bat
.venv\Scripts\activate
pip install -r requirements.txt
pyinstaller projeto-gastos.spec --clean --noconfirm
```

O executável será gerado em `dist/projeto-gastos.exe`.

## Testes

```bat
.venv\Scripts\activate
python -m pytest
```

## Estrutura

```
app/
  __init__.py        # create_app()
  runner.py          # entrypoint para .exe (abre browser)
  json_store.py      # persistência JSON com lock
  routes/            # blueprints Flask
  templates/         # Jinja2 templates
  static/            # CSS, JS
tests/               # pytest tests (115+)
data/                # dados do usuário (gitignored)
dist/                # .exe gerado (gitignored)
```
