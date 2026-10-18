"""Exhaustive finite comparison against states allowing prefetch/early eviction."""
import importlib.util
import itertools
from pathlib import Path
import unittest

p=Path(__file__).with_name('verify.py')
s=importlib.util.spec_from_file_location('resident',p)
v=importlib.util.module_from_spec(s)
exec(compile(p.read_bytes(),str(p),'exec'),v.__dict__)

def unrestricted(events):
    all_states=[frozenset(x) for n in range(3) for x in itertools.combinations(range(3),n)]
    states={frozenset():0}
    for target,src in events:
        needed={target}|({src} if src!=111 else set())
        states={new:min(cost+len(new-old) for old,cost in states.items())
                for new in all_states if needed.issubset(new)}
    return min(states.values())

class ScheduleTests(unittest.TestCase):
    def test_all_short_request_words(self):
        alphabet=[(i,111) for i in range(3)]+[(i,j) for i,j in itertools.combinations(range(3),2)]
        checked=0
        for length in range(1,5):
            for word in itertools.product(alphabet,repeat=length):
                exact=unrestricted(word)
                self.assertEqual(v.plan(word)['loads'],exact)
                self.assertEqual(v.greedy_loads(word),exact)
                checked+=1
        self.assertEqual(checked,1554)

    def test_invalid_self_request(self):
        with self.assertRaisesRegex(ValueError,'schedule role'):
            v.plan([(2,2)])

if __name__=='__main__': unittest.main()
