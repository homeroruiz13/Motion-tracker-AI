from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

class BlackjackWebCounter:
    def __init__(self, driver_path):
        self.options = Options()
        self.options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(service=Service(driver_path), options=self.options)
        self.url = "https://www.lasvegasdirect.com/blackjack/"
        self.running_count = 0
        self.card_values = {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
            '7': 0, '8': 0, '9': 0,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        }

    def start_game(self):
        self.driver.get(self.url)
        time.sleep(5)  # Wait for the game to load

    def extract_card_values(self, card_elements):
        """Extract card values from the web elements."""
        cards = []
        for card in card_elements:
            card_text = card.get_attribute('alt')
            if card_text:
                cards.append(card_text.replace(' of', '').split()[0])  # Extract rank only
        return cards

    def update_count(self, cards):
        """Update running count based on visible cards."""
        for card in cards:
            if card in self.card_values:
                self.running_count += self.card_values[card]

    def play_round(self):
        """Simulate a single round of extracting data and providing suggestions."""
        # Locate player's cards
        player_cards = self.driver.find_elements(By.CSS_SELECTOR, "#player-cards img")
        dealer_cards = self.driver.find_elements(By.CSS_SELECTOR, "#dealer-cards img")

        # Extract card values
        player_hand = self.extract_card_values(player_cards)
        dealer_hand = self.extract_card_values(dealer_cards)

        # Update the count
        self.update_count(player_hand + dealer_hand)

        # Display running count and suggestions
        print(f"Player's Hand: {player_hand}")
        print(f"Dealer's Visible Card: {dealer_hand[0] if dealer_hand else 'Unknown'}")
        print(f"Running Count: {self.running_count}")

        # Suggest next move based on basic strategy
        suggestion = self.get_dynamic_strategy(player_hand, dealer_hand[0] if dealer_hand else None)
        print(f"Suggested Action: {suggestion}")

    def get_dynamic_strategy(self, player_hand, dealer_card):
        """Provide strategy suggestion based on player's hand and dealer's visible card."""
        # Simplified example based on hard totals
        player_value = self.calculate_hand_value(player_hand)

        # Surrender rules
        if player_value == 16 and dealer_card in ['9', '10', 'J', 'Q', 'K', 'A']:
            return "Surrender"
        if player_value == 15 and dealer_card in ['10', 'J', 'Q', 'K', 'A']:
            return "Surrender"

        # Splits
        if len(player_hand) == 2 and player_hand[0] == player_hand[1]:
            pair = player_hand[0]
            if pair == 'A':
                return "Always split aces"
            if pair == '10':
                return "Never split tens"
            if pair == '9' and dealer_card not in ['7', '10', 'J', 'Q', 'K', 'A']:
                return "Split"
            if pair == '8':
                return "Always split 8's"
            if pair == '7' and dealer_card in ['2', '3', '4', '5', '6', '7']:
                return "Split"
            if pair == '6' and dealer_card in ['2', '3', '4', '5', '6']:
                return "Split"
            if pair == '5' and dealer_card in ['2', '3', '4', '5', '6', '7', '8', '9']:
                return "Double"
            if pair == '4' and dealer_card in ['5', '6']:
                return "Split"
            if pair in ['2', '3'] and dealer_card in ['2', '3', '4', '5', '6', '7']:
                return "Split"

        # Soft totals
        if 'A' in player_hand:
            if player_value == 20:
                return "Always stand"
            if player_value == 19 and dealer_card == '6':
                return "Double"
            if player_value == 19:
                return "Stand"
            if player_value == 18 and dealer_card in ['2', '3', '4', '5', '6']:
                return "Double"
            if player_value == 18 and dealer_card in ['9', '10', 'J', 'Q', 'K', 'A']:
                return "Hit"
            if player_value == 18:
                return "Stand"
            if player_value in [17, 16, 15, 14, 13] and dealer_card in ['4', '5', '6']:
                return "Double"
            if player_value in [17, 16, 15, 14, 13]:
                return "Hit"

        # Hard totals
        if player_value >= 17:
            return "Stand"
        if player_value == 16 and dealer_card in ['2', '3', '4', '5', '6']:
            return "Stand"
        if player_value == 16:
            return "Hit"
        if player_value == 15 and dealer_card in ['2', '3', '4', '5', '6']:
            return "Stand"
        if player_value == 15:
            return "Hit"
        if player_value in [13, 14] and dealer_card in ['2', '3', '4', '5', '6']:
            return "Stand"
        if player_value in [13, 14]:
            return "Hit"
        if player_value == 12 and dealer_card in ['4', '5', '6']:
            return "Stand"
        if player_value == 12:
            return "Hit"
        if player_value == 11:
            return "Always double"
        if player_value == 10 and dealer_card in ['2', '3', '4', '5', '6', '7', '8', '9']:
            return "Double"
        if player_value == 10:
            return "Hit"
        if player_value == 9 and dealer_card in ['3', '4', '5', '6']:
            return "Double"
        if player_value == 9:
            return "Hit"
        if player_value <= 8:
            return "Hit"

        return "No suggestion"

    def calculate_hand_value(self, hand):
        """Calculate the value of a hand, accounting for Aces."""
        value = 0
        aces = 0
        for card in hand:
            if card == 'A':
                value += 11
                aces += 1
            elif card in ['J', 'Q', 'K'] or card == '10':
                value += 10
            else:
                value += int(card)

        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value

    def close(self):
        self.driver.quit()

# Example usage:
# Replace 'path_to_chromedriver' with the actual path to your ChromeDriver
# blackjack_counter = BlackjackWebCounter(driver_path='path_to_chromedriver')
# blackjack_counter.start_game()
# while True:
#     blackjack_counter.play_round()
#     input("Press Enter to continue...")
# blackjack_counter.close()
