"""Literal packed-input execution, independent of row-factor discovery.
Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
"""
def execute(records, inputs, omitted=()):
    values=list(inputs)
    index=0
    for frame,d,sources in records:
        if frame!=0:raise ValueError('nonzero D frame')
        for s in sources:
            if index not in omitted:values[d]=values[d]^values[s]
            index+=1
    return values


def complete_single_coverage(records, inputs):
    baseline=execute(records,inputs)
    count=sum(len(ss) for _,_,ss in records)
    failures=[];patterns={1:0,2:0,3:0};target_misses=[]
    for k in range(count):
        actual=execute(records,inputs,(k,))
        pattern=0;target_pattern=0
        for row,(x,y) in enumerate(zip(actual,baseline)):
            pattern|=x^y
            if 111<=row<222:target_pattern|=x^y
        if not pattern:failures.append(k)
        else:patterns[pattern]+=1
        if not target_pattern:target_misses.append(k)
    if failures:raise ValueError('literal single-fault coverage failed: '+str(failures[:8]))
    return {'faults':count,'detection_patterns':{str(k):v for k,v in patterns.items()},
            'target_only_missed_indices':target_misses,
            'literal_ADD_updates':count*(count-1),'observed_output_values':count*len(inputs)}


def backward_activation(gates, index, n):
    # Pull a scalar coordinate functional through the prefix in reverse.
    support={gates[index][1]}
    for d,s in reversed(gates[:index]):
        if d in support:
            if s in support:support.remove(s)
            else:support.add(s)
    return sorted(support)
