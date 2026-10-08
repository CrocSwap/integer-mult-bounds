"""Regenerate accepted words from byte-pinned discovery fixtures."""
from pathlib import Path
import argparse,gzip,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--upstream',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    upstream=a.upstream.resolve();work=a.work.resolve();work.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((PACKAGE/'manifest.json').read_text(encoding='utf-8'))
    for rel,digest in manifest['files'].items():
        if rel.startswith('discovery/') and rel.endswith(('.gz','.py')):
            assert hashlib.sha256((PACKAGE/rel).read_bytes()).hexdigest()==digest,rel
    runners=list(HERE.glob('runner-*.py'));assert len(runners)==1
    text=runners[0].read_text(encoding='utf-8')
    original="FROZEN=HERE.parents[1]/'matrix-synthesis/bridge/pr62'"
    assert text.count(original)==1
    text=text.replace(original,'FROZEN=Path('+repr(str(upstream))+')')
    original_new="new=\"ROOT=Path(__file__).resolve().parents[2]/'matrix-synthesis/bridge/pr62/references/frame-compiler/pr48'\""
    assert text.count(original_new)==1
    new_root='ROOT=Path('+repr(str(upstream/'references/frame-compiler/pr48'))+')'
    text=text.replace(original_new,'new='+repr(new_root))
    runner=work/'run_strategy.py';runner.write_text(text,encoding='utf-8',newline='\n')
    for h in (23,25):
        (work/f'matching-h{h}.json').write_bytes(gzip.decompress((HERE/f'matching-h{h}.json.gz').read_bytes()))
        oracle=list(HERE.glob(f'pair-profiles-h{h}-*.jsonl.gz'));assert len(oracle)==1
        (work/f'pair-profiles-h{h}.jsonl').write_bytes(gzip.decompress(oracle[0].read_bytes()))
        subprocess.run([sys.executable,str(runner),'--h',str(h),'--strategy','profile_cost4_repro','--exchange'],check=True)
        generated=work/'profile_cost4_repro_exchange'/f'h{h}'/'word.json.gz'
        expected=PACKAGE/'words'/f'word-{h}.json.gz'
        assert gzip.decompress(generated.read_bytes())==gzip.decompress(expected.read_bytes()),f'h{h} raw word differs'
        assert generated.read_bytes()==expected.read_bytes(),f'h{h} deterministic gzip differs'
        print('PASS exact regeneration axis',h,flush=True)

if __name__=='__main__':main()
