# DirectGen Local

Aplicacion web local para generar imagenes con modelos de Hugging Face usando DirectML en Windows. El frontend es React/Vite y el backend es FastAPI.

## Estado del MVP

- Imagen: soporte principal via Diffusers + `torch-directml` sobre DirectX 12.
- Hugging Face: busqueda por tarea, descarga con `snapshot_download` y registro local.
- DirectML: deteccion de `torch-directml`, proveedores ONNX Runtime y mensajes de diagnostico.
- ONNX: mantenido como ruta experimental para modelos compatibles con `DmlExecutionProvider`.
- Video: incluido en UI/API como modo experimental; el backend devuelve error claro hasta implementar un adaptador estable.

## Requisitos

- Windows 10/11 con GPU DirectX 12 y drivers recientes.
- Python 3.11 recomendado.
- Node.js 22+.
- Espacio en disco suficiente para modelos grandes. El preset recomendado ocupa ~4-5 GB.

## Arranque

```powershell
.\scripts\setup-api.ps1
.\scripts\setup-directml.ps1
.\scripts\start-api.ps1
```

En otra terminal:

```powershell
.\scripts\start-web.ps1
```

Abre `http://127.0.0.1:5173`.

Tambien puedes iniciar todo con:

```powershell
.\scripts\start-all.ps1
```

## Instalador Windows

El release incluye `DirectGenLocalInstaller.exe`. Este instalador:

- Descarga el codigo del release desde GitHub.
- Instala la app en `%LOCALAPPDATA%\DirectGenLocal`.
- Ejecuta el setup base de Python y `npm install`.
- Crea `DirectGenLocal.cmd` y un acceso directo en el escritorio.

El instalador no descarga dependencias DirectML pesadas ni modelos por defecto. Despues de instalar, ejecuta:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\DirectGenLocal\scripts\setup-directml.ps1"
```

## Verificar DirectML

```powershell
.\scripts\check-runtime.ps1
```

El campo clave es `directml_ready`. Debe ser `true`. Para la ruta recomendada tambien debe aparecer `torch_directml_available: true`.

Si solo quieres abrir la UI y revisar el flujo sin instalar dependencias ML pesadas, puedes omitir `setup-directml.ps1`. La app arrancara, pero `/api/runtime` reportara que DirectML no esta listo.

## Modelo recomendado para primera prueba

Usa el preset principal Torch-DirectML:

```text
CompVis/stable-diffusion-v1-4
```

El preset anterior SDXL Olive (`softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx`) queda marcado como experimental porque reproduce un fallo conocido de ONNX Runtime con `com.microsoft.GroupNorm(1)` en DirectML.

## Arquitectura

- `apps/web`: cabina React para prompt, parametros, modelos y jobs.
- `apps/api`: FastAPI local con registro de modelos, Hugging Face, runtime DirectML y cola de jobs en memoria.
- `data/models`: snapshots locales de Hugging Face.
- `data/outputs`: imagenes generadas servidas por la API en `/outputs`.

## Verificacion de desarrollo

```powershell
python -m pytest apps/api/tests
cd apps\web
npm run build
```
