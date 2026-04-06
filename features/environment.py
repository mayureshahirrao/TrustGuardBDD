"""Behave environment configuration — runs before/after features, scenarios, steps."""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("auth_api_tests")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def before_all(context):
    """Initialise shared state available to every scenario."""
    context.base_url = os.getenv("BASE_URL", "http://13.232.201.222:3000")
    context.default_password = "SecurePass123!"
    logger.info(f"Base URL: {context.base_url}")


def before_scenario(context, scenario):
    """Reset per-scenario state."""
    context.response = None
    context.payload = None
    context.email = None
    context.token = None
    context.otp = None
    context.saved = {}  # general-purpose dict for multi-step scenarios


def after_scenario(context, scenario):
    """Log outcome for observability."""
    status = scenario.status.name
    logger.info(f"Scenario [{status}]: {scenario.name}")
