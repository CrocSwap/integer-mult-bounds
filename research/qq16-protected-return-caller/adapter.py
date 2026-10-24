"""Opt-in exact-caller protected-return adoption with installation inventories.

Chris R / Clear1nsight's original return transaction is supplied unchanged from
its authenticated archive. New cross-caller inventory composition: JoyboyBrian,
with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
import types


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rewrite_return(method, producer_source, replacement):
    """Retain the complete source entry; replace only transfer + marker erase."""
    tree = ast.parse(producer_source)
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                 and n.name == 'enter_child']
    need(len(functions) == 1, 'one original external child entry')
    function = functions[0]
    anchors = [i for i, n in enumerate(function.body)
               if ast.unparse(n) == 'transfer(result, self.packet(target))']
    need(len(anchors) == 1 and
         ast.unparse(function.body[anchors[0]+1]) == 'erase_marker(result)',
         'exact fixed protected-return interval')
    function.body[anchors[0]:anchors[0]+2] = ast.parse('_return_protocol(self, target, result)').body
    env = dict(method.__func__.__globals__)
    env.update(zip(method.__func__.__code__.co_freevars,
                   (cell.cell_contents for cell in method.__func__.__closure__ or ())))
    env['_return_protocol'] = replacement
    code = compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])),
                   method.__func__.__code__.co_filename, 'exec')
    exec(code, env)
    return env['enter_child']


class ReturnProtocol:
    """Finite role tables only; payload lengths never control the transaction."""
    def __init__(self, parent, installation, owned_tapes, adopt_return,
                 transfer, erase_marker, *, mode='adopt', observe=None):
        need(mode in ('fixed', 'adopt', 'stale-engines', 'stale-external'), 'known return variant')
        self.parent, self.installation = parent, installation
        self.owned_tapes, self.adopt_return = owned_tapes, adopt_return
        self.transfer, self.erase_marker = transfer, erase_marker
        self.mode, self.observe = mode, observe
        roles = installation.engine_roles
        self.auxiliary = installation.storage.external_roles[len(roles[0])+len(roles[1]):]
        need(parent.native_child is installation.native_child and
             installation.service.native_child is installation.native_child,
             'exact sequential original backend')
        self.check_inventory()

    def check_inventory(self):
        i = self.installation
        actual = (self.owned_tapes(i.service), self.owned_tapes(i.native_child))
        for saved, current in zip(i.engine_roles, actual, strict=True):
            need(len(saved) == len(current) == len({id(t) for t in saved}) and
                 {id(t) for t in saved} == {id(t) for t in current},
                 'current complete engine inventory')
        combined = (*i.engine_roles[0], *i.engine_roles[1])
        need(len({id(t) for t in combined}) == len(combined), 'disjoint current engine inventories')
        need(not {id(t) for t in self.owned_tapes(self.parent)}.intersection(map(id, combined)),
             'producer disjoint from current engine inventories')
        external = (*combined, *self.auxiliary)
        need(len(i.storage.external_roles) == len(external) and
             all(a is b for a, b in zip(i.storage.external_roles, external, strict=True)),
             'current complete external inventory')
        i.storage._distinct()

    @staticmethod
    def exchange(roles, old, new):
        need(sum(t is old for t in roles) == 1 and all(t is not new for t in roles),
             'one finite role replacement')
        return tuple(new if t is old else t for t in roles)

    def __call__(self, caller, target, result):
        i = self.installation
        need(caller is self.parent or caller is i.service, 'one of the two installed callers')
        need(i.native_child.closed and result is i.native_child.output,
             'closed original protected return')
        # These checks inspect fixed object bindings, never payload cells/lengths.
        if self.mode != 'stale-engines':
            self.check_inventory()
        old = caller.packet(target)
        before = self.observe('before', caller, old, result) if self.observe else None
        if self.mode == 'fixed':
            self.transfer(result, old)
            self.erase_marker(result)
        else:
            self.adopt_return(caller, target, result)
            if self.mode != 'stale-engines':
                service, native = i.engine_roles
                if caller is i.service:
                    service = self.exchange(service, old, result)
                native = self.exchange(native, result, old)
                i.engine_roles = service, native
                if self.mode != 'stale-external':
                    i.storage.external_roles = (*service, *native, *self.auxiliary)
                self.check_inventory()
        if self.observe:
            self.observe('after', caller, old, result, before)


def install(parent, installation, owned_tapes, producer_source, adopt_return,
            transfer, erase_marker, *, mode='adopt', observe=None):
    """Install before input, after the original connection factory has succeeded."""
    need(parent.closed and installation.service.closed and installation.native_child.closed
         and installation.calls == 0, 'closed original installation before first input')
    protocol = ReturnProtocol(parent, installation, owned_tapes, adopt_return,
                              transfer, erase_marker, mode=mode, observe=observe)
    for caller in (parent, installation.service):
        method = rewrite_return(caller.enter_child, producer_source, protocol)
        caller.enter_child = types.MethodType(method, caller)
    # The protocol is held by function globals, never inserted in an inventoried
    # engine object: owned_tapes must not recursively acquire another controller.
    return protocol
