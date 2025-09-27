import random
from typing import Dict, List, Tuple
from .cards import card_value
from .ev import expected_value_per_remaining_card, sum_cards

class MarketMakingBot:
    def __init__(self, idx: int, rng: random.Random) -> None:
        self.idx = idx
        self.rng = rng

    def quote(
        self,
        private_card: str,
        community_cards: List[str],
        remaining_deck: List[str],
        multipliers: Dict[str, int],
        num_flops_total: int,
        num_players: int,
    ) -> Tuple[int, int, int]:
        # Midpoint = EV(final table) from bot's perspective
        bot_private = card_value(private_card, multipliers)
        cv = sum_cards(community_cards, multipliers)

        remaining_comm = num_flops_total - len(community_cards)
        unknown_private = num_players - 1
        num_unknown = remaining_comm + unknown_private

        ev_per_card = expected_value_per_remaining_card(remaining_deck, multipliers)
        ev_unknown = ev_per_card * num_unknown

        midpoint = bot_private + cv + ev_unknown

        spread = self.rng.randint(10, 20)
        asym = self.rng.randint(-5, 5)
        bid = int(midpoint - spread - asym)
        ask = int(midpoint + spread + asym)

        volume = 2 ** len(community_cards)
        return bid, ask, volume