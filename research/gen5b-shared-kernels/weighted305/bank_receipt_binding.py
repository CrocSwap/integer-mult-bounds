"""Our standalone exact role-bank receipt binding, independent of candidate size.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
import reproduce_pr305 as base
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def bind_banks(result, receipt_path, table_path, expected_status):
    banks=json.loads(receipt_path.read_text());table=json.loads(table_path.read_text())
    physical_R=base.read('expected/kernel-pins.json')['physical_R']
    assert banks['status']==expected_status
    assert banks['source_head']==base.HEAD and banks['candidate_sha256']==result['candidate_sha256']
    counts={int(r):n for r,n in banks['family_counts'].items()}
    assert counts==result['residual_census']
    assert sum(counts.values())==banks['helper_roles']==result['physical_R']==physical_R
    assert base.mass(counts)==banks['residual_rank_per_replica']
    assert table['stages']==5 and table['replicas']==60 and table['width']==120
    assert table['stage_banks']==banks['banks_per_stage']==result['banks_per_stage']
    assert 120*banks['banks_per_stage']==60*base.mass(counts)
    assert banks['total_banks']==5*banks['banks_per_stage']
    assert banks['literal_data_stock']==60*4*1760==422400
    assert banks['literal_stock']==422400+banks['total_banks']==result['literal_stock']
    assert F(banks['unreplicated_stock'])==result['unreplicated_stock']==F(banks['literal_stock'],60)
    assert 120*banks['literal_stock']-60*result['rank_mass']==60*result['deficit']==264000
    assert banks['checked_role_replica_assignments_per_stage']==60*physical_R
    assert banks['total_stage_assignments']==5*60*physical_R
    families={int(r):roles for r,roles in table['families'].items()}
    assert {r:len(roles)for r,roles in families.items()}==counts
    allroles=[role for roles in families.values()for role in roles]
    assert len(allroles)==len(set(allroles))==physical_R
    patterns=table['patterns'];expected_masks=[]
    for row in patterns:
        assert sum(row['widths'])==120
        expected_masks.extend([(1<<len(row['widths']))-1]*row['count'])
    assert len(expected_masks)==banks['banks_per_stage']
    masks=[0]*len(expected_masks);hash_state=hashlib.sha256();assigned=0
    for width,roles in sorted(families.items()):
        assert roles==sorted(roles)
        segments=table['segments'][str(width)]
        for index,role in enumerate(roles):
            for replica in range(60):
                q=60*index+replica
                matches=[s for s in segments if s['lo']<=q<s['hi']]
                assert len(matches)==1
                segment=matches[0];offset,within=divmod(q-segment['lo'],len(segment['blocks']))
                bank=segment['bank_start']+offset;block,x=segment['blocks'][within]
                pattern=patterns[segment['pattern']]
                assert pattern['widths'][block]==width and sum(pattern['widths'][:block])==x
                assert 0<=offset<pattern['count'] and 0<=x<x+width<=120
                bit=1<<block;assert not masks[bank]&bit;masks[bank]|=bit;assigned+=1
                hash_state.update(f'{role},{replica},{bank},{block},{x},{width}\n'.encode())
    assert assigned==60*physical_R and masks==expected_masks
    assert hash_state.hexdigest()==table['assignment_sha256']==banks['assignment_sha256']
    assert banks['all_banks_full'] and banks['stages_have_disjoint_bank_namespaces']
    assert banks['maximum_block_scalar']==max(len(p['widths'])for p in patterns)==40
    return dict(status='PASS_REENUMERATED_ROLE_BANK_STOCK_BINDING',
        assignments_per_stage=assigned,total_stage_assignments=5*assigned,
        assignment_sha256=hash_state.hexdigest(),receipt_sha256=digest(receipt_path),
        address_table_sha256=digest(table_path),literal_stock=banks['literal_stock'],
        unreplicated_stock=F(banks['unreplicated_stock']),replicas=60,stages=5,
        physical_R=physical_R,banks_per_stage=banks['banks_per_stage'],all_blocks_full=True,
        scope='Re-enumerated every role/replica block address, rejected collisions and gaps, and bound normalized/literal stock and rank to pricing. Unchanged address-normalizer/compiler contracts remain inherited.')

