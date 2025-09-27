from typing import Dict, Iterable, List, Tuple
from .cards import card_value

def sum_cards(cards: Iterable[str], multipliers: Dict[str, int]) -> int:
    return sum(card_value(c, multipliers) for c in cards)

def expected_value_per_remaining_card(remaining: List[str], multipliers: Dict[str, int]) -> float:
    if not remaining:
        return 0.0
    total = sum_cards(remaining, multipliers)
    return total / len(remaining)

def expected_final_table_value(
    player_card: str,
    community_cards: List[str],
    remaining_deck: List[str],
    multipliers: Dict[str, int],
    num_flops_total: int,
    num_players: int,
) -> float:
    # Known values
    pv = card_value(player_card, multipliers)
    cv = sum_cards(community_cards, multipliers)

    # Unknown: remaining community cards + all other private cards
    remaining_comm = num_flops_total - len(community_cards)
    unknown_private = num_players - 1
    num_unknown = remaining_comm + unknown_private

    ev_per_card = expected_value_per_remaining_card(remaining_deck, multipliers)
    ev_unknown = ev_per_card * num_unknown
    return pv + cv + ev_unknown

def infer_bot_private_value_from_quotes(
    bid: int,
    ask: int,
    community_cards: List[str],
    remaining_deck: List[str],
    multipliers: Dict[str, int],
    num_flops_total: int,
    num_players: int,
) -> float:
    midpoint = 0.5 * (bid + ask)
    cv = sum_cards(community_cards, multipliers)

    remaining_comm = num_flops_total - len(community_cards)
    unknown_private = num_players - 1
    num_unknown = remaining_comm + unknown_private

    ev_per_card = expected_value_per_remaining_card(remaining_deck, multipliers)
    ev_unknown = ev_per_card * num_unknown

    # midpoint = bot_card_value + cv + ev_unknown
    return midpoint - cv - ev_unknown

def combine_ev_components(
    player_card: str,
    community_cards: List[str],
    remaining_deck: List[str],
    multipliers: Dict[str, int],
    inferred_bot_values: Iterable[float],
    num_flops_total: int,
) -> Tuple[float, float, float, float, float]:
    pv = card_value(player_card, multipliers)
    cv = sum_cards(community_cards, multipliers)
    bots_sum = float(sum(inferred_bot_values))
    remaining_comm = num_flops_total - len(community_cards)
    ev_per_card = expected_value_per_remaining_card(remaining_deck, multipliers)
    ev_remaining_comm = ev_per_card * remaining_comm
    total = pv + cv + bots_sum + ev_remaining_comm
    return pv, cv, bots_sum, ev_remaining_comm, total