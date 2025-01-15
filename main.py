import random
import numpy as np


class Game:
    def __init__(self):
        self.flops = []  # Community cards
        self.deck = []  # Deck of cards
        self.multiplier_dict = {}  # To store dynamic multipliers for suits
        self.available_suits = []  # To store dynamically chosen suits
        self.num_flops = 4  # Number of community cards to reveal

        # Prompt user for the number of bots
        self.num_bots = self.get_num_bots()
        self.num_players = self.num_bots + 1  # Total players = bots + 1 (the user)

        self.player_position = random.choice(range(self.num_players))  # Randomly assign player position

        # Set up multipliers and suits dynamically
        self.setup_suits_and_multipliers()

        # Initialize the deck based on available suits
        self.initialize_deck()

        # Deal one card to each player (including the user)
        self.cards = [self.deck.pop() for _ in range(self.num_players)]
        print(f'\nYour card is: {self.cards[self.player_position]}')

        self.position = 0
        self.pnl = 0
        self.trades = []  # Player's trades

        # Track inferred bot card values (initialize with None for each bot)
        self.bot_card_estimates = [None] * self.num_bots

        # Game Mode
        self.game_mode = self.get_game_mode()

    def get_game_mode(self):
        """Prompt the user to choose the game difficulty."""
        print("\n--- Choose Game Difficulty ---")
        print("1. Easy: Hints are provided.")
        print("2. Normal: No hints, no assessments.")
        print("3. Hard: The game will ask you questions at random moments.")
        print("----------------------------------")

        while True:
            try:
                choice = int(input("Enter the difficulty level (1 for Easy, 2 for Normal, 3 for Hard): "))
                if choice in [1, 2, 3]:
                    return choice
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number (1, 2, or 3).")


    def get_num_bots(self):
        """Prompt the user to input the number of bots."""
        while True:
            try:
                num_bots = int(input("Enter the number of bots in the game (default: 4): ") or 4)
                if num_bots < 1:
                    print("You must have at least 1 bot. Try again.")
                else:
                    return num_bots
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def setup_suits_and_multipliers(self):
        """Prompt the user to set up suits and multipliers dynamically."""
        print("\n--- Game Setup: Choose Suits and Multipliers ---")
        print("You can choose which suits to include in the game and assign their multipliers.")
        print(
            "Default setup excludes Diamonds (D) and includes Clubs (C), Hearts (H), and Spades (S) with their default multipliers.")
        print("Type 'skip' to use the default setup without customization.\n")

        # Default multipliers and suits
        default_multipliers = {'d': -10, 'c': 10, 'h': -10, 's': 10}
        default_suits = ['c', 'h', 's']  # Default suits (exclude diamonds)

        # Allow the user to skip customization
        skip = input(
            "Would you like to customize the suits and multipliers? (Type 'skip' to use defaults): ").strip().lower()
        if skip == 'skip':
            print("\nSkipping customization. Using default setup.")
            self.available_suits = default_suits
            self.multiplier_dict = {suit: default_multipliers[suit] for suit in default_suits}
            return

        # Otherwise, proceed with customization
        for suit in ['d', 'c', 'h', 's']:
            include_suit = input(
                f"Include {suit.upper()} (y/n)? [default: {'y' if suit in default_suits else 'n'}]: ").lower()
            if include_suit == 'n' or (include_suit == '' and suit not in default_suits):
                print(f"{suit.upper()} excluded.")
                continue

            self.available_suits.append(suit)

            try:
                multiplier = input(f"Set multiplier for {suit.upper()} [default: {default_multipliers[suit]}]: ")
                if multiplier:
                    self.multiplier_dict[suit] = int(multiplier)
                else:
                    self.multiplier_dict[suit] = default_multipliers[suit]
            except ValueError:
                print(f"Invalid input! Using default multiplier for {suit.upper()}: {default_multipliers[suit]}")
                self.multiplier_dict[suit] = default_multipliers[suit]

        # If no suits are selected, fallback to defaults
        if not self.available_suits:
            print("\nNo suits selected! Using default setup.")
            self.available_suits = default_suits
            self.multiplier_dict = {suit: default_multipliers[suit] for suit in default_suits}

        print("\n--- Final Setup ---")
        print(f"Available suits: {self.available_suits}")
        print(f"Multipliers: {self.multiplier_dict}")
        print("---------------------------------------------------\n")

    def initialize_deck(self):
        """Initialize the deck based on available suits."""
        for suit in self.available_suits:
            self.deck.extend(f'{suit}{x + 1}' for x in range(13))
        random.shuffle(self.deck)

    def calculate_expected_final_table(self):
        """
        Calculate the expected value of the final table from the player's perspective.

        Returns:
            float: Expected value of the final table.
        """

        # Helper function to calculate the value of a card
        def card_value(card):
            suit = card[0]  # Suit of the card (e.g., 's', 'c', 'h')
            rank = int(card[1:])  # Rank of the card (e.g., 8 from "s8")
            return self.multiplier_dict[suit] * rank

        # 1. Calculate the player's card value
        player_card_value = card_value(self.cards[self.player_position])

        # 2. Calculate the total value of revealed community cards
        community_value = sum(card_value(c) for c in self.flops)  # `self.flops` holds revealed community cards

        # 3. Calculate the expected value of unknown cards
        remaining_cards = self.deck  # Remaining cards in the deck
        total_remaining_value = sum(card_value(c) for c in remaining_cards)  # Total value of remaining cards
        num_remaining_cards = len(remaining_cards)  # Number of remaining cards
        expected_value_per_card = total_remaining_value / num_remaining_cards if num_remaining_cards > 0 else 0

        # Number of unknown cards: remaining community cards + bot cards
        num_unknown_cards = self.num_flops - len(self.flops) + (self.num_players - 1)

        # Expected value of all unknown cards
        expected_value_unknown_cards = expected_value_per_card * num_unknown_cards

        # 4. Calculate the final table expected value
        final_table_expected_value = player_card_value + community_value + expected_value_unknown_cards

        return final_table_expected_value

    def print_rules(self):
        """Print the rules of the game."""
        print("\n--- Rules of the Game ---")
        print("1. You are a market taker, and you will trade based on the quotes provided by bots.")
        print(f"2. There are {self.num_bots} bots in the game, and you are competing against them.")
        print("3. At the start, you are dealt one private card. Community cards will be revealed in each round.")
        print("4. The following suits are included in the game, with their respective multipliers:")
        for suit, multiplier in self.multiplier_dict.items():
            print(f"   - {suit.upper()}: {multiplier} multiplier.")
        print("5. Each bot will quote a bid (price to sell at) and an ask (price to buy at) in every round.")
        print("6. You can choose to:")
        print("   - Buy at the ask price (positive trade).")
        print("   - Sell at the bid price (negative trade).")
        print("   - Skip the trade (enter 0).")
        print("7. At random points, you will be asked to guess your current trade position (long, short, or neutral).")
        print("8. At the end, you will be asked to guess your final position and PnL.")
        print("---------------------------------------------------\n")

    def flop(self):
        """Reveal a community card."""
        self.flops.append(self.deck.pop())
        print(f'Community cards: {self.flops}')

    def card_value(self, card):
        """Calculate the value of a single card."""
        value = int(card[1:])  # Extract the numerical value of the card
        return self.multiplier_dict.get(card[0]) * value

    def bot_market_making(self, card, bot_index):
        """
        Bots provide bid and ask quotes based on the expected value of the final table.

        Parameters:
            card (str): The bot's private card (e.g., "s8").
            bot_index (int): The index of the bot (used for adding slight variations).

        Returns:
            tuple: (bid, ask, volume)
        """



        # 1. Calculate the bot's card value
        bot_card_value = self.card_value(card)

        # 2. Calculate the total value of revealed community cards
        community_value = sum(self.card_value(c) for c in self.flops)  # `self.flops` holds the revealed community cards

        # 3. Calculate the expected value of the unknown cards
        remaining_cards = self.deck  # Remaining cards in the deck
        total_remaining_value = sum(self.card_value(c) for c in remaining_cards)  # Sum of values of all remaining cards
        num_remaining_cards = len(remaining_cards)  # Number of remaining cards
        expected_value_per_card = total_remaining_value / num_remaining_cards if num_remaining_cards > 0 else 0

        # Number of unknown cards: remaining community cards + other players' private cards
        num_unknown_cards = self.num_flops - len(self.flops) + (self.num_players - 1)

        # Expected value of all unknown cards
        expected_value_unknown_cards = expected_value_per_card * num_unknown_cards

        # 4. Calculate the midpoint (expected value of the final table)
        mid_point = bot_card_value + community_value + expected_value_unknown_cards

        # 5. Add a spread to create bid and ask quotes
        spread = random.randint(10, 20)  # Slight variation for each bot
        asymmetry = random.randint(-5, 5)
        bid = int(mid_point - spread - asymmetry)
        ask = int(mid_point + spread + asymmetry)

        # 6. Calculate trade volume (volume increases with each revealed community card)
        volume = 2 ** len(self.flops)  # Volume doubles as more community cards are revealed

        return bid, ask, volume

    def infer_bot_card_value(self, bid, ask):
        """
        Infer the bot's card value based on their bid and ask quotes.

        Parameters:
            bid (int): The bot's bid price.
            ask (int): The bot's ask price.

        Returns:
            float: The inferred value of the bot's card.
        """
        # 1. Calculate the midpoint from the bid and ask
        midpoint = (bid + ask) / 2

        # 2. Calculate the total value of revealed community cards
        community_value = sum(self.card_value(c) for c in self.flops)

        # 3. Calculate the expected value of unknown cards
        remaining_cards = self.deck  # Remaining cards in the deck
        total_remaining_value = sum(self.card_value(c) for c in remaining_cards)  # Total value of remaining cards
        num_remaining_cards = len(remaining_cards)
        expected_value_per_card = total_remaining_value / num_remaining_cards if num_remaining_cards > 0 else 0

        # Number of unknown cards: remaining community cards + player cards
        num_unknown_cards = self.num_flops - len(self.flops) + (self.num_players - 1)

        # Expected value of all unknown cards
        expected_value_unknown_cards = expected_value_per_card * num_unknown_cards

        # 4. Infer the bot's card value
        bot_card_value = midpoint - community_value - expected_value_unknown_cards

        return bot_card_value

    def get_final_table_components(self):
        """
        Calculate the components of the expected final table value.

        Returns:
            tuple: (player_card_value, community_value, inferred_bot_values_sum, expected_value_remaining_community_cards)
        """
        # 1. Calculate the player's card value
        player_card_value = self.card_value(self.cards[self.player_position])

        # 2. Calculate the total value of revealed community cards
        community_value = sum(self.card_value(c) for c in self.flops)

        # 3. Use the most recent inferred bot card values
        inferred_bot_values = [
            estimate for estimate in self.bot_card_estimates if estimate is not None
        ]
        inferred_bot_values_sum = sum(inferred_bot_values)

        # 4. Calculate the expected value of remaining unknown cards
        remaining_cards = self.deck  # Remaining cards in the deck
        total_remaining_value = sum(self.card_value(c) for c in remaining_cards)  # Total value of remaining cards
        num_remaining_cards = len(remaining_cards)
        expected_value_per_card = total_remaining_value / num_remaining_cards if num_remaining_cards > 0 else 0

        # Number of remaining community cards (if any)
        num_remaining_community_cards = self.num_flops - len(self.flops)

        # Expected value of remaining community cards
        expected_value_remaining_community_cards = expected_value_per_card * num_remaining_community_cards

        return player_card_value, community_value, inferred_bot_values_sum, expected_value_remaining_community_cards

    def calculate_expected_final_table_with_inferred_bots(self):
        """
        Calculate the expected value of the final table from the player's perspective,
        using the most recent inferred bot card values.

        Returns:
            float: Expected value of the final table.
        """
        # Get all components using the helper method
        player_card_value, community_value, inferred_bot_values_sum, expected_value_remaining_community_cards = (
            self.get_final_table_components()
        )

        # Calculate the final table expected value
        final_table_expected_value = (
                player_card_value
                + community_value
                + inferred_bot_values_sum
                + expected_value_remaining_community_cards
        )

        return final_table_expected_value

    def player_market_taking(self, bot_index):
        """Player takes the market by buying at ask or selling at bid."""
        card = self.cards[self.player_position]
        bids, asks, volumes = [], [], []

        # Collect all bot quotes
        for i in range(self.num_bots):
            bid, ask, volume = self.bot_market_making(card, i)
            bids.append(bid)
            asks.append(ask)
            volumes.append(volume)

        # Calculate expected value of the final table using inferred bot card values
        expected_value = self.calculate_expected_final_table_with_inferred_bots()

        # Infer the current bot's card value
        current_bot_bid, current_bot_ask = bids[bot_index], asks[bot_index]
        inferred_bot_card_value = self.infer_bot_card_value(current_bot_bid, current_bot_ask)

        # Update the bot's card estimate
        self.bot_card_estimates[bot_index] = inferred_bot_card_value

        # Display information to the player
        print(f"\nExpected Value of the Final Table (using inferred bot values): {expected_value:.2f}")
        print(
            f"Bot {bot_index + 1}'s market: Bid = {current_bot_bid}, Ask = {current_bot_ask}, Volume = {volumes[bot_index]}"
        )
        print(f"Inferred Card Value of Bot {bot_index + 1}: {inferred_bot_card_value:.2f}")
        print(f"Your card: {card}")
        print(f"Community cards: {self.flops}")

        # If Easy Mode, display the player's card value explicitly and show the equation
        if self.game_mode == 1:  # Easy mode
            # Get all components using the helper method
            player_card_value, community_value, inferred_bot_values_sum, expected_value_remaining_community_cards = (
                self.get_final_table_components()
            )

            # Show the player's card value
            print(f"Your Card Value: {player_card_value:.2f}")

            # Show the equation breakdown
            print("\n--- Calculation Breakdown of Expected Value of the Final Table ---")
            print(f"Player Card Value: {player_card_value:.2f}")
            print(f"Revealed Community Cards Value: {community_value:.2f}")
            print(f"Sum of Inferred Bot Values: {inferred_bot_values_sum:.2f}")
            print(f"Expected Value of Remaining Community Cards: {expected_value_remaining_community_cards:.2f}")
            print(f"Equation: {player_card_value:.2f} (Player Card) + {community_value:.2f} (Community Cards) + "
                  f"{inferred_bot_values_sum:.2f} (Inferred Bot Values) + "
                  f"{expected_value_remaining_community_cards:.2f} (Unknown Community Cards)")
            print("--- End of Breakdown ---")

        while True:
            try:
                trade = int(input("Enter your trade (positive to buy at ask, negative to sell at bid, 0 to skip): "))
                if abs(trade) <= volumes[bot_index]:
                    if trade < 0:
                        print(f"You sold {abs(trade)} {'lot' if abs(trade) == 1 else 'lots'} at {current_bot_bid}")
                        self.trades.append((trade, current_bot_bid))
                    elif trade > 0:
                        print(f"You bought {abs(trade)} {'lot' if abs(trade) == 1 else 'lots'} at {current_bot_ask}")
                        self.trades.append((trade, current_bot_ask))
                    break
                elif trade == 0:
                    print("You chose not to trade with this bot.")
                    break
                else:
                    print("Invalid trade volume. Try again.")
            except ValueError:
                print("Please enter a valid integer.")

    def random_trade_check(self):
        """Ask the user to guess their current position at random points."""
        position = sum(trade[0] for trade in self.trades)  # Current position from trades
        print("\n--- Position Check ---")
        guess = input("Guess your current position (e.g., 'long 3', 'short 2', or 'neutral'): ").strip().lower()

        if position > 0:
            actual_position = f"long {position}"
        elif position < 0:
            actual_position = f"short {abs(position)}"
        else:
            actual_position = "neutral"

        if guess == actual_position:
            print("Correct! Your guess matches your actual position.")
        else:
            print(f"Incorrect. Your actual position is {actual_position}.")

    def start(self):
        """Main game loop."""
        self.print_rules()  # Print the rules at the start of the game
        for round in range(self.num_flops):
            print(f"\n--- Round {round + 1}/{self.num_flops} ---")

            # Each bot provides a quote, and the player interacts with each bot
            for bot_index in range(self.num_bots):
                print(f"\nBot {bot_index + 1}'s turn:")
                self.player_market_taking(bot_index)

            # Randomly check the user's position in some rounds
            if self.game_mode == 3 and random.random() < 0.5:  # 50% chance to ask
                self.random_trade_check()

            # Reveal the next community card
            self.flop()

        # Final trading round when all community cards are revealed
        print("\n--- Final Trading Round (All Community Cards Revealed) ---")
        for bot_index in range(self.num_bots):
            print(f"\nBot {bot_index + 1}'s turn (Final Round):")
            self.player_market_taking(bot_index)

    def settle(self):
        """Ask the user to guess their final position and PnL before revealing the actual values."""
        # Calculate the player's actual PnL and position
        actual_position = sum(trade[0] for trade in self.trades)  # Net position from trades
        actual_pnl = sum(trade[0] * trade[1] for trade in self.trades)  # Total PnL from trades

        # Calculate the final table value
        def card_value(card):
            suit = card[0]  # Suit of the card (e.g., 's', 'c', 'h')
            rank = int(card[1:])  # Rank of the card (e.g., 8 from "s8")
            return self.multiplier_dict[suit] * rank

        # 1. Player card value
        player_card_value = card_value(self.cards[self.player_position])

        # 2. Community card values
        community_value = sum(card_value(c) for c in self.flops)

        # 3. Bot card values
        bot_card_values = [card_value(bot_card) for bot_card in self.cards if
                           bot_card != self.cards[self.player_position]]

        # 4. Final table value
        final_table_value = player_card_value + community_value + sum(bot_card_values)

        if self.game_mode == 3:
            print("\n--- Final Guess ---")
            guessed_position = input(
                "What is your final position? (e.g., 'long 3', 'short 2', or 'neutral'): ").strip().lower()
            guessed_pnl = int(input("What is your final PnL? "))

        # Display the actual values after the guess
        print("\n--- Final Check ---")
        print(
            f"Your actual final position: {'long' if actual_position > 0 else 'short' if actual_position < 0 else 'neutral'} {abs(actual_position)} lots"
        )
        print(f"Your actual final PnL: {actual_pnl}")
        print(f"The Final Table Value: {final_table_value:.2f}")

        if self.game_mode == 3:
            # Feedback
            expected_position = (
                f"long {actual_position}" if actual_position > 0 else f"short {abs(actual_position)}" if actual_position < 0 else "neutral"
            )
            if guessed_position == expected_position:
                print("Correct! Your final position guess is accurate.")
            else:
                print(f"Incorrect. Your actual final position is {expected_position}.")

            if guessed_pnl == actual_pnl:
                print("Correct! Your final PnL guess is accurate.")
            else:
                print(f"Incorrect. Your actual final PnL is {actual_pnl}.")


# Initialize the game
game = Game()
game.start()
game.settle()