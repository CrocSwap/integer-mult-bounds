from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
OVER = support.WORD
OVER_SHA = support.WORD_SHA
