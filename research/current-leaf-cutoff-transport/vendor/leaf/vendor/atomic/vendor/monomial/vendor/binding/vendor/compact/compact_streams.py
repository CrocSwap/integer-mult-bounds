"""Literal complete-row rotations, bit gates and exceptional-record repair."""
import native_sources
native_sources.activate()
from compact_counts import (append_bits, bit_at, copy_bits, power_two,
                            read_fixed, write_fixed)
from cardinal_counts import Count
from encoded import compare, subtract
from session import borrowed_tape
from stream import Counter
from words import BLANK, need


def rotate(source, plan, control, operation, factory):
    target = operation[1]
    before, suffix = plan.single_extents(target)
    left, right, output = factory(), factory(), factory()
    try:
        source.rewind()
        for merging in (False,True):
            remaining, ordinal = Counter(before), Count.literal(0)
            try:
                while not remaining.finished:
                    state = plan.prefix_state(ordinal,target)
                    try:
                        cut = control.offset(state,operation,plan)
                    finally:
                        plan.close_state(state)
                    complement = subtract(plan.radices[target],cut)
                    first,second = Count.product(complement,suffix),Count.product(cut,suffix)
                    cut.close()
                    complement.close()
                    try:
                        if merging:
                            copy_bits(right,output,second)
                            copy_bits(left,output,first)
                        else:
                            copy_bits(source,left,first)
                            copy_bits(source,right,second)
                    finally:
                        first.close()
                        second.close()
                    ordinal.increment()
                    remaining.decrement()
            finally:
                remaining.close()
                ordinal.close()
            if not merging:
                need(source.read() == BLANK, "complete rotation source")
                left.rewind()
                right.rewind()
        need(left.read() == right.read() == BLANK, "complete rotation pieces")
        source.clear()
        output.rewind()
        return output
    except BaseException:
        output.clear()
        raise
    finally:
        left.clear()
        right.clear()
        before.close()
        suffix.close()


def digit_permutation(source, plan, first, second, mapping, factory):
    need(compare(first,second) < 0 and compare(second,plan.bits) < 0, "two ordered address bits")
    need(tuple(sorted(mapping)) == (0,1,2,3), "fixed four-state permutation")
    one = Count.literal(1)
    difference, tail = subtract(second,first), subtract(plan.bits,second)
    middle_bits, after_bits = subtract(difference,one), subtract(tail,one)
    before, middle, after = power_two(first),power_two(middle_bits),power_two(after_bits)
    suffix = Count.product(after,plan.record_bits)
    for value in (one,difference,tail,middle_bits,after_bits,after):
        value.close()
    output = factory()
    buckets = tuple(factory() for _ in range(4))
    inverse = tuple(mapping.index(index) for index in range(4))
    prefixes = Counter(before)
    source.rewind()
    try:
        while not prefixes.finished:
            for merging in (False,True):
                for a in range(2):
                    intervening = Counter(middle)
                    try:
                        while not intervening.finished:
                            for b in range(2):
                                if merging:
                                    copy_bits(buckets[inverse[2*a+b]],output,suffix)
                                else:
                                    copy_bits(source,buckets[2*a+b],suffix)
                            intervening.decrement()
                    finally:
                        intervening.close()
                if not merging:
                    for bucket in buckets:
                        bucket.rewind()
            for bucket in buckets:
                need(bucket.read() == BLANK, "complete bit-gate bucket")
                borrowed_tape(bucket).clear()
            prefixes.decrement()
        need(source.read() == BLANK, "complete bit-gate source")
        source.clear()
        output.rewind()
        return output
    except BaseException:
        output.clear()
        raise
    finally:
        for value in (before,middle,suffix,prefixes):
            value.close()
        for bucket in buckets:
            bucket.clear()


