# Source-only F4/A4 reuse excerpts

These are exact text excerpts from hash-pinned local sources. No source was imported or run.

## private native owner verification

/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028/areas/fresh-round-financial-version-bindings-v1/active_current.py

SHA256 f651f9acd3328db337f334a31d1cccec38098eecf9e72e9c62deaf06bd79bd45; 91614 bytes; lines 303-327

```python
303:     def verify(record):
304:         need(record['phase'] not in ('FAILED_UNCERTAIN_NO_RETRY', 'RELEASED', 'CLOSE_UNKNOWN'), 'live private owner phase')
305:         kernel_integrity(record['lease'])
306:         need(unknown_state[0] is False and first_state[0] is None, 'no earlier original failure/uncertainty')
307:         need(record['pid'] == os.getpid(), 'same actual process/context; no fork or DATA restoration')
308:         values = lease_state(record['lease'])
309:         need(values['fd'] is record['owned_fd'], 'same captured actual native descriptor field')
310:         observation = lease_image['verify'](record['lease'])  # Original real native verification.
311:         kernel_integrity(record['lease'])
312:         need(observation['parent']['start_ticks'] == record['birth']['start_ticks'] and
313:              observation['parent']['pid'] == record['birth']['pid'], 'native generation unchanged')
314:         return observation
315: 
316:     def close_actual(record):
317:         need(record['lease_close_entered'] is False, 'one actual lease close; never replay a numeric FD')
318:         record['lease_close_entered'] = True
319:         if record['lease'] is None or record['lease_acquire_entered'] is False:
320:             return  # Original pure initializer never acquired any native descriptor.
321:         kernel_integrity(record['lease'], allow_uncertain=True)
322:         values = lease_state(record['lease'])
323:         need(values['phase'] not in ('CLOSE_ENTERED', 'CLOSE_RETURNED', 'CLOSE_UNKNOWN'),
324:              'original source lease was already closed/uncertain; no repeated FD close')
325:         if record['owned_fd'] is not None:
326:             need(values['fd'] is record['owned_fd'], 'no replaced native descriptor on cleanup')
327:         lease_image['close'](record['lease'])
```

## sameproducer native guard

/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028/areas/fresh-round-financial-version-bindings-v1/active_current.py

SHA256 f651f9acd3328db337f334a31d1cccec38098eecf9e72e9c62deaf06bd79bd45; 91614 bytes; lines 594-624

```python
594:     def verify_own_inflight_slot(record,snapshot):
595:         name=record['own_request']['label']; path=F.FIN_ENTRIES/name/'METER_BODY.json'
596:         need(snapshot['wires'].get(str(path))=='','exact original own planned zero-byte producer slot; never zero elapsed')
597:         # Actual inherited stdout is inspected now, never supplied/restored as
598:         # a saved numeric handle. This does NOT invent a cross-process producer
599:         # binding: a controller whose FD1 is a child log must fail this guard.
600:         # Genuine source-private one-use producer/capture role and pristine OS
601:         # primitives remain selected operating premises, not JSON/lease proof.
602:         kernel_integrity(record['lease'])
603:         before=os.fstat(1)
604:         need(type(before) is os.stat_result,'actual native stdout stat result before fields')
605:         need(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode)==0o600 and
606:              before.st_uid==os.getuid() and before.st_nlink==1 and before.st_size==0,
607:              'actual current inherited producer stdout must be regular owned0600 single-link empty')
608:         before_identity=(before.st_dev,before.st_ino,before.st_mode,before.st_nlink,
609:                          before.st_uid,before.st_size,before.st_mtime_ns,before.st_ctime_ns)
610:         expected_slot={'path':str(path),'bytes':0,'sha256':hashlib.sha256(b'').hexdigest(),'mode':0o600}
611:         row,raw=funding_io('_read_frame_pin',expected_slot,os.getuid())
612:         after=os.fstat(1)
613:         need(type(after) is os.stat_result,'actual paired native stdout stat result before fields')
614:         after_identity=(after.st_dev,after.st_ino,after.st_mode,after.st_nlink,
615:                         after.st_uid,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
616:         need(raw==b'' and row['mode']==0o600 and row['uid']==os.getuid() and row['nlink']==1 and
617:              type(row['identity']) is list and tuple(row['identity'])==before_identity==after_identity,
618:              'actual inherited FD1 and exact canonical own BODY path have paired stable native custody identity')
619:         if record['producer_stdout_identity'] is None:
620:             record['producer_stdout_identity']=before_identity  # Private observation, never owner constructor.
621:         else:
622:             need(record['producer_stdout_identity']==before_identity,'same original current producer descriptor identity')
623:         kernel_integrity(record['lease'])
624:         need(record['own_start_pin']==manual['provenance']['original_start_pin'] and record['own_clock_ns']==record['own_start']['body_begin_ns'],'original current START/clock lineage')
```

