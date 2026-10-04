"""Pytest configuration for Merithra tests.

Ensures the merithra package is importable by adding the project root to sys.path.
"""

import sys
from pathlib import Path

# Add project root to Python path so `merithra` package is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))