def flip_digit(source, plan, position, factory):
    need(compare(position,plan.bits) < 0, "selected address bit exists")
    one, tail = Count.literal(1),subtract(plan.bits,position)
    after_bits = subtract(tail,one)
    before, after = power_two(position),power_two(after_bits)
    suffix = Count.product(after,plan.record_bits)
    for value in (one,tail,after_bits,after):
        value.close()
    left,right,output = factory(),factory(),factory()
    prefixes = Counter(before)
    source.rewind()
    try:
        while not prefixes.finished:
            copy_bits(source,left,suffix)
            copy_bits(source,right,suffix)
            left.rewind()
            right.rewind()
            copy_bits(right,output,suffix)
            copy_bits(left,output,suffix)
            need(left.read() == right.read() == BLANK, "complete flip pieces")
            borrowed_tape(left).clear()
            borrowed_tape(right).clear()
            prefixes.decrement()
        need(source.read() == BLANK, "complete flip source")
        source.clear()
        output.rewind()
        return output
    except BaseException:
        output.clear()
        raise
    finally:
        for value in (before,suffix,prefixes):
            value.close()
        left.clear()
        right.clear()


def stable_radix(source, key_bits, record_bits, factory):
    """LSD partitions on an encoded pass index and two reused physical buckets."""
    position, passes = Count.literal(0),Counter(key_bits)
    current = source
    try:
        while not passes.finished:
            buckets, output = (factory(),factory()),None
            current.rewind()
            try:
                while current.read() != BLANK:
                    key = read_fixed(current,key_bits)
                    try:
                        bucket = buckets[bit_at(key,position)]
                        write_fixed(key,bucket,key_bits)
                        copy_bits(current,bucket,record_bits)
                    finally:
                        key.close()
                current.clear()
                output = factory()
                for bucket in buckets:
                    append_bits(bucket,output)
                output.rewind()
                current,output = output,None
            finally:
                for bucket in buckets:
                    bucket.clear()
                if output is not None:
                    output.clear()
            position.increment()
            passes.decrement()
        return current
    except BaseException:
        current.clear()
        raise
    finally:
        position.close()
        passes.close()


def repair(source, plan, control, factory):
    good,bad,holes = factory(),factory(),factory()
    output = None
    remaining,index = Counter(plan.records),Count.literal(0)
    source.rewind()
    try:
        while not remaining.finished:
            state = plan.decode(index)
            try:
                exceptional = control.bad(state)
                holes.append(int(exceptional))
                if exceptional:
                    control.execute_state(state,plan,True)
                    control.ideal_state(state)
                    destination = plan.encode(state)
                    try:
                        write_fixed(destination,bad,plan.bits)
                        copy_bits(source,bad,plan.record_bits)
                    finally:
                        destination.close()
                else:
                    copy_bits(source,good,plan.record_bits)
            finally:
                plan.close_state(state)
            index.increment()
            remaining.decrement()
        need(source.read() == BLANK, "complete repair input row")
        source.clear()
        remaining.close()
        index.close()
        remaining,index = None,None
        bad.rewind()
        bad = stable_radix(bad,plan.bits,plan.record_bits,factory)
        good.rewind()
        holes.rewind()
        output = factory()
        remaining,index = Counter(plan.records),Count.literal(0)
        while not remaining.finished:
            hole = holes.read()
            need(hole in (0,1), "one repair hole bit per complete record")
            holes.step(1)
            if hole:
                destination = read_fixed(bad,plan.bits)
                try:
                    need(compare(destination,index) == 0, "sorted exceptional destination fills this hole")
                    copy_bits(bad,output,plan.record_bits)
                finally:
                    destination.close()
            else:
                copy_bits(good,output,plan.record_bits)
            index.increment()
            remaining.decrement()
        need(good.read() == bad.read() == holes.read() == BLANK, "complete repair reinsertion")
        output.rewind()
        result,output = output,None
        return result
    finally:
        good.clear()
        bad.clear()
        holes.clear()
        if output is not None:
            output.clear()
        if remaining is not None:
            remaining.close()
        if index is not None:
            index.close()