## explicit financial phase entry/target/commit

/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028/areas/fresh-round-financial-version-bindings-v1/active_current.py

SHA256 f651f9acd3328db337f334a31d1cccec38098eecf9e72e9c62deaf06bd79bd45; 91614 bytes; lines 856-948

```python
856:         def enter_enclosing_manual(self, mode):
857:             r=rec(self)
858:             try:
859:                 kernel_integrity(r['lease']); need(type(mode) is str and mode in ('INITIALIZE_ONLY','PAYLOAD_PRELUDE','CLOSE_ONLY'),'fixed source mode')
860:                 verify(r); need(r['phase']=='HELD' and r['financial_mode'],'real held financial owner only')
861:                 r['phase']='ENCLOSING_MANUAL_VALIDATING'; r['manual_mode']=mode
862:                 snapshot=funding_io('read_financial_opening',manual['financial_opening_pin'],os.getuid())
863:                 need(snapshot['schema']=='fresh-financial-snapshot-v1' and snapshot['head_pin']==manual['financial_head_pin'],'exact actual current financial head')
864:                 bind_financial_own(r,snapshot,mode); r['financial_snapshot']=snapshot
865:                 financial_guard(r); r['phase']='ENCLOSING_MANUAL_ACTIVE'
866:                 if mode=='CLOSE_ONLY': return self.prepare_metadata_close()
867:                 return {'schema':'fresh-enclosing-manual-observation-v1','mode':mode,'own_request':r['own_request'],
868:                         'financial_head_pin':snapshot['head_pin'],'native_capability':False,'execution_permission':False}
869:             except BaseException as e:
870:                 raise fail(r,e)
871: 
872:         def prepare_metadata_close(self):
873:             r=rec(self)
874:             try:
875:                 verify(r); need(r['financial_mode'] and role=='CLOSER' and r['manual_mode']=='CLOSE_ONLY' and
876:                                 r['phase']=='ENCLOSING_MANUAL_ACTIVE' and r['financial_target'] is None,'one explicit close-only transition')
877:                 assessment=financial_guard(r); evidence=financial_pure('financial_evidence',r['financial_snapshot'])
878:                 own=evidence['entries'][r['own_request']['label']]; intent=own['command']['metadata_close_intent']
879:                 target=evidence['entries'][intent['target_id']]
880:                 need(target['entry_id']!=r['own_request']['label'] and target['phase']=='FORMAL_AWAIT_CLOSE','visible distinct prior formal target, never own operation')
881:                 r['financial_target']=json.loads(json.dumps(target)); financial_pure('financial_plain',r['financial_target'])  # Separate DATA slot, never native owner.
882:                 current,raw_head,raw_reg=head(r,r['head_pin']); reg,_,starts,closes=F.registry(raw_reg)
883:                 name=target['entry_id']
884:                 need(current['registry_pin']==intent['current_registry_pin'] and name in starts and name not in closes and
885:                      starts[name]==intent['formal_start_pin'] and set(starts)-set(closes)=={name},'actual complete formal registry/current target lineage')
886:                 baseline_raw=read(r,intent['baseline_registry_pin']); baseline,_,bst,bc=F.registry(baseline_raw)
887:                 need(set(bst)==set(bc) and reg['events']==baseline['events']+[{'kind':'REGISTER','label':name,'pin':starts[name]}],
888:                      'all other formal entries closed; exact target START after baseline')
889:                 start=F.decode(read(r,starts[name])); need(start['label']==name and start['command_sha256']==target['command_sha256'],'genuine registered target START')
890:                 receipt_raw=read(r,intent['receipt_pin']); review_raw=read(r,intent['review_pin']); receipt=F.decode(receipt_raw)
891:                 body=target['meter_body']['body']
892:                 financial_pure('_formal_receipt',receipt,starts[name],name,target['body_ns'],body['begin_ns'],body['end_ns'],intent['review_pin'])
893:                 need(hashlib.sha256(review_raw).hexdigest()==receipt['independent_outcome_review_sha256'],'exact independent pinned target review')
894:                 journal={'schema':'fresh-metadata-close-intent-v1','closer_id':r['own_request']['label'],'target_id':name,
895:                          'own_command_pin':own['record_pins']['command'],'target_start_pin':starts[name],
896:                          'expected_financial_head_pin':r['financial_snapshot']['head_pin'],'expected_formal_head_pin':r['head_pin'],
897:                          'receipt_pin':intent['receipt_pin'],'review_pin':intent['review_pin']}
898:                 folder=CONTROL/'_metadata-close-intents'
899:                 if not folder.exists(): os.mkdir(folder,0o700); sync_dir(r,folder.parent)
900:                 r['phase']='METADATA_CLOSE'; r['close_intent_pin']=publish(r,folder/(r['own_request']['label']+'.json'),canonical(journal),0o444)
901:                 # Original own request, START and clocks have not been assigned target fields.
902:                 financial_guard(r)
903:                 return {'schema':'fresh-metadata-close-prepared-v1','own_request':r['own_request'],'target_id':name,
904:                         'intent_pin':r['close_intent_pin'],'financial_budget':assessment,'native_capability':False,'execution_permission':False}
905:             except BaseException as e:
906:                 raise fail(r,e)
907: 
908:         def publish_metadata_close(self):
909:             r=rec(self)
910:             try:
911:                 verify(r); need(r['financial_mode'] and role=='CLOSER' and r['manual_mode']=='CLOSE_ONLY' and
912:                                 r['phase']=='METADATA_CLOSE' and r['financial_target'] is not None and r['close_formal_committed'] is None,
913:                                 'one real source-private metadata close, no payload upgrade')
914:                 financial_guard(r)
915:                 target=r['financial_target']; own_id=r['own_request']['label']; name=target['entry_id']
916:                 own=financial_pure('financial_evidence',r['financial_snapshot'])['entries'][own_id]; intent=own['command']['metadata_close_intent']
917:                 current,raw_head,raw_reg=head(r,r['head_pin']); reg,_,starts,closes=F.registry(raw_reg)
918:                 need(current['registry_pin']==intent['current_registry_pin'] and starts.get(name)==intent['formal_start_pin'] and
919:                      set(starts)-set(closes)=={name},'unchanged actual target registry, no retry/stale fallback')
920:                 raw=read(r,intent['receipt_pin']); receipt=F.decode(raw); review_raw=read(r,intent['review_pin']); body=target['meter_body']['body']
921:                 financial_pure('_formal_receipt',receipt,starts[name],name,target['body_ns'],body['begin_ns'],body['end_ns'],intent['review_pin'])
922:                 need(hashlib.sha256(review_raw).hexdigest()==receipt['independent_outcome_review_sha256'],'same reviewed target receipt')
923:                 r['phase']='METADATA_CLOSE_PUBLICATION_PENDING'
924:                 rp=publish(r,DOMAIN/name/'receipt.json',raw,0o600)
925:                 new=F.decode(raw_reg); new['predecessor_sha256']=hashlib.sha256(raw_reg).hexdigest()
926:                 new['events'].append({'kind':'CLOSE','label':name,'pin':rp})
927:                 committed,committed_raw,committed_reg=advance(r,current,raw_head,raw_reg,new)
928:                 immutable_head=pinned(HEADS/('HEAD-%06d.json'%committed['sequence']),committed_raw,0o600)
929:                 need(read(r,immutable_head)==committed_raw,'genuine immutable formal CLOSE head readback')
930:                 r['close_formal_committed']={'receipt_pin':rp,'formal_head_pin':immutable_head,'head_pin':r['head_pin']}
931:                 candidate=financial_pure('financial_commit_candidate',r['financial_snapshot'],own_id,name,rp,immutable_head,r['close_intent_pin'])
932:                 candidate['wires'][rp['path']]=raw.decode('utf-8')
933:                 candidate['wires'][immutable_head['path']]=committed_raw.decode('utf-8')
934:                 candidate['wires'][committed['registry_pin']['path']]=committed_reg.decode('utf-8')
935:                 candidate['wires'][r['close_intent_pin']['path']]=read(r,r['close_intent_pin']).decode('utf-8')
936:                 # New target manifest is metadata publication for the pinned target,
937:                 # not another cost/body/source rewrite or a native process retry.
938:                 state=F.financial_decode(candidate['wires'][F.financial_decode(candidate['opening_wire'].encode())['suffix_state_pin']['path']].encode())
939:                 mp=next(p for p in state['ordered_entries'] if F.financial_decode(candidate['wires'][p['path']].encode())['attempt_id']==name)
940:                 publish(r,Path(mp['path']),candidate['wires'][mp['path']].encode(),0o444)
941:                 publish_financial_candidate(r,candidate,allow_target_commit=True)
942:                 r['phase']='METADATA_CLOSE_AFTER_TARGET_COMMIT'; financial_guard(r)
943:                 need(r['own_request']==manual['request'] and r['own_start_pin']==manual['provenance']['original_start_pin'],'own lineage retained after target close')
944:                 return {'schema':'fresh-metadata-close-observation-v1','own_request':r['own_request'],'target_id':name,
945:                         'receipt_pin':rp,'formal_head_pin':immutable_head,'financial_head_pin':r['financial_snapshot']['head_pin'],
946:                         'own_reservation_ns':r['own_reservation_ns'],'native_capability':False,'execution_permission':False,'all_costs_settled':False}
947:             except BaseException as e:
948:                 raise fail(r,e)
```

