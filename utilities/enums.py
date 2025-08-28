
from enum import Enum

# HTTP method definition using Enum
class HttpMethod(Enum):
    GET: int = 0
    POST: int = 1

# Operation mode using Enum
class Mode(Enum):
    static: int = 0 # Mode.value -> int, Mode.name -> str
    teleoperation: int = 1
    mapping: int = 2
