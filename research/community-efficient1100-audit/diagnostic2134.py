"""A restored source-count profile omitted by the stated two-profile census.
This is not a successful paired-readout construction or a claim about its coverage.
"""
import importlib.util
from collections import Counter
from pathlib import Path
root=Path('/tmp/pr-efficient1100/sources/2134')
f=root/'research/six-source-trio-path-seed87a169/search.py'
spec=importlib.util.spec_from_file_location('trio',f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
word=[0,1,2,3,3,4,4,5,5,5,5,5,5]
counts=Counter(word);odds=[x for x in range(6)if counts[x]%2];assert len(word)==13 and len(odds)==3
complete=[counts[x]+(x in odds)for x in range(6)]
assert sum(complete)==16 and all(x>0 and x%2==0 for x in complete)
try:m.analyze_word(word)
except ValueError as exc:print('Omitted restored profile:',sorted(counts.values()),'TRIO',odds,'total',sorted(complete),'rejection:',exc)
else:raise AssertionError('example now accepted; rerun scope review')
