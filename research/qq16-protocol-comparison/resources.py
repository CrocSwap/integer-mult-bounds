# SPDX-License-Identifier: Apache-2.0
"""Fixed-role resource checks for the complex protocol comparison.

Checker routines inspect identities/finite role graphs only. They do not supply
payload operations, decoded runtime addresses, or an unpriced Tape allocator.
Chris R with OpenAI Codex assistance; physical source: Jose Manuel #3385.
"""

def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def controller_inventory(slots=704, private=8):
    """Literal source Machine controller roles, excluding shared primitives."""
    need(type(slots) is int and slots > 0 and type(private) is int and private >= 0,
         'fixed controller packet inventory')
    parts={'roles':20, 'bank_packets':slots, 'private_packets':private,
           'capsule':15, 'protected_output':1, 'controller_pool':256,
           'bank_pool':16, 'bank_output':1, 'parking_ports':2}
    return {'parts':parts, 'tapes':sum(parts.values())}


def inventory(q):
    """One original primitive bundle, plus a dedicated controller-only bank."""
    need(type(q) is int and q > 0, 'positive fixed native parameter')
    native = 6 * ((1 << 24) + 1) + 28416 + 662 + 2*q*q + 417
    machine = 3348 + native
    root = 678
    controller = controller_inventory()['tapes']
    need(machine == 2*q*q + 100696145 and controller == 1023,
         'source complete Machine and additional controller inventories')
    return {'root_wrapper':root, 'machine_with_exclusive_native':machine,
            'additional_controller':controller,
            'shared_primitive_bundle':machine-controller,
            'A_original':root+machine,
            'B_protocol_only':root+machine+controller,
            'B_adopt':root+machine+controller,
            'CD_safe_bound':root+3*machine+(1 << 20),
            'B_increment':controller,
            'CD_increment_over_B_bound':2*machine+(1 << 20)-controller,
            'separate_engine_candidate_deferred':root+2*machine,
            'units':'fixed physical tapes; historical visited backing additional',
            'source_inventory_hypothesis':True}


def startup_retirement_bound(q):
    """Conservative added-controller bill; the shared primitive is unchanged."""
    j = inventory(q)['additional_controller']
    return {'added_machine_tapes':j, 'added_controller_tapes':j,
            'actions_upper_bound':64*j+1024,
            'units':'read + write + unit move actions',
            'scope':'fresh controller-only inventory through successful terminal marker retirement',
            'excludes':'common primitive initialization/cleanup, fixed compilation, host allocation wall time, charged call bodies'}


def fixed_engine_tapes(engine, Tape):
    """Compile ONLY the extra controller's fixed physical-role tuple.

    Named source constructor fields make the ownership boundary explicit.
    Shared scalar/leaf/monomial objects, their Ordinary backend and the original
    child controller are intentionally absent. No payload is traversed.
    The tuple is compiled before input and retained across internal role swaps.
    """
    tapes=(*engine.roles.values(), *engine.bank.packets, *engine.private,
           *engine.capsule.values(), engine.output, *engine.pool.tapes,
           *engine.bank.pool.tapes, engine.bank.output,
           engine.parking.stack, engine.parking.reverse)
    need(all(isinstance(t,Tape) for t in tapes) and
         len({id(t) for t in tapes})==len(tapes), 'distinct fixed controller inventory')
    expected=controller_inventory(engine.binding.slots,engine.binding.private)['tapes']
    need(len(tapes)==expected, 'complete literal controller constructor inventory')
    return tuple(tapes)


