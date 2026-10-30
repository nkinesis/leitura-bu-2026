"""
Leitura de QR code de boletim de urna (BU)
SPDX-License-Identifier: LGPL-3.0-or-later
Autor: Gabriel C. Ullmann, 2026
Baseado em: https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/manual-do-qr-code-no-boletim-de-urna/@@display-file/file/manual-do-qr-code-no-boletim-de-urna.pdf
"""

import binascii
import hashlib
import base64
import re
import asn1tools
from ecpy.curves import Curve
from ecpy.ecdsa import ECDSA
from ecpy.eddsa import EDDSA
from ecpy.keys import ECPublicKey
from asn1crypto import x509 as asn1_x509
from pprint import pprint

# --- DADOS LIDOS DOS QRCODES DO BU urna 2020 ---
# Leia os QR codes do BU e insira os campos na variável correspondente
campo_HASH_do_qrcode_BU = "insira_dados_aqui1"
campo_ASSI_do_qrcode_bu = "insira_dados_aqui2"
campo_CERT_do_qrcode1 = "insira_dados_aqui3"
campo_CERT_do_qrcode2 = "insira_dados_aqui4"

# --- ASN.1 para leitura de SubjectPublicKeyInfo (com bloco DEFINITIONS)
_SUBJECT_PUBLIC_KEY_INFO_ASN1 = """
SubjectPublicKeyInfo DEFINITIONS ::= BEGIN
SubjectPublicKeyInfo ::= SEQUENCE {
 algorithm AlgorithmIdentifier,
 subjectPublicKey BIT STRING
}
AlgorithmIdentifier ::= SEQUENCE {
 algorithm OBJECT IDENTIFIER,
 parameters ANY OPTIONAL
}
END
""" 
_SUBJECT_PUBLIC_KEY_INFO_DECODER = asn1tools.compile_string(_SUBJECT_PUBLIC_KEY_INFO_ASN1, codec="der")
def extrai_chave_publica_der(cert_der):
  try:
    cert = asn1_x509.Certificate.load(cert_der)
    spki_bytes = cert['tbs_certificate']['subject_public_key_info'].dump()
    spki = _SUBJECT_PUBLIC_KEY_INFO_DECODER.decode('SubjectPublicKeyInfo', spki_bytes)
    algo = spki['algorithm']['algorithm']
    pubkey_bytes = spki['subjectPublicKey'][0]
    if algo == "1.2.840.10045.2.1": # ecPublicKey (UE 2013)
      curve = Curve.get_curve('secp521r1')
      pubkey = ECPublicKey(curve.decode_point(pubkey_bytes))
      return pubkey, ECDSA(), algo
    elif algo == "1.3.6.1.4.1.44588.2.1": # Ed521
      curve = Curve.get_curve('Ed521')
      pubkey = ECPublicKey(curve.decode_point(pubkey_bytes))
      return pubkey, EDDSA(hashlib.shake_256, hash_len=132), algo
    else:
      raise RuntimeError(f"Algoritmo de chave pública não suportado: {algo}")
  except Exception as e:
    print(f"Falha ao extrair chave pública: {e}")
    raise
 
def verificar_assinatura(cert_der, assinatura, dados_hash_qr):
  try:
    pubkey, verifier, _ = extrai_chave_publica_der(cert_der)
    mensagem = hashlib.sha512(dados_hash_qr).digest()
    print("mensagem: " + str(mensagem))
    print("assinatura: " + str(assinatura))
    print("pubkey: " + str(pubkey))
    if verifier.verify(mensagem, assinatura, pubkey):
      print("Assinatura VÁLIDA!")
      return True
    else:
      print("Assinatura INVÁLIDA! (ecpy.verify retornou False)")
      return False
  except Exception as e:
    print(f"Assinatura INVÁLIDA: {e}")
    return False

def extrai_certificado_der(cert_bytes):
  asn1_x509.Certificate.load(cert_bytes)
  return cert_bytes

def extrai_certificado_pem(cert_bytes):
  cert_ascii = cert_bytes.decode("ascii")
  pem_body = "".join(re.findall(r"-----BEGIN CERTIFICATE-----(.*)-----END CERTIFICATE-----", cert_ascii, re.DOTALL)).replace("\n", "")
  cert_der = base64.b64decode(pem_body)
  asn1_x509.Certificate.load(cert_der)
  return cert_der 

def extrai_certificado(campo_cert1, campo_cert2):
  cert_bytes = binascii.unhexlify(campo_cert1.strip() + campo_cert2.strip())
  try:
    return extrai_certificado_der(cert_bytes)
  except Exception:
    return extrai_certificado_pem(cert_bytes)

if __name__ == "__main__":
  cert_bytes = extrai_certificado(campo_CERT_do_qrcode1, campo_CERT_do_qrcode2)
  pprint(asn1_x509.Certificate.load(cert_bytes).native)
  assinatura_bytes = binascii.unhexlify(campo_ASSI_do_qrcode_bu)
  hash_bytes = binascii.unhexlify(campo_HASH_do_qrcode_BU)
  verificar_assinatura(cert_bytes, assinatura_bytes, hash_bytes)