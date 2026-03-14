import logging
import sys
import os
from core.settings import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)


def setup_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s | %(name)s | %(message)s"
    )

    if not logger.handlers:

        # File handler
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


"""
from utils.logger import setup_logger

# Initialize logger with a custom name
logger = setup_logger("socket")  # Can also be "recipes", "auth", etc.

# 🔍 DEBUG: Internal, low-level information for development
logger.debug("Detailed info: function started, variables set, etc.")

# ✅ INFO: High-level operations, like connections, successful events
logger.info("User connected to /recipes namespace")
logger.info(f"Recipe {recipe_id} metadata sent to user {user.name}")

# ⚠️ WARNING: Something unexpected, but not a crash
logger.warning("Missing recipe_id in received socket data")
logger.warning(f"User {user.email} tried to access restricted resource")

# ❌ ERROR: A serious problem occurred, but app continues
logger.error("Failed to fetch recipe from database")

# 💥 EXCEPTION: Like .error(), but logs full traceback (use inside except blocks)
try:
    ...
except Exception as e:
    logger.exception(f"Unhandled error in on_get_meta: {e}")
"""