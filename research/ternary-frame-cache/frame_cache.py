"""Exact, invocation-local frame interning and ordered transition reuse.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
The supplied rank and subtraction routines remain the retained rational ones.
"""


class FrameCache:
    def __init__(self, rank, sub):
        self.rank = rank
        self.sub = sub
        self.frames = []
        self.by_value = {}
        # Keep the object alive alongside its index: id() reuse is impossible.
        self.by_identity = {}
        self.transitions = {}
        self.calls = 0

    def intern(self, frame):
        identity = id(frame)
        prior = self.by_identity.get(identity)
        if prior is not None:
            return prior[1]
        # Tuple equality, not a digest or rank, identifies exact rational frames.
        index = self.by_value.get(frame)
        if index is None:
            index = len(self.frames)
            self.frames.append(frame)
            self.by_value[frame] = index
        self.by_identity[identity] = (frame, index)
        return index

    def transition(self, old, new):
        self.calls += 1
        key = (self.intern(old), self.intern(new))
        answer = self.transitions.get(key)
        if answer is None:
            answer = (self.rank(self.sub(new, old)),
                      self.rank(new) - self.rank(old))
            self.transitions[key] = answer
        return answer

    def statistics(self):
        return dict(edge_calls=self.calls, exact_frames=len(self.frames),
                    ordered_pairs=len(self.transitions),
                    hits=self.calls - len(self.transitions),
                    retained_matrix_objects=len(self.by_identity))
