"""Bounded package-local reader for NEW Unit13 static DATA only.

Only literal inputs/input-NNN.data members are read. No arbitrary manifest-path
fallback, original module imports/execution, native observations or admission.
"""
from __future__ import annotations
import os
import stat
import sys
from at_random_producer_v2 import SOURCE_PINS,FILE_CAP,TOTAL_CAP,FormatError,authenticate_sources,make_witness,check_witness

ATTEMPTS=[]


class ReaderState:
    def __init__(self):
        self.first=None;self.cleanup=[];self.fds=[];self.records=[];self.total=0;self.calls=0;self.pending=False
    def fail(self,error):
        if self.first is None:self.first=error
        elif error is not self.first:self.cleanup.append(error)
        return self.first
    def slot(self):self.fds.append(None);return len(self.fds)-1
    def close(self,index):
        fd=self.fds[index];self.fds[index]=None
        if fd is not None:
            try:os.close(fd)
            except BaseException as error:self.fail(error)


def require(condition,code):
    if condition is not True:raise FormatError(code)


def metadata(info):
    return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns)


def read_package(directory):
    """Read authenticated fixed corpus; state survives all read/cleanup failures."""
    state=ReaderState();ATTEMPTS.append(state);result=None
    try:
        require(type(directory) is str and directory.startswith('/') and len(directory)<=4096 and directory.isascii(),'package_absolute_path')
        parts=directory.split('/')[1:]
        require(len(parts)<=64 and all(part not in ('','.','..') for part in parts),'package_path_spelling')
        root=state.slot();state.pending=True
        state.fds[root]=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);state.pending=False
        inputs=state.slot();state.pending=True
        state.fds[inputs]=os.open('inputs',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=state.fds[root]);state.pending=False
        before_root=metadata(os.fstat(state.fds[root]));before_inputs=metadata(os.fstat(state.fds[inputs]));bundle={}
        for role,(identifier,size,digest) in SOURCE_PINS.items():
            name='input-%03d.data'%identifier
            record={'role':role,'member':name,'chunks':[],'raw':None,'calls':0,'metadata':None};state.records.append(record)
            index=state.slot();state.pending=True
            state.fds[index]=os.open(name,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=state.fds[inputs]);state.pending=False
            try:
                before=os.fstat(state.fds[index]);record['metadata']=metadata(before)
                require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size==size and size<=FILE_CAP,'package_member_kind_size')
                count=0
                while count<size:
                    require(record['calls']<8192,'package_read_calls');record['calls']+=1;state.calls+=1
                    block=os.read(state.fds[index],min(65536,size-count));record['chunks'].append(block)
                    require(type(block) is bytes and 0<len(block)<=size-count,'package_read_progress')
                    count+=len(block);state.total+=len(block);require(state.total<=TOTAL_CAP,'package_aggregate')
                record['raw']=b''.join(record['chunks']);bundle[role]=record['raw']
                after=metadata(os.fstat(state.fds[index]));named=metadata(os.stat(name,dir_fd=state.fds[inputs],follow_symlinks=False))
                require(record['metadata']==after==named,'package_member_endpoint_drift')
            except BaseException as error:state.fail(error)
            finally:state.close(index)
            if state.first is not None:raise state.first
        require(before_inputs==metadata(os.fstat(state.fds[inputs])) and before_root==metadata(os.fstat(state.fds[root])),'package_directory_endpoint_drift')
        authenticate_sources(bundle);result=bundle
    except BaseException as error:state.fail(error)
    finally:
        for index in range(len(state.fds)-1,-1,-1):state.close(index)
    if state.first is not None:raise state.first
    return result


def main(argv=None):
    args=sys.argv[1:] if argv is None else argv
    require(type(args) is list and len(args)==1 and type(args[0]) is str,'one_package_argument')
    bundle=read_package(args[0]);raw=make_witness(bundle);check_witness(bundle,raw)
    offset=0;calls=0
    while offset<len(raw):
        require(calls<4096,'stdout_write_calls');calls+=1
        written=sys.stdout.buffer.write(raw[offset:])
        require(type(written) is int and 0<written<=len(raw)-offset,'stdout_write_progress');offset+=written
    sys.stdout.buffer.flush()
    return 0


if __name__=='__main__':raise SystemExit(main())
