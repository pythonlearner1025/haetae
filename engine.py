from pokerkit.pokerkit import Automation
from pokerkit.pokerkit import NoLimitTexasHoldem, UnfixedLimitHoldem
from pokerkit.pokerkit import Deck, Card, State
from collections import deque

import numpy as np

def get_new_game(
    n_players, 
    bb=2, 
    alpha=1.0,
    deck_cards=[],
    player_hands=[]
    ) -> State:
    # https://pokerkit.readthedocs.io/en/latest/simulation.html#pre-defined-games
    automations = (
        Automation.ANTE_POSTING,
        Automation.BET_COLLECTION,
        Automation.BLIND_OR_STRADDLE_POSTING,
        Automation.CARD_BURNING,
        Automation.HOLE_DEALING,
        Automation.BOARD_DEALING,
        Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        Automation.HAND_KILLING,
        Automation.CHIPS_PUSHING,
        Automation.CHIPS_PULLING,
    )
  # Define Dirichlet distribution parameters
    a = [alpha] * n_players  # You can adjust these values to control the distribution
    # Generate Dirichlet distribution
    dirichlet_dist = tuple(np.random.dirichlet(a).tolist())

    # Adjust the distribution to ensure minimum value is 0.15
    buy_in = bb*50
    min_value = 0.1
    adjusted_dist = np.maximum(dirichlet_dist, min_value)
    adjusted_dist = adjusted_dist / adjusted_dist.sum()  # Renormalize
    adjusted_dist *= buy_in
    adjusted_dist = adjusted_dist / adjusted_dist.sum() * buy_in # Renormalize to ensure sum is 100
    adjusted_dist = np.round(adjusted_dist)  # Round to nearest integer
    
    # Convert to tuple
    dirichlet_dist = tuple(adjusted_dist.tolist())
    with open('log', 'w') as f:
        f.write(f'{dirichlet_dist}')

    state = NoLimitTexasHoldem.create_state(
        automations,
        True,
        0,
        [bb/2, bb], # blinds
        1/1000, # min bet,
        dirichlet_dist,
        n_players
    )

    if deck_cards:
        custom_deck = create_custom_deck(deck_cards)
        custom_deck_cards = create_custom_deck_cards(deck_cards)
        state.deck = custom_deck 
        state.deck_cards = custom_deck_cards
    if player_hands:    
        state.hole_cards = [list(tuple(Card.parse(hand))) for hand in player_hands]

    return state

def is_terminal(game, p):
    stats = game.statuses
    return not stats[p]

def create_custom_deck(card_strings: list[str]) -> tuple[Card, ...]:
    """Create a custom deck from a list of card strings.

    >>> custom_deck = create_custom_deck(['As', 'Kh', 'Qd', 'Jc'])
    >>> custom_deck
    (As, Kh, Qd, Jc)
    >>> len(custom_deck)
    4

    :param card_strings: A list of card strings (e.g., ['As', 'Kh', 'Qd'])
    :return: A tuple of Card objects
    """
    return tuple(Card.parse(' '.join(card_strings)))

def create_custom_deck_cards(card_strings: list[str]) -> deque[Card]:
    """Create a custom deck from a list of card strings.

    >>> custom_deck = create_custom_deck(['As', 'Kh', 'Qd', 'Jc'])
    >>> custom_deck
    deque([As, Kh, Qd, Jc])
    >>> len(custom_deck)
    4

    :param card_strings: A list of card strings (e.g., ['As', 'Kh', 'Qd'])
    :return: A deque of Card objects
    """
    return deque(Card.parse(' '.join(card_strings)))

def test():
    bb_frac = 0.02
    game = get_new_game(2, deck_cards=['Ac', 'Ad', '2c', '3c', '4c'])
    print(type(game))
    print(game.min_completion_betting_or_raising_to_amount)
    print(game.stacks)
    print(game.hole_cards)
    print(game.bets)

    print(game.actor_index) # action is on p3
    game.check_or_call() # p3 cc
    print(game.actor_index)
    game.check_or_call() # p1 cc
    print(game.actor_index)
    # fork the game
    game.complete_bet_or_raise_to(0.03) # p2 cbr
    game.check_or_call() # p3 cc
    game.check_or_call() # p1 cc
    print("flop?")
    print(game.bets)
    print(game.deck_cards)
    print(game.board_cards)
    # flop
    game.complete_bet_or_raise_to(0.01) #p1 cbr
    game.fold() # p2 fold
    game.check_or_call() #p3 checks
    game.complete_bet_or_raise_to(0.01)
    game.fold()
    print(game.bets)
    print(game.stacks)
    print(game.payoffs)
    mbbs = [payoff/(bb_frac/1000) for payoff in game.payoffs]
    print(mbbs)

if __name__ == '__main__':
    test()
    #game = get_new_game(2, remaining_cards=['Ac', 'Ad', '2c', '3c', '4c'])
    #print(game.deck)