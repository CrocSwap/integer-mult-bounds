"""Sample descendants even when timeout or child tools create process groups.
This is a sampled watchdog, not a kernel-enforced memory limit.
"""
import os, signal, subprocess
class ProcessTreeWatch:
    def __init__(self, root):
        self.root=root
        self.known={root}
        self.groups={root}
    def sample(self):
        table={}
        for line in subprocess.check_output(['ps','-axo','pid=,ppid=,pgid=,rss='],text=True).splitlines():
            fields=line.split()
            if len(fields)==4:
                pid,ppid,pgid,rss=map(int,fields);table[pid]=(ppid,pgid,rss)
        # Drop exited PIDs between samples to reduce risk of PID reuse.
        self.known.intersection_update(table)
        if self.root in table:self.known.add(self.root)
        changed=True
        while changed:
            changed=False
            for pid,(ppid,pgid,rss) in table.items():
                if pid not in self.known and (ppid in self.known or pgid==self.root):
                    self.known.add(pid);changed=True
        self.groups={table[pid][1] for pid in self.known}
        return sum(table[pid][2] for pid in self.known),dict((pid,table[pid]) for pid in self.known)
    def stop(self):
        self.sample()
        # Kill children individually too: groups can differ from the root group.
        for pid in sorted(self.known-{self.root},reverse=True):
            try:os.kill(pid,signal.SIGKILL)
            except ProcessLookupError:pass
        try:os.killpg(self.root,signal.SIGKILL)
        except ProcessLookupError:pass
