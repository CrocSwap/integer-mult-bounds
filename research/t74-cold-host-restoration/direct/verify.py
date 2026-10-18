"""Entry point for the independent standard-library direct census."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from reproduce import main
if __name__ == '__main__':main()
