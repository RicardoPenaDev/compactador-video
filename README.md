# Compactador de Vídeo

> Aplicação web local para compactar vídeos MP4 com foco em envio pelo WhatsApp.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-black?logo=flask)](https://flask.palletsprojects.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Video%20Compression-0078D4)](https://ffmpeg.org/)
[![Status](https://img.shields.io/badge/Local-100%25%20offline-success)]()

## Visão geral

O **Compactador de Vídeo** foi feito para reduzir vídeos MP4 de forma simples, rápida e totalmente local.
Ele é útil principalmente para preparar arquivos para compartilhamento no WhatsApp, sem depender de serviços externos.

## Destaques

- Processamento **100% local**
- Compactação com **H.264 + AAC**
- Interface simples com **drag and drop**
- Limpeza automática de arquivos temporários
- Versão executável `.exe` para Windows

## Requisitos

Antes de rodar o projeto, você precisa de:

- Python 3.x
- FFmpeg instalado e disponível no `PATH`
- Flask

## Como rodar

Instale a dependência principal:

```bash
pip install flask
```

Inicie a aplicação:

```bash
python app.py
```

Abra no navegador:

```txt
http://localhost:5000
```

## Como usar

1. Envie ou arraste um arquivo `.mp4`
2. Clique em **Compress Video**
3. Aguarde o processamento
4. Baixe o vídeo compactado

## Gerar o executável

No Windows, rode:

```bat
build.bat
```

O executável será gerado em:

```txt
dist/CompressorVideo.exe
```

## Estrutura do projeto

| Arquivo / pasta | Função |
|---|---|
| `app.py` | Backend Flask e lógica de compressão |
| `templates/` | Interface web |
| `build.bat` | Geração do executável |
| `uploads/` | Arquivos enviados em runtime |
| `output/` | Vídeos compactados gerados em runtime |

## Comportamento esperado

- O alvo é um arquivo em torno de **64 MB**, mas isso varia conforme o vídeo original.
- Vídeos muito longos ou complexos podem continuar acima do alvo.
- Arquivos temporários são limpos automaticamente após 30 minutos.
