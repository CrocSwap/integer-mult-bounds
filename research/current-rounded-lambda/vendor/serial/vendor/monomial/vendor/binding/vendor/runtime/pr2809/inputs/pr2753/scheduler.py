"""Iterative evaluator: child depth does not consume the Python call stack."""
from dataclasses import dataclass
from types import GeneratorType
from words import need

@dataclass
class Invocation:
    body: object

def complete(body):
    need(isinstance(body,GeneratorType),"a suspended stream program")
    stack=[body]
    value=None
    try:
        while stack:
            try:
                request=stack[-1].send(value)
            except StopIteration as done:
                stack.pop()
                value=done.value
                continue
            need(isinstance(request,Invocation) and isinstance(request.body,GeneratorType),
                 "only a complete child invocation may suspend the caller")
            stack.append(request.body)
            value=None
        return value
    finally:
        for pending in reversed(stack): pending.close()
