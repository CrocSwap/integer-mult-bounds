"""Separate unbounded tapes for products of arbitrary spectator cardinalities."""
from counts import Count as RetainedCount
from words import LEFT, ONE, RIGHT, ZERO, need


class Count(RetainedCount):
    def zero(self):
        self.rewind()
        result=self.read()==ZERO
        self.step(1)
        result=result and self.read()==RIGHT
        self.rewind()
        return result

    def add(self,other):
        source=Count(other)
        self.rewind();source.rewind()
        carry=0;left_done=False
        try:
            while True:
                if not left_done and self.read()==RIGHT:left_done=True
                right_done=source.read()==RIGHT
                if left_done and right_done and not carry:break
                a=ZERO if left_done else self.read()
                b=ZERO if right_done else source.read()
                need(a in (ZERO,ONE) and b in (ZERO,ONE),"binary cardinality sum")
                total=a+b+carry
                self.tape.write(total&1);carry=total>>1
                self.step(1)
                if not right_done:source.step(1)
            self.tape.write(RIGHT)
            self.normalize()
        finally:source.close()

    @classmethod
    def product(cls,left,right):
        factor,scan,result=cls(left),cls(right),cls.literal(0)
        scan.msb()
        try:
            while scan.read()!=LEFT:
                result.multiply_small(2)
                if scan.read()==ONE:result.add(factor)
                else:need(scan.read()==ZERO,"binary multiplier digit")
                scan.step(-1)
            scan.step(1)
            return result
        except ValueError:
            result.close()
            raise
        finally:
            factor.close();scan.close()


def positive(value):
    need(isinstance(value,Count) and not value.zero(),"independent positive cardinality tape")