def retire_empty_roles(tapes, codec=None):
    """Paid terminal erasure of a complete compile-time-owned empty inventory.

    Caller supplies the complete distinct Tape tuple compiled before input and
    has proved every body empty with its head at the local origin. Dense closed
    source state, not this first-symbol check alone, rules out hidden suffixes.
    No borrowed port or still-live engine role belongs to this tuple.
    """
    from words import BLANK, LEFT
    need(type(tapes) is tuple and len({id(t) for t in tapes}) == len(tapes),
         'distinct fixed retirement inventory')
    for tape in tapes:
        need(tape.read() == BLANK, 'successful empty body before final retirement')
        tape.step(-1)
        marker = tape.read()
        need(marker in (LEFT, BLANK), 'canonical closed role origin')
        if marker == LEFT:
            tape.write(BLANK)
        tape.step(1)
    if codec is not None:
        # Ordinary.finish(False/fitted) already erased both dictionary roles.
        # These checks use the literal codec ports without reconstructing a
        # prefix, decoding a length, or reclaiming historical backing.
        need(codec._read(0) == '_' and codec._read(1) == '_',
             'closed numerical codec ports')
        codec._move(1, -1)
        need(codec._read(1) == '_', 'numerical codec origin already retired')
        codec._move(1, 1)
    return len(tapes)


def guard_recheck(q, gamma):
    """Recheck the source's conservative inventory/height allowance at fixed q.

    Caller authenticates q and Gamma against production_native/check_bounds.
    This finite integer check is not prime/native admission or a new norm proof.
    """
    need(type(gamma) is int and gamma > 0, 'positive fixed cover size')
    inv = inventory(q)
    E = 1 << 100000
    s = 1041408 * gamma
    answers = {}
    for name in ('A_original', 'B_protocol_only', 'CD_safe_bound'):
        stock = (14336 + inv[name]) * gamma
        literal = 2*(1 << 30000)*stock*stock + 8*s + 4*stock + 4 + 32*73
        need(literal < E, 'enlarged fixed inventory within retained literal reserve')
        answers[name] = {'literal_bits': literal.bit_length(),
                         'reserve_bits': E.bit_length(), 'strictly_below_reserve': True}
    return answers


def binding_tuple(machine):
    """All source aliases of logical parked roles, in actual constructor order."""
    expected = (*machine.roles.values(), *machine.bank.packets, *machine.private)
    need(len({id(t) for t in expected}) == len(expected), 'exclusive logical parked roles')
    need(len(machine.parked) == len(expected) and
         all(a is b for a,b in zip(machine.parked, expected)), 'complete Machine parked binding')
    need(len(machine.parking.roles) == len(expected) and
         all(a is b for a,b in zip(machine.parking.roles, expected)), 'complete Parking logical binding')
    need(all(machine.output is not t for t in expected), 'fixed public Machine output separate')
    return expected


def check_child_exchange(parent, backend, target, old_packet, old_result,
                         parent_output, external_ports=()):
    """Postcondition checker for a finite internal completed-child role exchange.

    External ports include cached aliases not permitted to move. This checks the
    supplied complete finite port list; it cannot discover arbitrary host aliases.
    """
    binding_tuple(parent)
    need(parent.output is parent_output, 'parent public output identity preserved')
    need(parent.packet(target) is old_result and backend.output is old_packet,
         'exact completed child role permutation')
    need(old_result is not old_packet, 'distinct exchange endpoints')
    need(all(p is not old_result and p is not old_packet for p in external_ports),
         'no immutable external alias of exchanged roles')
    need(backend.closed and backend.mode == 'closed', 'closed backend after completed child')
    need(parent.bank.state == 'gathered' and parent.bank.source is parent.roles['current'],
         'parent gathered-bank continuation preserved')
    need(parent.group is not None and parent.bank.selection ==
         {key: slot for slot,key in enumerate(parent.group.keys)},
         'immutable consumer keys still name the same logical slots')
    return {'target': target, 'all_parked_bindings_checked': True,
            'fixed_public_output_preserved': True, 'backend_output_rebound': True}


