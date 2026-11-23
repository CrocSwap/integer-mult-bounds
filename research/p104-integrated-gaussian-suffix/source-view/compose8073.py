"""Recreate the Gaussian successor from the live #8073 package, keeping the #8072 result intact."""
from pathlib import Path
from shutil import copyfile
from hashlib import sha256,sha1
import json,runpy,subprocess,sys

parent=Path(__file__).resolve().parent
root=parent/'combined'
source=parent/'source8073'
root.mkdir(exist_ok=True)
provenance=json.loads((parent/'source-blobs.json').read_bytes())
assert provenance['head']=='cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e' and provenance['repository']=='CrocSwap/integer-mult-bounds'
files=provenance['files']
assert len(files)==15
for row in files:
    if row['filename'].startswith('research/p104-weighted-k7-suffix/'):
        name=Path(row['filename']).name
        original=(parent if name=='peer8057.tar.gz' else source)/name
        data=original.read_bytes()
        assert sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row['sha']
        copyfile(original,root/name)
# Restore all 88 peer inputs using the exact 8073 manifest, then materialize
# its own ordinary suffix implementation, including every retained negative.
peer=runpy.run_path(str(root/'verify.py'))['restore'](root/'peer')
runpy.run_path(str(root/'prepare.py'))['materialize'](peer)
subprocess.run([sys.executable,'-IB',str(peer/'bootstrap.py'),str(root/'runtime')],check=True)

def adapt(file,edits=()):
    data=(parent/file).read_text()
    for old,new,n in edits:
        if data.count(old)!=n:raise ValueError((file,old,data.count(old),n))
        data=data.replace(old,new)
    (root/file).write_text(data)

adapt('build_successor.py',[
 ('Profile((8192, 124649, 524288), 490950, Q(".003898214283192"))','Profile((8192, 117168, 524288), 501831, Q(".003898219753506"))',1),
 ('Profile((8358, 132157, 524288), 479787, Q(".003898216827298"))','Profile((8192, 124612, 524288), 491002, Q(".003898222531555482"))',1),
 ('cost == 318292011 and premium == 515','cost == 318291911 and premium == 517',1),
 ('cost == 318291831 and premium == 514','cost == 318291611 and premium == 515',1),
 ('(517115, 490950)','(516570, 501831)',1),('(517611, 479787)','(517112, 491002)',1),
 ('Q(".00389821412325")','Q(".003898214283192")',1),
 ('\'Q(".003898214283192")\')','\'Q(".003898219753506")\')',1),
 ('Q(79971, 500000000000000)','Q(2735157, 500000000000000)',1),
 ('Q(1272053, 500000000000000)','Q(1389024741, 500000000000000000)',1)])
adapt('run_successor.py')
adapt('check_successor_cutoff.py')
adapt('check_six_ordinary.py')
adapt('check_corrupt_owner.py')
adapt('check_successor_tiers.py',[
 ('(8358,132157,524288)','(8192,124612,524288)',1),
 (".003898216827298",".003898222531555482",1),("479787","491002",1),("1145064","1148568",1),
 ("(8456,140677,665029)","(8290,132966,657318)",1)])
adapt('certify_frontier.py',[
 ('strict_gain_over_8072_ceiling','strict_gain_over_8073_ceiling',1),
 ('ORD_DEBIT = Q(11239, 8192)','ORD_DEBIT = Q(11204, 8192)',1),
 ('OLD_UPPER = Q(523209464347189355219919950737,','OLD_UPPER = Q(523210198560303585338978849681,',1),
 ('disclosed=Q(int(value*10**15),10**15)','disclosed=Q(int(value*10**18),10**18)',1),
 ('"lower_decimal":dec(disclosed,15)','"lower_decimal":dec(disclosed,18)',1)])
adapt('check_six_price.py',[
 ('.003898216827298','.003898222531555482',1),('f.CLOCK_CAP=318292011','f.CLOCK_CAP=318291911',1),
 ('318291831','318291611',1),('hi==C-debit/479787-f.STOP','hi==f.ordinary(TERMINAL.rank_logs)-f.STOP',1),
 ('.0000000025441059','.0000000027780494',1)])
subprocess.run([sys.executable,'-IB',str(root/'build_successor.py')],check=True)
