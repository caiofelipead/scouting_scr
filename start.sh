# Railway Start Script (alternativa ao start.py)
#!/bin/bash

# Configurar Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Executar uvicorn do diretório raiz
exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
