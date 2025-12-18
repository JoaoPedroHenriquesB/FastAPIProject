from pwdlib import PasswordHash

pwd = PasswordHash.recommended()


def hash_password(password: str):
    return pwd.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd.verify(password, hashed_password)
