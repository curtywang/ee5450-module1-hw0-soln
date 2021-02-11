import logging
from typing import List, Union, Tuple
import random
from dataclasses import dataclass
import numpy as np


BLACKJACK_INSTRUCTIONS = {
    'English': {
        'WELCOME': 'Welcome to Blackjack!',
        'NUM_PLAYERS': 'How many players? ',
        'NUM_DECKS': 'How many decks? ',
        'START': 'Starting game... ',
        'PLAYER_INST': 'Type h to hit or s to stay.',
        'PLAYER_HIT': 'Chose to hit and drew',
        'PLAYER_STAY': 'Chose to Stay.',
        'DEALER_HIT': 'Dealer hit and drew a',
        'DEALER_STAY': 'Dealer stays at',
        'PLAY_AGAIN': 'Type y to play another game: '
    }
}


@dataclass
class Card(object):
    suit: str
    number: int

    @staticmethod
    def _convert_card_num_to_str(num) -> str:
        if num == 1:
            return 'Ace'
        elif num == 11:
            return 'Jack'
        elif num == 12:
            return 'Queen'
        elif num == 13:
            return 'King'
        else:
            return str(num)

    def __str__(self):
        return f'{self._convert_card_num_to_str(self.number)} of {self.suit}'


class Blackjack(object):
    """ Blackjack game object.
    """
    def __init__(self, num_decks: int = 1, num_players: int = 1):
        """
        Constructor for the Blackjack game object.

        :param num_decks: number of decks in this game; defaults to 1 deck
        :param num_players: number of players in this game; defaults to 1 player
        """
        self._SUITS = ("Spades", "Hearts", "Clubs", "Diamonds")
        self._ACE_LOW = 1
        self._ACE_HIGH = 11
        self._LOWEST_CARD = 1
        self._HIGHEST_CARD = 13
        self._WINNING_SUM = 21
        self._MAX_ROYALTY = 10
        self._num_decks = num_decks
        self._num_players = num_players
        self._card_stack = self._create_stack(num_decks)
        self._dealer_stack = []
        self._player_stacks = [[] for _ in range(self._num_players)]
        self._player_dones = [False for _ in range(self._num_players)]
        self._current_turn = 0

    def _create_stack(self, num_decks: int) -> List[Card]:
        """
        Creates the stack of the cards (52 * num_decks), shuffled.

        :param num_decks: number of decks to use
        :return: stack of all card objects, shuffled.
        """
        the_list = []
        for _ in range(num_decks):
            for suit in self._SUITS:
                the_list.extend([Card(suit, num)
                                 for num in range(self._LOWEST_CARD, self._HIGHEST_CARD + 1)])
        random.shuffle(the_list)
        return the_list

    def calculate_optimal_ace_sum(self, number_of_ace_cards: int, current_sum: int,
                                  target_sum: int) -> int:
        """
        Greedy approximation search for optimal sum of Ace cards in a player's stack.

        :param number_of_ace_cards: number of Ace cards in the stack
        :param current_sum: current sum without Ace cards
        :param target_sum: target sum after ace cards
        :return: the optimal Ace-only sum to use
        """
        ace_sum = 0
        for card_idx in range(number_of_ace_cards):
            if current_sum + ace_sum + self._ACE_HIGH <= target_sum - card_idx:
                ace_sum += self._ACE_HIGH
            else:
                ace_sum += self._ACE_LOW
        return ace_sum

    def _calculate_no_aces(self, stack: List[int]) -> int:
        """
        Calculates sum of a stack without aces

        :param stack: List of all the card numbers without Aces
        :return: Sum of clipped cards (clipped to self._MAX_ROYALTY)
        """
        return np.clip(np.array(stack), a_min=1, a_max=self._MAX_ROYALTY).sum()

    def _calculate_stack_sum(self, stack: List[Card]) -> int:
        """
        Calculates the blackjack sum of a stack (list) of Card objects.

        :param stack: List of Card objects to calculate the sum with
        :return: The sum that minimizes the distance to optimal_sum
        """
        num_cards_ace = len([idx for idx, card in enumerate(stack) if card.number == 1])
        sum_of_cards_without_ace = self._calculate_no_aces([card.number for card in stack if card.number != 1])
        ace_sum = self.calculate_optimal_ace_sum(num_cards_ace, sum_of_cards_without_ace, self._WINNING_SUM)
        return sum_of_cards_without_ace + ace_sum

    def _draw_card(self) -> Card:
        """
        Draw a card from the main stack.

        :return: Card object
        """
        return self._card_stack.pop()

    def dealer_draw(self, silent: bool = False) -> bool:
        """
        Play the dealer, which is forced to stay at 17.

        :param silent: True if this is a silent draw (no logging).
        :return: dealer is done hitting.
        """
        current_sum = self._calculate_stack_sum(self._dealer_stack)
        if current_sum < 17:
            drawn_card = self._draw_card()
            self._dealer_stack.append(drawn_card)
            if not silent:
                print(f"Dealer: {BLACKJACK_INSTRUCTIONS['English']['DEALER_HIT']} {drawn_card}")
            return False
        else:
            print(f"Dealer: {BLACKJACK_INSTRUCTIONS['English']['DEALER_STAY']} {current_sum}")
            return True

    def player_draw(self, player_idx: int) -> Card:
        """
        Draw a card for the player.

        :param player_idx:  The player to which a card should be drawn
        :return: The drawn card (already placed in the player's stack)
        """
        drawn_card = self._draw_card()
        self._player_stacks[player_idx].append(drawn_card)
        return drawn_card

    def _player_choice(self, player_idx: int) -> bool:
        """
        Ask player for the choice.

        :param player_idx:
        :return: player is done hitting
        """
        player_input = 'g'
        while player_input not in ('h', 's'):
            player_input = input(f"Player {player_idx}: {BLACKJACK_INSTRUCTIONS['English']['PLAYER_INST']} ")
            if player_input == 'h':
                drawn_card = self.player_draw(player_idx)
                print(f"Player {player_idx}: {BLACKJACK_INSTRUCTIONS['English']['PLAYER_HIT']} {drawn_card}")
                return self._calculate_stack_sum(self._player_stacks[player_idx]) > 21
            elif player_input == 's':
                print(f"Player {player_idx}: {BLACKJACK_INSTRUCTIONS['English']['PLAYER_STAY']}")
                return True

    def _get_sums(self) -> Tuple[int, List[int]]:
        """
        Computes the dealer and player sums.

        :return: (dealer_sum, [player_sum])
        """
        return self._calculate_stack_sum(self._dealer_stack), [self._calculate_stack_sum(stack)
                                                               for stack in self._player_stacks]

    def _compute_winner(self, dealer_sum: int, player_sum: int) -> str:
        """
        Computes the winner, between the dealer and player.

        :param dealer_sum: optimal sum of the dealer's stack
        :param player_sum: optimal sum of the player's stack
        :return: the winner: NONE, DEALER, or PLAYER
        """
        if dealer_sum == self._WINNING_SUM and player_sum == self._WINNING_SUM:
            return 'NONE'
        elif dealer_sum == self._WINNING_SUM:
            return 'DEALER'
        elif self._WINNING_SUM > dealer_sum > player_sum:
            return 'DEALER'
        elif player_sum > self._WINNING_SUM:
            return 'DEALER'
        elif player_sum == self._WINNING_SUM:
            return 'PLAYER'
        elif dealer_sum < player_sum < self._WINNING_SUM:
            return 'PLAYER'
        else:
            return 'NONE'

    def compute_winners(self) -> List[str]:
        """
        Computes the winners of the current game.

        :return: List of the winner between each player and the dealer.
        """
        dealer_sum, player_sums = self._get_sums()
        return [self._compute_winner(dealer_sum, player_sum) for player_sum in player_sums]

    def print_dealer_single(self):
        print(f"Dealer: {self._dealer_stack[0]}")

    def print_dealer_full(self):
        print(f"Dealer: {', '.join([str(card) for card in self._dealer_stack])}",
              f" at sum {self._calculate_stack_sum(self._dealer_stack)}")

    def print_player_stack(self, player_idx: int):
        player_stack = self._player_stacks[player_idx]
        player_sum = self._calculate_stack_sum(player_stack)
        print(f"Player {player_idx}: {', '.join([str(card) for card in player_stack])} at sum {player_sum}")

    def get_stacks(self):
        return self._dealer_stack, self._player_stacks

    def initial_deal(self):
        self.dealer_draw()
        self.dealer_draw(silent=True)  # second draw is hidden
        for player_idx in range(self._num_players):
            for _ in range(2):
                self.player_draw(player_idx)

    def run(self):
        print(BLACKJACK_INSTRUCTIONS['English']['START'])
        self.initial_deal()
        self.print_dealer_single()
        while not all(self._player_dones):
            for player_idx in range(self._num_players):
                if not self._player_dones[player_idx]:
                    if self._current_turn < 1:
                        self.print_player_stack(player_idx)
                    self._player_dones[player_idx] = self._player_choice(player_idx)
                    self.print_player_stack(player_idx)
            self._current_turn += 1
        while not self.dealer_draw():
            self.print_dealer_full()
        self.print_dealer_full()
        print(f"Final winners: {self.compute_winners()}")
        return

    @property
    def num_players(self):
        return self._num_players


def main():
    play_another = True
    while play_another:
        print(f"{BLACKJACK_INSTRUCTIONS['English']['WELCOME']}")
        num_players_input = int(input(f"{BLACKJACK_INSTRUCTIONS['English']['NUM_PLAYERS']}"))
        num_decks_input = int(input(f"{BLACKJACK_INSTRUCTIONS['English']['NUM_DECKS']}"))
        the_game = Blackjack(num_decks=num_decks_input, num_players=num_players_input)
        the_game.run()
        play_another_input = input(f"{BLACKJACK_INSTRUCTIONS['English']['PLAY_AGAIN']}")
        if play_another_input != 'y':
            play_another = False
    return False


if __name__ == '__main__':
    # logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=print)
    main()
