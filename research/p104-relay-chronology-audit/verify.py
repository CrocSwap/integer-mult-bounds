"""Source-bound replay with semantic controls and typed receipts."""
from pathlib import Path
import argparse
import copy
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import audit
import independent


def rejection(function,label):
    try:
        function()
    except ValueError:
        return label
    raise ValueError('accepted control: '+label)


def controls(base,word,C,records):
    result=[]
    def mutate(label,action):
        changed=copy.deepcopy(word)
        action(changed)
        result.append(rejection(lambda:audit.replay(base,changed,C),label))
    def flip_read(changed):
        op=next(o for o in changed['ops'] if o[0]=='read')
        op[3]=str(-audit.Q(op[3]))
    mutate('source_coefficient',flip_read)
    mutate('missing_dirty_compensation',lambda w:w['ops'].pop(1))
    def remove_return(changed):
        index=max(i for i,o in enumerate(changed['ops']) if o[0]=='read')
        changed['ops'].pop(index)
    mutate('missing_helper_cleanup',remove_return)
    def early_write(changed):
        op=next(o for o in changed['ops'] if o[0]=='write' and o[4]==len(base['program']))
        op[4]=0
    mutate('early_target_write',early_write)
    def wrong_frame(changed):
        op=next(o for o in changed['ops'] if o[0]=='move')
        op[2]=[]
    mutate('nonincreasing_move',wrong_frame)
    mutate('lifetime_header',lambda w:w.__setitem__('lifetimes',w['lifetimes']+1))
    broken=copy.deepcopy(base)
    op=next(o for o in broken['program'] if o[0]=='add')
    op[3]=str(-audit.Q(op[3]))
    result.append(rejection(lambda:audit.replay(broken,word,C),'original_channel_coefficient'))
    wrong=copy.deepcopy(records)
    wrong[0]['forced_targets']=[]
    result.append(rejection(lambda:independent.check_floor(base,wrong),'omitted_line_forced_demands'))
    # The global line-only premise is genuinely false, despite the repaired floor.
    audit.require(sum(len(r['later_targets']) for r in records)==336,'later-read countercontrol')
    result.append('336_valid_later_reads_preserved')
    return result


def run():
    base,fixture,word=audit.load()
    C=audit.correction(fixture)
    receipt=audit.replay(base,word,C)
    historical=json.loads((HERE/'inputs/WORD.json').read_bytes())
    old=audit.replay(base,historical,C)
    old_independent=independent.check(base,historical)
    receipt['word_variant']='relay-v2 fac9e821d31bc199b49e8ed463074a50d1264311'
    receipt['historical_v1']={'boundary_inputs':old['boundary_inputs'],'endpoint_coefficients':old['endpoint_coefficients'],
        'total_events':old['total_events'],'new_helpers':old['new_helpers'],'combined_rank_mass':old['combined_rank_mass'],
        'endpoint_sha256':old['endpoint_sha256'],'independent_column_sha256':old_independent['column_sha256']}
    records=audit.floor_certificate(base,C)
    retained=json.loads((HERE/'LINE-WITNESS.json').read_bytes())
    audit.require(audit.canonical(records)==audit.canonical(retained),'complete line witness regeneration')
    receipt.update(status='PASS_P104_RELAY_CHRONOLOGY_AUDIT',independent=independent.check(base,word),
                   line_floor=independent.check_floor(base,records),controls=controls(base,word,C,records),
                   line_witness_sha256=__import__('hashlib').sha256(audit.canonical(records)).hexdigest(),
                   limits='Independent finite logical/frame audit and written line-departure proof. Eight inherited nonzero private erasures remain. No new native/hosting/precision/supplier/kappa or unrestricted merge-loss identity.')
    return receipt


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.out:audit.require(not args.out.exists(),'output already exists')
    receipt=run()
    if args.out:
        with args.out.open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    else:
        audit.require(audit.canonical(receipt)==audit.canonical(json.loads((HERE/'RESULT.json').read_bytes())),'typed receipt mismatch')
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
