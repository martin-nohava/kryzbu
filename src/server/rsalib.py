import os
from pathlib import Path
from Crypto.PublicKey import RSA


class Rsa:
    """
    | Class containing logic for RSA key pair generation, storing and manimulation on server.
    |
    | **Global variables in this class:**
    | **KEY_SIZE** (*int*) – size of generated keys in bits
    | **KEY_PATH** (*Path*) – location for storing keys
    | **KEY_FILE_NAMES** (*tuple*) – filenames of keys
    
    """

    KEY_SIZE = 2048
    KEY_PATH = Path("server/_data/keys/")
    KEY_FILE_NAMES = ("priv.pem", "publ.pem")

    @staticmethod
    def init()->None:
        """
        Function for RSA key pair generation, priv.pem and publ.pem are automatically generated if they do not exist.
        """
        # Check if keypair exists in filesystem
        if not os.path.exists(
            Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[0]
        ) or not os.path.exists(Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[1]):
            key = RSA.generate(Rsa.KEY_SIZE)
            private_key = key.export_key()
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
    def get_pub_key_location()->Path:
        """
        Returns RSA public key

        :rtype: Path

        """
        return Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[1]

    @staticmethod
    def get_priv_key_location()->Path:
        """
        Returns RSA private key

        :rtype: Path

        """
        return Rsa.KEY_PATH / Rsa.KEY_FILE_NAMES[0]
