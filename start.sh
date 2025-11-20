#!/bin/bash

# Script para iniciar FOMTAN Analytics
# Asegura que se use el entorno virtual correcto

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verificar si existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "Error: No se encontró el entorno virtual (.venv)"
    echo "Por favor, crea el entorno virtual primero con: python3 -m venv .venv"
    exit 1
fi

# Activar el entorno virtual y ejecutar
echo "Iniciando FOMTAN Analytics..."
source .venv/bin/activate

# Suprimir mensajes informativos de TensorFlow (opcional)
export TF_CPP_MIN_LOG_LEVEL=2

python run.py
