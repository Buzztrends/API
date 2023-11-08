import os
import base64
from bcrypt import hashpw, checkpw,gensalt


def hash_password(password:str)->str:
    salt = gensalt()
    hashed_bytes = hashpw(password=password.encode("utf-8"),salt=salt)
    hashed_password = base64.b64encode(hashed_bytes).decode("utf-8")

    return hashed_password


if __name__ == "__main__":
    password = "mypassword"
    enc_pass = hash_password(password)

    print(f"Password:{password}\nEncrypted Password:{enc_pass}")