#!/usr/bin/env python3
"""Replay PR186, then check a new physical-frame plan and its complete assembly.

Standard-library Python. The scalar words, bit banks, aliases and terminal
compiler are retained with their original source pins and credits.
Prepared by huxint with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,copy,gzip,importlib.util,io,json,shutil,subprocess,sys,tempfile,time,zipfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE=ROOT/'research/coordinated-frames-and-entrance-banks'
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)


def require(ok,message):
    if not ok:raise ValueError(message)


def digest(path):return sha256(path.read_bytes()).hexdigest()


def manifest():
    files={p.relative_to(HERE).as_posix():digest(p) for p in sorted(HERE.rglob('*'))
           if p.is_file() and '__pycache__' not in p.parts and p.name not in ('SOURCE.json','certificate.json','RESULTS.md')}
    return dict(base_pr=186,base_commit='166a34d75e853e933855f0f7e940fe77c4bb6b8d',
                base_files_sha256=digest(BASE/'FILES.json'),base_archive_manifest_sha256=digest(BASE/'BASELINE.json'),
                files=files,assistance='huxint with substantial OpenAI Codex assistance')


def prepare(root):
    """Verify the immutable parent files and extract its pinned source closure."""
    meta=json.loads((BASE/'FILES.json').read_text())
    names={p.relative_to(BASE).as_posix() for p in BASE.rglob('*') if p.is_file() and p.name!='FILES.json'}
    require(names==set(meta['files']),'Parent upload inventory changed')
    require({n:digest(BASE/n) for n in names}==meta['files'],'Parent upload hashes changed')
    baseline=json.loads((BASE/'BASELINE.json').read_text());parts=[]
    for row in baseline['parts']:
        b=(BASE/row['file']).read_bytes()
        require(len(b)==row['bytes'] and sha256(b).hexdigest()==row['sha256'],'Parent archive part')
        parts.append(b)
    blob=b''.join(parts);require(sha256(blob).hexdigest()==baseline['archive_sha256'],'Parent archive hash')
    root.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for entry in z.infolist():require((root/entry.filename).resolve().is_relative_to(root.resolve()),'Archive path')
        z.extractall(root)
    package=root/'research/coordinated-frames-and-entrance-banks'
    excluded={x['file'] for x in baseline['parts']}
    for p in BASE.rglob('*'):
        if p.is_file() and p.name not in excluded:
            out=package/p.relative_to(BASE);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
    return package


def run(script,*args,output=None):
    result=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],text=True,capture_output=True)
    require(result.returncode==0,str(script.name)+' rejected the construction:\n'+result.stdout+result.stderr)
    return json.loads(output.read_text()) if output is not None else result.stdout


def write_gzip(path,value):
    b=gzip.compress((json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    path.write_bytes(b[:9]+b'\xff'+b[10:])


def verify():
    require(not sys.flags.optimize,'Run without -O')
    require(json.loads((HERE/'SOURCE.json').read_text())==manifest(),'Own source closure changed')
    with tempfile.TemporaryDirectory(prefix='continued-frame-cuts-') as temporary:
        root=Path(temporary)/'source';package=prepare(root)
        print('Replaying the complete pinned PR186 complex and bank-bit certificate...',flush=True)
        run(package/'verify_inner.py')
        parent=json.loads((package/'certificate.json').read_text())
        sys.path.insert(0,str(root/'scripts'))
        from paired_cube_physical import physical
        selected=package/'selected/complex';candidate=root/'build/continued-candidate'
        shutil.copytree(selected,candidate)
        read=lambda name:json.loads(gzip.decompress((selected/(name+'.json.gz')).read_bytes()))
        g,witness,word,row=map(read,('graph','frames','word','profile-before'))
        pairs=read('physical-pairs');frames=json.loads((HERE/'selected/frames.json').read_text())['frames']
        raw=physical(g,witness,word,row,frames,pairs)
        write_gzip(candidate/'physical-frames.json.gz',frames);write_gzip(candidate/'profile.json.gz',raw)
        pins={p.name:digest(p) for p in candidate.glob('*.json.gz')}
        (candidate/'result.json').write_text(json.dumps(dict(pins=pins),sort_keys=True)+'\n')
        print('Checking new frames, signed formal columns, terminal chronology and both sink directions...',flush=True)
        output=root/'build/new-physical.json'
        actual=run(package/'complex/physical.py','--candidate',candidate,'--source',root,'--out',output,output=output)
        actual.pop('seconds',None);actual.pop('maxrss',None)
        actual['source_sha256']={Path(k).relative_to(root).as_posix():v for k,v in actual['source_sha256'].items()}
        selection_path=root/'build/new-sinks.json'
        sinks=run(package/'complex/check_sinks.py','--candidate',candidate,'--output',selection_path,output=selection_path)
        for name in ('seconds','rss_kib'):sinks.pop(name,None)
        # Store a deterministic selection; the formal checker reads its actual actions.
        selection_path.write_text(json.dumps(sinks,sort_keys=True,indent=2)+'\n')
        formal_path=root/'build/new-formal-sinks.json'
        formal=run(package/'complex/formal_sinks.py','--candidate',candidate,'--selection',selection_path,
                   '--formal-helper',package/'complex/physical.py','--output',formal_path,output=formal_path)
        formal.pop('seconds',None)
        old_sinks=parent['complex']['physical']['terminal_compiler']
        require(sinks['eligible_count']==old_sinks['eligible_count']==46,'Retain every checked terminal')
        actions=lambda x:[{k:s[k] for k in ('role','pivot','root_index','targets','writes')} for s in x['sinks']]
        require(actions(sinks)==actions(old_sinks),'The terminal scalar actions changed')
        paid={k:row[k] for k in ('h','v','c','q','matched','total_M_operations','loss')}
        paid.update(R=sinks['new_physical_R'],scalar_role_reserve=row['R'],reuse_pairs=raw['pairs'],terminal_sinks=46,
                    m=66,W_per_vertex=sinks['new_W'],rank_per_vertex=sinks['new_rank'],deficit_per_vertex=1320,
                    child_histogram=sinks['child_histogram'],maxchild=max(map(int,sinks['child_histogram'])))
        require(all(z['dirty']==paid['R'] and z['columns']==paid['W_per_vertex'] for z in formal['columns']),
                'Every new physical source, target and dirty column')
        sys.path.insert(0,str(package/'arithmetic'))
        import certificate as arithmetic
        from interval_moment import saving_grid
        arithmetic.normalized_body_check()
        p=dict(m=paid['m'],W=paid['W_per_vertex'],N=1320,L=0,total_rank=paid['rank_per_vertex'],
               maxchild=paid['maxchild'],child_multiplicities=paid['child_histogram'])
        moment=saving_grid(p,10**18);saving=moment['accepted']['saving']
        final=arithmetic.price(paid,saving,arithmetic.COARSE,arithmetic.BETA,arithmetic.ETA,arithmetic.WEAKENING,'balanced')
        require(final['kappa']>Q(parent['kappa']),'Final assembled improvement over the parent')
        require(final['actual_bit_saving']==Q(parent['arithmetic']['actual_uniform_bit_saving']),'Unchanged checked bank-bit supplier')
        require(final['finite_bridge']['complex']['local_group_upper']==actual['scalar_bound']['local_group_upper'],
                'Full original scalar reserve remains charged')
        controls=[]
        def reject(name,call):
            try:call()
            except (ValueError,AssertionError):controls.append(name)
            else:raise ValueError('Negative control accepted: '+name)
        reject('next final grid point',lambda:arithmetic.assembly(final['finite_bridge'],paid,final['a'],
                final['kappa']+Q(1,10**18),beta=arithmetic.BETA,h=arithmetic.ETA,a_complex=saving))
        bad=copy.deepcopy(final['finite_bridge']);bad['complex']['W']=paid['W_per_vertex']
        reject('full group omitted',lambda:arithmetic.validate_shared_bridge(bad,paid))
        bad_row=copy.deepcopy(paid);key=next(iter(bad_row['child_histogram']));bad_row['child_histogram'][key]+=1
        reject('unrecounted child',lambda:arithmetic.validate_shared_bridge(final['finite_bridge'],bad_row))
        bad_frames=copy.deepcopy(frames);bad_frames[0][1]=[]
        reject('zero operation frame',lambda:physical(g,witness,word,row,bad_frames,pairs))
        before=dict(read('physical-frames'));after=dict(frames)
        return arithmetic.js(dict(status='PASS complete conditional witness',kappa=final['kappa'],
            parent_kappa=parent['kappa'],complex_saving=saving,changed_operation_frames=sum(before.get(i)!=after.get(i) for i in before.keys()|after.keys()),
            complex_profile=paid,complex_moment=moment,physical=actual,terminal=sinks,terminal_formal=formal,
            parent_complete_certificate_sha256=digest(package/'certificate.json'),
            checked_bit_certificate_sha256=sha256(json.dumps(parent['bit'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            unchanged_checked_bit_saving=final['actual_bit_saving'],arithmetic=final,controls=controls,
            inherited_assembly_controls=parent['arithmetic']['adverse_controls'],
            source_manifest_sha256=digest(HERE/'SOURCE.json'),
            scope='Physical frame refinement of the complete PR186 witness. All inherited compiler, bank, analytic, row, prime, precision, layout and fixed-tape contracts remain conditional.'))


def report(result):
    def decimal(value):
        n=Q(value)*10**18;require(n.denominator==1,'Displayed exact grid point')
        return '0.'+str(n.numerator).zfill(18)
    p=result['complex_profile'];k=Q(result['kappa']);parent=Q(result['parent_kappa'])
    return ('# Checked result\n\n'
        'Conditional kappa = **'+result['kappa']+' = '+decimal(k)+'**.\n\n'
        'This is %.6f%% above the pinned PR186 value %s.\n\n'%(float(100*(k/parent-1)),decimal(parent))+
        'The complex supplier binds, with saving '+result['complex_saving']+' = '+decimal(result['complex_saving'])+'.\n\n'
        '| Checked complex quantity | Value |\n|---|---:|\n'
        '| Changed operation frames relative to PR186 | %d |\n'%result['changed_operation_frames']+
        '| Physical auxiliary roles | %d |\n| Persistent roles W | %d |\n'%(p['R'],p['W_per_vertex'])+
        '| Rank mass | %d |\n| Deficit | %d |\n| Terminal sinks | %d |\n\n'%(p['rank_per_vertex'],p['deficit_per_vertex'],p['terminal_sinks'])+
        'The pinned complete parent, its bank-bit supplier, both new complex shear directions, every terminal, '
        'all 47 strict assembly constraints and adjacent-grid exclusions are replayed.\n\n'
        'These are conditional finite certificates. The inherited all-size compiler, shared-core/bank, '
        'weighted-bit, row-restoration, prime, precision/recovery, balanced-layout and fixed-tape contracts remain assumptions.\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args();start=time.monotonic()
    require(not sys.flags.optimize,'Run without -O')
    if a.write:(HERE/'SOURCE.json').write_text(json.dumps(manifest(),sort_keys=True,indent=2)+'\n')
    result=verify();text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if a.write:
        (HERE/'certificate.json').write_text(text);(HERE/'RESULTS.md').write_text(report(result))
    else:
        require(text==(HERE/'certificate.json').read_text(),'Complete frozen certificate differs')
        require(report(result)==(HERE/'RESULTS.md').read_text(),'Displayed result differs from certificate')
    print('PASS kappa='+result['kappa']+'; full parent replay, both new complex directions, 46 terminals and exact assembly (%.1fs)'%(time.monotonic()-start),flush=True)


if __name__=='__main__':main()