## initializer

/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028/areas/fresh-round-financial-version-bindings-v1/active_current.py

SHA256 f651f9acd3328db337f334a31d1cccec38098eecf9e72e9c62deaf06bd79bd45; 91614 bytes; lines 965-991

```python
965:         def initialize(self, initial_registry_raw):
966:             r = rec(self)
967:             try:
968:                 verify(r); need(((not r['financial_mode'] and r['phase'] == 'HELD') or (r['financial_mode'] and r['phase'] == 'ENCLOSING_MANUAL_ACTIVE' and r['manual_mode'] in ('INITIALIZE_ONLY','PAYLOAD_PRELUDE'))) and expected is None and role == 'PUBLISHER', 'one initial publisher')
969:                 need(opening is not None and opening['funding_source_sha256'] == FUNDING_SHA, 'current selected funding/opening binding')
970:                 selected = funding_io('validate_opening_binding', opening, os.getuid())
971:                 read_manual(r, F.opening_evidence(selected)['state_sha256'])
972:                 reg, _, starts, closes = F.registry(initial_registry_raw)
973:                 need(not starts and not closes and reg['predecessor_sha256'] is None and
974:                      reg['opening_pin'] == selected['opening_pin'], 'empty new registry with complete selected current opening')
975:                 for p in (DOMAIN.parent, DOMAIN, STAGE, HEADS, HANDOFFS, CLAIMS):
976:                     if not p.exists():
977:                         os.mkdir(p, 0o700)
978:                     directory(p)
979:                     sync_dir(r, p.parent)
980:                 need(guarded_io('names', DOMAIN, 2) == [] and guarded_io('names', HEADS, 2) == [] and
981:                      not HEAD.exists(), 'no prior/orphan initialization')
982:                 stage_empty()
983:                 rp = publish(r, CONTROL / 'REGISTRY-000000.json', initial_registry_raw, 0o444)
984:                 raw = canonical({'schema': 'fresh-active-head-v1', 'sequence': 0,
985:                                  'registry_pin': rp, 'previous_head_sha256': None})
986:                 publish(r, HEADS / 'HEAD-000000.json', raw, 0o600)
987:                 r['head_pin'] = publish(r, HEAD, raw, 0o600)
988:                 head(r, r['head_pin'])
989:                 return F.decode(canonical(r['head_pin']))
990:             except BaseException as e:
991:                 raise fail(r, e)
```