def visited_bound(volumes, overhead=0):
    """Exact finite-history accounting identity, *not* a physical allocator.

    volumes is a sequence of snapshots mapping fixed physical role IDs to the
    visited extents reached so far. Clears cannot reduce a role's contribution.
    """
    need(type(overhead) is int and overhead >= 0, 'nonnegative fixed backing')
    maxima = {}
    for snapshot in volumes:
        need(isinstance(snapshot, dict), 'fixed-role extent snapshot')
        for role, extent in snapshot.items():
            need(type(extent) is int and extent >= 0, 'nonnegative visited extent')
            maxima[role] = max(maxima.get(role, 0), extent)
    return overhead + sum(maxima.values())


def checks():
    inv = inventory(3)
    need(inv['A_original'] == 2*9+100696823, 'source total restored')
    need(inv['B_protocol_only']-inv['A_original'] == inv['B_increment'],
         'fair B charged one additional controller, no QQ16 auxiliaries')
    need(visited_bound([{'a':10,'b':3},{'a':0,'b':7}]) == 17,
         'historical high-water survives erasure')
    need(visited_bound([{'a':10,'b':3},{'a':3,'b':10}]) == 20,
         'role exchange may enlarge both physical historical maxima')
    failures=[]
    for name, thunk in [('negative backing', lambda: visited_bound([{'a':-1}])),
                        ('nonintegral fixed parameter', lambda: inventory(True))]:
        try: thunk()
        except ValueError: failures.append(name)
        else: raise ValueError('accepted resource mutation: '+name)
    return {'status':'PASS_RESOURCE_ACCOUNTING', 'inventory_at_q3':inv,
            'high_water_clear_control':17, 'high_water_exchange_control':20,
            'rejected':failures,
            'limits':'Constructor/source hypotheses and adapter lifecycle proof required; no production allocation claimed.'}


def adoption_controls(adapter_class, Tape):
    """Actual Tape role/guard controls, explicitly synthetic fixed-control cuts.

    This does not replace the comparative fixture's reached native call cuts.
    It isolates all-alias and wrong-head rejection at the new transfer site.
    """
    from types import SimpleNamespace
    from words import BLANK
    def cut():
        parent = object.__new__(adapter_class)
        parent.binding = SimpleNamespace(slots=2, private=1)
        parent.roles = {'current':Tape(), 'header':Tape()}
        parent.bank = SimpleNamespace(packets=(Tape(),Tape()), output=Tape())
        parent.private = (Tape(),)
        parent.output = Tape()
        parent.capsule = {'current':Tape()}
        parent.parked = (*parent.roles.values(), *parent.bank.packets, *parent.private)
        parent.parking = SimpleNamespace(roles=parent.parked, stack=Tape(), reverse=Tape())
        parent.native_child = SimpleNamespace(output=Tape(), closed=True)
        for t in (*parent.bank.packets, *parent.private):
            for b in (1,0,1,1):t.append(b)
            t.rewind()
        for b in (0,1,1,0):parent.native_child.output.append(b)
        parent.native_child.output.rewind()
        return parent
    successes=[]
    for target in (0,2):
        parent=cut(); old=parent.packet(target); result=parent.native_child.output
        public=parent.output
        parent.adopt_return(target,result)
        binding_tuple(parent)
        need(parent.packet(target) is result and parent.native_child.output is old
             and parent.output is public and old.read() == BLANK,
             'completed bank/private transfer all bindings')
        successes.append('bank' if target==0 else 'private')
    rejected=[]
    for name in ('stale_parked_order','stale_parking_roles','protected_output_alias',
                 'wrong_return_head','wrong_target_head'):
        parent=cut();result=parent.native_child.output
        if name=='stale_parked_order':
            parent.parked=parent.parked[::-1];parent.parking.roles=parent.parked
        elif name=='stale_parking_roles':parent.parking.roles=parent.parked[::-1]
        elif name=='protected_output_alias':parent.output=result
        elif name=='wrong_return_head':result.step(1)
        else:parent.packet(0).step(1)
        try:parent.adopt_return(0,result)
        except ValueError:rejected.append(name)
        else:raise ValueError('accepted adoption mutation: '+name)
    return {'status':'PASS_ADOPTION_RESOURCE_CONTROLS',
            'physical_role_successes':successes, 'rejected':rejected,
            'scope':'Synthetic fixed-control cuts with actual source Tape and adapter; reached cuts tested separately.'}


