# SPDX-License-Identifier: Apache-2.0
"""Generic original-arithmetic external child adapter and internal return swap.

Chris R with OpenAI Codex assistance. The fixed-copy boundary adapts #4166
(Jose Manuel's original #3385 Machine remains the child implementation).
The optional return swap adapts Tekalign's #3380 finite-role idea at a new site.
Dependencies must be authenticated before this module is instantiated.
"""

def need(ok, message):
    if not ok:
        raise ValueError(message)


def machine_class(Machine, Count, transfer, erase_marker):
    from words import BLANK, LEFT
    class ExternalMachine(Machine):
        def __init__(self, binding, native, catalogue, native_child, *, adopt=False,
                     observe=None, shared=True):
            need(native_child is not self and native_child.closed,
                 'separate closed original child controller')
            if shared:
                # Source Machine constructor restricted to controller storage.
                # The exact existing primitive bundle is lent sequentially.
                from bank_packets import BankPackets
                from records import Tape
                from scratch_pool import ScratchPool
                from session import OuterScope
                from parking import Parking, FiniteFields
                from machine import INPUTS, DERIVED
                need(binding is native_child.binding,
                     'shared baseline retains the exact original binding')
                self.binding = binding
                self.bank = BankPackets(binding.families, binding.cover.size, binding.slots)
                self.private = tuple(Tape() for _ in range(binding.private))
                self.roles = {name: Tape() for name in ('current', 'header', *INPUTS, *DERIVED)}
                self.capsule = {name: Tape() for name in ('current', *INPUTS)}
                self.output = Tape()
                self.pool = ScratchPool(256)
                self.scope = OuterScope(self.pool)
                self.scalar, self.leaf, self.monomial = (native_child.scalar,
                    native_child.leaf, native_child.monomial)
                self.parked = (*self.roles.values(), *self.bank.packets, *self.private)
                self.parking = Parking(self.parked)
                groups = max(1, *(binding.group_count(i) for i in range(len(binding.events))))
                self.header = FiniteFields((2, len(binding.events), groups, binding.cover.size,
                    65536, binding.slots + binding.private, binding.dimension))
                self.root = True
                self.event = self.subgroup = self.cover_index = self.pc = 0
                self.group = None
                self.mode = 'closed'
                self.closed = True
                self.observe = observe
            else:
                super().__init__(binding, native, catalogue, observe)
                need(native_child.monomial.compact.binary.native is not native,
                     'distinct ordinary inventories for independent experiment')
            self.native_child = native_child
            self.shared_primitives = bool(shared)
            self.primitive_bundle = (self.scalar, self.leaf, self.monomial)
            self.adopt_child_return = bool(adopt)
            self.external_calls = 0
            self.retired = False

        def run(self, payload, descriptors):
            need(not self.retired and self.closed and self.native_child.closed,
                 'closed external caller and original child')
            need(self.native_child.output.read() == BLANK,
                 'consume preceding dedicated child output')
            self.external_calls = 0
            return super().run(payload, descriptors)

        def enter_child(self):
            need(self.scope.manager is None,
                 'parent allocator released before external child')
            self.primitive_boundary()
            if self.shared_primitives:
                need(self.primitive_bundle == (self.scalar, self.leaf, self.monomial) ==
                     (self.native_child.scalar, self.native_child.leaf, self.native_child.monomial),
                     'exact shared primitive bundle with exclusive sequential lease')
                need(self.native_child.closed and self.native_child.scope.manager is None,
                     'no simultaneous primitive or child controller lease')
            root, event, subgroup, cover, next_pc, target, rank = self.header.read(
                self.roles['header'])
            need((bool(root), event, subgroup, cover, next_pc) ==
                 (self.root, self.event, self.subgroup, self.cover_index, self.pc + 1),
                 'prepared child belongs to current source instruction')
            need(self.group.code[self.pc][0] == 'child' and
                 self.group.code[self.pc][2:] == (target, rank),
                 'literal prepared child target and rank')
            descriptors = {}
            for name, tape in self.capsule.items():
                if name != 'current':
                    value = object.__new__(Count)
                    value.tape = tape
                    descriptors[name] = value
            result = self.native_child.run(self.capsule['current'], descriptors)
            need(self.native_child.closed and result is self.native_child.output,
                 'closed original child protected return')
            if self.adopt_child_return:
                self.adopt_return(target, result)
            else:
                transfer(result, self.packet(target))
                erase_marker(result)
            for tape in self.capsule.values():
                tape.clear()
            self.roles['header'].clear()
            self.pc = next_pc
            self.external_calls += 1
            if self.observe:
                self.observe(self, 'external-child-return')

        def adopt_return(self, target, result):
            """Exchange two exclusively owned internal physical roles.

            Finite source target selectors carry no input-dependent addressing.
            Only fixed binding tables change; no payload inspection or copied
            data substitutes for the explicit erasure of the old packet.
            """
            old = self.packet(target)
            need(result is self.native_child.output and old is not result,
                 'exclusive protected return and target')
            need(result not in (*self.parked, *self.capsule.values(), self.output,
                                self.bank.output, self.parking.stack, self.parking.reverse),
                 'protected return has no caller alias')
            need(len({id(t) for t in self.parked}) == len(self.parked) and
                 self.parking.roles == self.parked and
                 self.parked == (*self.roles.values(), *self.bank.packets, *self.private) and
                 self.parked.count(old) == 1,
                 'complete current parked-role bindings')
            for tape in (old, result):
                tape.step(-1)
                try:
                    need(tape.read() == LEFT, 'canonical adopted return and target heads')
                finally:
                    tape.step(1)
            # Both bodies are at their canonical head under the Machine return
            # contract. Clear is a physical walk; high-water backing persists.
            old.clear()
            erase_marker(old)
            if target < self.binding.slots:
                self.bank.packets = tuple(result if i == target else t
                    for i, t in enumerate(self.bank.packets))
            else:
                slot = target - self.binding.slots
                self.private = tuple(result if i == slot else t
                    for i, t in enumerate(self.private))
            self.parked = (*self.roles.values(), *self.bank.packets, *self.private)
            self.parking.roles = self.parked
            self.native_child.output = old

        def discard(self):
            # Source exception handling invokes this only at controlled heads.
            super().discard()
            self.native_child.discard()
    return ExternalMachine


