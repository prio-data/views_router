import os
from typing import List,Dict
import enum
from dataclasses import dataclass
from collections import namedtuple

COMPONENT_PATH_SIZE = 3

is_divisible_by = lambda x,y: (x/y)%1==0

def chunk(x:List[any],chunksize):

    try:
        assert is_divisible_by(len(x),chunksize)
    except AssertionError as ae:
        raise ValueError("Size of list to chunk is not divisible by chunk size") from ae

    n_chunks = int(len(x)/chunksize)
    return [x[i*chunksize:chunksize+(i*chunksize)] for i in range(n_chunks)]


class RemoteKind(enum.Enum):
    transitive=0
    terminal=1

Remote = namedtuple("remote",("name","url","kind"))

class Remotes:

    _REMOTES = {
        RemoteKind.transitive:[
                "trf"
            ],
        RemoteKind.terminal:[
                "base"
            ]
    }

    def __init__(self,**kwargs):
        self.remotes = []
        remotes_kinds = self._remotes_kinds

        for key,value in kwargs.items():
            try:
                assert key in remotes_kinds.keys()
            except AssertionError as ae:
                raise TypeError(f"{key} is not a valid keyword argument for Remotes") from ae
            self.remotes.append(Remote(name=key,url=value,kind=remotes_kinds[key]))

        names = [rmt.name for rmt in self.remotes]
        missing = {k for k in remotes_kinds if k not in names}
        if missing: 
            raise TypeError(f"All remotes must be defined, was missing {missing}")

    def __getitem__(self,key):
        try:
            remote,*_ = [rmt for rmt in self.remotes if rmt.name == key]
        except ValueError as ve:
            raise KeyError(f"Remote {key} not defined") from ve
        return remote

    def _of_kind(self,kind):
        return [rmt for rmt in self.remotes if rmt.kind==kind]

    @property
    def transitive(self):
        return self._of_kind(RemoteKind.transitive)

    @property
    def terminal(self):
        return self._of_kind(RemoteKind.terminal)

    @property
    def _remotes_kinds(self):
        remotes_kinds = dict()
        for remote_kind,remotes in self._REMOTES.items():
            remotes_kinds.update({rmt:remote_kind for rmt in remotes})
        return remotes_kinds 

    @classmethod
    def kind_of(cls,remote_name:str)->str:
        for kind in cls._REMOTES:
            if remote_name in cls._REMOTES[kind]:
                return kind
        raise ValueError(f"{remote_name} not defined as remote")

@dataclass
class Component:
    root: str
    path: str
    args: str

    @property
    def rel_path(self):
        return os.path.join(self.root,self.path,self.args)
    
    @classmethod
    def from_chunk(cls,*args):
        root,path,args = args
        return cls(root=root,path=path,args=args)

@dataclass
class Path:
    path: str
    root: str
    components: List[Component]

    @classmethod
    def parse(cls,path:str):
        """
        Parses and validates the submitted path 
        """
        root,*raw_components = path.split("/") 
        chunks = chunk(raw_components,COMPONENT_PATH_SIZE)
        components = [Component.from_chunk(*chk) for chk in chunks]
        *transitive,terminal = components
        try:
            raised = RemoteKind.terminal
            assert Remotes.kind_of(terminal.root) is RemoteKind.terminal
            raised = RemoteKind.transitive
            for component in transitive:
                assert Remotes.kind_of(component.root) is RemoteKind.transitive
        except AssertionError as ae:
            if raised is RemoteKind.terminal:
                msg = "Final path component must be terminal component (like base)"
            else:
                msg = ("Only final path component can be terminal, " 
                    "others must be transitive (like trf)"
                    )
            raise ValueError(msg) from ae

        return cls(path=path,root=root,components=components)

    def url(self,remotes:Dict[str,str]):
        dest,*rest = self.components
        return os.path.join(
                remotes[dest.root].url,
                self.root,
                dest.path,
                dest.args,
                *[cpt.rel_path for cpt in rest]
            )
