"""Run the exact ordinary child-tariff controls from the authenticated #8076 checker."""
from pathlib import Path
import runpy
import sys

checker, runtime=map(Path,sys.argv[1:])
sys.argv=[str(checker),str(runtime)]
data=runpy.run_path(str(checker))
data['ordinary_debit']()
