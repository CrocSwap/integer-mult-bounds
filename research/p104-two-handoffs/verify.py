"""Reproduce the conditional kappa of the two successor hand-offs.  Apache-2.0.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
Runs the hand-off word through PR5551's own chain (replay, transpose, native maps,
physical caller, pricing with all 54 strict + 4 functional outer checks), then the
supporting Variant A through the UNMODIFIED PR5545 local.py.  About 5-10 minutes.
"""
from fractions import Fraction
import difflib,gzip,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import closure,need,load,read
import handoff

LOCAL_LITERALS=[("'public':735","'public':737"),('range(743)','range(745)'),('0 <= r < 743','0 <= r < 745'),
    ('r >= 735 and r not in live_owned','r >= 737 and r not in live_owned'),('0 <= s < 743','0 <= s < 745'),
    ('current[:735]','current[:737]'),('if r < 735 else','if r < 737 else'),('All 743 public','All 745 public'),
    ('for r in range(735) if r not in main','for r in range(737) if r not in main'),("'public_inputs':735","'public_inputs':737"),
    ('743*743','745*745'),('n = 743','n = 745'),('if r < 735:','if r < 737:'),('for r in range(735):','for r in range(737):')]
PRICING_LITERALS=[("Q('.00304153'), Q('.0030415305')","Q('.00304282'), Q('.0030428205')"),("PREVIOUS = Q('.00304117')","PREVIOUS = Q('.00304153')"),
    ('sum(targets.values()) == 12814','sum(targets.values()) == 12850')]
INTERVAL=['76070606559/25000000000000','304282426237/100000000000000']   # raw crossing, kappa in (.00304282426236, .00304282426237)

def patch(text,table):
    for a,b in table:
        need(text.count(a)>=1,'literal present: '+a);text=text.replace(a,b)
    return text

def chain(root,L,pricing_text,word,tag):
    sys.modules['local']=L;L.ROOT=root
    C=L.load(root/'research/p104-productive-controller/caller.py','p104_two_handoffs_caller_'+tag)
    tmp=HERE/('.pricing-'+tag+'.py');tmp.write_text(pricing_text)
    try: P=L.load(tmp,'p104_two_handoffs_pricing_'+tag)
    finally: tmp.unlink()
    loc=L.replay(word);col=L.reverse_columns(word)
    print(tag,'PASS replay: paid',loc['paid'],'public',loc['public_inputs'],flush=True)
    nat=L.native(word);print(tag,'PASS native maps',nat['distinct_maps'],'helpers',nat['helpers'],flush=True)
    ctl=C.construct();need(ctl==read(root/'research/p104-productive-controller/CONTROLLER.json'),'Exact complete caller')
    phys=C.physical(ctl,word);print(tag,'PASS physical caller',flush=True)
    res=P.run(loc,nat,ctl,phys)
    return loc,res

def main():
    pinned=handoff.source()
    word=handoff.handoff(pinned);wa=handoff.variant_a(pinned)
    for name,w in(('WORD.json.gz',word),('WORD-VARIANT-A.json.gz',wa)):
        need(read(HERE/name)==w,name+' regenerates from the pinned PR5551 word')
    need(word['public']==737 and len(word['program'])==len(pinned['program']),'rename-only edit')
    part=sys.argv[sys.argv.index('--part')+1] if '--part' in sys.argv else 'all'
    need(part in('all','handoff','variant-a'),'--part must be handoff or variant-a')
    out={}
    with closure() as root:
        orig_local=(root/'research/p104-productive-controller/local.py').read_text()
        shipped=(HERE/'local.py').read_text()
        need(patch(orig_local,LOCAL_LITERALS)==shipped,'shipped local.py = closure local.py + literal changes only')
        pr_pricing=(HERE/'inputs/pr5551-pricing.py').read_text()
        need(patch(pr_pricing,PRICING_LITERALS)==(HERE/'pricing.py').read_text(),'shipped pricing.py = PR5551 pricing.py + literal changes only')
        # --- main claim: two successor hand-offs, patched local.py (737 public inputs)
        if part in ('all', 'handoff'):
            L=load(HERE/'local.py','local');L.ROOT=root
            loc,res=chain(root,L,(HERE/'pricing.py').read_text(),word,'handoff')
            need(res['raw_root_interval']==INTERVAL,'exact crossing interval')
            need(res['productive_fields']==12850 and res['paid_calls']==69912 and res['rank_mass_surplus']==760,'invoice')
            need(len(res['outer']['strict_checks'])==54 and len(res['outer']['functional_checks'])==4,'outer inventory')
            need(all(Fraction(x)>0 for k in('strict_checks','functional_checks') for x in res['outer'][k].values()),'all outer checks strict')
            out['handoff']=res;out['loc']=loc
        # --- supporting Variant A: helpers start at frames 608/613, UNMODIFIED local.py (735 public inputs)
        if part in ('all', 'variant-a'):
            L0=load(root/'research/p104-productive-controller/local.py','local');L0.ROOT=root
            need(Path(L0.__file__).read_text()==orig_local,'unmodified closure local.py')
            ptxt=patch(pr_pricing,PRICING_LITERALS[:2]).replace('sum(paid.values()) == 69912','sum(paid.values()) == 69876')
            locA,resA=chain(root,L0,ptxt,wa,'variantA')
            need(resA['raw_root_interval']==INTERVAL,'Variant A: same exact crossing interval')
            need(len(resA['outer']['strict_checks'])==54 and len(resA['outer']['functional_checks'])==4 and all(Fraction(x)>0 for k in('strict_checks','functional_checks') for x in resA['outer'][k].values()),'Variant A outer checks')
            out['variant_a']=resA
    lo,hi=[Fraction(x) for x in INTERVAL]
    print('Crossing kappa in (%s, %s) = (%.14f, %.14f)'%(INTERVAL[0],INTERVAL[1],lo,hi))
    print('Conditional complete kappa 0.0030428242; PR5551 0.0030415312; gain +1.2931e-6 (float price)')
    print('54 strict + 4 functional outer checks pass for: '+part)
    if '--write' in sys.argv and part=='all':
        loc=out['loc']
        (HERE/'RESULT.json').write_text(json.dumps({'status':'PASS_P104_TWO_HANDOFFS_CONDITIONAL_KAPPA_0030428242',
            'kappa_claimed':'.00304282','crossing_kappa_interval':INTERVAL,'crossing_kappa_decimal':'.0030428242',
            'previous_pr5551':'.00304153','paid_local':loc['paid'],'helpers_local':loc['helpers'],
            'handoff_complete_cost':out['handoff'],'variant_a_complete_cost':out['variant_a'],
            'conditions':['The five framework assumptions retained by PR5544/5545/5551.',
                          "PR5551's validity (unreproduced at time of writing).",
                          'Admissibility of a fresh helper starting at a non-canonical mid frame (Variant A passes the unmodified local.py; canonical-start rule exists only in the #4610 compact-width verifier).']},indent=1,sort_keys=True,default=str)+'\n')
    print('PASS P104_TWO_HANDOFFS')
main()
