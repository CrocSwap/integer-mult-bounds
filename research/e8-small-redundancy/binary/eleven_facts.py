"""Check the outside weights used in the eleven-centre proof."""
import json
import runpy
from pathlib import Path

ns = runpy.run_path(str(Path(__file__).with_name('parabolic_check.py')))
code = ns['code']
roots = ns['ROOTS']
e7 = next(h for h in ns['result']['hyperplanes'] if h['inside_count'] == 63)
mask = sum(1 << j for j in range(120) if j not in e7['inside'])
histogram = {}
small = []
for c in code:
    weight = (c & mask).bit_count()
    histogram[weight] = histogram.get(weight, 0) + 1
    if c and weight <= 13:
        small.append(c)
assert len(small) == 1 and small[0] == ns['root_code'][e7['normal']]
assert histogram == {0:1,1:1,24:63,25:63,28:128,29:128,32:63,33:63,56:1,57:1}
output = {'e7_outside_weight_histogram':histogram,'unique_nonzero_small_word':'K_normal','threshold':13}
print(json.dumps(output,indent=2))
Path(__file__).with_name('eleven-facts.json').write_text(json.dumps(output,indent=2)+'\n')
