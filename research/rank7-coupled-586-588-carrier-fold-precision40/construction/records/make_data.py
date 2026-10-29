"""Write the package's declared data records (stage 1 frame edits, stage-2 transforms, stage-3 re-based rewrites) to argv[1]."""
import json, sys
from pathlib import Path
S = Path('S')
A = S / 'r14/agents/A-extract/out'; RW = S / 'r14/agents/RW/out/L27+2957'
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
fe = json.load(open(A / 'L22-base-FRAME-EDITS.json')); assert fe == json.load(open(A / 'L22-extra-FRAME-EDITS.json'))
rec = {'stage': 'stage 1: joint codimension-2 end-frame lowering (frame-only)',
       'providers': 'one record serves both providers (base and extra words are equal on every edited gate and end frame)',
       'groups': fe['groups'], 'helper_final_changes': fe['helper_final_changes'], 'frame_edits': fe['frame_edits'],
       'declared_local_profile': fe['declared_local_profile'], 'declared_width_inventory': fe['declared_width_inventory'],
       'addressing': 'index = position in the parent (PR2942) word section; gate = the literal gate without its frame; every new frame is a hyperplane of the old one'}
(out / 'STAGE1-FRAME-EDITS.json').write_text(json.dumps(rec, indent=1) + '\n')
for t in json.load(open(S / 'r14pub-build/derive/stage2-transforms.json')):
    r = {'step': t['step'], 'helper': t['helper'], 'normal': t['normal'], 'before': t['before'], 'after': t['after'],
         'frame_changes': t['frame_changes'],
         'addressing': 'before: input gates inserted right after the prelude; after: output gates appended to restore; frame_changes: addressed in the child word after insertion'}
    (out / f'TRANSFORM-{t["helper"]}.json').write_text(json.dumps(r, indent=1) + '\n')
rb = json.load(open(RW / 'REWRITES-2957-on-L27-base.json')); assert rb == json.load(open(RW / 'REWRITES-2957-on-L27-extra.json'))
(out / 'REWRITES-2957.json').write_text(json.dumps(rb, indent=1) + '\n')
print('data records written', sorted(p.name for p in out.iterdir()))
