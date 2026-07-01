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

## Configuration

### Environment Variables

Configuration is validated on startup using Pydantic schema validation. All environment variables are optional with sensible defaults for development.

| Variable | Default | Production Rule | Description |
|----------|---------|-----------------|-------------|
| `ENVIRONMENT` | `development` | Recommended: `production` | Deployment environment |
| `SECRET_KEY` | `dev-secret-key` | **Required**: Must NOT be `dev-secret-key` | Flask session secret key |
| `DEBUG` | `true` | **Required**: Must be `false` | Flask debug mode |

### Validation Rules

- **Production Environment**: 
  - `SECRET_KEY` must be changed from the default `dev-secret-key` to a secure random string
  - `DEBUG` must be set to `false`
  - If validation fails, app startup will raise `ConfigError` with detailed message

- **Development Environment**:
  - `SECRET_KEY` can use the default `dev-secret-key`
  - `DEBUG` can be `true` for automatic reloading and error pages

### Example: Running in Production

```bash
# Set environment variables before running
set ENVIRONMENT=production
set SECRET_KEY=your-secure-random-key-here-min-32-chars
set DEBUG=false

python app.py
```

Or in `.env` file (if using `python-dotenv`):
```
ENVIRONMENT=production
SECRET_KEY=your-secure-random-key-here-min-32-chars
DEBUG=false
```

### Validation on Startup

The `config.py` module validates all configuration on import. If validation fails:

```
RuntimeError: Configuration error: Configuration validation failed: SECRET_KEY cannot be "dev-secret-key" in production
```

This ensures security constraints are enforced before the app starts.

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
