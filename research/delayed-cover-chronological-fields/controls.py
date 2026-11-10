"""Literal program faults, with explicit semantic/ownership rejection gates."""
import producer as p
from check import fixture,need
from join_check import fixture as joined


def mutate(name):
    def change(program,meta):
        rows=list(program.instructions);ev=meta['events']
        if name=='skip_payload_move':
            at=ev['payload_advance'];need(rows[at]==('move',p.PAYLOAD,1),'actual payload move')
            rows[at]=('goto',at+1)
        elif name=='stop_field_carry':
            at=ev['field_carry'];op,tape,pairs,default=rows[at];targets=dict(pairs)
            targets[p.Z]=targets[p.O]=targets[p.RIGHT]
            rows[at]=(op,tape,tuple(sorted(targets.items())),default)
        elif name=='skip_prefix_erasure': rows[ev['prefix_clear']]=('goto',ev['fibre_begin'])
        elif name=='skip_state_retirement': rows[ev['state_retire']]=('goto',ev['state_retired'])
        elif name=='wrong_source_code':
            at=next(i for i,row in enumerate(rows) if row==('write',p.STATE,p.O))
            rows[at]=('write',p.STATE,p.Z)
        elif name=='early_halt': rows[ev['ready']]=('halt',)
        else: raise ValueError('known producer mutation')
        return p.m.Program(tuple(rows),program.tapes,program.entry)
    return change


def run():
    result=[]
    for name in ('skip_payload_move','stop_field_carry','skip_prefix_erasure',
                 'skip_state_retirement','wrong_source_code','early_halt'):
        try: fixture(dimension=1,codes=(1,0),width=2,fibre=3,program_override=mutate(name))
        except ValueError as error: result.append({'name':name,'detected':str(error)})
        else: raise ValueError('undetected literal fault: '+name)
    for name in ('skip_service','skip_code_pop','zero_call_label'):
        try: joined(width=2,depth=1,mutant=name)
        except ValueError as error: result.append({'name':name,'detected':str(error)})
        else: raise ValueError('undetected source-join fault: '+name)
    return result


if __name__=='__main__':
    import json
    print(json.dumps(run(),sort_keys=True))
