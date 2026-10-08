#!/usr/bin/env python3
"""Portable rectangular producer replay using unchanged inherited source.

Adapted from the research regeneration by Rohan Arun with Codex assistance.
The graph, positive labels and matchers retain icekylinx's source attribution.
"""
from hashlib import sha256
from pathlib import Path
import argparse,gc,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from partial_swap.graph import graph,export
from partial_swap.positive import run as positive


def run(dimensions=(27,28),work=None):
    work=ROOT/'build/rectangular-semantic/producers' if work is None else work
    work.mkdir(parents=True,exist_ok=True)
    inputs=json.loads((HERE/'inputs.json').read_text());expected_hash=inputs['source_sha256']
    for alias,digest in expected_hash.items():
        if alias.startswith(('PR21/scripts/','PR25/scripts/')):
            path=ROOT/alias.split('/',1)[1]
            assert sha256(path.read_bytes()).hexdigest()==digest,alias
    binaries={}
    for name in ('match_exported_dag','match_positive_dag'):
        output=work/name
        subprocess.run(['c++','-O3','-std=c++17',str(ROOT/'scripts/partial_swap'/f'{name}.cpp'),'-o',str(output)],check=True)
        binaries[name]=output
    records={}
    for h in dimensions:
        assert h in (27,28),'This replay certifies the two new dimensions only'
        started=time.monotonic();c=graph(h);scalar=c.verify();dag=work/f'producer-{h}.bin';export(c,dag);del c;gc.collect()
        first=json.loads(subprocess.check_output([str(binaries['match_exported_dag']),str(dag),str(dag)+'.links'],text=True))
        labels=positive(str(dag))
        final=json.loads(subprocess.check_output([str(binaries['match_positive_dag']),str(dag),str(dag)+'.positive'],text=True))
        record=dict(v=final['v'],roles=final['R'],additions=final['c'],outputs=final['q'],matches=final['matched'],loss=final['loss'],histogram=final['histogram'])
        prior=inputs['producers'][str(h)]
        assert record==prior['record'] and scalar==prior['scalar']
        assert first==prior['original'] and labels==prior['labels'] and final==prior['positive']
        actual={}
        for path in (dag,Path(str(dag)+'.links'),Path(str(dag)+'.positive')):
            digest=sha256(path.read_bytes()).hexdigest();assert digest==expected_hash['fresh-local/'+path.name],path.name
            actual[path.name]=digest
        records[str(h)]=dict(record=record,scalar=scalar,original_matching=first,positive_matching=final,
                            labels=labels,deterministic_artifact_sha256=actual,certificate_equal=True,
                            elapsed_seconds=time.monotonic()-started)
        print('PASS freshly regenerated rectangular h='+str(h)+'; roles='+str(record['roles']),flush=True)
    result=dict(status='FRESH NEW-DIMENSION PRODUCERS MATCH ARCHIVED SEMANTICS AND DETERMINISTIC HASHES',
                producers=records,scope='Elapsed times and archival report-byte hashes are not reproducibility assertions.')
    (work/'replay.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path);args=p.parse_args();run(work=args.work_dir)
