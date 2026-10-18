"""Exact weighted signed inverse-D prefixes; Apache-2.0.
Prepared for @woklerx with substantial OpenAI Codex assistance.
"""

def events(word):
    seq=[]
    for phase in ('D','A'):
        for frame,d,sources in word[phase]:
            seq.extend((phase,'add',d,s)for s in sources)
    for j,r in enumerate(word['ret']):
        seq.append(('scatter','copy',661,r))
        for target,donors in enumerate(word['scatter']):
            if j in donors:seq.append(('scatter','add',111+target,661))
        seq.append(('scatter','erase',661,r))
    for phase in ('B','C'):
        for frame,d,sources in word[phase]:
            seq.extend((phase,'add',d,s)for s in sources)
    return seq


def positive(seq,reverse=False):
    values=[1]*661+[0];peak=1
    for phase,op,d,s in reversed(seq)if reverse else seq:
        if reverse and op!='add':op='erase'if op=='copy'else'copy'
        if op=='add':values[d]+=values[s]
        elif op=='copy':values[d]=values[s]
        else:values[d]=0
        peak=max(peak,values[d])
    return peak,values


def compute(word):
    seq=events(word);forward,_=positive(seq);old_reverse,_=positive(seq,True)
    before,entry=positive([e for e in seq if e[0]!='D'],True)
    if entry[661]!=0:raise ValueError('private entry not empty')
    weights=entry[:661];inverse=[(d,s)for phase,op,d,s in reversed(seq)if phase=='D']
    rows=[{r:1}for r in range(661)];bounds=[];peak=max(weights);witness=None
    for step,(d,s)in enumerate(inverse,1):
        for r,c in rows[s].items():
            rows[d][r]=rows[d].get(r,0)-c
            if rows[d][r]==0:del rows[d][r]
        bound=sum(abs(c)*weights[r]for r,c in rows[d].items());bounds.append(bound)
        if bound>peak:
            peak=bound;witness={'prefix_length':step,'destination':d,'source':s,
                'weighted_norm':bound,'coefficients':[[r,c]for r,c in sorted(rows[d].items())]}
    new_reverse=max(before,peak)
    def price(b):
        local=64*forward**3*b**2;nine=(1<<18)*forward**5*b**4
        return {'local_expression':str(local),'local_strict_bits':local.bit_length(),
            'nine_expression':str(nine),'nine_strict_bits':nine.bit_length()}
    return {'forward_positive_peak':forward,'old_reverse_positive_peak':old_reverse,
       'pre_D_reverse_peak':before,'entry_weights':weights,'reverse_D_ADDs':len(inverse),
       'prefix_destination_bounds':bounds,'weighted_box_D_peak':peak,'hybrid_reverse_peak':new_reverse,
       'attaining_box_witness':witness,'old_expression':price(old_reverse),'hybrid_expression':price(new_reverse),
       'complete_ADDs':sum(e[1]=='add'for e in seq),'D_grouped_records':len(word['D'])}
