"""Real coefficient closures, complete small ADD controls, actual symbolic extents."""
import argparse
import json
from pathlib import Path
import sys
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parent))
from binding import loaded, need, consumer_coefficient, action
from census import observed
from fixtures import fixture, saved, preserved
from ledger import bound


def value(count):
    digits=[]
    for symbol in count.tape.cells[1:]:
        if symbol == 3:
            break
        need(symbol in (0,1),'encoded count digits')
        digits.append(symbol)
    return sum(x<<i for i,x in enumerate(digits))


def expected(data, modulus, coefficient):
    result=[None]*len(data)
    for index,bit in enumerate(data):
        x,y=divmod(index,modulus)
        result[x*modulus+(y+coefficient*x)%modulus]=bit
    return result


def case_run(m,data,branch='adapter-good',warm=(0,0),quota=None):
    case=fixture(m,branch=branch,rank=1,depth=2,modulus=9,warm=warm)
    # Compile the actual dimension64 plan instead of the predecessor's summary.
    case.plan=m.plan.compile_plan(case.low,1,3,case.good)
    closure,digest=consumer_coefficient(m,data,case)
    calls=[]
    with observed(m,(case.r,case.ix)) as census:
        for tape in (case.program.tape,case.fields.tape):
            census.tapes[id(tape)]=tape
            census.categories[id(tape)]='entry'
        one=case.ix.literal(1)
        depth=case.ix.literal(2)
        parent=case.ix.literal(64)
        geometry=m.numeric.Geometry(case.plan,case.ix,one,depth,case.code,case.program)
        trace=m.trace.execute(geometry)
        first=next(trace)
        need((first.kind,first.first.inspect(),first.second.inspect())==('add',1,0),'actual first generated adapter ADD')
        if branch!='adapter-good':
            while first.kind!='add' or first.request.kind!='child':
                first=next(trace)
        request=first.request
        positions=(first.first.inspect(),first.second.inspect())
        spectators=[m.cardinal_counts.Count.literal(1) for _ in range(3)]
        actual_layout=m.layout.Layout(geometry,parent,case.ring,3,*spectators)
        actual_extents=actual_layout.extents(first.second,first.first)
        actual_values=tuple(value(x) for x in actual_extents)
        wanted=(1,1,9**126) if branch=='adapter-good' else (1,9**126,1)
        need(actual_values==wanted,'actual64dim complete spectator extent')
        for x in actual_extents:x.close()
        del actual_extents,x
        actual_layout.close()
        # Complete2atom component calibration, not the actual128atom packet.
        small_geometry=m.numeric.Geometry(SimpleNamespace(dimension=1),case.ix,one,depth,case.code,case.program)
        small_parent=case.ix.literal(1)
        layout=m.layout.Layout(small_geometry,small_parent,case.ring,3,*spectators)
        source=m.records.Tape()
        bits=[(i*7+i//3+1)%2 for i in range(81)]
        for bit in bits:source.append(bit)
        source.rewind()
        component_target,component_source=case.ix.literal(1),case.ix.literal(0)
        before=saved(case)
        histories=[len(case.r.words),len(case.ix.words)]
        lives=[len(case.r.live),len(case.ix.live)]
        allowance=bound((1,1,1),9,2,case.program.code_bits,len(case.program.tape.cells),
                        histories,lives,(case.r.bits,case.ix.bits),branch!='adapter-good')
        census.start()
        census.quota=quota
        census.phase='preparation'
        def coefficient(reference):
            census.phase='callback'
            out=closure(case.fields.tape,reference)
            calls.append(out.inspect())
            census.observe()
            census.phase='traversal'
            return out
        # Component-only coordinate map; the actual generated event stays separate.
        event=SimpleNamespace(kind='add',first=component_target,second=component_source,request=request)
        output=action(m,data)(source,event,layout,coefficient)
        census.phase='returned'
        census.observe()
        need(calls==[case.expected]*2,'two real coefficient returns')
        need(list(output.cells[1:])==expected(bits,9,case.expected),'complete independent ADD permutation')
        preserved(case,before)
        need(source.head==1 and all(t.tape.head==1 for t in spectators),'borrowed source/count heads')
        for identity,(_,snapshot) in census.baseline.items():
            need(bytes(census.tapes[identity].cells)==snapshot,'borrowed array bytes')
        private=[t for identity,t in census.tapes.items() if identity not in census.baseline]
        need(private==[output],'all new record/count/bucket arrays released except owned output')
        need(census.peak<=census.baseline_cells+allowance['extra'],'complete source-cell envelope')
        need(census.record_peak<=allowance['record_allowance'],'complete record envelope')
        result={'branch':branch,'warm':list(warm),'component_bits':81,'actual_packet_bits':str(9**128),
                'actual_extents':[str(x) for x in actual_values],'actual_generated_command':list(positions),
                'closure_ast_sha256':digest,'calls':calls,'entry_cells':census.baseline_cells,
                'peak_cells':census.peak,'extra_peak':census.peak-census.baseline_cells,
                'record_peak':census.record_peak,'phases':census.phases,'allowance':allowance,
                'slots':[len(case.r.words),len(case.ix.words)]}
        census.active=False
        output.clear();source.clear();layout.close();small_geometry.close()
        trace.close();geometry.close()
        for x in spectators:x.close()
    return result


def run():
    with loaded() as (m,data):
        rows=[case_run(m,data),case_run(m,data,warm=(40000,64)),case_run(m,data,'child-good')]
        need(rows[1]['peak_cells']>rows[0]['peak_cells'],'warm erased history remains charged')
        need(rows[2]['record_peak']>rows[0]['allowance']['record_allowance'],
             'four-stack-only bound rejects actual child extension')
        need(rows[2]['record_peak'] > rows[2]['allowance']['record_allowance']
             - rows[2]['allowance']['extended_program_bound'],
             'omitting extended Program rejects actual record peak')
        # The complete successful ledger is measured independently of the bound.
        try:
            case_run(m,data,quota=rows[0]['peak_cells']-1)
        except RuntimeError as error:
            need(str(error)=='complete backing quota','only intended quota failure accepted')
        else:
            raise RuntimeError('one-cell-short total quota accepted')
        return {'status':'PASS_COMPLETE_ADD_SOURCE_BACKING','cases':rows,
                'omitted_extended_program_rejected':True,'child_four_stack_only_bound_rejected':True,'one_cell_short_rejected':True,'full_gl64_payload_executed':False,
                'physical_supplier_admitted':False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--emit',action='store_true');args=parser.parse_args()
    result=run()
    if not args.emit:
        stored=json.loads((Path(__file__).parent/'RESULT.json').read_text())
        need(json.dumps(result,sort_keys=True)==json.dumps(stored,sort_keys=True),'complete typed receipt')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
