"""Closed source-bound replay. @woklerx with OpenAI Codex, Apache-2.0."""
import argparse,gzip,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from engine import HERE,canonical,compute,require

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true');p.add_argument('--output',type=Path)
    a=p.parse_args();result,programs=compute()
    if a.write:
        (HERE/'CERTIFICATE.json').write_bytes(canonical(result)+b'\n')
        (HERE/'CANDIDATE-PROGRAMS.json.gz').write_bytes(gzip.compress(canonical(programs),mtime=0))
    else:
        require(canonical(result)==canonical(json.loads((HERE/'CERTIFICATE.json').read_bytes())),'certificate mismatch')
        require(canonical(programs)==canonical(json.loads(gzip.decompress((HERE/'CANDIDATE-PROGRAMS.json.gz').read_bytes()))),'candidate programs mismatch')
    if a.output:a.output.write_bytes(canonical(result)+b'\n')
    print(result['status'])
    for direction,row in result['orientations'].items():
        print(direction,'eligible',len(result['helpers']),'winner',row['winner']['helper'],row['winner']['best_k'],'saving',row['prices']['copy-init']['saving_complex'],'complex primitives')
if __name__=='__main__':main()
