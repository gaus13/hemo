from pwdlib import PasswordHash

# see in fastapi docs, also PasswordHash.recommended() 
# factory automatically selects the most secure algorithm available (typically Argon2id)
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure hash.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that the plain password matches the stored hash.
    """
    return password_hash.verify(plain_password, hashed_password)