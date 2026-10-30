"""
Leitura de QR code de boletim de urna (BU)
SPDX-License-Identifier: LGPL-3.0-or-later
Autor: Gabriel C. Ullmann, 2026
"""
import sys
import cv2


def decode(image):
    """
    Lê QR code a partir de uma imagem.
    :param image: matriz de pixels
    :return: lista de caracteres lidos (ou array vazio, caso falhe)
    """
    detectors = []
    if hasattr(cv2, "QRCodeDetectorAruco"):
        detectors.append(cv2.QRCodeDetectorAruco())
    detectors.append(cv2.QRCodeDetector())

    for detector in detectors:
        try:
            found, texts, _, _ = detector.detectAndDecodeMulti(image)
        except cv2.error:
            continue
        texts = [t for t in texts if t] if found else []
        if texts:
            return list(dict.fromkeys(texts))
    return []

def main():
    if len(sys.argv) != 2:
        print(f"Comando: python {sys.argv[0]} <image_path>")
        sys.exit(1)

    image = cv2.imread(sys.argv[1])
    if image is None:
        print(f"Não foi possível ler a imagem: {sys.argv[1]}")
        sys.exit(1)

    texts = decode(image)
    if not texts:
        print("Não há QR code na imagem!")
        return

    for i, text in enumerate(texts, 1):
        print(f"[QR code {i}] -> {text}")
        print()


if __name__ == "__main__":
    main()