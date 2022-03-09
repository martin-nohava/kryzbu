import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class Rsa:

  PUBLIC_EXPONENT = 65537
  KEY_SIZE = 2048
  KEY_PATH = Path('server/_data/keys/')
  PRIVATE_KEY_PASS = b"pivate-key-will-be-encrypted-with-this-pass"
  KEY_FILE_NAMES = (
    'rsa.pem',
    'rsa.pub'
  )

  @staticmethod
  def init():
    # Check if keypair exists in filesystem
    if not os.path.exists(Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[0]) or not os.path.exists(Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[1]):
      private_key = rsa.generate_private_key(
          Rsa.PUBLIC_EXPONENT,
          Rsa.KEY_SIZE
      )

      encrypted_pem_private_key = private_key.private_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PrivateFormat.PKCS8,
          encryption_algorithm=serialization.BestAvailableEncryption(Rsa.PRIVATE_KEY_PASS)
      )

      pem_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
      )

      private_key_file = open(Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[0], "w")
      private_key_file.write(encrypted_pem_private_key.decode())
      private_key_file.close()

      public_key_file = open(Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[1], "w")
      public_key_file.write(pem_public_key.decode())
      public_key_file.close()

      print('INFO: RSA key-pair generated.')
    else:
      print('INFO: RSA key-pair found.')