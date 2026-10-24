#!/usr/bin/env python3
"""Check the selected reader obstruction in the frozen response."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[2]/'root/sign-metric-normal-20261020/RESPONSE.json'
PIN='9ae1c4bf391f8ac082d2137e686f7de474005002399648bff5d443c3bc215c9c'


def need(condition,label):
    if not condition:
        raise ValueError(label)


def residue_mod5(value):
    value=Q(value)
    return value.numerator*pow(value.denominator,-1,5)%5


def main():
    raw=SOURCE.read_bytes()
    need(sha256(raw).hexdigest()==PIN,'Frozen response')
    packet=json.loads(raw)
    selected=set(packet['selected'])
    rows=[]
    for k,block in enumerate(packet['blocks']):
        if len(block['ports'])!=8:
            continue
        restricted={int(j):[Q(x),Q(y)] for j,(x,y) in packet['correction_V'][k].items() if int(j) in selected}
        need(len(restricted)==1,'One selected reader entry in each small row')
        port,(a,b)=next(iter(restricted.items()))
        need(a*a+b*b==5,'Selected reader norm5')
        need(a!=0 and b==-2*a,'Selected reader is a sign times1-2i')
        # The map i -> 3 in F5 sends i^2+1 and 1-2i to zero.
        need((3*3+1)%5==0 and (residue_mod5(a)+3*residue_mod5(b))%5==0,
             'Proper ideal obstruction over the Gaussian dyadic ring')
        rows.append({'row':k,'selected_port':port,'coefficient':[str(a),str(b)],'norm':'5'})
    need(len(rows)==8,'Eight small-block obstructions')
    result={'source_sha256':PIN,'small_selected_rows':rows,
            'selected_column_count':24,
            'selected_reader_has_Gaussian_dyadic_right_inverse':False,
            'certificate':'Apply the ring map Z[i,1/2] -> F5 with i -> 3. Eight rows of V_P vanish; a right inverse would give an identity row.',
            'scope':'No arbitrary selected-reader normalization over the Gaussian dyadic ring. Code-image divisions and other source columns are not excluded.'}
    (HERE/'READER-CHECKS.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
