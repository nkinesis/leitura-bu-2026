"""
Leitura de QR code de boletim de urna (BU)
SPDX-License-Identifier: LGPL-3.0-or-later
Autor: Gabriel C. Ullmann, 2026
"""
import sys
import cv2


def preprocess_variants(image):
    """
    Gera variantes da imagem para aumentar a chance de leitura do QR code pelo OpenCV
    :param image: matriz de pixels (BGR)
    :return: lista com a imagem em tons de cinza, ampliada (se pequena), binarizada (P&B) e invertida
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variants = [gray]

    h, w = gray.shape
    if max(h, w) < 2000:
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        variants.append(gray)

    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )
    variants.append(thresh)
    variants.append(cv2.bitwise_not(gray))
    return variants


def decode_region(image, points, detectors):
    """
    Tenta ler um QR code localizado, mas não decodificado, recortando e ampliando sua região
    :param image: matriz de pixels
    :param points: vértices do QR code localizado
    :param detectors: lista de detectores do OpenCV
    :return: texto lido (ou string vazia, caso falhe)
    """
    x, y, w, h = cv2.boundingRect(points.astype("int32"))
    pad = max(w, h) // 4
    crop = image[max(y - pad, 0):y + h + pad, max(x - pad, 0):x + w + pad]
    crop = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    for detector in detectors:
        try:
            text, _, _ = detector.detectAndDecode(crop)
        except cv2.error:
            continue
        if text:
            return text
    return ""


def decode(image):
    """
    Ler QR codes a partir da imagem
    :param image: matriz de pixels
    :return: lista de textos lidos, sem duplicatas (ou lista vazia, caso falhe)
    """
    detectors = []
    if hasattr(cv2, "QRCodeDetectorAruco"):
        detectors.append(cv2.QRCodeDetectorAruco())
    detectors.append(cv2.QRCodeDetector())

    results = []
    for variant in preprocess_variants(image):
        for detector in detectors:
            try:
                found, texts, points, _ = detector.detectAndDecodeMulti(variant)
            except cv2.error:
                continue
            if not found:
                continue
            for text, pts in zip(texts, points):
                if not text:
                    text = decode_region(variant, pts, detectors)
                if text:
                    results.append(text)
    return list(dict.fromkeys(results))


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