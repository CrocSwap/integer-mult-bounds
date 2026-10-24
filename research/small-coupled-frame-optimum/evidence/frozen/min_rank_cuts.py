#!/usr/bin/env python3
"""Separately authorized exact integer cut objectives on the frozen DP."""
import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
FROZEN='b1536a86967312bb8c9da7b177dacd54093bea71462bbbfeffdf7325260d96bc'

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path)
    p.add_argument('--output-dir',type=Path,default=HERE/'cuts-normal');args=p.parse_args()
    need=HERE/'optimize.py'
    if hashlib.sha256(need.read_bytes()).hexdigest()!=FROZEN:raise ValueError('Frozen fixed-C implementation changed')
    spec=importlib.util.spec_from_file_location('frozen_small_frame_dp',need)
    dp=importlib.util.module_from_spec(spec);spec.loader.exec_module(dp)
    args.output_dir.mkdir(exist_ok=True)
    summary={'status':'PASS_ALL_EIGHT_SOURCE_CUT_MINIMA','scope':'Same18smallcomponents/68variables; large1271at source; no Pareto search','objectives':{},'fixed_c_script_sha256':FROZEN}
    for k in range(1,9):
        class IntegerPrice:
            def __init__(self):
                self.n=0;self.refinements=0;self.comparisons=0;self.certificates=[];self.cache={}
            def prepare(self):self.bounds={r:(Q(min(r,k)),Q(min(r,k)))for r in range(10)}
            def interval(self,h):
                x=Q(sum(n*min(r,k)for r,n in enumerate(h)))
                return x,x
            def compare(self,a,b):
                if a==b:return 0
                diff=dp.sub(a,b)
                if diff in self.cache:return self.cache[diff]
                self.comparisons+=1;x=self.interval(diff)[0];s=(x>0)-(x<0)
                self.cache[diff]=s;self.cache[tuple(-v for v in diff)]=-s
                self.certificates.append({'difference_histogram':list(diff),'integer_difference':int(x),'sign':s})
                return s
        dp.Price=IntegerPrice
        output=args.output_dir/f'CUT-{k}.json'
        sys.argv=[str(need),'--output',str(output)]
        if args.source_root:sys.argv+=['--source-root',str(args.source_root)]
        dp.main()
        result=json.loads(output.read_text())
        result['objective']={'name':'min_rank_cut','k':k,'exact_integer_weights':[min(r,k)for r in range(10)]}
        result.pop('C');result['driver_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        result['comparison']['method']='Exact integer min-rank-cut weighted histogram comparison; distinct histograms may tie exactly'
        rows={}
        for d,entry in result['directions'].items():
            old=sum(n*min(r,k)for r,n in enumerate(entry['original_histogram']))
            new=sum(n*min(r,k)for r,n in enumerate(entry['optimal_full_histogram']))
            rows[d]={'source':old,'minimum':new,'changed_nodes':entry['changed_nodes'],'bucket_states':entry['bucket_states']}
            if new<old:summary['status']='STOP_LOWER_CUT_FOUND_NO_ALL_CONCAVE_CEILING'
            if new>old:raise ValueError('Source fallback failed')
        output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        summary['objectives'][str(k)]={'directions':rows,'receipt_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
        print(json.dumps({'cut':k,'directions':rows,'status':summary['status']}),flush=True)
        if summary['status']!='PASS_ALL_EIGHT_SOURCE_CUT_MINIMA':break
    (args.output_dir/'SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
