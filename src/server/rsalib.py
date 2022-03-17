import os
from pathlib import Path
from Crypto.PublicKey import RSA


class Rsa:

    KEY_SIZE = 2048
    KEY_PATH = Path("server/_data/keys/")
    PRIVATE_KEY_PASS = b"pivate-key-will-be-encrypted-with-this-pass"
    KEY_FILE_NAMES = ("rsa.pem", "rsa.pub")

    @staticmethod
    def init():
        # Check if keypair exists in filesystem
        if not os.path.exists(
            Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[0]
        ) or not os.path.exists(Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[1]):
            key = RSA.generate(Rsa.KEY_SIZE)
            private_key = key.export_key(
                passphrase=Rsa.PRIVATE_KEY_PASS,
                pkcs=8,
                protection="scryptAndAES128-CBC",
            )
            file_out = open(Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[0], "wb")
            file_out.write(private_key)
            file_out.close()

            public_key = key.publickey().export_key()
            file_out = open(Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[1], "wb")
            file_out.write(public_key)
            file_out.close()

            print("INFO: RSA key-pair generated.")
        else:
            print("INFO: RSA key-pair found.")

    @staticmethod
    def get_pub_key_location():
        return Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[1]
