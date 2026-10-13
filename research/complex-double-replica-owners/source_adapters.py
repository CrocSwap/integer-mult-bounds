"""Materialize narrowly parameterized derivatives of the pinned PR799 checkers.

Apache-2.0. Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance.
The existing code and its contributor notices are retained. The explicit edits
below change only replication-dependent cardinalities and the associated bill.
Unchanged legality, scalar, phase, normalization and admission guards still run.
"""
from pathlib import Path
import hashlib, json, shutil

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'gauge44-frames-x'

# Every replacement is exact, and its multiplicity is asserted. This makes the
# full difference inspectable without vendoring the complete ancestry again.
EDITS = {
 'emit_allcold.py': [
  ('==72', '==144', 3),
  (';T=8;', ';T=16;', 1),
  ('==2560', '==5120', 1),
  ('deficit=2560', 'deficit=5120', 1),
 ],
 'audit_allcold.py': [
  (';T=8;', ';T=16;', 1),
  ('CALLS=72', 'CALLS=144', 1),
  ('==72', '==144', 3),
  ('range(8)', 'range(16)', 2),
  ('0<=r<8', '0<=r<16', 1),
  ("0<=e['time']<72", "0<=e['time']<144", 1),
  ('==2560', '==5120', 1),
  ('deficit=2560', 'deficit=5120', 2),
  ('invocations=72', 'invocations=144', 1),
 ],
 'invoice_allcold.py': [
  ('stages,replicas,blocks_per_stream=9,8,4', 'stages,replicas,blocks_per_stream=9,16,4', 1),
  ("owners['deficit']==2560", "owners['deficit']==5120", 1),
  ('all 72 invocation and 72 bridge sweeps', 'all 144 invocation and 144 bridge sweeps', 1),
 ],
 'assemble.py': [
  ("owner['hosted_residuals']==72*R", "owner['hosted_residuals']==144*R", 1),
  ("invoice['bridge_sweeps']==72", "invoice['bridge_sweeps']==144", 1),
  ('data_and_owner_families=7168', 'data_and_owner_families=14336', 1),
  ('len(calls)==72', 'len(calls)==144', 1),
  ('for r in range(8)', 'for r in range(16)', 1),
  ('parent_live,parent_physical,parent_idle=11704,12218,16128',
   'parent_live,parent_physical,parent_idle=23408,23922,32256', 1),
  ('parent_live-2*112*4*8', 'parent_live-2*112*4*16', 1),
  ('parent_physical==parent_live+parent_banks+8+2', 'parent_physical==parent_live+504+8+2', 1),
  ('bridges,shifts=2*112*72,4*112*8', 'bridges,shifts=2*112*144,4*112*16', 1),
  ('4*112*8*9+2*112*8*9+2*72*R', '4*112*16*9+2*112*16*9+2*144*R', 1),
  ("(72*invoice['local_adapters']", "(144*invoice['local_adapters']", 1),
  ('+37+72+72+4', '+37+144+144+4', 1),
  ("owner['deficit']==2560", "owner['deficit']==5120", 1),
  (',conservative_b,2560,True)', ',conservative_b,5120,True)', 1),
  (',b,2560,False)', ',b,5120,False)', 1),
  ('explicit all72 whole-owner dispatch', 'explicit all144 whole-owner dispatch with a two-copy remainder trade', 1),
  ('44 cold dimension-four ends', 'the accepted PR799 X4 local word and all 72 cold helper ends', 1),
  ('this bit composition is unreviewed.', 'This is a new T16 composition of the accepted PR799 and PR589 suppliers.', 1),
  ('# parent R0=504 dedicated helpers per stage bank', '# two independent bank groups, each with R0=504 helpers; restored private workspace is shared', 1),
 ],
 'assembly_controls.py': [
  ('1 + 37 + 72 + 72 + 4', '1 + 37 + 144 + 144 + 4', 1),
 ],
}

def materialize(out):
    """Write fresh code/ and inputs/; SOURCE-PINS binds every consumed byte."""
    if not __debug__:
        raise RuntimeError('Source adaptation requires enabled assertions')
    out=Path(out); assert not out.exists(), 'runtime output must be new'
    pins=json.loads((HERE/'SOURCE-PINS.json').read_text())
    for rel, expected in pins.items():
        assert hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()==expected, ('source pin',rel)
    (out/'code').mkdir(parents=True)
    result={}
    for path in sorted((SOURCE/'code').glob('*.py')):
        assert 'code/'+path.name in pins, ('unbound source',path.name)
        raw=path.read_text()
        for old,new,count in EDITS.get(path.name,[]):
            assert raw.count(old)==count, ('exact edit count',path.name,old,raw.count(old),count)
            raw=raw.replace(old,new)
        target=out/'code'/path.name;target.write_text(raw)
        result[path.name]={'source_sha256':pins['code/'+path.name],
                           'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                           'edits':EDITS.get(path.name,[])}
    (out/'inputs').mkdir()
    shutil.copyfile(SOURCE/'inputs/PR589-EXPECTED.json',out/'inputs/PR589-EXPECTED.json')
    (out/'ADAPTERS.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    import sys
    materialize(sys.argv[1])
