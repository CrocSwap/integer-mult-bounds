from pathlib import Path
import sys
if len(sys.argv)!=2:raise SystemExit('Usage: python3 SCRIPT OUTPUT_DIRECTORY')
OUTPUT=Path(sys.argv[1]).expanduser().resolve()
OUTPUT.mkdir(parents=True,exist_ok=True)
