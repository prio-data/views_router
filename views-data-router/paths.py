"""
Basic path operations for providing richer routing
I'll write a proper path parser once I have a little more time to spend
"""
import re
from operator import add
from typing import Callable,Any
from functools import partial
from pydantic import BaseModel
from pydantic import constr
import settings

router_path = constr(regex="")

PATH_YEAR = r"[0-9]{4}(?=/[a-z]+/?$)"

class Path(BaseModel):
    path: router_path
    year: int

    @classmethod
    def from_path_string(cls,path_string:router_path):
        return cls(path=path_string,year = path_year(path_string))

class PathBounds(BaseModel):
    start: Path 
    end: Path 

class PathNav(BaseModel):
    bounds: PathBounds
    next: Path 
    previous: Path 
    current: Path

def year_manipulation(op):
    def inner(path:router_path,*args,**kwargs):
        year = path_year(path)
        path = re.sub(PATH_YEAR,str(op(year,*args,**kwargs)),path)
        return path
    return inner

year_add = year_manipulation(add) 
year_replace = year_manipulation(lambda _,y: y)

def path_year(path):
    year = re.search(PATH_YEAR,path)
    try:
        assert year is not None
    except AssertionError as ae:
        raise ValueError(f"Year not found in path: {path}") from ae
    else:
        return int(year[0])

def nav_summary(path_string):
    return PathNav(
            bounds=PathBounds(
                start=Path.from_path_string(year_replace(path_string,settings.DB_MIN_YEAR)),
                end=Path.from_path_string(year_replace(path_string,settings.DB_MAX_YEAR))
                ),
            current = Path.from_path_string(path_string),
            next = Path.from_path_string(year_add(path_string,1)),
            previous = Path.from_path_string(year_add(path_string,-1)),
        )
