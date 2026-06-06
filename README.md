# Compactador de Vídeo

Aplicação web local para compactar vídeos MP4 com foco em envio pelo WhatsApp.

## O que ele faz

- Processa vídeos **100% localmente**
- Compacta com **H.264 + AAC**
- Tenta manter o arquivo em um tamanho amigável para WhatsApp
- Faz limpeza automática de arquivos temporários
- Funciona também como executável `.exe` para Windows

## Requisitos

- Python 3.x
- FFmpeg instalado e disponível no `PATH`
- Flask

## Instalação

```bash
pip install flask
```

## Como rodar

```bash
python app.py
```

Depois abra:

```txt
http://localhost:5000
```

## Gerar o executável

No Windows, execute:

```bat
build.bat
```

O executável será gerado em:

```txt
dist/CompressorVideo.exe
```

## Como usar

1. Envie ou arraste um arquivo `.mp4`
2. Clique em **Compress Video**
3. Aguarde o processamento
4. Baixe o vídeo compactado

## Estrutura do projeto

- `app.py` — backend Flask e compressão com FFmpeg
- `templates/` — interface web
- `build.bat` — empacota o `.exe`
- `uploads/` — arquivos enviados em tempo de execução
- `output/` — vídeos compactados gerados em tempo de execução

## Observações

- O alvo é cerca de **64 MB**, mas isso depende do vídeo original.
- Vídeos muito longos podem continuar maiores do que o desejado.
- Os arquivos temporários são apagados automaticamente após 30 minutos.

## Publicação

Este é o único projeto desta pasta que vale ser publicado em modo público no GitHub.
