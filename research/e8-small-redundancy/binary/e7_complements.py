"""Check the complements of maximal proper E7 root flats."""
import json
import runpy
from pathlib import Path

namespace = runpy.run_path(str(Path(__file__).with_name('parabolic_check.py')))
roots = namespace['ROOTS']
simple = namespace['simple']
rankq = namespace['rankq']
result = namespace['result']
e7 = next(item for item in result['hyperplanes'] if item['inside_count'] == 63)
system = simple[:e7['delete']] + simple[e7['delete']+1:]
output = []
for delete in range(7):
    basis = system[:delete] + system[delete+1:]
    inside = [q for q in e7['inside'] if rankq(basis + [roots[q]]) == 6]
    complement = [q for q in e7['inside'] if q not in inside]
    r = rankq([roots[q] for q in complement])
    assert r == 7
    output.append({'delete':delete,'inside_count':len(inside),'complement_count':len(complement),'complement_rank':r})
print(json.dumps(output,indent=2))
Path(__file__).with_name('e7-complements.json').write_text(json.dumps(output,indent=2)+'\n')
