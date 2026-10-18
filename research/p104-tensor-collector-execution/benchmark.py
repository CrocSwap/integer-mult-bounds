"""Serial fresh-process same-input timings; not a pass/fail speed threshold."""
import argparse
import datetime
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lanes import need
from verify import stable


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--multiplicity',type=int,choices=[1,2],default=1)
    p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--timeout',type=int,default=600)
    args=p.parse_args()
    need(1 <= args.repeats <= 5 and 1 <= args.timeout <= 600, 'bounded benchmark')
    rows=[]
    reference=None
    for trial in range(args.repeats):
        for mode in (['original','packed'] if trial%2==0 else ['packed','original']):
            cmd=[sys.executable,'-I','-B',str(HERE/'run.py'),'--mode',mode,'--multiplicity',str(args.multiplicity)]
            started=time.perf_counter()
            try:
                proc=subprocess.run(cmd,capture_output=True,text=True,timeout=args.timeout,check=True)
            except subprocess.TimeoutExpired:
                rows.append(dict(trial=trial,mode=mode,completed=False,timeout_seconds=args.timeout,wall_seconds=time.perf_counter()-started))
                continue
            data=json.loads(proc.stdout)
            clean=stable(data)
            if reference is None:
                reference=clean
            need(clean==reference, 'same input, all endpoints and counts across benchmark processes')
            rows.append(dict(trial=trial,completed=True,wall_seconds=time.perf_counter()-started,**data))
    summaries={}
    for mode in ['original','packed']:
        complete=[row for row in rows if row['mode']==mode and row['completed']]
        if complete:
            summaries[mode]={key:statistics.median(row[key] for row in complete)
                             for key in ['wall_seconds','execution_seconds','oracle_check_seconds','peak_rss_kib']}
    print(json.dumps(dict(schema_version=1,recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                         python=sys.version,platform=platform.platform(),multiplicity=args.multiplicity,
                         repetitions=args.repeats,rows=rows,medians=summaries,receipt=reference,
                         scope='One shared host; fresh serial processes. Execution includes input packing and output unpacking. Wall time also includes authentication, fixture and independent oracle. No physical C-machine benchmark.'),indent=2,sort_keys=True))


if __name__=='__main__':
    main()
