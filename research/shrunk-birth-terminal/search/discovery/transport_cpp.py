"""Portable wrapper for the independently cross-checked integer solver."""
from pathlib import Path
import subprocess

def transport(left_capacity,right_capacity,edges):
    nl,nr=len(left_capacity),len(right_capacity)
    rows=[f'{nl} {nr} {len(edges)}',' '.join(map(str,left_capacity)), ' '.join(map(str,right_capacity))]
    rows += [f'{i} {j} {w}' for i,j,w in edges]
    out=subprocess.check_output([str(Path(__file__).with_name('transport-bin'))], input='\n'.join(rows)+'\n', text=True)
    lines=out.splitlines()
    count,sent,gain,iterations=map(int,lines[0].split())
    flows=[tuple(map(int,line.split()))for line in lines[1:]]
    assert len(flows)==count
    rewards={(i,j):w for i,j,w in edges}
    assert len(rewards)==len(edges)
    assert sum(n for i,j,n in flows)==sent
    assert sum(n*rewards[i,j]for i,j,n in flows)==gain
    assert all(n>0 for i,j,n in flows)
    assert all(sum(n for k,j,n in flows if k==i)<=c for i,c in enumerate(left_capacity))
    assert all(sum(n for i,k,n in flows if k==j)<=c for j,c in enumerate(right_capacity))
    return flows,dict(flow=sent,integer_surrogate_gain=gain,augmentations=iterations,
                     classes=[nl,nr],eligible_class_edges=len(edges))

if __name__=='__main__':
    from random import Random
    from transport import transport as python_transport
    rng=Random(20261009)
    for trial in range(240):
        nl,nr=rng.randrange(1,8),rng.randrange(1,8)
        left=[rng.randrange(1,4)for _ in range(nl)]
        right=[rng.randrange(1,4)for _ in range(nr)]
        edges=[(i,j,rng.randrange(1,10**8))for j in range(nr)for i in range(nl)if rng.randrange(3)]
        assert transport(left,right,edges)==python_transport(left,right,edges)
    print('PASS 240 Python/C++ exact flow, reward and iteration comparisons')
