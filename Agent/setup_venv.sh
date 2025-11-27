#!/bin/bash
# Script para crear un nuevo entorno virtual limpio con uv y configurar ML-Agents

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Configurando entorno virtual con uv${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Verificar que uv está instalado
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ uv no encontrado${NC}"
    echo -e "${YELLOW}Instalando uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Error instalando uv${NC}"
        exit 1
    fi
    # Cargar uv en el PATH
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Mostrar versión de uv
UV_VERSION=$(uv --version)
echo -e "${GREEN}✓ uv encontrado: ${UV_VERSION}${NC}"

# Cambiar al directorio del script
cd "$SCRIPT_DIR"

# Eliminar venv existente si existe
if [ -d ".venv" ]; then
    echo -e "${YELLOW}⚠ Eliminando entorno virtual existente...${NC}"
    rm -rf .venv
fi

# Sincronizar dependencias con uv (esto crea el venv y instala todo)
# Usamos Python 3.10 porque mlagents requiere torch 1.11.0 que solo tiene wheels para Python 3.10
echo -e "${GREEN}Sincronizando dependencias con uv (Python 3.10)...${NC}"
uv sync --python 3.10

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Error sincronizando dependencias${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Configuración completada exitosamente${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Para activar el entorno virtual, ejecuta:${NC}"
echo -e "  source .venv/bin/activate"
echo ""
echo -e "${YELLOW}O usa uv run directamente:${NC}"
echo -e "  uv run python envs/train_car_mlagents.py"
echo ""
echo -e "${YELLOW}Para verificar la instalación:${NC}"
echo -e "  uv run python -c 'import mlagents; print(mlagents.__version__)'"
echo ""

