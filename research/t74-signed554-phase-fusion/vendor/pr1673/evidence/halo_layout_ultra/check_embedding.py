"""Exact simultaneous zero embedding/cropping in lexicographic order."""
from itertools import product
from pathlib import Path
import json,math
HERE=Path(__file__).resolve().parent
def check(s,t):
    original=list(product(*(range(n) for n in s)));it=iter(enumerate(original,1))
    embedded=[];valid=[]
    for x in product(*(range(n) for n in t)):
        if all(a<n for a,n in zip(x,s)):
            item=next(it);assert item[1]==x;embedded.append(item);valid.append(True)
        else:embedded.append(None);valid.append(False)
    assert next(it,None) is None
    cropped=[v for v,keep in zip(embedded,valid) if keep]
    assert cropped==list(enumerate(original,1))
    return dict(source=s,target=t,source_records=math.prod(s),target_records=math.prod(t),
                all_axes_embedded_in_one_ordered_pass=True,crop_restores_exact_order=True)
def main():
    cases=[check([3,5],[4,8]),check([7,3,6],[8,4,8]),check([5,7,3,2],[8,8,4,2])]
    out=dict(status='PASS_SIMULTANEOUS_RECTANGULAR_EMBEDDING_AND_CROP',cases=cases)
    (HERE/'EMBEDDING-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
