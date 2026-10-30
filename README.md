# Como checar um boletim de urna (BU) das Eleições 2026
Por Gabriel C. Ullmann, 2026

## Descrição
Este repositório contém scripts Python que podem ser utilisados para ler boletins de urna (BUs) e validar sua assinatura digital.

## Requisitos
- Python 3.12 ou superior
- Instalação das dependências Python (`pip install -r requirements.txt`)

## Resumo dos arquivos
| **Arquivo**                 | **Conteúdo**                                                                                                      |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------|
| /imagens                    | Fotos dos boletins de urna das seções 260 e 525 (Montreal - ZZ, Canadá), relativos ao 2º turno das eleições 2026  |
| leitura-bu-com-preproc.py   | Ler QR codes de um boletim de urna (com pré-processamento das fotos para melhorar a precisão da leitura)          |
| leitura-bu-simples.py       | Ler QR codes de um boletim de urna                                                                                |
| validacao-assinatura-bu.py  | Validar assinatura dos QR codes de um boletim de urna                                                             |

## Link para tutorial em vídeo 
TBD

## Licença
LGPL-3 (consulte `LICENSE.md` para mais informações)

## Fontes
Consulte links no arquivo `leitura-bu.pdf`.