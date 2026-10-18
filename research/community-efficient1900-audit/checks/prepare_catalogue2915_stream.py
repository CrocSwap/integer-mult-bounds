from pathlib import Path
import json,shutil
P=Path('/tmp/pr-efficient1900');pkg=P/'sources/2915/research/selected-bit-fast-primitives';src=pkg/'check_catalogue.py';original=src.read_text();(P/'original-check_catalogue2915.py').write_text(original)
s=original.replace('import sys\n','import sys\nfrom unittest.mock import patch\n')
s=s.replace('    registry, receipt = selected_registry(catalogue)','''    # This census visits each owner chart once. Recompute the pure matrix
    # accessor rather than retaining every dense Fraction matrix in its LRU.
    matrix = type(catalogue).chart_matrix.__wrapped__
    with patch.object(catalogue, "chart_matrix", lambda chart: matrix(catalogue, chart)):
        registry, receipt = selected_registry(catalogue)
    print("catalogue registry complete", len(registry.words), flush=True)''')
s=s.replace('        cases += 1','''        cases += 1
        # Each compiled route is checked and digested before the next; retaining
        # prior low-carry programs adds memory without adding coverage.
        registry.compiled.clear()''')
assert s!=original;src.write_text(s);dst=P/'resolutions/2915/research/selected-bit-fast-primitives/check_catalogue.py';dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(s)
shutil.copy2(P/'check-2915.json',P/'check-2915-original-resource-stop.json');shutil.copy2(P/'check-2915.log',P/'check-2915-original-resource-stop.log')
print('Prepared diagnostic-only cache-lifetime resolution; all matrices and programs still checked')
