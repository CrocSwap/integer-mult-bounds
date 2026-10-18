"""Actual selected child7 through Compact, C^2, inverse and parked return."""
from pathlib import Path
import argparse, copy, hashlib, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import HERE,load,need
import oracle

def encoded(value): return json.dumps(value,indent=2,sort_keys=True)+'\n'

def result():
    full,frame,native,pins=load()
    import compose as physical
    prior=physical.prior
    reduced={k:v for k,v in full.items() if k not in ('left','right')}
    for name in ('left','right'):
        r=full[name]
        need(r['matrix_rows'][4:]==[1<<j for j in range(4,9)] and
             all(row<16 for row in r['matrix_rows'][:4]) and r['offset']<16 and
             not any(r['linear_Z4'][4:]) and
             all(not(r['quadratic_rows'][i]>>(i+1)) for i in range(4,9)) and
             all(not(r['quadratic_rows'][i]>>4) for i in range(4)), 'exact four-axis factor')
        reduced[name]={k:(v[:4] if isinstance(v,list) else v) for k,v in r.items()}
        for x in range(512):
            y,p=oracle.monomial(r,x);z,q=oracle.monomial(reduced[name],x%16)
            need((y,p)==(z|(x&~15),q),'all original monomial columns including spectators')
    single=oracle.columns(reduced);original=oracle.columns(full)
    target=native.canonical_frame(9,frame)
    for x,col in enumerate(original):
        vec,den=target.zero_state(x)
        need({j:(a*(2>>den),b*(2>>den)) for j,(a,b) in enumerate(vec) if a or b}==col,
             'all source canonical operator columns')
        need(col=={y|(x&~15):z for y,z in single[x%16].items()},'whole child factor with five unchanged axes')
    cols=oracle.tensor_columns(single)
    outer,bits=3,24
    lay=physical.layout(bits)
    values=[((i+1)*16,((i*i+7*i)%12289-6144)*16) for i in range(outer*lay.records)]
    raw=prior.encode(values,bits)
    meter=prior.Meter();grid=prior.Grid(bits,8)
    dirty=[bytearray((i+i//3)%2 for i in range(n)) for n in (23,113)]
    ancestor=bytes((i//2+i)%2 for i in range(47))
    park=prior.Park(meter,ancestor)
    active=prior.TrackingTape(meter,raw)
    inactive=[prior.TrackingTape(meter,d) for d in dirty]
    out,restored=physical.invoke(active,inactive,park,reduced,grid,outer)
    expected=oracle.apply(values,lay,cols,outer)
    need(prior.decode(out.data,bits)==expected,'complete finite Compact-child composition')
    need([bytes(t.data) for t in restored]==list(map(bytes,dirty)) and park.cells==ancestor,
         'arbitrary dirty caller packets and ancestor restore')
    output_sha=hashlib.sha256(out.data).hexdigest()
    out,restored=physical.invoke(out,restored,park,reduced,grid,outer,True)
    need(out.data==raw and [bytes(t.data) for t in restored]==list(map(bytes,dirty)),
         'literal inverse after full Compact repairs returns exact original')
    need(park.minimum_head==park.floor and park.cells==ancestor,'opaque ancestor untouched')
    positive=physical.report(meter,grid,park)
    need(meter.repair_records>0 and meter.ordinary_calls and all(c['width']==1 for c in meter.ordinary_calls),
         'actual Compact dispatch with ordinary compact swaps and exceptional repair')
    controls={}
    smallvalues=values[:lay.records];smallraw=prior.encode(smallvalues,bits)
    expected_small=oracle.apply(smallvalues,lay,cols,1)
    # At K=G=1 the raw low-bit map already agrees. Keep this observed boundary
    # as a positive control; it does not license omitting repair at other K.
    omitted=physical.child(prior.TrackingTape(prior.Meter(),smallraw),reduced,prior.Grid(bits,8),1,1,fault='omit_repair')
    need(prior.decode(omitted.data,bits)==expected_small,'K1 omission positive boundary')
    for fault in ('wrong_inverse_key','single_constant_phase'):
        try:
            wrong=physical.child(prior.TrackingTape(prior.Meter(),smallraw),reduced,prior.Grid(bits,8),1,1,fault=fault)
        except ValueError as error:
            need(fault=='wrong_inverse_key','unexpected semantic control rejection '+str(error))
            controls[fault]='REJECT: '+str(error)
        else:
            need(prior.decode(wrong.data,bits)!=expected_small,'effective composed control '+fault)
            controls[fault]='REJECT: incorrect full endpoint'
    wrong=physical.child(prior.TrackingTape(prior.Meter(),smallraw),reduced,prior.Grid(bits,8),1,1,round_child=True)
    need(prior.decode(wrong.data,bits)!=expected_small,'return rounding changes exact child')
    controls['child_return_rounding']='REJECT: incorrect endpoint'
    bad=copy.deepcopy(reduced);bad['right']['offset']^=1
    need(oracle.tensor_columns(oracle.columns(bad))!=cols,'wrong actual affine translation')
    controls['wrong_translation']='REJECT: canonical operator mismatch'
    try: prior.Grid(8,4).divide(bytearray([1]+[0]*7),1)
    except ValueError as error: need(str(error)=='division discards only reserved zero bits','division failure reason')
    else: raise ValueError('unreserved exact division accepted')
    controls['unreserved_grid']='REJECT'
    try: prior.Park(prior.Meter(),ancestor).pop(1)
    except ValueError as error: need(str(error)=='opaque ancestor boundary','park failure reason')
    else: raise ValueError('ancestor access accepted')
    controls['ancestor_boundary']='REJECT'
    # An actual selected binary-word gate, now on a repair-sensitive complete
    # rectangle. Source axis0 is also the actual C-child axis.
    gate=next(op for op in physical.monomial.binary_word(reduced['right']) if op[0]=='add' and op[2]==0)
    from compact import Compact,Layout,execute
    from arithmetic import c_axis
    repair_layout=Layout((('u',1),('t',1),('v0',4),('v1',4),('b',1)),2*bits)
    repair_word=Compact(1,2,1,1,'v0','v1',False)
    repair_values=values[:repair_layout.records]
    repair_raw=prior.encode(repair_values,bits)
    ideal=[None]*repair_layout.records
    for index,value in enumerate(repair_values):
        state=repair_layout.decode(index);state['v1']^=state['v0']&10
        ideal[repair_layout.encode(state)]=value
    repaired=execute(prior.TrackingTape(prior.Meter(),repair_raw),repair_layout,repair_word)
    need(prior.decode(repaired.data,bits)==ideal,'actual selected gate complete repair-sensitive rectangle')
    raw_gate=execute(prior.TrackingTape(prior.Meter(),repair_raw),repair_layout,repair_word,omit_repair=True)
    need(prior.decode(raw_gate.data,bits)!=ideal,'omitting repair changes actual selected gate')
    expected_gate=ideal
    for bit in (1,3):
        expected_gate=oracle.axis(expected_gate,repair_layout.bits,repair_layout.position('v0',bit))
    grid_repair=prior.Grid(bits,8)
    for bit in (1,3):
        repaired=c_axis(repaired,repair_layout.bits,repair_layout.position('v0',bit),1,grid_repair)
        raw_gate=c_axis(raw_gate,repair_layout.bits,repair_layout.position('v0',bit),1,prior.Grid(bits,8))
    need(prior.decode(repaired.data,bits)==expected_gate and prior.decode(raw_gate.data,bits)!=expected_gate,
         'repair-sensitive actual gate followed by actual two-axis child')
    for bit in (3,1): repaired=c_axis(repaired,repair_layout.bits,repair_layout.position('v0',bit),1,grid_repair,True)
    repaired=execute(repaired,repair_layout,repair_word)
    need(repaired.data==repair_raw and not grid_repair.workspace,'gate/child/inverse complete return')
    controls['omit_repair_at_K2']='REJECT: complete gate/child endpoint'
    return {'status':'PASS_SELECTED_COMPACT_CHILD_RETURN','source_child':7,'source_events':[9394,9396],
            'old_frame':0,'new_frame':9,'frame':frame,'native_rank':1,'tensor_columns':2,
            'actual_native_columns':512,'source_monomial_columns':1024,'active_axes':4,'factored_spectator_axes':5,
            'tensor_operator_columns':256,'tensor_nonzero_coefficients':sum(map(len,cols)),
            'columns_sha256':hashlib.sha256(encoded(cols).encode()).hexdigest(),
            'outer_rows':outer,'address_records':outer*lay.records,'layout_fields':lay.fields,
            'bits':bits,'fractional_bits':8,'initial_grid_quantum':16,'packet_bits':len(raw),
            'forward_output_sha256':output_sha,'forward_and_inverse':positive,
            'repair_boundary':{'K1_omission':'PASS exact small-domain boundary only',
                               'source_gate':gate,'source_axis':0,'local_target':'v1',
                               'K2_complete_records':repair_layout.records,'rho':1,'both_directions_restore':True},
            'rejected_controls':controls,'source_members':pins,
            'scope':'Complete finite actual f=2 Compact/leaf/return boundary; exact four-axis factor and arbitrary spectator implication. Small K=G=1 all-exception regime; no fast recursive callee, full supplier or new kappa.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',type=Path);args=parser.parse_args()
    if args.write and args.write.exists(): raise FileExistsError(args.write)
    saved=None if args.write else json.loads((HERE/'RESULT.json').read_text())
    receipt=result();text=encoded(receipt)
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as f: f.write(text)
    else: need(json.dumps(saved,sort_keys=True)==json.dumps(receipt,sort_keys=True),'complete receipt mismatch')
    print('PASS_SELECTED_COMPACT_CHILD_RETURN native_columns=512 tensor_columns=256 records=12288 repair_records=2048 controls=7')

if __name__=='__main__': main()
