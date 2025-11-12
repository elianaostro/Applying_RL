# Instalación de ML-Agents - Solución de Problemas de Compatibilidad

## Problema

ML-Agents tiene dependencias antiguas que entran en conflicto con versiones modernas de Python, PyTorch y numpy:

- `mlagents==1.1.0` requiere `numpy>=1.23.5,<1.24.0`
- `numpy==1.23.5` requiere `distutils` para compilarse desde el código fuente
- `distutils` fue removido de Python 3.12

## Soluciones

### Opción 1: Usar Python 3.11 (Recomendado)

ML-Agents funciona mejor con Python 3.11:

```bash
# Si usas pyenv o similar
pyenv install 3.11.9
pyenv local 3.11.9

# Luego instalar dependencias
cd Agent
uv sync
```

### Opción 2: Instalar numpy desde wheel precompilado

Si debes usar Python 3.12, puedes intentar instalar numpy desde un wheel precompilado:

```bash
cd Agent
pip install numpy==1.23.5 --only-binary :all:
uv sync
```

### Opción 3: Entorno Virtual Separado para ML-Agents

Crear un entorno separado solo para ML-Agents:

```bash
# Crear entorno con Python 3.11
python3.11 -m venv venv_mlagents
source venv_mlagents/bin/activate

# Instalar solo ML-Agents
pip install mlagents==1.1.0

# Usar este entorno solo para entrenar con ML-Agents
```

### Opción 4: Usar pip directamente (sin uv)

A veces `pip` puede resolver mejor las dependencias:

```bash
cd Agent
pip install -r requirements.txt
```

## Verificación

Después de instalar, verifica que ML-Agents funciona:

```bash
mlagents-learn --help
```

Si ves la ayuda de ML-Agents, la instalación fue exitosa.

## Nota sobre PyTorch

ML-Agents 1.1.0 debería funcionar con PyTorch 2.0+, pero si encuentras problemas, puedes usar una versión específica:

```bash
pip install torch==2.0.0
```

