# Trading Card Market Game

A turn-based market-taking game where you trade against bots quoting bid/ask markets on a deck of cards. Card suits carry multipliers that determine the final table value. Your job: infer value, size trades within quoted volume, and manage risk through the community card reveals.

## Features

- Market-taking gameplay: you trade against bots’ quotes (no order posting).
- Configurable suits and per-suit multipliers.
- Difficulty modes:
  - Easy: shows inferred bot value and expected final value after each trade.
  - Normal: standard information.
  - Hard: occasional position-guess checks; no extra hints.

## Quick Start

Run the CLI

```bash
# From the repository root:
python -m poker_market.cli
```

## How to Play (CLI)

When you start the game, you’ll be guided through a short setup:

1) Choose the number of bots and difficulty.
2) Optionally customize which suits are in play and their multipliers.
3) Optionally set a random seed for reproducibility.
4) Choose the number of community cards (rounds).

You’ll then see the rules and the starting state (your private card and hidden info summary). Each round:

- For each bot:
  - You see its current quote: bid, ask, and available volume.
  - Enter your trade:
    - Positive number = buy at the ask.
    - Negative number = sell at the bid.
    - Zero = skip.
  - Your trade size must be within the bot’s quoted volume.

- After each bot interaction:
  - Easy mode: the CLI shows the bot’s inferred value and your expected value based on that inference.
  - Normal/Hard: no extra hints.

- After all bots in the round, a community card is revealed. The set of community cards cumulatively determines the final table value.

At random times in Hard mode, you may be asked to guess your current position (long/short/neutral). At the end, you’ll see your final position, trading PnL, and the final table value. Hard mode may also ask for final guesses.

## Game Rules

- You are a market taker: you only hit/lift bots’ quotes.
- Bots post a bid (they’ll buy from you) and an ask (they’ll sell to you), each with a volume cap. You cannot trade more than the posted volume.
- You are dealt one private card at the start.
- Community cards are revealed one by one over several rounds.
- Suits determine how card values translate into the final table value via multipliers (e.g., C=10, H=-10, S=10 by default).
- Your PnL comes from trading decisions vs. the eventual table value.