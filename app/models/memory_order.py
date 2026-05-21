from dataclasses import dataclass

@dataclass
class MemoryOrder:
    id: int
    symbol: str
    side: str
    type: str
    price: float
    quantity: float
    filled_quantity: float
