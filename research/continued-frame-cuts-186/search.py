#!/usr/bin/env python3
"""Optional continued-frame discovery. Requires numpy; verification does not.

This searches from the already checked selected frame plan. It does not
replace the frozen witness or regenerate any published certificate.
Prepared by huxint with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse,gzip,json,shutil,subprocess,sys,tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from verify import prepare


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--labels',type=int,default=100)
    p.add_argument('--lines',type=int,default=700)
    p.add_argument('--planes',type=int,default=700)
    p.add_argument('--rounds',type=int,default=2)
    p.add_argument('--seed',type=int,default=192)
    a=p.parse_args();out=a.output.resolve()
    if sys.flags.optimize:raise ValueError('Run without -O')
    try:import numpy
    except ImportError:raise SystemExit('Discovery requires numpy; install it in a virtual environment. The verifier uses only the standard library.')
    with tempfile.TemporaryDirectory(prefix='continued-cut-search-') as temporary:
        root=Path(temporary)/'source';package=prepare(root);selected=package/'selected/complex'
        base=root/'build/search-base';base.mkdir(parents=True)
        for source,target in (('graph','graph'),('frames','frames'),('word','selection'),('profile-before','record')):
            (base/(target+'.json')).write_bytes(gzip.decompress((selected/(source+'.json.gz')).read_bytes()))
        pairs=json.loads(gzip.decompress((selected/'physical-pairs.json.gz').read_bytes()))
        (base/'input-pairs.json').write_text(json.dumps(dict(pairs=pairs))+'\n')
        scripts=root/'research/continued-cut-discovery';shutil.copytree(HERE/'discovery',scripts)
        command=[sys.executable,'-B',str(scripts/'lattice_cuts.py'),'--baseline',str(base),
                 '--frames',str(HERE/'selected/frames.json'),'--pairs',str(base/'input-pairs.json'),
                 '--output',str(out),'--labels',str(a.labels),'--lines',str(a.lines),'--planes',str(a.planes),
                 '--rounds',str(a.rounds),'--seed',str(a.seed)]
        subprocess.run(command,check=True)
    print('Discovery complete. The output still needs complete terminal and assembly admission.')


if __name__=='__main__':main()
