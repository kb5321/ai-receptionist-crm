from dotenv import load_dotenv
import os
import psycopg2
from passlib.hash import pbkdf2_sha256

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


username = os.getenv("ADMIN_USERNAME")
plain_password = os.getenv("ADMIN_PASSWORD")
role = os.getenv("ADMIN_ROLE", "admin")

if not username:
    raise ValueError("ADMIN_USERNAME is not configured")

if not plain_password:
    raise ValueError("ADMIN_PASSWORD is not configured")

password_hash = pbkdf2_sha256.hash(plain_password)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute(
    """
    INSERT INTO admin_users (username, password_hash, role)
    VALUES (%s, %s, %s)
    """,
    (username, password_hash, role)
)

conn.commit()
cur.close()
conn.close()

print("Admin user created")
print("Username:", username)
print("Temporary password:", plain_password)