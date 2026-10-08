from pathlib import Path
import json
from independent_controls import corner_labels,expected_pivots,completion,check_cuts
h=45;rows,cols=corner_labels(h);pivots=expected_pivots(h)
wrong=[(c,(j+h+1)%(h+2)) for j,(c,g) in enumerate(cols)]
results={}
for name,fn in [('retained_old_column_offset',lambda:completion(h,rows,wrong)),('old_offset_suffix_rank_cut',lambda:check_cuts(h,rows,wrong,pivots)),('nonpermutation_repeated_label',lambda:completion(h,[(0,b) if i==h+2 else (r,b) for i,(r,b) in enumerate(rows)],cols))]:
    try:fn()
    except AssertionError:results[name]='rejected'
    else:raise AssertionError('Negative control unexpectedly passed: '+name)
Path(__file__).with_name('NEGATIVE_CONTROLS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
