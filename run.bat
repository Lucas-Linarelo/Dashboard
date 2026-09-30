@echo off
setlocal EnableDelayedExpansion
title Setup e Execucao - Projeto Caprem
color 0A

echo ===================================================
echo   Preparando o ambiente para a Automacao Caprem
echo ===================================================
echo.

echo [1/4] Verificando instalacao do Python...
python --version >nul 2>&1
if %errorlevel% EQU 0 goto PYTHON_INSTALADO

echo Python nao encontrado. Baixando instalador oficial...
curl -# -o python_installer.exe "https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"
start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del python_installer.exe
set "PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python312\Scripts\;%USERPROFILE%\AppData\Local\Programs\Python\Python312\;%PATH%"

python --version >nul 2>&1
if %errorlevel% EQU 0 goto PYTHON_INSTALADO

color 0C
echo.
echo ERRO CRITICO: Python nao reconhecido. Reinicie o computador.
pause
exit /b

:PYTHON_INSTALADO
echo - Python pronto.
echo.

echo [2/4] Instalando dependencias (Pandas)...
python -m pip install pandas --quiet
if %errorlevel% NEQ 0 goto ERRO_PIP
echo - Dependencias prontas.
echo.

echo [3/4] Procurando arquivos na pasta 'Arquivo Original'...
if not exist "Arquivo Original" mkdir "Arquivo Original"
if not exist "Arquivo Final" mkdir "Arquivo Final"
echo.

set count=0
for %%f in ("Arquivo Original\*.csv") do (
    set /a count+=1
    set "file[!count!]=%%f"
    echo [!count!] %%f
)

if %count%==0 (
    color 0E
    echo AVISO: Nenhum arquivo .csv encontrado na pasta 'Arquivo Original'.
    pause
    exit /b
)

echo.
set /p choice="Digite o numero do arquivo que deseja processar: "
set "SELECTED_FILE=!file[%choice%]!"

if "!SELECTED_FILE!"=="" (
    color 0C
    echo ERRO: Escolha invalida.
    pause
    exit /b
)

echo.
echo [4/4] Gerando dashboard interativo...
echo ===================================================
echo.
python main.py "!SELECTED_FILE!"
echo.
echo ===================================================
echo Processamento concluido com sucesso!
pause
exit /b

:ERRO_PIP
color 0C
echo ERRO: Falha ao instalar o Pandas. Verifique sua internet.
pause
exit /b