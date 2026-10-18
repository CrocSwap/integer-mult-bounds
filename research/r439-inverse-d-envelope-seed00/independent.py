"""One-hot scalar execution independent of symbolic-row arithmetic.
Apache-2.0; substantial OpenAI Codex assistance for @woklerx.
"""

def need(ok,msg):
    if not ok:raise ValueError(msg)


def entry_box(word):
    # Reverse the literal record hierarchy, not envelope.events.
    x=[1]*661;peak=1
    for name in ('C','B'):
        for frame,d,sources in reversed(word[name]):
            for s in reversed(sources):x[d]+=x[s];peak=max(peak,x[d])
    for j in reversed(range(9)):
        private=x[word['ret'][j]];peak=max(peak,private)
        for t in reversed(range(111)):
            if j in word['scatter'][t]:x[111+t]+=private;peak=max(peak,x[111+t])
        private=0
    for frame,d,sources in reversed(word['A']):
        for s in reversed(sources):x[d]+=x[s];peak=max(peak,x[d])
    return x,peak


def inverse_operations(word):
    return [(d,s)for frame,d,sources in reversed(word['D'])for s in reversed(sources)]


def columns(word,weights):
    ops=inverse_operations(word);bounds=[0]*len(ops);supports=[0]*len(ops)
    # Each run contains actual integer values from one unit input; there are
    # no coefficient-vector or row-subtraction operations in this oracle.
    for source in range(661):
        x=[0]*661;x[source]=1
        for k,(d,s)in enumerate(ops):
            x[d]-=x[s];bounds[k]+=abs(x[d])*weights[source];supports[k]+=int(x[d]!=0)
        # Replay the original D forwards to prove its inverse on every column.
        for frame,d,donors in word['D']:
            for s in donors:x[d]+=x[s]
        need(x==[int(r==source)for r in range(661)],'inverse D endpoint')
    return bounds,supports


def attain(word,weights,witness):
    coefficients=dict(witness['coefficients'])
    x=[weights[r]*(1 if coefficients.get(r,0)>0 else -1 if coefficients.get(r,0)<0 else 0)for r in range(661)]
    need(all(abs(z)<=b for z,b in zip(x,weights)),'box membership')
    for d,s in inverse_operations(word)[:witness['prefix_length']]:x[d]-=x[s]
    need(x[witness['destination']]==witness['weighted_norm'],'attaining box corner')
    return x[witness['destination']]


def row_backward(word,witness):
    # Pull the one output functional back through its prefix, in reverse time.
    a=[0]*661;a[witness['destination']]=1
    for d,s in reversed(inverse_operations(word)[:witness['prefix_length']]):a[s]-=a[d]
    return [[r,c]for r,c in enumerate(a)if c]


def mod_two_boundary(word):
    x=[1<<r for r in range(661)]
    for frame,d,ss in word['D']:
        for s in ss:x[d]^=x[s]
    return x
