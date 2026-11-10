"""Complete internal node: peel, fresh rows, recursive caller and return."""
from cardinal_counts import Count, positive
from cardinality import multiply_atom_power
from consumer import Consumer, IncomingWeights
from driver import Driver
import fresh_rows
from packet import read_prefix
import peel
from plan import Request
from topology import SelectedTopology
from words import Unsigned, need
from scheduler import complete


def selected_topology(catalogue):
    """One immutable source table per catalogue, shared by every frame.

    The retained topology's recipe/call caches include its identity in their
    keys. Recreating that identity per child would retain source-table copies
    after those children returned. Keep the single owner on the fixed-q
    catalogue instead of introducing another global frame-keyed cache.
    """
    result=getattr(catalogue,"_recursive_caller_topology",None)
    if result is None:
        result=SelectedTopology(catalogue)
        catalogue._recursive_caller_topology=result
    need(result.catalogue is catalogue,"selected topology belongs to its fixed source")
    return result


class Node:
    def __init__(self,context,indices,program,parent_size,depth,topology,consumer,incoming,stock_multiple=1):
        self.context,self.indices,self.program=context,indices,program
        self.parent_size,self.depth=parent_size,depth
        self.topology,self.consumer,self.incoming=topology,consumer,incoming
        self.stock_multiple=stock_multiple
        raw=Unsigned(indices);dimension,one=indices.literal(context.dimension),indices.literal(1)
        columns,remainder=raw.divmod(parent_size,dimension)
        valid=not columns.zero()
        indices.free_many(dimension,one,columns,remainder)
        need(valid,"complete internal node width")

    def run(self,*args,**kwargs):
        return complete(self.run_generator(*args,**kwargs))

    def run_generator(self,source,old_directory,old_count,row_count,before,gap,suffix,observe=None):
        old_count,row_count,before,gap,suffix=(Count(value) for value in (old_count,row_count,before,gap,suffix))
        for value in (old_count,row_count,before,gap,suffix):positive(value)
        context,indices=self.context,self.indices
        unused=leading=fibre=None;peeled=None;families={}
        try:
            old_directory.rewind();first=read_prefix(old_directory,self.depth);old_directory.rewind()
            zero=indices.zero()
            try:
                value=self.incoming.coefficient(first,Request("incoming",zero))
                context.arena.free(value)
            finally:first.clear();indices.free(zero)
            unused=fresh_rows.quotient(row_count,context,self.topology.families)
            stock=Count(unused)
            try:need(stock.divide_small(self.stock_multiple)==0,"selected compatible unused stock factor")
            finally:stock.close()
            leading=Count.product(unused,before)
            fibre=Count.product(leading,gap)
            total=Unsigned(indices).times_small(self.parent_size,2)
            multiply_atom_power(fibre,total,context.ring,context.q);indices.free(total)
            following=Count.product(fibre,suffix);fibre.close();fibre=following
            peeled=peel.run(source,context,indices,self.parent_size,self.depth,self.program,
                            old_directory,old_count,row_count,before,gap,suffix,self.incoming)
            families=fresh_rows.split(peeled,context,self.topology.families,old_count,fibre)
            driver=Driver(context,self.topology,self.consumer,old_directory,old_count,leading,gap,suffix,fibre,observe,child_stock=unused,child_before=before)
            yield from driver.global_word(families)
            return fresh_rows.merge(families,context,self.topology.families,old_count,fibre)
        finally:
            for tape in families.values():tape.clear()
            if peeled is not None and peeled is not source:peeled.clear()
            for value in (unused,leading,fibre,old_count,row_count,before,gap,suffix):
                if value is not None:value.close()
            source.rewind();old_directory.rewind()


class SelectedNode(Node):
    def __init__(self,context,indices,program,parent_size,depth,catalogue,specifications):
        need(context.dimension==64 and context.codes is catalogue.codes and
             specifications.catalogue is catalogue,"one source-bound selected node")
        topology=selected_topology(catalogue)
        consumer=Consumer(context,indices,program,specifications,parent_size,depth)
        incoming=IncomingWeights(context,indices,program,specifications,parent_size,depth)
        super().__init__(context,indices,program,parent_size,depth,topology,consumer,incoming,9475)
