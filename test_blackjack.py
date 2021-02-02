from unittest import TestCase, mock
from blackjack import Blackjack, Card


class TestBlackjack(TestCase):
    def setUp(self) -> None:
        self.blackjack = Blackjack(1, 1)

    def test__create_stack(self):
        self.assertEqual(len(self.blackjack._create_stack(1)), 52)
        self.assertEqual(len(self.blackjack._create_stack(2)), 2 * 52)
        self.assertEqual(len(self.blackjack._create_stack(3)), 3 * 52)

    def test_calculate_optimal_ace_sum(self):
        self.assertEqual(self.blackjack.calculate_optimal_ace_sum(1, 20, 21), 1)
        self.assertEqual(self.blackjack.calculate_optimal_ace_sum(2, 20, 21), 2)
        self.assertEqual(self.blackjack.calculate_optimal_ace_sum(1, 10, 21), 11)
        self.assertEqual(self.blackjack.calculate_optimal_ace_sum(2, 9, 21), 12)

    def test__calculate_no_aces(self):
        self.assertEqual(self.blackjack._calculate_no_aces([1, 2, 3]), 6)
        self.assertEqual(self.blackjack._calculate_no_aces([1, 12, 13]), 21)
        self.assertEqual(self.blackjack._calculate_no_aces([1, 11, 10]), 21)

    def test__calculate_stack_sum(self):
        small_stack = [Card('D', 1), Card('D', 3), Card('D', 1), Card('D', 1)]
        blackjack_stack = [Card('D', 1), Card('D', 10)]
        self.assertEqual(self.blackjack._calculate_stack_sum(small_stack), 16)
        self.assertEqual(self.blackjack._calculate_stack_sum(blackjack_stack), 21)

    def test__draw_card(self):
        drawn_card = self.blackjack._draw_card()
        self.assertLess(drawn_card.number, 14)
        self.assertGreater(drawn_card.number, 0)

    def test__dealer_draw(self):
        self.blackjack._dealer_stack = [Card('Spades', 11), Card('Spades', 8)]
        self.assertEqual(self.blackjack._dealer_draw(True), True)
        self.blackjack._dealer_stack = [Card('Spades', 11), Card('Spades', 5)]
        self.assertEqual(self.blackjack._dealer_draw(True), False)

    def test__player_draw(self):
        self.assertEqual(self.blackjack._player_draw(0), self.blackjack._player_stacks[0][-1])

    @mock.patch('blackjack.input', create=True)
    def test__player_choice(self, mocked_input: mock.Mock):
        mocked_input.side_effect = ['h', 's']
        self.blackjack._player_draw(0)
        self.assertEqual(self.blackjack._player_choice(0),
                         self.blackjack._calculate_stack_sum(self.blackjack._player_stacks[0]) > 21)
        self.assertEqual(self.blackjack._player_choice(0),
                         True)

    def test__get_sums(self):
        self.blackjack._dealer_stack = [Card('D', 12)]
        self.blackjack._player_stacks[0] = [Card('D', 12)]
        self.assertEqual(self.blackjack._get_sums(), (10, [10]))
        self.blackjack._dealer_stack = [Card('D', 1), Card('D', 12)]
        self.blackjack._player_stacks[0] = [Card('D', 1), Card('D', 12)]
        self.assertEqual(self.blackjack._get_sums(), (21, [21]))

    def test__compute_winner(self):
        self.assertEqual(self.blackjack._compute_winner(21, 21), 'NONE')
        self.assertEqual(self.blackjack._compute_winner(21, 23), 'DEALER')
        self.assertEqual(self.blackjack._compute_winner(21, 15), 'DEALER')
        self.assertEqual(self.blackjack._compute_winner(17, 21), 'PLAYER')

    def test__initial_deal(self):
        self.blackjack._dealer_stack = []
        self.blackjack._player_stacks = [[]]
        self.blackjack._initial_deal()
        self.assertEqual(len(self.blackjack._dealer_stack), 2)
        self.assertEqual(len(self.blackjack._player_stacks[0]), 2)
