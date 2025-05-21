# **Market Making Simulation Game**

## **Overview**

This is a Python-based market making simulation game where the player competes against bots in a trading scenario. The game combines elements of probability, decision-making, and strategy. The player is dealt a private card, and community cards are revealed over several rounds. The bots provide buy (bid) and sell (ask) quotes, and the player can choose to trade or skip based on the provided market conditions. The game ends with a final settlement, where the player’s performance is evaluated.

---

## **Features**

1. **Dynamic Game Setup**:
   - Customizable suits and multipliers for game cards.
   - Adjustable number of bots.
   - Choose from three difficulty levels: **Easy**, **Normal**, **Hard**.

2. **Game Modes**:
   - **Easy**: Hints are provided, such as the breakdown of calculations and inferred bot values.
   - **Normal**: A standard game without additional hints or random assessments.
   - **Hard**: Introduces random assessments where the player must guess their trading position and PnL.

3. **Trading System**:
   - Bots provide bid and ask prices based on their private card, community cards, and remaining unknown cards.
   - The player can buy, sell, or skip trades each round.

4. **Final Settlement**:
   - The game calculates the final table value and evaluates the player’s performance (position and profit/loss).

---

## **How to Play**

1. **Game Setup**:
   - Choose the number of bots (default: 4).
   - Customize the suits and their multipliers or use the default setup.
   - Select the difficulty level:
     - **Easy**: Hints are displayed to guide the player.
     - **Normal**: Standard gameplay without hints.
     - **Hard**: Introduces random questions about the player’s position.

2. **Game Flow**:
   - Each player is dealt a private card.
   - Community cards are revealed over multiple rounds.
   - Players interact with bots (one at a time) to trade based on the bots’ bid/ask quotes.
   - The player’s goal is to maximize their profit/loss (PnL) based on trading decisions.

3. **Trading**:
   - **Buy**: Enter a positive number to buy at the bot’s ask price.
   - **Sell**: Enter a negative number to sell at the bot’s bid price.
   - **Skip**: Enter `0` to skip trading with the bot.

4. **Final Settlement**:
   - At the end of the game, the player’s final position and PnL are calculated based on all trades.
   - In **Hard mode**, the player must guess their final position and PnL for bonus points.

---

## **Game Components**

1. **Cards**:
   - Each card has a suit (e.g., Spades, Clubs) and a rank (e.g., 1 to 13).
   - The value of a card is calculated as `rank × multiplier`, where the multiplier is determined by the suit.

2. **Bots**:
   - Each bot has a private card and provides bid/ask quotes during its turn.
   - Quotes are influenced by:
     - The bot’s private card value.
     - Total value of revealed community cards.
     - Expected value of unknown cards.

3. **Community Cards**:
   - These are revealed incrementally in each round.
   - Their values contribute to the final table’s expected value.

4. **Final Table Value**:
   - The sum of:
     - Player’s private card value.
     - Revealed community cards’ values.
     - Inferred bot card values.
     - Expected value of remaining unknown cards.

---

## **Difficulty Levels**

1. **Easy**:
   - Provides hints, including:
     - Player’s card value.
     - Breakdown of the expected final table value calculation.
     - Inferred bot card values.

2. **Normal**:
   - Regular gameplay without hints or assessments.

3. **Hard**:
   - Includes random assessments:
     - The player must guess their current position (e.g., long/short/neutral) during the game.
     - At the end of the game, the player must guess their final position and PnL.

---

## **Game Rules**

1. **Objective**:
   - Maximize your profit/loss (PnL) by making informed trades based on the bots’ quotes and the revealed cards.

2. **Trading**:
   - Each bot provides a bid (price to sell at) and ask (price to buy at).
   - The player can choose to:
     - **Buy**: Enter a positive number to buy at the ask price.
     - **Sell**: Enter a negative number to sell at the bid price.
     - **Skip**: Enter `0` to skip trading with the bot.

3. **Calculation of Card Values**:
   - Card Value = `rank × multiplier`.
   - Default multipliers:
     - Spades (S): +10
     - Clubs (C): +10
     - Hearts (H): -10
     - Diamonds (D): -10

4. **Position**:
   - Track your trades to calculate your current position (long, short, or neutral).

5. **Settlement**:
   - At the end of the game, the final table value is calculated.
   - The player’s profit/loss is evaluated, along with their net position.

---

## **Key Methods**

### **Game Initialization**
- `__init__`: Sets up the game, including the deck, suits, multipliers, and player/bot cards.

### **Game Setup**
- `get_game_mode`: Lets the player choose a difficulty level.
- `setup_suits_and_multipliers`: Allows customization of suits and their multipliers.
- `initialize_deck`: Creates a shuffled deck based on the selected suits.

### **Core Gameplay**
- `print_rules`: Displays the game rules.
- `flop`: Reveals a community card.
- `bot_market_making`: Generates bid/ask quotes from bots.
- `player_market_taking`: Handles the player’s interaction with a bot.
- `random_trade_check`: Asks the player to guess their current position (in Hard mode).

### **Calculations**
- `card_value`: Calculates the value of a single card.
- `infer_bot_card_value`: Infers a bot’s card value based on its bid/ask quotes.
- `get_final_table_components`: Calculates components of the final table value.
- `calculate_expected_final_table_with_inferred_bots`: Calculates the expected value of the final table using inferred bot values.

### **Settlement**
- `settle`: Evaluates the player’s performance at the end of the game.

---

## **How to Run**

1. Ensure you have Python installed (version 3.6 or higher is recommended).
2. Copy the code into a file named `main.py`.
3. Run the game using:
   ```bash
   python main.py
   ```
4. Follow the interactive prompts to set up and play the game.

---

## **Example Gameplay**

### Game Start:
```
Enter the number of bots in the game (default: 4): 3

--- Choose Game Difficulty ---
1. Easy: Hints are provided.
2. Normal: No hints, no assessments.
3. Hard: The game will ask you questions at random moments.
----------------------------------
Enter the difficulty level (1 for Easy, 2 for Normal, 3 for Hard): 1

--- Game Setup: Choose Suits and Multipliers ---
Would you like to customize the suits and multipliers? (Type 'skip' to use defaults): skip

Your card is: c10
```

### Bot Interaction:
```
--- Round 1/4 ---

Bot 1's turn:
Expected Value of the Final Table (using inferred bot values): 145.50
Bot 1's market: Bid = 110, Ask = 130, Volume = 4
Inferred Card Value of Bot 1: 75.00
Your card: c10
Community cards: ['s8']

Your Card Value: 100.00

--- Calculation Breakdown of Expected Value of the Final Table ---
Player Card Value: 100.00
Revealed Community Cards Value: 80.00
Sum of Inferred Bot Values: 160.00
Expected Value of Remaining Community Cards: 30.00
Equation: 100.00 (Player Card) + 80.00 (Community Cards) + 160.00 (Inferred Bot Values) + 30.00 (Unknown Community Cards)
--- End of Breakdown ---

Enter your trade (positive to buy at ask, negative to sell at bid, 0 to skip): 2
You bought 2 lots at 130.
```

### Final Settlement:
```
--- Final Check ---
Your actual final position: long 4 lots
Your actual final PnL: 120
The Final Table Value: 365.00
```

---

## **Future Enhancements**
1. Add AI improvements for bots to make more dynamic decisions.
2. Introduce player-vs-player multiplayer mode.
3. Add visualization for the game flow (e.g., graphs or tables).

---

## **Contributing**

Feel free to fork this repository and submit pull requests with improvements or new features. Suggestions are always welcome!

---

## **License**

This project is licensed under the MIT License.
