@echo off
echo Instalando PyInstaller e dependencias...
pip install pyinstaller flask

echo Gerando executavel...
python -m PyInstaller --noconfirm --onefile --windowed --name "CompressorVideo" --add-data "templates;templates" app.py

echo.
echo ==========================================
echo Build concluido!
echo Executavel gerado em: dist/CompressorVideo.exe
echo ==========================================
pause
