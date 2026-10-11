import json
import os
lab=[tuple(l) for l in json.load(open(os.environ.get('W3LABELS','labels.json')))['lab']]
idx={l:i for i,l in enumerate(lab)}
def comps(*a): raise NotImplementedError
def name(*a): raise NotImplementedError
