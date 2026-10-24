#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Independent Gaussian integer products for the four emitted flag operators."""
import argparse,gzip,hashlib,json
from pathlib import Path
from check_interface import SOURCE,SOURCE_PINS,H,N,HERE,require,sha,span,phase_recipe,mono,equal
from check_flag_prelude import frame_recipe,physical,unit_entry

def rd(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)

def digest(data):return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()

def check_product(g,s,t,sign):
    K=phase_recipe(g);S=frame_recipe(s);T=frame_recipe(t);entries=[]
    for col in range(N):
        unit=({col:(1,0)},0);out=physical(unit,S,T,K,sign)
        entry=unit_entry(out);require(entry is not None,'nonmonomial exact product')
        entries.append(entry)
    require(len({e[0] for e in entries})==N,'monomial is not a permutation')
    p=[x[0] for x in entries];phase=[x[1] for x in entries];back=[0]*N
    for x,y in enumerate(p):back[y]=x
    # Exact inverse-transpose of each unitary monomial is its complex conjugate.
    dual=(p,back,[(-z)%4 for z in phase])
    for col in range(N):
        unit=({col:(1,0)},0)
        require(equal(mono(mono(unit,dual,1),dual,-1),unit),'dual inverse product')
    return dict(forward_recipe_sha256=digest(entries),inverse_transpose_recipe_sha256=digest([[y,(-z)%4] for y,z in entries]),
                exact_columns_per_orientation=N,source_basis=s,target_basis=t,sign=sign)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--native-base',type=Path,default=HERE/'native-evidence/base');ap.add_argument('--out',type=Path,default=HERE/'FOUR-OPERATORS-INDEPENDENT.json');a=ap.parse_args()
    for name,h in SOURCE_PINS.items():require(sha(SOURCE/name)==h,'immutable source pin')
    flags=rd(HERE/'FLAG-FOUR.json');cache={};results=[];wordpins={};canonicalpins={}
    for tag,provider in [('base','gauge44'),('extra','extra')]:
        path=HERE/'words'/('FOUR-'+tag+'.json.gz');w=rd(path);wordpins[path.name]=sha(path)
        f=next(x for x in flags['cases'] if x['provider']==provider and x['baseline']=='high48')
        for record in f['records']:
            op=record['operator'];require(op in (49,50,51,52),'changed operator domain')
            pos,lender,g,U,E=w['warps'][op-1]
            require(g==record['G_columns'] and lender==record['lender'],'emitted operator does not match reviewed flag')
            aevents=[e for e in w['A'] if e[0]=='warp' and abs(e[2])==op]
            require(len(aevents)==2 and aevents[0][2]==op and aevents[1][2]==-op,'prelude warp pair')
            require(aevents[0][1]==aevents[1][1]==lender and aevents[0][3:]==aevents[1][3:][::-1],'prelude source/frame round trip')
            products=[('prelude',aevents[0][3],aevents[0][4],1),('prelude_inverse',aevents[1][3],aevents[1][4],-1),
                      ('handoff',U,E,1),('FULL_cleanup',[1<<j for j in range(H-1,-1,-1)],[1<<j for j in range(H-1,-1,-1)],-1)]
            details=[]
            for label,s,t,sign in products:
                key=tuple(g),tuple(s),tuple(t),sign
                if key not in cache:cache[key]=check_product(g,s,t,sign)
                details.append(dict(label=label,**cache[key]))
            results.append(dict(provider=provider,operator=op,lender=lender,products=details))
    # Also verify exact canonical literal frame products used by the native base.
    native=a.native_base/'CANONICAL-WORD.json.gz';c=rd(native)
    require(gzip.decompress((a.native_base/'FULL-WORD.json.gz').read_bytes())==gzip.decompress((HERE/'words/FOUR-base.json.gz').read_bytes()),'native binding')
    canonicalpins[str(native)]=sha(native);canonical=[]
    for sign,op,f0,f1 in c['warp_edges']:
        if op not in (49,50,51,52):continue
        g=c['warps'][op-1]['G_columns'];s=c['frames'][f0];t=c['frames'][f1]
        key=tuple(g),tuple(s),tuple(t),sign
        if key not in cache:cache[key]=check_product(g,s,t,sign)
        canonical.append(dict(operator=op,from_frame=f0,to_frame=f1,**cache[key]))
    require(len(canonical)==16,'native four-operator class coverage')
    # A wrong prelude target line is an actual nonmonomial mutation.
    first=flags['cases'][0]['records'][0];S=frame_recipe(first['entrance_basis']);wrong=frame_recipe([51]);K=phase_recipe(first['G_columns'])
    rejected=sum(unit_entry(physical(({col:(1,0)},0),S,wrong,K)) is None for col in range(N))
    require(rejected==N,'wrong-G-flag interface control')
    result=dict(status='PASS_FOUR_EMITTED_OPERATORS_EXACT_512_COLUMNS_BOTH_ORIENTATIONS',
                flag_four_sha256=sha(HERE/'FLAG-FOUR.json'),word_sha256=wordpins,native_sha256=canonicalpins,
                emitted_provider_operator_records=results,canonical_native_classes=canonical,unique_products_checked=len(cache),
                wrong_target_line_rejected_columns=rejected,
                scope='Only four new operators; all emitted and native canonical frame classes, exact Gaussian integers, no predecessor operator code imported. Full native program, recursive labels, global hosting and exponent remain separate obligations.')
    a.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

if __name__=='__main__':main()
