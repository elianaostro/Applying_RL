#!/bin/bash
# Script para entrenar el agente CarAgent con ML-Agents

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Entrenamiento CarAgent con ML-Agents${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 no encontrado${NC}"
    exit 1
fi

# Verificar que mlagents está instalado
if ! python3 -c "import mlagents" 2>/dev/null; then
    echo -e "${YELLOW}⚠ ML-Agents no está instalado${NC}"
    echo "Instalando ML-Agents..."
    pip install mlagents>=0.30.0
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Error instalando ML-Agents${NC}"
        exit 1
    fi
fi

# Cambiar al directorio del script
cd "$SCRIPT_DIR"

# Ejecutar el script de entrenamiento
python3 envs/train_car_mlagents.py "$@"

