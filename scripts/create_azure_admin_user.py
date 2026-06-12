import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

load_dotenv()

AZURE_DATABASE_URL = os.getenv("AZURE_DATABASE_URL")

if not AZURE_DATABASE_URL:
    raise ValueError("AZURE_DATABASE_URL is not configured")

os.environ["DATABASE_URL"] = AZURE_DATABASE_URL

import create_admin_user