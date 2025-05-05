import os
import sys


def pytest_configure(config):
    """Allow test scripts to import scripts from parent folder."""
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, src_path)
