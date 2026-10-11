import json,sys
O=sys.argv[1]
l=json.load(open(O+'/cout/legality.json'));c=json.load(open(O+'/cout/columns.json'));k=json.load(open(O+'/cout/columns_k5.json'))
R=715
print('legality',l['status'],l['copies'],l['erasures'])
assert l['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies']==l['erasures']==9
print('columns_h',c['status'],c['formal_columns_checked'])
assert c['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked']==4*120+R
print('columns_k5',k['status'],k['formal_columns_checked'],len(k['stages']),k['bridge_additions'],len(k['negative_controls']),all(x['rejected'] for x in k['negative_controls']))
assert k['status']=='PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k['formal_columns_checked']==10*120+R
assert k['bridge_additions']==24*120 and len(k['stages'])==11 and len(k['negative_controls'])==24 and all(x['rejected'] for x in k['negative_controls'])
print('ALL PASS')
