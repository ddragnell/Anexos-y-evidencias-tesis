@echo off
REM Demostracion del proxy preventivo: abre http://localhost:8000/
REM Requiere la carpeta modelos\ner-bert-final (descargada de Google Drive).
cd /d "%~dp0"
if not exist "modelos\ner-bert-final\config.json" (
  echo No encuentro modelos\ner-bert-final\config.json
  echo Descarga la carpeta ner-bert-final de MyDrive\modelos-ner y descomprimela dentro de modelos\
  pause
  exit /b 1
)
if not exist ".venv-demo\Scripts\python.exe" (
  echo Creando el entorno de la demostracion, solo la primera vez...
  py -3 -m venv .venv-demo || python -m venv .venv-demo
  ".venv-demo\Scripts\python.exe" -m pip install -q --upgrade pip
  ".venv-demo\Scripts\python.exe" -m pip install -q torch --index-url https://download.pytorch.org/whl/cpu
  ".venv-demo\Scripts\python.exe" -m pip install -q transformers fastapi uvicorn openai
)
if not defined OPENAI_API_KEY set /p OPENAI_API_KEY=Clave de OpenAI para enviar a la IA (opcional, Enter para omitir): 
set NER_BACKEND=hf
set NER_MODELO=%~dp0modelos\ner-bert-final
echo Cargando el modelo, espera unos segundos y se abrira el navegador...
start "" cmd /c "timeout /t 25 >nul & start http://localhost:8000/"
".venv-demo\Scripts\python.exe" -m uvicorn proxy.servidor:app --port 8000
pause
