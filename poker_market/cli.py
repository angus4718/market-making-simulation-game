from __future__ import annotations
from typing import Optional, Dict, List, Tuple

from .game import Game
from .cards import DEFAULT_MULTIPLIERS, DEFAULT_SUITS

def prompt_int(prompt: str, default: Optional[int] = None, min_val: Optional[int] = None) -> int:
    while True:
        raw = input(f"{prompt}" + (f" [default {default}]" if default is not None else "") + ": ").strip()
        if not raw and default is not None:
            return default
        try:
            v = int(raw)
            if min_val is not None and v < min_val:
                print(f"Please enter a value >= {min_val}.")
                continue
            return v
        except ValueError:
            print("Please enter an integer.")

def prompt_choice(prompt: str, choices: List[int], default: int) -> int:
    while True:
        v = prompt_int(prompt, default=default)
        if v in choices:
            return v
        print(f"Choose one of {choices}.")

def prompt_yes_no(prompt: str, default: Optional[bool] = None) -> bool:
    suffix = ""
    if default is True:
        suffix = " [Y/n]"
    elif default is False:
        suffix = " [y/N]"
    while True:
        raw = input(f"{prompt}{suffix}: ").strip().lower()
        if not raw and default is not None:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please answer y or n.")

def configure_suits_and_multipliers() -> tuple[List[str], Dict[str, int]]:
    print("\n--- Configure Suits and Multipliers ---")
    print("Default: suits = ['c','h','s'] (diamonds excluded). Multipliers: c=10, h=-10, s=10, d=-10.")
    customize = prompt_yes_no("Customize suits and multipliers?", default=False)

    if not customize:
        suits = list(DEFAULT_SUITS)
        multipliers = {s: DEFAULT_MULTIPLIERS[s] for s in suits}
        return suits, multipliers

    enabled = {}
    for s, name, default in (("c", "Clubs", "y"), ("h", "Hearts", "y"), ("s", "Spades", "y"), ("d", "Diamonds", "n")):
        enabled[s] = prompt_yes_no(f"Enable {name} ({s})?", default=(default == "y"))

    suits = [s for s, on in enabled.items() if on]
    if not suits:
        print("No suits selected. Falling back to defaults: ['c','h','s'].")
        suits = list(DEFAULT_SUITS)

    multipliers: Dict[str, int] = {}
    for s in suits:
        multipliers[s] = prompt_int(f"Set multiplier for {s}", default=DEFAULT_MULTIPLIERS[s])

    print(f"Selected suits: {suits}")
    print(f"Multipliers: {multipliers}")
    return suits, multipliers

def print_rules(suits: List[str], multipliers: Dict[str, int], num_bots: int) -> None:
    print("\n--- Rules of the Game ---")
    print("1. You are a market taker, and you will trade based on the quotes provided by bots.")
    print(f"2. There are {num_bots} bots in the game, and you are competing against them.")
    print("3. At the start, you are dealt one private card. Community cards will be revealed in each round.")
    print("4. The following suits are included in the game, with their respective multipliers:")
    for s in suits:
        label = s.upper()
        print(f"   - {label}: {multipliers[s]} multiplier.")
    print("5. Each bot will quote a bid (price to sell at) and an ask (price to buy at) in every round.")
    print("6. You can choose to:")
    print("   - Buy at the ask price (positive trade).")
    print("   - Sell at the bid price (negative trade).")
    print("   - Skip the trade (enter 0).")
    print("7. At random points, you may be asked to guess your current trade position (long, short, or neutral).")
    print("8. At the end, you may be asked to guess your final position and PnL (depending on difficulty).\n")

def preview_bot_market(game: Game, bot_index: int) -> Tuple[int, int, int]:
    """
    Returns (bid, ask, volume) for the bot without consuming a trade if possible.
    Prefer a side-effect-free method if Game exposes one; otherwise we assume
    play_round_with_bot(..., 0) does not change position or irreversible state.
    """
    if hasattr(game, "peek_bot_market"):
        p = game.peek_bot_market(bot_index)
        return int(p["bid"]), int(p["ask"]), int(p.get("volume", 0))
    # Fallback: snapshot via zero-size trade
    snap = game.play_round_with_bot(bot_index, 0)
    return int(snap["bid"]), int(snap["ask"]), int(snap["volume"])

