"""Derive a fresh immutable source for the two staged paired entrances.

The complete predecessor source is authenticated, then its literal producer
chain is extended. Earlier declared-edit checks retain their exact predecessor
word; the new word receives its own deterministic stage and arbitrary-input
audit with semantic defect controls. No tracked repository source is changed.
"""
import argparse
from pathlib import Path
import gzip,hashlib,json,shutil,sys,types
sys.dont_write_bytecode=True
OLD_MANIFEST='fa3e2d855ac5298ecc849e596d79dcef7a72668a276b6524585bc0cd616ce474'
def need(x,s):
    if not x:raise AssertionError(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def tree(p):
    z={}
    for f in sorted(p.rglob('*')):
        need(not f.is_symlink(),'regular source')
        if f.is_file() and f!=p/'MANIFEST.json':z[f.relative_to(p).as_posix()]=sha(f)
    return z
def replace(path,a,b):
    s=path.read_text();need(s.count(a)==1,'one exact preimage '+str(path)+' '+a[:70]);path.write_text(s.replace(a,b))
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('source','pair','review','out'):ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args();OLD=args.source.resolve();out=args.out.resolve();pair=args.pair.resolve();review=args.review.resolve()
    need(not out.exists() and not out.is_relative_to(OLD) and not OLD.is_relative_to(out),'fresh disjoint source output')
    need(not out.is_relative_to(pair),'output outside declared pair input')
    receipt=out.parent/(out.name+'-DERIVATION.json')
    need(not receipt.exists(),'fresh derivation receipt')
    need(sha(OLD/'MANIFEST.json')==OLD_MANIFEST and tree(OLD)==read(OLD/'MANIFEST.json'),'complete pinned predecessor')
    shutil.copytree(OLD,out);borrow=out/'new/borrow'
    need(sha(pair/'staged_pair.py')=='25fc9b025dbb90358032013303adea650a5f19937fd3edf30b6c6fd023e2d747','exact declared producer')
    producer=types.ModuleType('exact_staged_pair');producer.__file__=str(pair/'staged_pair.py')
    exec(compile((pair/'staged_pair.py').read_bytes(),producer.__file__,'exec'),producer.__dict__)
    shutil.copy2(pair/'staged_pair.py',borrow/'staged_pair.py')
    records={};providers=read(out/'new/BORROW-PROVIDERS.json')
    for tag,pid in [('base','gauge44'),('extra','extra')]:
        word=borrow/f'words/BORROW-WORD-43{tag}.json.gz'
        predecessor=borrow/f'inputs/PR3133-FINAL-{tag}.json.gz';shutil.copy2(word,predecessor)
        rec=pair/f'STAGED-PAIR-RECORD-{tag}.json.gz'
        need(producer.apply(read(word),read(rec))==read(pair/f'STAGED644-660-{tag}.json.gz'),'fresh exact declared staged word '+tag)
        shutil.copy2(rec,borrow/f'inputs/STAGED-PAIR-RECORD-{tag}.json.gz')
        shutil.copy2(pair/f'STAGED644-660-{tag}.json.gz',word)
        r=read(rec);need(sha(predecessor)==r['source_compressed_sha256'] and sha(word)==r['target_compressed_sha256'],'literal source and target pins')
        w=read(word);remain=sorted(set(range(224,704))-set(w['removed']))
        providers[pid]['widths']=[len(w['helper_final'].get(str(h),range(9)))-len(w['start_extra'].get(str(h),[])) for h in remain]
        providers[pid]['actual_paid_profile']=w['report']['local_profile']
        need(len(remain)==408 and len(w['helper_final'])==91,'unchanged helper/private ABI')
        records[tag]=dict(source=sha(predecessor),target=sha(word),recipe=sha(rec))
    save(out/'new/BORROW-PROVIDERS.json',providers)
    anchor="    final=json.loads(gzip.decompress(shipped.read_bytes()))"
    block="""    # Exact staged incoming pair, after the complete PR3133 edit stage.
    import staged_pair
    staged_parent=json.loads(gzip.decompress((D/'inputs'/f'PR3133-FINAL-{wt}.json.gz').read_bytes()))
    assert chain[-1]==staged_parent
    staged_record=json.loads(gzip.decompress((D/'inputs'/f'STAGED-PAIR-RECORD-{wt}.json.gz').read_bytes()))
    chain.append(staged_pair.apply(chain[-1],staged_record));steps.append('staged-incoming-pair644-660')
"""
    replace(out/'new/rebuild_borrow.py',anchor,block+anchor)
    verify=out/'verify.py';s=verify.read_text();line=next(z for z in s.splitlines() if z.startswith("run('declared-edit-review'"))
    predecessor_line=line.replace("P/'new/borrow/words/BORROW-WORD-43base.json.gz'","P/'new/borrow/inputs/PR3133-FINAL-base.json.gz'").replace("P/'new/borrow/words/BORROW-WORD-43extra.json.gz'","P/'new/borrow/inputs/PR3133-FINAL-extra.json.gz'")
    need(line!=predecessor_line,'earlier stage candidate paths rebound to exact predecessor')
    extra="run('staged-pair-independent-audit',P/'new/borrow/staged_pair_review.py','--borrow',P/'new/borrow','--out',work/'staged-pair-independent-audit')"
    verify.write_text(s.replace(line,predecessor_line+'\n'+extra))
    shutil.copy2(review,borrow/'staged_pair_review.py')
    after=tree(out);before=tree(OLD);changes={n:dict(before=before.get(n),after=after.get(n)) for n in set(after)|set(before) if after.get(n)!=before.get(n)}
    expected={'new/BORROW-PROVIDERS.json','new/rebuild_borrow.py','verify.py','new/borrow/staged_pair.py','new/borrow/staged_pair_review.py'}
    for tag in ['base','extra']:expected|={f'new/borrow/words/BORROW-WORD-43{tag}.json.gz',f'new/borrow/inputs/PR3133-FINAL-{tag}.json.gz',f'new/borrow/inputs/STAGED-PAIR-RECORD-{tag}.json.gz'}
    need(set(changes)==expected and tree(OLD)==before,'exact changed source footprint; predecessor preserved')
    save(out/'MANIFEST.json',after)
    save(receipt,dict(status='PASS_EXACT_STAGED_PAIR_SOURCE_OVERLAY',parent_manifest_sha256=OLD_MANIFEST,
        manifest_sha256=sha(out/'MANIFEST.json'),source_file_count=len(after),source_commit='staged-pair644-660-on-pr3133',
        changes=changes,word_bindings=records,builder_sha256=sha(Path(__file__)),
        scope='Deterministic new producer stage and retained predecessor checks; native/owner/physical/prefix/outer admission remains separate.'))
    print('PASS_EXACT_STAGED_PAIR_SOURCE_OVERLAY',sha(out/'MANIFEST.json'),len(after),flush=True)
if __name__=='__main__':main()
