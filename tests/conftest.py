 
# tests/conftest.py
# Makes src/ and src/packages/ importable for all tests
import sys, os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, 'src'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'src', 'packages'))