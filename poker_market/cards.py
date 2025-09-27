import random
from typing import Dict, List, Sequence

SUITS_ORDER = ["d", "c", "h", "s"]

DEFAULT_MULTIPLIERS: Dict[str, int] = {"d": -10, "c": 10, "h": -10, "s": 10}
DEFAULT_SUITS: Sequence[str] = ("c", "h", "s")  # diamonds excluded by default

def build_deck(suits: Sequence[str]) -> List[str]:
    deck: List[str] = []
    for suit in suits:
        for rank in range(1, 14):
            deck.append(f"{suit}{rank}")
    return deck

def shuffle_deck(deck: List[str], rng: random.Random) -> None:
    rng.shuffle(deck)

def card_value(card: str, multipliers: Dict[str, int]) -> int:
    suit = card[0]
    rank = int(card[1:])
    return multipliers[suit] * rank

def validate_suits_and_multipliers(
    suits: Sequence[str],
    multipliers: Dict[str, int],
) -> None:
    if not suits:
        raise ValueError("At least one suit must be enabled.")
    for s in suits:
        if s not in DEFAULT_MULTIPLIERS:
            raise ValueError(f"Unknown suit: {s}")
        if s not in multipliers:
            raise ValueError(f"Missing multiplier for suit {s}")

def pretty_cards(cards: Sequence[str]) -> str:
    return "[" + ", ".join(cards) + "]"