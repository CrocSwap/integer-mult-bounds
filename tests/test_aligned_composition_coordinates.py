"""Bijection and adverse-coordinate controls for the actual PR74 relabel functions."""
from pathlib import Path
from itertools import combinations
from copy import deepcopy
from hashlib import sha256
import gzip,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts/experiments'))
from aligned_composition_nodeops import relabel
from aligned_composition_graph import configuration

class CoordinateControls(unittest.TestCase):
    def test_selected_permutations_are_exact_integer_bijections(self):
        for h in (23,25):
            perm=configuration(h)['coordinate_permutation']
            self.assertEqual(sorted(perm),list(range(h)))
            self.assertTrue(all(type(x) is int for x in perm))
        self.assertEqual(configuration(23)['coordinate_permutation'],[5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 17, 19, 20, 21, 22, 0, 1, 3, 2, 4])

    def test_every_selected_word_roundtrips_full_coordinate_inverse(self):
        for h in (23,25):
            word=json.loads(gzip.decompress((ROOT/f'certificates/aligned-composition-word-{h}.json.gz').read_bytes()))
            perm=configuration(h)['coordinate_permutation'];inverse=[perm.index(i) for i in range(h)]
            parent=relabel(deepcopy(word),inverse)
            # Dict iteration and scatter order are deliberately retained by the actual function.
            raw=(json.dumps(parent,separators=(',',':'))+'\n').encode()
            selection=json.loads((ROOT/'research/aligned-composition/word-bindings.json').read_text())[str(h)]
            self.assertEqual(sha256(raw).hexdigest(),selection['parent_word_sha256'])
            self.assertEqual(relabel(parent,perm),word)

    def test_relabel_preserves_physical_operations_and_frame_inclusions(self):
        h=5;triples=list(combinations(range(h),3));v=len(triples);perm=[4,0,2,1,3]
        word=dict(h=h,v=v,frames=[[3,7],[1,31]],sources={str(i):i for i in range(v)},
            scatter=[[v+i,2*v+i] for i in reversed(range(v))],outputs=[[2*v+i,0,0,list(t)] for i,t in enumerate(triples)],
            ops=[[2*v,2*v+1,0]],events=[[2*v,0,1]])
        changed=relabel(deepcopy(word),perm)
        self.assertEqual(changed['ops'],word['ops']);self.assertEqual(changed['events'],word['events'])
        self.assertEqual(set(map(int,changed['sources'])),set(range(v)))
        self.assertEqual([b for a,b in changed['scatter']],[b for a,b in word['scatter']])
        self.assertEqual(set(a for a,b in changed['scatter']),set(range(v,2*v)))
        (a,b),(c,d)=changed['frames'];self.assertEqual(c&~a,0);self.assertEqual(b&~d,0)

    def test_invalid_permutation_and_scatter_source_are_rejected(self):
        word=dict(h=3,v=1,frames=[[1,7]],sources={'0':0},scatter=[[1,2]],outputs=[[2,0,0,[0,1,2]]])
        for permutation in ([0,1,1],[0,1],[0,1,3]):
            with self.subTest(permutation=permutation),self.assertRaises(AssertionError):relabel(deepcopy(word),permutation)
        word['scatter'][0][0]=0
        with self.assertRaises(AssertionError):relabel(word,[0,1,2])

if __name__=='__main__':unittest.main()