## factory identity and actual native acquisition

/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028/areas/fresh-round-financial-version-bindings-v1/active_current.py

SHA256 f651f9acd3328db337f334a31d1cccec38098eecf9e72e9c62deaf06bd79bd45; 91614 bytes; lines 1236-1280

```python
1236:     def open_owner():
1237:         need(opened[0] is False, 'one context per exact bound source-role invocation')
1238:         opened[0] = True
1239:         unchanged_class(Context, context_image, context_functions, active_globals)
1240:         ctx = Context(sentinel)
1241:         r = {'role': role, 'pid': os.getpid(), 'lease': None, 'birth': None,
1242:              'phase': 'PRIVATE_BEFORE_ACQUIRE', 'first': None, 'secondary': [], 'secondary_saturated': False,
1243:              'request': None, 'start': None, 'start_pin': None, 'baseline_registry_pin': None,
1244:              'head_pin': expected, 'publication': None,
1245:              'protocol_anchor_ns': None, 'lease_close_entered': False,
1246:              'lease_initialized': False, 'lease_acquire_entered': False, 'owned_fd': None,
1247:              'kernel_memory_uncertain': False, 'financial_mode': type(manual) is dict and manual.get('schema') == 'fresh-active-financial-manual-entry-binding-v1',
1248:              'own_request': None, 'own_start_pin': None, 'own_start': None, 'own_clock_ns': None, 'own_reservation_ns': None,
1249:              'manual_mode': None, 'financial_snapshot': None, 'financial_publication': False, 'financial_target': None,
1250:              'close_intent_pin': None, 'close_formal_committed': None, 'candidate_pending': None,
1251:              'producer_stdout_identity': None, 'formal_link_pending': None}
1252:         contexts[ctx] = r  # Private ownership/role identity BEFORE fallible initialization/acquire.
1253:         try:
1254:             values = kernel_integrity()
1255:             need(all(slot[1] in ('FREE', 'CLOSED') for slot in values['slots']),
1256:                  'fresh role begins with no borrowed/pending IO slot')
1257:             r['protocol_anchor_ns'] = time.monotonic_ns()  # Partial local window only.
1258:             need(type(r['protocol_anchor_ns']) is int and r['protocol_anchor_ns'] >= 0, 'genuine finite local protocol anchor')
1259:             unchanged_class(LeaseType, lease_image, lease_functions, cg)
1260:             r['lease'] = object.__new__(LeaseType)  # No metaclass/class __call__/foreign __new__ dispatch.
1261:             lease_state(r['lease'], fields=set())
1262:             lease_image['__init__'](r['lease'])
1263:             r['lease_initialized'] = True
1264:             kernel_integrity(r['lease'])
1265:             r['phase'] = 'ACQUIRE_PENDING'; r['lease_acquire_entered'] = True
1266:             lease_image['acquire'](r['lease'])
1267:             kernel_integrity(r['lease'])
1268:             acquired = lease_state(r['lease'])
1269:             r['owned_fd'] = acquired['fd']; r['birth'] = dict(acquired['birth'])
1270:             r['phase'] = 'HELD'; verify(r)
1271:             return ctx
1272:         except BaseException as e:
1273:             fail(r, e)
1274:             # Exactly one actual cleanup entry; unsafe metadata remains unknown debt,
1275:             # never guessed/replayed descriptor cleanup or a reconstructed owner.
1276:             try:
1277:                 close_actual(r)
1278:             except BaseException as close_error:
1279:                 fail(r, close_error)
1280:             raise r['first']
```

