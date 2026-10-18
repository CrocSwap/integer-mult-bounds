"""Transported COPY/XOR/ERASE on staged complete packets and physical families."""
from counts import Count
from directory import produce
from records import Tape
from routes import copy_rows, route_packet
from selection import gather, scatter
from stream import Counter
from words import BLANK, ONE, ZERO, need


def xor_packet(source, target, context, old_count, fibre, factory=Tape):
    output, outer = factory(), Counter(old_count)
    source.rewind()
    target.rewind()
    try:
        while not outer.finished:
            highs = Counter(context.highs)
            while not highs.finished:
                bits = Counter(fibre)
                while not bits.finished:
                    left, right = source.read(), target.read()
                    need(left in (ZERO, ONE) and right in (ZERO, ONE), "aligned Boolean operands")
                    output.append(left ^ right)
                    source.step(1)
                    target.step(1)
                    bits.decrement()
                bits.close()
                highs.decrement()
            highs.close()
            outer.decrement()
        need(source.read() == target.read() == BLANK, "complete aligned XOR")
        output.rewind()
        return output
    except ValueError:
        output.clear()
        raise
    finally:
        outer.close()
        source.rewind()
        target.rewind()


def staged(source, targets, episode, context, old_count, fibre, residual, factory=Tape):
    """Call the concrete residual once, then retain its transported ERASE guard."""
    need(tuple(targets) == episode.targets and len({id(tape) for tape in targets.values()}) == len(targets)
         and all(tape is not source for tape in targets.values()), "distinct staged live roles")
    need(len(episode.records) == len(episode.targets)+2 and
         episode.records[0][:3] == (2,episode.source,episode.private) and
         episode.records[-1][:3] == (3,episode.source,episode.private) and
         episode.records[0][3:5] == episode.records[-1][3:5] and
         all(record[0] == 1 and record[1] == target and record[2] == episode.private
             and record[3] in (-1,1) and target != episode.source
             for target, record in zip(episode.targets, episode.records[1:-1])),
         "closed source-preserving COPY interval")
    initial, outer = factory(), Counter(old_count)
    source.rewind()
    while not outer.finished:
        copy_rows(source, initial, context.highs, fibre)
        outer.decrement()
    outer.close()
    need(source.read() == BLANK, "complete staged COPY source")
    source.rewind()
    initial.rewind()
    private, result = None, {}
    try:
        private = residual(initial)
        need(private is not initial and private is not source and
             all(private is not value for value in targets.values()), "owned transported private result")
        for target in episode.targets:
            result[target] = xor_packet(private, targets[target], context, old_count, fibre, factory)
        # Only reads of private and source occur after the completed transport.
        # The authenticated literal word therefore supplies the transported
        # equality guard; comparison with untransported source would be wrong.
        need(source.head == private.head == 1, "transported source lifetime closes at ERASE")
        return result
    except ValueError:
        for value in result.values():
            value.clear()
        raise
    finally:
        if private is not None and private is not initial and private is not source:
            private.clear()
        initial.clear()


def physical(families, episode, source_route, common_code, context, old_directory,
             old_fields, old_count, fibre, residual, factory=Tape):
    """Gather, route, produce fields, execute, scatter and erase local work.

    residual(source, directory, prefix_count) must execute the completed
    common-view residual and preserve its inputs. The verifier supplies the
    actual PR2501 packet interpreter, including its leaf expansion.
    """
    request, common, low = context.codes.decode(common_code)
    need(common and request == episode.request and low == source_route.target_low
         and source_route.chart == episode.chart, "current common-view source binding")
    source = gather(families[episode.source_family], context, old_count, source_route.low, fibre, factory)
    common_source = directory = prefixes = changed = None
    targets, result = {}, {}
    try:
        common_source = route_packet(source, source_route, context, old_count, fibre, factory)
        for role, family in zip(episode.targets, episode.target_families):
            targets[role] = gather(families[family], context, old_count, low, fibre, factory)
        directory, prefixes = produce(old_directory, old_fields, old_count, common_code, context)
        changed = staged(common_source, targets, episode, context, old_count, fibre,
                         lambda value: residual(value, directory, prefixes), factory)
        for role, family in zip(episode.targets, episode.target_families):
            result[family] = scatter(families[family], changed[role], context, old_count, low, fibre, factory)
        return result
    except ValueError:
        for value in result.values():
            value.clear()
        raise
    finally:
        source.clear()
        if common_source is not None:
            common_source.clear()
        for collection in (targets, changed or {}):
            for value in collection.values():
                value.clear()
        if directory is not None:
            directory.clear()
        if prefixes is not None:
            prefixes.close()