def install(root_layer, ordinary_factory=None, *, adopt=False, shared=True):
    """Compile-time variant B: original binding, two controllers sharing primitives.

    The retained original root Machine becomes the dedicated child. Root plan,
    payload ports, numerical geometry, selected arithmetic and external output
    identity are unchanged. Shared mode allocates only fixed controller storage;
    the independent mode is a finite experimental comparator only.
    """
    from machine import Machine, transfer
    from cardinal_counts import Count
    from session import erase_marker
    need(root_layer.closed and root_layer.machine.closed,
         'closed RootLayer construction')
    original = root_layer.machine
    native = None if shared else ordinary_factory()
    if not shared:
        need(native is not original.monomial.compact.binary.native,
             'distinct original and added ordinary engine')
    parent = machine_class(Machine, Count, transfer, erase_marker)(
        original.binding, native, original.scalar.recipes, original, adopt=adopt, shared=shared)
    from resources import fixed_engine_tapes
    from records import Tape
    if shared:
        # Only newly allocated controller roles belong to the extra inventory.
        parent.retirement_tapes = tuple(dict.fromkeys((
            *parent.parked, *parent.capsule.values(), parent.output,
            parent.bank.output, *parent.bank.pool.tapes, *parent.pool.tapes,
            parent.parking.stack, parent.parking.reverse)))
    else:
        parent.retirement_tapes = fixed_engine_tapes(parent, Tape)
    root_layer.machine = parent
    return parent


def retire_installed(root_layer):
    """Pay final marker retirement after the last call; future reuse is illegal.

    RootLayer.run has already consumed the internal Machine output when this is
    used at the complete outer boundary. Its public result tape is untouched.
    The finite extra-role tuple was compiled before any payload was loaded.
    """
    from resources import retire_empty_roles
    from words import BLANK
    parent = root_layer.machine
    need(root_layer.closed and parent.closed and parent.native_child.closed and
         not parent.retired and parent.output.read() == BLANK,
         'closed consumed final installed call before retirement')
    count = retire_empty_roles(parent.retirement_tapes,
        codec=None if parent.shared_primitives else parent.monomial.compact.binary.native.runtime.numerical)
    parent.retired = True
    return count