## literal old bindings

/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028/areas/fresh-round-bootstrap-loader-v3/bootstrap_loader.py

SHA256 e681aa3ee4c48d2a3273899a1bb11af76929d440d05f47320e7fea26df9f9f3e; 11188 bytes; lines 30-40

```python
30: SLOTS = [[None, 'FREE', None, False] for unused in range(32)]
31: RETAINED = []
32: USED = [False]
33: CONTROLLER = R / 'areas/fresh-controller-composition-v2/composed_controller.py'
34: CONTROLLER_PIN = {'bytes':81343,'sha256':'c88736fce81d737ae13ac1bf47500dc9d72920bd4910efe1b49074797d6e3231'}
35: FUNDING = R / 'areas/fresh-round-provenance-bridge-v1/funding_current.py'
36: ACTIVE = R / 'areas/fresh-round-provenance-bridge-v1/active_current.py'
37: # Exact frozen source selection; source acceptance and operational admission
38: # remain separate, and this component creates no command permission.
39: SELECTED = {'funding': {'bytes': 61942, 'sha256': '6d4489fa1b2602f0b5e9c93deefb988aa597db9c73dc686d1538de32e4b05b4a'}, 'active': {'bytes': 49454, 'sha256': '32959cae22ab82df40d3ad9bf1014c752121d2f88a258bb36bb0fe221f7e6124'}}
40: 
```

