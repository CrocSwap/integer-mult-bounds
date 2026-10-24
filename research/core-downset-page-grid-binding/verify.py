"""Actual multi-interior Core with independent rational stage/page checks.
JoyboyBrian with OpenAI Codex assistance. Apache-2.0.
"""
import argparse,json,time,sys
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import load,need,HERE

def maximum(matrix):return max((abs(z.re)+abs(z.im) for row in matrix for z in row),default=Q(0))
def subtract(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def action(a,b):return [[sum((x*b[k][j] for k,x in enumerate(row)),b[0][j]*0) for j in range(len(b[0]))] for row in a]
def reject(call,reason):
    try:call()
    except (ValueError,AssertionError) as e:
        need(reason in str(e),'wrong control rejection '+str(e));return
    raise ValueError('control accepted '+reason)

def page_check(obj):
    eta=Q(1,1<<obj.bits)
    def check(rounded,exact,limit):
        need(len(rounded)==len(exact),'page rows')
        for a,b in zip(rounded,exact):
            need(len(a)==len(b) and sum(abs(x-y) for x,y in zip(a,b))<=limit,'page error budget')
            need(all((x/eta).denominator==1 for x in a),'prepared page grid')
    check(obj.lower_page,obj.lower_coupling,(2*obj.width+1)*eta)
    check(obj.upper_page,obj.upper_coupling,(2*obj.width+1)*eta)
    if obj.kind=='broad':check(obj.schur_page,obj.schur,(2*obj.schur_band+1)*eta)
    else:
        s=obj.solver;w=s.width
        for label,factor in [('lower',s.lower),('upper',s.upper_reverse)]:
            check(s.factor_pages[label],factor,(2*obj.width+1)*eta)
            for j,start in enumerate(range(0,len(factor),w)):
                exact=[[factor[start+i][start+k] if start+i<len(factor) and start+k<len(factor) else Q(i==k) for k in range(w)] for i in range(w)]
                inverse=s.exact_inverses[tuple(map(tuple,exact))]
                need(all(sum(exact[i][k]*inverse[k][j] for k in range(w))==Q(i==j) for i in range(w) for j in range(w)),'independent inverse-page identity')
                check(s.diagonal_pages[label][j],exact,w*eta)
                check(s.inverse_pages[label][j],inverse,2*w*eta)

def stage_check(obj,stage,before,after):
    need(maximum(before)<=obj.stage_radius and maximum(after)<=obj.stage_radius,'actual current-state radius')
    if stage=='boundary_inverse':
        residual=maximum(subtract(action(obj.schur,[after[i] for i in obj.boundary]),[before[i] for i in obj.boundary]))
        error=residual/obj.gap
        need(all(before[i]==after[i] for i in obj.interior),'inverse boundary spectators')
    else:
        wanted=[list(r) for r in before]
        if stage.startswith('interior_'):
            for cell in obj.cells:
                values=[before[i] for i in cell['indices']]
                for j in range(len(values[0])):
                    need(sum(z[j].norm2() for z in values)<=obj.dense_radius**2,'computed raw Euclidean entrance')
                exact=cell['inverse'] if stage.endswith('inverse') else cell['matrix']
                out=action(exact,values)
                for i,r in zip(cell['indices'],out):wanted[i]=r
        elif stage=='boundary_forward':
            for i,r in zip(obj.boundary,action(obj.schur,[before[i] for i in obj.boundary])):wanted[i]=r
        else:
            lower=stage.startswith('lower_');targets,sources=(obj.boundary,obj.interior) if lower else (obj.interior,obj.boundary)
            page=obj.lower_coupling if lower else obj.upper_coupling
            if sources:
                for i,r in zip(targets,action(page,[before[i] for i in sources])):
                    sign=-1 if stage.endswith('negative') else 1
                    wanted[i]=[x+sign*y for x,y in zip(before[i],r)]
        error=maximum(subtract(after,wanted))
    need(error<=obj.stage_error,'independent local stage defect')
    return error

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    start=time.monotonic();raw,core,Bound,Raw,binding=load()
    from exact import C,Mat,ceil_log2,vector_hash
    from gaussian_reference import Reference,Entry
    import raw_gaussian
    ref=Reference(raw,384,1,2,4,18,320);length=7*ref.spec.target_halfwidth+17
    baseline=json.loads(raw['research/rational-unitary-fft/CORE-RESULT.json'])
    rows=[]
    for kind in ('narrow','broad'):
        print('BUILD_CORE',kind,flush=True)
        obj=Bound(raw,ref,kind,8,8+length,16,1,20,3,physical_band=max(2*ref.spec.source_halfwidth+2,ref.spec.target_halfwidth))
        old=next(x for x in baseline['cases'] if x['label']==kind+'-core')
        need(obj.n==143 and len(obj.cells)==2 and all(len(c['indices'])==16 for c in obj.cells),'original multi-interior discriminator')
        need(obj.reference_hash==old['reference_matrix_sha256'] and core.matrix_hash(obj.schur)==old['schur_sha256'],'same original reference and exact Schur')
        for c,oc in zip(obj.cells,old['interior_blocks']):
            need(core.matrix_hash(c['matrix'])==oc['reference_sha256'] and core.matrix_hash(c['inverse'])==oc['reference_inverse_sha256'],'same exact interior factors')
            need(isinstance(c['probe'],Raw) and isinstance(c['program'],Raw),'both actual constructor sites bound')
            need(c['probe'].data_bits<=obj.bits==c['program'].data_bits==c['program'].child.builder.bound['data_bits'],'complete common grid')
        k=obj.factor_bound;ys=6*k**5;err=Q(1,1<<20)/(10*k**4)
        sparse=1+ceil_log2(((2*obj.width+1)*ys+1)/err)
        boundary=20+ceil_log2(10*k**4)+41+16*ceil_log2(obj.p)+ceil_log2(ys)
        broad=1+ceil_log2(((2*obj.schur_band+1)*ys+1)/err)
        floors={'incoming':3,'sparse':sparse,'boundary_or_apply':boundary if kind=='narrow' else broad,'raw_probe':max(c['probe'].data_bits for c in obj.cells)}
        need(obj.bits==max(floors.values()),'independently reconstructed grid floors')
        page_check(obj)
        rhs=Mat([[C(Q((3*i)%7-3,8),Q((5*i)%5-2,8))] for i in range(obj.n)])
        answer,execution,traces=obj.execute(rhs,capture=True)
        errors=[stage_check(obj,*trace) for trace in traces]
        paid_dense=sum(sum(map(len,c['program'].inverse_plan if stage.endswith('inverse') else c['program'].plan)) for stage,_,_ in traces if stage.startswith('interior_') for c in obj.cells)
        need(execution['statistics']['dense_gate_applications']==paid_dense,'complete actual dense invoice')
        if obj.solver:
            w=obj.solver.width;blocks=(len(obj.boundary)+w-1)//w;rhs_batches=(2+w-1)//w
            scalar=2*(2*blocks-1)*rhs_batches*7**(w.bit_length()-1)
            need(execution['statistics']['boundary_scalar_products']==scalar,'complete two-pass ceiling invoice')
        if kind=='narrow':endpoint=maximum(subtract(action(obj.matrix,answer),rhs))/obj.gap
        else:endpoint=maximum(subtract(answer,action(obj.matrix,rhs)))
        need(endpoint<=5*k**4*err==Q(1,1<<21),'independent complete reference endpoint')
        # Actual stale final binding at this same entrance requests a different grid.
        cell=obj.cells[0]
        stale=raw_gaussian.RawGaussian(raw,ref,kind,cell['source_start'],16,obj.dense_radius,obj.dense_target,obj.bits)
        need(stale.data_bits>obj.bits,'missing final binding has incompatible actual request')
        # Corrupt actual prepared page and test the independent page contract.
        page=obj.solver.inverse_pages['lower'][0] if obj.solver else obj.schur_page
        saved=page[0][0];page[0][0]+=1
        reject(lambda:page_check(obj),'page error budget');page[0][0]=saved
        key=kind,obj.coordinates[0],obj.coordinates[0];saved=ref.entries[key]
        ref.entries[key]=Entry(Q(2),'unit-diagonal',0,Q(0))
        reject(lambda:obj.execute(rhs),'same immutable reference core');ref.entries[key]=saved
        # Current-state certificate must detect omitted genuine coupling, not root-radius bookkeeping.
        trace=next(x for x in traces if x[0].startswith('upper_'))
        reject(lambda:stage_check(obj,trace[0],trace[1],trace[1]),'independent local stage defect')
        need(obj.bits<old['budget']['data_bits'],'finite common-grid change')
        rows.append({'kind':kind,'old_data_bits':old['budget']['data_bits'],'data_bits':obj.bits,'floors':floors,'missing_final_request':stale.data_bits,'record':obj.record(),'execution':execution,'local_error_hash':vector_hash(C(e) for e in errors),'endpoint_error_hash':vector_hash([C(endpoint)]),'output_hash':core.matrix_hash(answer),'nonzero_endpoint_error':endpoint>0})
        print('CHECK_CORE',kind,flush=True)
    result={'status':'PASS_COMPLETE_CORE_GRID_BINDING','binding':binding,'cases':rows,'controls_per_kind':['actual old final grid incompatible','corrupt actual page','changed immutable reference','omitted actual upper coupling'],'physical_tape_execution':False,'inherited_analytic_premises':True}
    result=json.loads(json.dumps(result))
    if args.record:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(result==json.loads((HERE/'RESULT.json').read_text()),'frozen result mismatch')
    print('PASS_COMPLETE_CORE_GRID_BINDING',round(time.monotonic()-start,6))
if __name__=='__main__':main()