def primitive_history_fingerprint(bundle):
    """Checker-only digest of closed primitive state, including allocator order.

    bundle is the canonical (scalar, leaf, monomial) tuple. Physical identities,
    meters and historical blank backing are deliberately excluded; finite free
    queues, active leases, current heads and meaningful symbols are included.
    This is an oracle, never a machine implementation or a runtime selector.
    """
    import hashlib, json
    from words import BLANK
    need(type(bundle) is tuple and len(bundle)==3, 'canonical primitive bundle tuple')
    Tape=type(bundle[0].output)  # source constructor name may be sealed at a cut
    seen=set(); states=[]
    ignored={'binding','catalogue','topology','programs','program','recipes',
             'recipe','actions','observe','codes','specifications','meter',
             'counts','codec_counts','last_fitted','context','geometry_state',
             'transform','manager','available','live','cells','head'}
    def visit(value,path):
        if id(value) in seen:return
        seen.add(id(value))
        if isinstance(value,Tape):
            meaningful=bytes(value.cells).rstrip(bytes([BLANK]))
            states.append((path,'tape',value.head,meaningful.hex()))
            return
        if isinstance(value,dict):
            for key in sorted(value,key=repr):visit(value[key],path+'['+repr(key)+']')
        elif isinstance(value,(tuple,list)):
            for index,child in enumerate(value):visit(child,path+'['+str(index)+']')
        elif hasattr(value,'__dict__') and not isinstance(value,type):
            attrs=vars(value)
            if 'available' in attrs:
                states.append((path,'available',list(attrs['available'])))
            if 'live' in attrs:
                live=attrs['live']
                states.append((path,'live',sorted(live)))
            if 'closed' in attrs:states.append((path,'closed',attrs['closed']))
            if 'initialized' in attrs:states.append((path,'initialized',attrs['initialized']))
            if 'heads' in attrs and 'tapes' in attrs and isinstance(attrs['tapes'],list) and all(isinstance(t,dict) for t in attrs['tapes']):
                states.append((path,'codec',list(attrs['heads']),
                               [sorted(t.items()) for t in attrs['tapes']]))
            for name,child in attrs.items():
                if name not in ignored:visit(child,path+'.'+name)
    for name,obj in zip(('scalar','leaf','monomial'),bundle):visit(obj,name)
    raw=json.dumps(states,sort_keys=True,separators=(',',':')).encode()
    return {'sha256':hashlib.sha256(raw).hexdigest(),
            'state_records':len(states),
            'available_queues':sum(row[1]=='available' for row in states),
            'tape_states':sum(row[1]=='tape' for row in states),
            'scope':'finite fixture oracle; excludes control compilation, meters and historical blank backing'}


def primitive_history_control(bundle):
    """A blank-engine history mutation must not pass the matching-state oracle."""
    arena=bundle[2].compact.binary.native.banks[0]
    need(not arena.live and len(arena.available)>1, 'closed finite arena for history control')
    before=primitive_history_fingerprint(bundle)
    saved=list(arena.available)
    try:
        arena.available[0],arena.available[-1]=arena.available[-1],arena.available[0]
        after=primitive_history_fingerprint(bundle)
        need(before['sha256']!=after['sha256'], 'reject false blank-state cancellation')
    finally:
        arena.available[:]=saved
    need(primitive_history_fingerprint(bundle)==before, 'history mutation restored exactly')
    return {'status':'PASS_PRIMITIVE_HISTORY_CONTROL',
            'closed_free_order_mutation_detected':True,
            'original_state_restored':True}