def prompt_trade_limited_by_volume(max_vol: int) -> int:
    """
    Prompt for trade size with constraint: abs(trade) <= max_vol.
    Positive => buy at ask, Negative => sell at bid, Zero => skip.
    """
    while True:
        trade = prompt_int(f"Enter trade (<= {max_vol} in magnitude; positive=buy ask, negative=sell bid, 0=skip)", default=0)
        if abs(trade) <= max_vol:
            return trade
        print(f"Trade size exceeds available volume ({max_vol}). Please enter between {-max_vol} and {max_vol}.")

def main() -> None:
    print("=== Trading Card Market Game ===")
    num_bots = prompt_int("Enter number of bots", default=4, min_val=1)
    difficulty = prompt_choice("Difficulty (1=Easy, 2=Normal, 3=Hard)", [1, 2, 3], default=2)

    suits, multipliers = configure_suits_and_multipliers()

    use_seed = prompt_yes_no("Set a deterministic seed?", default=False)
    seed: Optional[int] = None
    if use_seed:
        seed = prompt_int("Seed (integer)", default=12345)

    num_flops = prompt_int("Number of community cards", default=4, min_val=1)

    game = Game(
        num_bots=num_bots,
        difficulty=difficulty,
        suits=suits,
        multipliers=multipliers,
        seed=seed,
        num_flops=num_flops,
    )

    # Show rules with the actual suits/multipliers and bot count
    print_rules(game.suits, game.multipliers, game.num_bots)

    print("Game setup:")
    print(f"Suits: {game.suits}  Multipliers: {game.multipliers}")
    print(game.describe_state())

    # Rounds
    for r in range(game.num_flops):
        print(f"\n--- Round {r+1}/{game.num_flops} ---")
        for b in range(game.num_bots):
            print(f"\nBot {b+1}")
            # Show the bot's current market BEFORE prompting for trade
            bid, ask, vol = preview_bot_market(game, b)
            print(f"Bot market: bid {bid} / ask {ask}  vol {vol}")

            # Get user's trade, limited by available volume
            trade = prompt_trade_limited_by_volume(vol)

            # Execute the trade and receive the snapshot for this bot
            snapshot = game.play_round_with_bot(b, trade)

            # Only show inference/EV in Easy mode
            if difficulty == 1:
                if 'inferred' in snapshot:
                    print(f"Inferred bot value: {snapshot['inferred']:.2f}")
                if 'ev_with_inferred' in snapshot:
                    print(f"EV (with inferred): {snapshot['ev_with_inferred']:.2f}")

        # Random check in hard mode
        if difficulty == 3:
            from random import random
            if random() < 0.5:
                pos, _ = game.settle_position_pnl()
                guess = input("Guess your current position (e.g., 'long 3', 'short 2', 'neutral'): ").strip().lower()
                actual = "neutral" if pos == 0 else ("long " + str(pos) if pos > 0 else "short " + str(-pos))
                print("Correct!" if guess == actual else f"Not quite. Actual: {actual}")

        game.reveal_flop()
        print("Community:", game.flops)

    print("\n--- Final Trading Round ---")
    for b in range(game.num_bots):
        print(f"\nBot {b+1}")
        bid, ask, vol = preview_bot_market(game, b)
        print(f"Bot market: bid {bid} / ask {ask}  vol {vol}")

        trade = prompt_trade_limited_by_volume(vol)
        snapshot = game.play_round_with_bot(b, trade)

        if difficulty == 1:
            if 'inferred' in snapshot:
                print(f"Inferred bot value: {snapshot['inferred']:.2f}")
            if 'ev_with_inferred' in snapshot:
                print(f"EV (with inferred): {snapshot['ev_with_inferred']:.2f}")

    print("\n--- Settle ---")
    pos, pnl = game.settle_position_pnl()
    table_val = game.final_table_value()
    print(f"Final position: {'long' if pos>0 else 'short' if pos<0 else 'neutral'} {abs(pos)}")
    print(f"Trade PnL: {pnl}")
    print(f"Final Table Value: {table_val}")

    if difficulty == 3:
        guess_pos = input("Final guess position: ").strip().lower()
        try:
            guess_pnl = int(input("Final guess PnL: ").strip())
        except ValueError:
            guess_pnl = None
        actual = "neutral" if pos == 0 else ("long " + str(pos) if pos > 0 else "short " + str(-pos))
        print("Position guess:", "Correct" if guess_pos == actual else f"Incorrect (actual {actual})")
        if guess_pnl is not None:
            print("PnL guess:", "Correct" if guess_pnl == pnl else f"Incorrect (actual {pnl})")

if __name__ == "__main__":
    main()