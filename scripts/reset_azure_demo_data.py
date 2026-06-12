import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from dotenv import load_dotenv

load_dotenv()

AZURE_DATABASE_URL = os.getenv("AZURE_DATABASE_URL")

if not AZURE_DATABASE_URL:
    raise ValueError("AZURE_DATABASE_URL is not configured in .env")

os.environ["DATABASE_URL"] = AZURE_DATABASE_URL

from reset_demo_data import reset_demo_data


if __name__ == "__main__":
    print("Resetting Azure demo database...")
    reset_demo_data()
    print("Azure demo database reset completed.")