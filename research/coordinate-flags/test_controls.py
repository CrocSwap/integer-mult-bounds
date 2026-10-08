"""Negative controls for coordinate binding and the physical word."""
import copy,gzip,json,tempfile,unittest
from pathlib import Path
import verify
class Controls(unittest.TestCase):
    def setUp(self):
        self.word=json.loads(gzip.decompress((verify.ROOT/'certificates/split-pair-word-23.json.gz').read_bytes()))
        self.config=json.loads((verify.HERE/'order-23.json').read_text())
    def test_duplicate_coordinate(self):
        self.config['order'][0]=self.config['order'][1]
        with self.assertRaises(AssertionError):verify.relabel(self.word,self.config)
    def test_inconsistent_mapping(self):
        self.config['mapping']['0']=0
        with self.assertRaises(AssertionError):verify.relabel(self.word,self.config)
    def rejected(self,word):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'word.json';p.write_text(json.dumps(word))
            with self.assertRaises(AssertionError):verify.replay(p)
    def test_unrelabelled_inputs(self):
        old=copy.deepcopy(self.word['sources']);word=verify.relabel(self.word,self.config);word['sources']=old;self.rejected(word)
    def test_unrelabelled_outputs(self):
        old=copy.deepcopy(self.word['outputs']);word=verify.relabel(self.word,self.config);word['outputs']=old;self.rejected(word)
    def test_missing_terminal_synthesis(self):
        word=verify.relabel(self.word,self.config);terminal=word['outputs'][0][0]
        word['ops']=[op for op in word['ops'] if op[0]!=terminal];self.rejected(word)
    def test_aliased_terminal(self):
        word=verify.relabel(self.word,self.config);word['outputs'][1][0]=word['outputs'][0][0];self.rejected(word)
if __name__=='__main__':unittest.main()
