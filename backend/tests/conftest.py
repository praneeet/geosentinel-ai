import sys
import os
import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.config import settings
settings.DEMO_MODE = False
settings.ENABLE_IN_APP_SCHEDULER = False

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