## authentic bootstrap source load and owner creation

/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028/areas/fresh-round-bootstrap-loader-v3/bootstrap_loader.py

SHA256 e681aa3ee4c48d2a3273899a1bb11af76929d440d05f47320e7fea26df9f9f3e; 11188 bytes; lines 201-251

```python
201: def open_fixed_publisher(approved_opening, expected_head_pin=None, approved_manual_entry=None):
202:     """Called only by the externally admitted exact source-private launcher.
203: 
204:     Parameters are permission/evidence DATA, never authentication roots. The
205:     actual controller, IO singleton, funding and ACTIVE modules all originate
206:     from this fixed transport; the caller cannot construct or replace them.
207:     The returned context really acquires/holds its own original native EX.
208:     No source result, hash or DATA declaration is execution permission. Caller
209:     must route every native close through ctx.release, retain error identity and
210:     retain the source objects through that close. This component has no payload,
211:     argv launcher, initializer invocation, scientific/native fault or retry.
212:     """
213:     need(USED[0] is False, 'one startup attempt, including failed source load')
214:     USED[0] = True  # Before fallible startup: no replay after partial module load.
215:     need(SELECTED is not None, 'final reviewed current source bindings unconfigured')
216:     clean_launch()
217:     need(FIRST[0] is None and IO_UNKNOWN[0] is False and
218:          all(s[1] in ('FREE', 'CLOSED') for s in SLOTS), 'known closed startup transport')
219:     name = 'h25_fresh_round_private_controller_bootstrap_v3'
220:     need(name not in sys.modules, 'private controller module name already used')
221:     raw = stable_source(CONTROLLER, CONTROLLER_PIN)
222:     controller = ModuleType(name)
223:     controller.__dict__.update(__file__=str(CONTROLLER), __name__=name,
224:         __package__=None, __spec__=None, __builtins__=builtins)
225:     sys.modules[name] = controller
226:     RETAINED.append((controller, raw))  # Retain even if compile/top-level load fails.
227:     exec(compile(raw, str(CONTROLLER), 'exec', dont_inherit=True), controller.__dict__)
228:     # This is actual source-private identity, not ModuleType/attribute imitation.
229:     # Original top-level creates controller.IO but never calls old run_owned/main.
230:     C = controller
231:     need(C.FIRST[0] is None and C.IO_UNKNOWN[0] is False and
232:          C.SOFT_DEADLINE[0] is None and C.ACTIVE_CASE[0] is None and
233:          not C.RETAINED_MODULES and
234:          all(s[1] in ('FREE', 'CLOSED') for s in C.IO.slots), 'pristine original controller state')
235:     funding, fp = C.load_source(FUNDING, SELECTED['funding'],
236:                                'h25_fresh_round_private_current_funding_v3')
237:     active, ap = C.load_source(ACTIVE, SELECTED['active'],
238:                               'h25_fresh_round_private_current_active_v3')
239:     RETAINED.append((funding, active, fp, ap))
240:     launch = C.clean_launch()  # Original task/signal/umask/stdio/process contract.
241:     need(C.FIRST[0] is None and C.IO_UNKNOWN[0] is False and
242:          all(s[1] in ('FREE', 'CLOSED') for s in C.IO.slots), 'known closed source loading before owner bind')
243:     factory = active.bind_api(C, funding, role='PUBLISHER',
244:         expected_head_pin=expected_head_pin, approved_opening=approved_opening,
245:         approved_manual_entry=approved_manual_entry)
246:     RETAINED.append((factory, launch))
247:     ctx = factory()  # Original actual GlobalLease acquire/verify; no DATA owner restore.
248:     RETAINED.append(ctx)
249:     return ctx
```

