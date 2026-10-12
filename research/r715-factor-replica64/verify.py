"""Run the full source-bound replica64 plus complex79 composition."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parent.parent/'r715-replica64-complex79/verify.py'),run_name='__main__')
