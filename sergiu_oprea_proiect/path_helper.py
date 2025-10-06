"""Helps with paths through the project"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
print(PROJECT_ROOT)

def resource(path: str) -> Path:
    """Always resolve paths relative to the project root."""
    return PROJECT_ROOT / path
