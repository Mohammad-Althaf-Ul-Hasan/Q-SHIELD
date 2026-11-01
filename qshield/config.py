"""
config.py
Central configuration for Q-SHIELD.
Loads settings from .env file and environment variables.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """Base configuration."""

    # ---- Flask ----
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default-dev-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    ENV = os.getenv("FLASK_ENV", "production")

    # ---- Database ----
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "quantum_db")

    @property
    def db_config(self):
        """Return MySQL connection dictionary."""
        return {
            "host": self.DB_HOST,
            "port": self.DB_PORT,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "database": self.DB_NAME,
        }

    # ---- QKD Protocol ----
    QBER_THRESHOLD = float(os.getenv("QBER_THRESHOLD", 0.11))
    DEFAULT_NUM_QUBITS = int(os.getenv("DEFAULT_NUM_QUBITS", 256))

    # ---- Key Lifecycle ----
    KEY_EXPIRY_MINUTES = int(os.getenv("KEY_EXPIRY_MINUTES", 30))

    # ---- QRNG API ----
    QRNG_API_URL = os.getenv(
        "QRNG_API_URL",
        "https://qrng.anu.edu.au/API/jsonI.php?length=1024&type=uint8",
    )

    # ---- Logging ----
    LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "app.log")


# Create a global config instance
config = Config()