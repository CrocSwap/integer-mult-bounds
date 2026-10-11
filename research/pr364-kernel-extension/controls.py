"""Independent packed-integer F2 operator replay and added-gate controls.
This checks all local source, target and dirty-input columns. It does not claim
signed integer decoder equality; bit payload exactness is the retained contract.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import hashlib
import json
import struct
from pathlib import Path


def controls(word):
    if not __debug__:
        raise SystemExit('Assertions must be enabled')
    word=Path(word)
    state=json.loads((word/'249-states.json').read_text())
    n,v=state['n'],state['v']
    raw=(word/'249-records.bin').read_bytes()
    records=list(struct.iter_unpack('<6i',raw))
    pivots={7107,7848}
    added=[i for i,(op,a,b,c,f,z) in enumerate(records) if op==1 and z in (44,45) and b in pivots]
    assert len(added)==12
    expected=[(1<<r)^((1<<(r-v)) if v<=r<2*v else 0) for r in range(n)]

    def replay(omit=None):
        value=[1<<r for r in range(n)]+[0]
        for i,(op,a,b,c,f,z) in enumerate(records):
            if i==omit: continue
            if op==1 and c%2: value[a]^=value[b]
            elif op==2: value[n]=value[a]
            elif op==3: value[n]=0
        differences=[value[r]^expected[r] for r in range(n) if value[r]!=expected[r]]
        columns=0
        for difference in differences: columns|=difference
        return dict(wrong_rows=len(differences),wrong_columns=columns.bit_count(),temporary_dirty=bool(value[n]))

    positive=replay()
    assert positive==dict(wrong_rows=0,wrong_columns=0,temporary_dirty=False)
    omitted=[]
    for i in added:
        result=replay(i)
        assert result['wrong_rows']>0 and result['wrong_columns']>0
        omitted.append(dict(omitted_record=i,record=records[i],**result))
    return dict(status='PASS_ALL_COLUMNS_AND_TWELVE_ADDED_GATE_OMISSION_CONTROLS',
                word_sha256=hashlib.sha256(raw).hexdigest(),formal_columns=n,
                positive_control=positive,negative_controls=omitted,
                scope='Exact local F2 operator. Physical five-stage columns, geometry, source spans and banks checked separately.')
