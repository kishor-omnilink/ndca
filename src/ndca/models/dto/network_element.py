from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class NetworkElementDTO:

    ne_id: str
    ne_name: str

    admin_state: Optional[str] = None
    oper_state: Optional[str] = None
    availability_state: Optional[list] = None
    description: Optional[str] = None
    source_type: Optional[str] = None