"""Actual producer + canonical parity arithmetic on heterogeneous dirty tags."""
from pathlib import Path
from random import Random
import argparse,json
from pi_exact import Gaussian as G
from mixed_center_adapter import producer_at_grid,decode_at_grid
from verify_mixed_center_image import read_dag,check_image


def main():
    if not __debug__: raise RuntimeError('run this exact audit without Python -O')
    ap=argparse.ArgumentParser();ap.add_argument('--dag',type=Path,required=True)
    a=ap.parse_args();g=read_dag(a.dag);roles,triples,_=check_image(g,19)
    rng=Random(45046);cases=[]
    for trial in range(2):
        xs=[G(rng.randint(-11,11),rng.randint(-11,11),rng.randrange(8)) for _ in triples]
        dirty=[G(rng.randint(-127,127),rng.randint(-127,127),rng.randrange(12))
               for _ in range(g['q'])]
        e=max(z.exponent for z in xs+dirty)
        produced=producer_at_grid(g,xs,grid_tag=e)
        updated=[z+w for z,w in zip(dirty,produced)]
        got=decode_at_grid(g,dirty,updated,roles,triples,28,19,grid_tag=e)
        assert got==xs
        assert [z-w for z,w in zip(updated,producer_at_grid(g,got,grid_tag=e))]==dirty
        assert all(z.fractions()==w.fractions() for z,w in zip(got,xs))
        cases.append(dict(trial=trial,source_values=len(xs),dirty_ports=len(dirty),
                          common_pi_grid=e,literal_canonical_restore=True))
    print(json.dumps(dict(status='passed',cases=cases,
        scope='actual common-frame scalar producer/decoder with canonical heterogeneous Gaussian tags'),indent=2))


if __name__=='__main__': main()
