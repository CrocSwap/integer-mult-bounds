from pathlib import Path
import sys, json
import argparse
import numpy as np
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
sys.path.insert(0, str(PACKAGE / 'code'))
import e8_cubed as e
roots,_=e.e8_shells()
full=np.concatenate((roots,-roots))

def partition(matrix, order):
    masks=[sum(int(value)<<j for j,value in enumerate(row)) for row in matrix]
    rectangles=[]
    def descend(indices, remaining):
        common=remaining
        for index in indices: common &= masks[index]
        if common:
            rectangles.append((tuple(indices), common))
            remaining ^= common
        indices=[i for i in indices if masks[i]&remaining]
        if not indices: return
        if len(indices)==1:
            rectangles.append((tuple(indices), masks[indices[0]]&remaining))
        else:
            middle=len(indices)//2
            descend(indices[:middle],remaining)
            descend(indices[middle:],remaining)
    descend(list(map(int,order)),(1<<matrix.shape[1])-1)
    replay=[0]*len(matrix)
    for rows,mask in rectangles:
        for r in rows:
            if replay[r]&mask: raise ValueError('overlap')
            replay[r] |= mask
    if replay!=masks: raise ValueError('not exact')
    c=len(rectangles); left=sum(len(rows) for rows,mask in rectangles); right=sum(mask.bit_count() for rows,mask in rectangles)
    return dict(rectangles=c,source_memberships=left,target_memberships=right,helpers=left+right-c,
                edges=sum(len(rows)*mask.bit_count() for rows,mask in rectangles))

def best(matrix):
    trials=[]
    rng=np.random.default_rng(420)
    for transpose in [False,True]:
        work=matrix.T if transpose else matrix
        for k in range(16):
            order=np.arange(len(work)) if k==0 else rng.permutation(len(work))
            result=partition(work,order)
            if transpose: result['source_memberships'],result['target_memberships']=result['target_memberships'],result['source_memberships']
            result.update(transpose=transpose,trial=k)
            trials.append(result)
    return min(trials,key=lambda x:x['helpers'])

parts=[]
for dot in range(-2,3):
    a=best((roots@roots.T)//4==dot)
    b=best((full@full.T)//4==-dot)
    c=a['rectangles']*b['rectangles']; left=a['source_memberships']*b['source_memberships']; right=a['target_memberships']*b['target_memberships']
    parts.append(dict(dot_a=dot,dot_b=-dot,A=a,B=b,product_rectangles=c,product_source_memberships=left,product_target_memberships=right,
                      helpers=left+right-c,edges=a['edges']*b['edges']))
out=dict(status='PASS_EXACT_ROOT_PAIR_ORTHOGONALITY_RECTANGLE_PARTITION',ports=28800,
         edges=sum(x['edges'] for x in parts),helpers=sum(x['helpers'] for x in parts),parts=parts,
         scope='Explicit independent rectangle side circuit on the mixed E8 squared ports only; each source span is rationally orthogonal to every target, positive definite. All five small partitions are exactly replayed and tensor products partition the full relation. This is a tested construction, not a lower bound for all rectangle partitions or shared-role circuits.')
if out != json.loads((HERE/'RECTANGLES.json').read_text()):
    raise ValueError('Root-pair rectangle receipt mismatch')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
if args.output:
    if args.output.resolve().is_relative_to(PACKAGE):
        raise ValueError('Replay output must be outside the package')
    args.output.write_text(json.dumps(out,indent=2)+'\n')
print(out['status'])
