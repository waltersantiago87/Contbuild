import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://contabilidade_user:contabilidade_pass@localhost:5432/contabilidade_db"
)
