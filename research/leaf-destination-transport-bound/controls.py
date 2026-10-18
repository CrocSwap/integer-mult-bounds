# Mutation controls: the lemmas/bound must depend on the exact inverse schedule.
import census, lemmas
orig=census.word
def bad_word(n, sign=1, x=0, y=1, depth=2, off=0):
    # MUTATION: negative call negates signs but does NOT reverse phase order.
    if n == 1: return [(x, y, off, sign)]
    mid = n // 2
    ops = [(x, depth, off, mid, 1), (depth, y, off + mid, n - mid, 1),
           (x, depth, off, mid, -1), (depth, y, off + mid, n - mid, -1)]
    if sign == -1: ops = [(s, d, o, k, -g) for s, d, o, k, g in ops]
    out = []
    for s, d, o, k, g in ops: out += bad_word(k, g, s, d, depth + 1, o)
    return out
def drop_restore(n, sign=1, x=0, y=1, depth=2, off=0):
    # MUTATION: omit the final restoring phase at the top level only.
    w=orig(n,sign,x,y,depth,off);
    if n<2: return w
    q=len(orig(n-n//2,1))
    return w[:-q] if sign==1 else w[:-len(orig(n//2,1))]
for name,mut in (('unreversed_inverse',bad_word),('dropped_restoration',drop_restore)):
    lemmas.word=mut;census.word=mut
    fails=[]
    for n in range(2,9):
        try: lemmas.check(n)
        except AssertionError as e: fails.append((n,e.args[0][0]))
    env=[census.census(n,mut(n,1))[0] for n in (4,8,16)]
    print(name,'lemma failures',fails[:4],'forward envelopes n=4,8,16:',env)
lemmas.word=orig;census.word=orig
print('unmutated forward envelopes n=4,8,16:',[census.census(n,orig(n,1))[0] for n in (4,8,16)])
