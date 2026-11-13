"""Retarget authenticated #7544 native replay to its single adjacent-MOVE edit."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path

SOURCE_SHA = '26c0e02327ee3f8772ef776d03dfb63c5581063bc3e0631b4110d2d237e06092'
OLD = '2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef'
NEW = 'bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745'
PINS = {
    'COMPOSED-WORD.json.gz': '926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c',
    '7544-NATIVE.json': 'a4ecb5d836b7c2cd466e9ffb512229198795b87b9697a241dd373b3e4bfe8804',
    'role902-WORD.json.gz': '6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32',
}


def sha(data):
    return sha256(data).hexdigest()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='exact adapted #7544 native Python source')
    parser.add_argument('frozen', type=Path, help='directory containing pinned old word, native, new word')
    parser.add_argument('output', type=Path, help='isolated root/producer54/validation_native/run.py')
    args = parser.parse_args()
    for name, digest in PINS.items():
        assert sha((args.frozen / name).read_bytes()) == digest, name
    for name, digest in (('COMPOSED-WORD.json.gz', OLD), ('role902-WORD.json.gz', NEW)):
        assert sha(decompress((args.frozen / name).read_bytes())) == digest, name
    source = args.source.read_bytes()
    assert sha(source) == SOURCE_SHA
    adapted = source.decode()
    patches = (
        (f"EXPECTED='{OLD}'", f"EXPECTED='{NEW}'\nCOMPARATOR='{OLD}'"),
        ("need(len(new_pairs)==2,'Both new chart pairs')",
         "need(len(new_pairs)==3 and (618,913) in new_pairs,'Three new chart pairs over #7481 including 618→913')"),
        ("affected |= new_pairs", "affected |= new_pairs | {(618,789),(789,913)}"),
        ("    return {'all_affected_pairs':report,'wrong_phase_rejected':True}",
         """    a,m,b=(interpreter.frame(word['frames'][f],9) for f in (618,789,913))
    old=interpreter.adjoint(a)+m+interpreter.adjoint(m)+b
    direct=interpreter.adjoint(a)+b
    interpreter.equal(old,direct,'Hosted 902 exact signed composition')
    for before,after in ((old,direct),(interpreter.adjoint(old),interpreter.adjoint(direct))):
        for column in range(512):
            need(interpreter.state(before,column)==interpreter.state(after,column),'Hosted 902 arbitrary-input action')
    return {'all_affected_pairs':report,'wrong_phase_rejected':True,'role902_exact_forward_and_adjoint_columns':512}"""),
        ("        need(new==read(ROOT/'frozen-composition/COMPOSED-WORD.json.gz'),'Literal composed word')",
         """        comp=read(ROOT/'frozen-composition/COMPOSED-WORD.json.gz')
        compN=read(ROOT/'frozen-composition/7544-NATIVE.json')
        need(sha256(canonical(comp)).hexdigest()==compN['word_canonical_sha256']==COMPARATOR,'Exact #7544 benchmark')
        need(comp['program'][40950:40953]==[['MOVE',902,618,789,False],['MOVE',902,789,913,False],['ADD',985,902,'-1',913]],'Exact contiguous role902 splice and first signed Y2 read')
        need(902 in comp['hosted']['Y2'] and 902<comp['public'],'Exact public hosted role')
        comp_program=comp['program'][:40950]+[['MOVE',902,618,913,False]]+comp['program'][40952:]
        need(new==dict(comp,program=comp_program),'Literal unique fused word and unchanged source metadata')
        need(new==read(ROOT/'frozen-composition/role902-WORD.json.gz'),'Independently pinned literal fused word')"""),
        ("        oldN,N=map(I.native,(old,new))",
         "        oldN,replayed_compN,N=map(I.native,(old,comp,new))\n"
         "        need(normalized(replayed_compN)==compN['native'],'Full independent source #7544 inventory')\n"
         "        need(all(N[k]==replayed_compN[k] for k in ('public','helpers','rises','owned_peak','lifetimes','bad_inputs')),'Fixed ownership and targets')\n"
         "        need(delta(N['paid'],replayed_compN['paid'])=={2:-2,4:1},'Single direct fusion price')"),
        ("=={1:-1,3:-1,4:-1,5:-1,6:1,7:1}", "=={1:-1,2:-2,3:-1,5:-1,6:1,7:1}"),
        ("len(old['program'])+19", "len(old['program'])+18"),
        ("        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721",
         """        bad=deepcopy(new);bad['program'][40950][2]=789
        controls['wrong_role902_move_source']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['program'].pop(40950)
        controls['missing_role902_paid_move']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721"""),
        ("PASS_COMPOSED_7481_7542_COMPLETE_NATIVE", "PASS_ROLE902_COMPLETE_NATIVE"),
    )
    for before, after in patches:
        assert adapted.count(before) == 1, before
        adapted = adapted.replace(before, after)
    compile(adapted, str(args.output), 'exec')
    with args.output.open('x') as output:
        output.write(adapted)
    print(json.dumps({'source_sha256': SOURCE_SHA, 'adapted_sha256': sha(adapted.encode()),
                      'pins': PINS, 'replacements': patches}, sort_keys=True, indent=2))


if __name__ == '__main__':
    assert __debug__
    main()
