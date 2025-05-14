from otree.api import *


doc = """
Select a random round for payment
"""


class C(BaseConstants):
    NAME_IN_URL = 'pay_random_round'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 4
    ENDOWMENT = cu(100)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    give_amount = models.CurrencyField(
        min=0, max=100, label="How much do you want to give?"
    )


# PAGES
class MyPage(Page):
    form_model = 'player'
    form_fields = ['give_amount']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        import random

        participant = player.participant

        # if it's the last round
        if player.round_number == C.NUM_ROUNDS:
            random_round = random.randint(1, C.NUM_ROUNDS)
            participant.selected_round = random_round
            player_in_selected_round = player.in_round(random_round)
            player.payoff = C.ENDOWMENT - player_in_selected_round.give_amount


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [MyPage, Results]
