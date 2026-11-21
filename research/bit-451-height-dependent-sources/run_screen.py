#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Supervise one fixed child with a hard 45s wall and a 15s receipt reserve."""
from argparse import ArgumentParser
from datetime import datetime,timezone
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import signal
import subprocess
import sys
import time

INDEPENDENT='f91280ef454af5d74559788e7f63fd442d8778937c52575160be2718354defcd'
SIGNED='148a6315592977093c90de293ca3a904da5cf8dd2fa7840d3a23538d1a87857b'


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


def source(path, pin):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=pin:
        raise ValueError('receipt hash: '+path.name)
    return json.loads(raw)


def verify(data,root):
    independent=root/'round342/independent'
    old=source(independent/'receipt.json',INDEPENDENT)
    bound=source(independent/'outer-verified.json',SIGNED)
    if not (data['small_x']['newton_ratios']==old['left_ratios'] and
            data['large_x_tail']['newton_ratios']==old['tail_ratios'] and
            [(x['G'],F(x['ratio'])) for x in data['large_x_prefix']]==
            [(x['g'],F(x['ratio'])) for x in old['finite']]):
        raise ValueError('different tested height or coefficient')
    price=data['price']; signed=bound['signed']
    for here,there in [('cap','cap'),('claim','candidate_grid_claim'),('tested','candidate_tested')]:
        if F(price[here])!=F(old[there]) or F(price[here])!=F(signed[here]):
            raise ValueError('wrong independent/signed '+here)
    if price['J']!=old['uniform_J'] or F(price['separation'])!=F(old['separation']):
        raise ValueError('different complete comparison')
    if [F(s[0]) for s in price['stages']]!=list(map(F,old['stages'])):
        raise ValueError('different strict stages')
    return {'round342/independent/receipt.json':INDEPENDENT,'round342/independent/outer-verified.json':SIGNED}


def main():
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--campaign-root',type=Path,required=True)
    cli.add_argument('--out',type=Path,required=True)
    args=cli.parse_args()
    if args.out.exists():
        raise SystemExit('Use a fresh destination, the existing receipt is sealed.')
    with TemporaryDirectory() as tmp:
        partial=Path(tmp)/'child.json'
        child=Path(__file__).resolve().with_name('screen.py')
        start=time.monotonic(); started_utc=utc()
        proc=subprocess.Popen([sys.executable,'-IB',str(child),'--campaign-root',str(args.campaign_root),
                               '--snapshot',str(partial)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              text=True,start_new_session=True)
        killed=False
        try:
            text,_=proc.communicate(timeout=max(0,45-(time.monotonic()-start)))
        except subprocess.TimeoutExpired:
            killed=True
            try:
                os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError:
                pass
            text,_=proc.communicate()
        elapsed=time.monotonic()-start; verification_utc=utc()
        data=json.loads(partial.read_bytes()) if partial.is_file() else {'events':[]}
        data['supervisor']={'start_utc':started_utc,'verification_utc':verification_utc,'deadline_seconds':45,
                            'reserve_seconds':15,'child_exit':proc.returncode,'killed':killed,'child_wall_seconds':elapsed,
                            'child_output':text[-2048:],'screen_sha256':sha256(child.read_bytes()).hexdigest()}
        if killed or elapsed>45:
            data['decision']='CAPPED_UNRESOLVED'
        elif proc.returncode!=0 or data.get('decision')=='RUNNING':
            data['decision']='CHILD_ERROR_UNRESOLVED'
        elif data.get('decision')=='ADVANCE_ONE_SIGNED_REPLAY':
            try:
                data['independent_match']=verify(data,args.campaign_root)
                data['decision']='PRIMARY_AND_INDEPENDENT_SIGNED_REPLAY_MATCH'
            except (ValueError,KeyError) as e:
                data.update(decision='MISMATCH_OR_UNRESOLVED',reason=str(e))
        data['supervisor']['receipt_utc']=utc()
        data['supervisor']['total_wall_seconds']=time.monotonic()-start
        if data['supervisor']['total_wall_seconds']>60:
            data['decision']='CAPPED_UNRESOLVED'
        args.out.write_text(json.dumps(data,indent=2)+'\n')
        print(data['decision'],data.get('reason',''),round(elapsed,4))


if __name__=='__main__':
    main()
