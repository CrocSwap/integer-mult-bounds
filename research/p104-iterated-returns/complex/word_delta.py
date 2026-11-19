#!/usr/bin/env python3
"""Export and restore source-bound sparse edits between canonical scalar graphs."""

from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json


def canonical(doc):
    return json.dumps(doc,sort_keys=True,separators=(',',':')).encode()


def digest(doc):
    return sha256(canonical(doc)).hexdigest()


def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if data.startswith(b'\x1f\x8b') else data)


def delta(before,after):
    source={row[0]:row[1:] for row in before}
    result={row[0]:row[1:] for row in after}
    return [[k,source.get(k),result.get(k)] for k in sorted(source.keys()|result.keys()) if source.get(k)!=result.get(k)]


def restore(word,journal,reverse=False):
    out=word.copy()
    old,new=('result','source') if reverse else ('source','result')
    require(digest(word)==journal[old+'_word_sha256'],'source word binding')
    for field,label in [('forms','changed_forms'),('moves','paid_move_changes')]:
        data={r[0]:r[1:] for r in word[field]}
        for k,a,b in journal[label]:
            before,after=(b,a) if reverse else (a,b)
            require(data.get(k)==before,f'{field} preimage {k}')
            if after is None:
                del data[k]
            else:
                data[k]=after
        out[field]=[[k,*v] for k,v in sorted(data.items())]
    out['schedule']=journal[new+'_schedule']
    require(digest(out)==journal[new+'_word_sha256'],'output word binding')
    return out


def require(ok,condition):
    if not ok:
        raise ValueError(condition)


def produce(source,child):
    require(source.keys()==child.keys() and all(source[k]==child[k] for k in source.keys()-{'forms','moves','schedule'}),
            'fixed geometry and boundary')
    result=dict(schema_version=1, source_word_sha256=digest(source),result_word_sha256=digest(child),
                changed_forms=delta(source['forms'],child['forms']),paid_move_changes=delta(source['moves'],child['moves']),
                source_schedule=source['schedule'],result_schedule=child['schedule'])
    require(restore(source,result)==child and restore(child,result,True)==source,'exact reversible canonical edit')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--child',type=Path)
    p.add_argument('--journal',type=Path,required=True)
    p.add_argument('--out',type=Path)
    p.add_argument('--reverse',action='store_true')
    a=p.parse_args()
    source=read(a.source)
    if a.child:
        journal=produce(source,read(a.child))
        a.journal.write_text(json.dumps(journal,separators=(',',':'))+'\n')
        print('literal delta',len(journal['changed_forms']),len(journal['paid_move_changes']),journal['result_word_sha256'])
    else:
        require(a.out is not None,'an output is required when applying the delta')
        out=restore(source,read(a.journal),a.reverse)
        a.out.write_bytes(gzip.compress(canonical(out),mtime=0))
        print('replayed',digest(out))


if __name__=='__main__':
    main()
