import random
from typing import Dict, List, Optional, Sequence, Tuple

from .cards import (
    DEFAULT_MULTIPLIERS,
    DEFAULT_SUITS,
    build_deck,
    shuffle_deck,
    card_value,
    validate_suits_and_multipliers,
    pretty_cards,
)
from .bots import MarketMakingBot
from .ev import (
    infer_bot_private_value_from_quotes,
    combine_ev_components,
)

class Game:
    def __init__(
        self,
        num_bots: int = 4,
        num_flops: int = 4,
        suits: Sequence[str] = DEFAULT_SUITS,
        multipliers: Optional[Dict[str, int]] = None,
        seed: Optional[int] = None,
        difficulty: int = 2,  # 1 easy, 2 normal, 3 hard
    ) -> None:
        self.rng = random.Random(seed)
        self.num_flops = num_flops
        self.num_bots = max(1, num_bots)
        self.num_players = self.num_bots + 1

        self.suits = list(suits)
        self.multipliers = dict(multipliers or {s: DEFAULT_MULTIPLIERS[s] for s in self.suits})
        validate_suits_and_multipliers(self.suits, self.multipliers)

        self.deck: List[str] = build_deck(self.suits)
        shuffle_deck(self.deck, self.rng)

        # deal private cards (1 per player)
        self.cards: List[str] = [self.deck.pop() for _ in range(self.num_players)]

        # randomly assign user seat
        self.player_position = self.rng.randrange(self.num_players)

        self.flops: List[str] = []
        self.trades: List[Tuple[int, int]] = []
        self.bot_card_estimates: List[Optional[float]] = [None] * self.num_bots
        self.difficulty = difficulty

        self.bots = [MarketMakingBot(i, self.rng) for i in range(self.num_bots)]

    @property
    def player_card(self) -> str:
        return self.cards[self.player_position]

    def reveal_flop(self) -> None:
        if self.deck:
            self.flops.append(self.deck.pop())

    def settle_position_pnl(self) -> Tuple[int, int]:
        position = sum(qty for qty, _ in self.trades)
        pnl = sum(qty * px for qty, px in self.trades)
        return position, pnl

    def get_bot_quote(self, bot_idx: int) -> Tuple[int, int, int]:
        # Bots quote based on their own private cards
        bot_private = self.cards[bot_idx if bot_idx < self.player_position else bot_idx + 1]
        return self.bots[bot_idx].quote(
            private_card=bot_private,
            community_cards=self.flops,
            remaining_deck=self.deck,
            multipliers=self.multipliers,
            num_flops_total=self.num_flops,
            num_players=self.num_players,
        )

    def infer_and_update_bot_value(self, bot_idx: int, bid: int, ask: int) -> float:
        val = infer_bot_private_value_from_quotes(
            bid=bid,
            ask=ask,
            community_cards=self.flops,
            remaining_deck=self.deck,
            multipliers=self.multipliers,
            num_flops_total=self.num_flops,
            num_players=self.num_players,
        )
        self.bot_card_estimates[bot_idx] = val
        return val

    def expected_value_with_inferred(self) -> float:
        inferred = [v for v in self.bot_card_estimates if v is not None]
        _, _, _, _, total = combine_ev_components(
            self.player_card, self.flops, self.deck, self.multipliers, inferred, self.num_flops
        )
        return total

    def describe_state(self) -> str:
        return (
            f"Your card: {self.player_card}  |  Community: {pretty_cards(self.flops)}  |  "
            f"Deck left: {len(self.deck)}"
        )

    def breakdown_if_easy(self) -> Optional[str]:
        if self.difficulty != 1:
            return None
        inferred = [v for v in self.bot_card_estimates if v is not None]
        pv, cv, bots_sum, ev_rem, total = combine_ev_components(
            self.player_card, self.flops, self.deck, self.multipliers, inferred, self.num_flops
        )
        lines = [
            "--- EV Breakdown ---",
            f"Player card value: {pv:.2f}",
            f"Revealed community value: {cv:.2f}",
            f"Sum inferred bot values: {bots_sum:.2f}",
            f"EV remaining community: {ev_rem:.2f}",
            f"Total EV: {total:.2f}",
        ]
        return "\n".join(lines)

    def play_round_with_bot(self, bot_idx: int, trade_qty: int) -> Dict[str, object]:
        bid, ask, vol = self.get_bot_quote(bot_idx)
        inferred = self.infer_and_update_bot_value(bot_idx, bid, ask)
        # clamp trade within [-vol, vol]
        trade_qty = max(-vol, min(vol, trade_qty))
        if trade_qty < 0:
            self.trades.append((trade_qty, bid))
        elif trade_qty > 0:
            self.trades.append((trade_qty, ask))
        snapshot = {
            "bot": bot_idx + 1,
            "bid": bid,
            "ask": ask,
            "volume": vol,
            "inferred": inferred,
            "ev_with_inferred": self.expected_value_with_inferred(),
        }
        return snapshot

    def final_table_value(self) -> int:
        # When all private and community cards are known
        player_val = card_value(self.player_card, self.multipliers)
        community_val = sum(card_value(c, self.multipliers) for c in self.flops)
        bots_vals = [
            card_value(c, self.multipliers)
            for i, c in enumerate(self.cards)
            if i != self.player_position
        ]
        return player_val + community_val + sum(bots_vals)