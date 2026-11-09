"""Independent integer oracle and genuine unchanged native Count execution."""
from pathlib import Path
import itertools,json,math
from source_binding import opened,authenticate,need


def oracle(shape):
    axes=[range(s) for ell,s in shape]
    result=[]
    for reversed_j in itertools.product(*reversed(axes)):
        js=tuple(reversed(reversed_j)); address=0;stride=1
        for (ell,s),j in zip(shape,js):
            t=2**ell;address+=((2*t*j+s)//(2*s))*stride;stride*=t
        result.append(address)
    return result


def exact_checks():
    checks=0;wrong_floor=0
    for ell in range(2,9):
        t=2**ell
        for s in range(t//2+1,t):
            r=s;c=0
            for j in range(s):
                expected=(2*t*j+s)//(2*s)
                need(c==expected and 0<=r<2*s,'independent nearest-coordinate recurrence')
                wrong_floor+=int((t*j)//s!=expected);checks+=1
                r+=2*(t-s);c+=1
                if r>=2*s:r-=2*s;c+=1
            need(c==t and r==s,'complete period remainder')
    need(wrong_floor>0,'floor-without-nearest control detects omission')
    return dict(scalar_coordinates=checks,wrong_floor_detections=wrong_floor)


def main():
    binding=authenticate();exact=exact_checks();cases=[];controls=[]
    with opened() as state:
        from extractor import Extract
        from cardinal_counts import Count
        from records import Tape
        from gaussian_rationals import write_count
        from session import erase_marker,initialize_marker
        from words import BLANK
        B=state.B
        def snapshot(t):
            return tuple(t.cells),t.head
        def packet(shape):
            t=Tape();erase_marker(t);initialize_marker(t)
            values=(len(shape),*(value for pair in shape for value in pair))
            for value in values:
                x=Count.literal(value);write_count(x,t);x.close()
            t.rewind();return t
        expected_errors={'pending-return':'consume protected extraction return','output-alias':'distinct external framed field',
            'short-full-field':'complete framed payload bits','extra-full-field':'complete full padded input and compact output',
            'compact-is-not-full-T':'complete framed payload bits','non-bit':'complete framed payload bits',
            'missing-frame':'complete framed record separator','invalid-axis-admission':'strict original dyadic axis admission',
            'zero-source-period':'positive','descriptor-alias':'distinct prepared descriptor ports',
            'truncated-descriptor':'complete rational record digit'}
        def reject(call,label):
            try:call()
            except (ValueError,RuntimeError,AssertionError) as error:
                need(expected_errors[label] in str(error),'expected guard, not an internal cleanup failure: '+label+': '+str(error));controls.append(label)
            else:raise ValueError('missing negative control: '+label)
        q=Count.literal(5)
        for shape in (((2,3),),((2,3),(3,5)),((2,3),(3,7),(3,5))):
            desc=packet(shape);before=(snapshot(desc),snapshot(q.tape))
            owner=Extract(B,desc,q)
            total=2**sum(ell for ell,s in shape);size=math.prod(s for ell,s in shape)
            records=[format((a*109+13)%65536,'016b')+'#' for a in range(total)]
            source=B.Tape('full-target',''.join(records));B.home(source)
            expected=''.join(records[a] for a in oracle(shape))
            frozen=(snapshot(owner.meta),snapshot(owner.initial))
            result=owner.run(source);need(result.inspect()==expected,'actual native exact source-coordinate extraction')
            need((snapshot(desc),snapshot(q.tape))==before,'borrowed descriptor preservation')
            need((snapshot(owner.meta),snapshot(owner.initial))==frozen,'immutable prepared metadata')
            need(source.inspect()==''.join(records) and source._head==1,'full padded input preserved and restored')
            need(all(t.head==1 and all(v==BLANK for v in t.cells[1:]) for t in (owner.first,owner.second)),'active packed state completely erased')
            need(all(t.head==1 and all(v==BLANK for v in t.cells) for t in owner.pool.tapes),'all fixed scratch backing erased')
            reject(lambda:owner.run(source),'pending-return')
            owner.consume();need(owner.run(source).inspect()==expected,'reusable packed successor state');owner.consume()
            history=B.Tape('borrowed-historical-capacity','0'*(8*len(''.join(records))))
            B.clear(history)
            for symbol in ''.join(records):B.append(history,symbol)
            B.home(history)
            need(history.bill()['retained_cells']>4*len(''.join(records)),'historical backing is larger than live extent')
            need(owner.run(history).inspect()==expected and history.inspect()==''.join(records),'historical capacity preserves exact extraction')
            owner.consume()
            reject(lambda:owner.run(owner.output),'output-alias')
            reject(lambda:owner.run(B.Tape('short',''.join(records[:-1]))),'short-full-field')
            reject(lambda:owner.run(B.Tape('extra',''.join(records)+records[0])),'extra-full-field')
            reject(lambda:owner.run(B.Tape('compact',expected)),'compact-is-not-full-T')
            reject(lambda:owner.run(B.Tape('bad-bit','x'+''.join(records)[1:])),'non-bit')
            reject(lambda:owner.run(B.Tape('bad-frame',''.join(records).replace('#','0',1))),'missing-frame')
            need(owner.output.inspect()=='' and all(t.head==1 and all(v==BLANK for v in t.cells) for t in owner.pool.tapes),'failed returns erase output and all scratch')
            cases.append(dict(shape=shape,T=total,S=size,selected_addresses=oracle(shape),payload_actions=source.bill(),historical_input_bill=history.bill()))
            owner.close()
        for shape in (((2,4),),((3,3),)):
            reject(lambda:Extract(B,packet(shape),q),'invalid-axis-admission')
        reject(lambda:Extract(B,packet(((2,0),)),q),'zero-source-period')
        reject(lambda:Extract(B,q.tape,q),'descriptor-alias')
        truncated=Tape();erase_marker(truncated);initialize_marker(truncated)
        for value in (1,2):
            x=Count.literal(value);write_count(x,truncated);x.close()
        truncated.rewind();reject(lambda:Extract(B,truncated,q),'truncated-descriptor')
        # Independent controls alter source identity, never the submitted program.
        shape=((2,3),(3,5));right=oracle(shape)
        floor_addresses=[(4*j//3)+4*(8*k//5) for k in range(5) for j in range(3)]
        swapped=oracle(tuple(reversed(shape)))
        need(right!=floor_addresses and right!=swapped,'nearest convention and axis-order controls')
        need(right!=list(range(15)),'contiguous-pad removal cannot replace global original-q projection')
        controls+=['wrong-nearest-convention','wrong-axis-order','contiguous-padding-only']
        q.close()
    result=dict(status='PASS',binding_files=binding,exact=exact,native_cases=cases,negative_controls=controls,
        scope='Exact encoded projection only; no Gaussian/transform/CRT execution or new kappa.')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
