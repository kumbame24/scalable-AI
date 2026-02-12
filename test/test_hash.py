from passlib.context import CryptContext

def test_hash():
    try:
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        password = "testpassword123"
        print(f"Hashing password: {password}")
        hashed = pwd_context.hash(password)
        print(f"Hashed: {hashed}")
        
        verified = pwd_context.verify(password, hashed)
        print(f"Verified: {verified}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hash()
