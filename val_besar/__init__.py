from otree.api import *
import random
import math

doc = """
For oTree beginners, it would be simpler to implement this as a discrete-time game 
by using multiple rounds, e.g. 10 rounds, where in each round both players can make a new proposal,
or accept the value from the previous round.

However, the discrete-time version has more limitations
(fixed communication structure, limited number of iterations).

Also, the continuous-time version works smoother & faster, 
and is less resource-intensive since it all takes place in 1 page.
"""


class C(BaseConstants):
    NAME_IN_URL = 'val_besar'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 20

    # Keep the roles, profits, salary, officer cost
    SALARY = 3125
    OFFICER_COST = 10
    SELLER_ROLE = 'Importir'
    BUYER_ROLE = 'Petugas Pajak'

    # Parameters for quantity and product price
    FIXED_PRICE = 20
    MEAN_QUANTITY = 200
    SD_QUANTITY = 40

    # Specific tariff (ST) for Mewah vs. Biasa
    ST_MEWAH = 3
    ST_BIASA = 2



class Subsession(BaseSubsession):

    def creating_session(self):
        # only in round 1 do your random grouping…
        if self.round_number == 1:
            self.group_randomly()
        # …and in all later rounds you “freeze” that same grouping
        else:
            self.group_like_round(1)

class Group(BaseGroup):
    deal_price = models.IntegerField()
    is_finished = models.BooleanField(initial=False)
    chance = models.IntegerField(initial=0)
    # New field to store the random quantity (so it remains consistent if page is refreshed)
    quantity = models.IntegerField(initial=0)
    category = models.StringField()


class Player(BasePlayer):
    amount_proposed = models.IntegerField()
    amount_accepted = models.IntegerField()
    mewah_tariff = models.FloatField()
    biasa_tariff = models.FloatField()
    goods_value = models.FloatField()
    pay = models.FloatField(initial=0)
    tariff = models.FloatField(initial=0)
    chance = models.IntegerField(initial=0)
    bribe = models.IntegerField(blank=True, label="Iuran kepada auditor")
    category = models.PositiveIntegerField(
        choices=[[0, 'Barang Mewah'], [1, 'Barang Biasa']],
        widget=widgets.RadioSelectHorizontal,
        label="katagori barang"
    )
    payment = models.FloatField(initial=0)
    penalty = models.FloatField(initial=0)
    potential_penalty = models.FloatField(initial=0)
    random_round = models.PositiveIntegerField()
    rekening = models.StringField(label="Nomor Rekening/Telepon")
    tipe_pembayaran = models.StringField(widget=widgets.RadioSelect,
                                label="Tipe Pembayaran",
                                choices=["Gopay", "Ovo","Shopee","BNI","Mandiri","BCA","BRI"])
    tipe_pembayaran_lain = models.StringField(
        blank=True,
        label="Jika lainnya, sebutkan:"
    )

class Bargain(Page):
    timeout_seconds = 180

    @staticmethod
    def vars_for_template(player: Player):
        """Randomize quantity (once) and show possible tariffs for Barang Mewah & Biasa."""
        group = player.group

        # Randomize quantity only once per group (if not yet set).
        if group.quantity == 0:
            q = max(1, int(random.gauss(C.MEAN_QUANTITY, C.SD_QUANTITY)))
            group.quantity = q

        # Compute possible tariffs for demonstration (e.g. to show on the template).
        player.goods_value = group.quantity * C.FIXED_PRICE

        # Compound tariff for Mewah
        player.mewah_tariff = (group.quantity * C.FIXED_PRICE * 0.20)
        # Compound tariff for Biasa
        player.biasa_tariff = (group.quantity * C.FIXED_PRICE * 0.15)

        return dict(
            other_role=player.get_others_in_group()[0].role,
            quantity=group.quantity,
            mewah_tariff=int(player.mewah_tariff),
            biasa_tariff=int(player.biasa_tariff),
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(my_id=player.id_in_group)

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        [other] = player.get_others_in_group()

        if 'amount' in data:
            try:
                amount = int(data['amount'])
            except Exception:
                print('Invalid message received', data)
                return
            if data['type'] == 'accept':
                if amount == other.amount_proposed:
                    player.amount_accepted = amount
                    group.deal_price = amount
                    group.is_finished = True
                    return {0: dict(finished=True)}
            if data['type'] == 'propose':
                player.amount_proposed = amount
            if data['type'] == 'reject':
                if amount == other.amount_proposed:
                    player.amount_accepted = 0
                    group.deal_price = 0
                    group.is_finished = True
                    return {0: dict(finished=True)}

        proposals = []
        for p in [player, other]:
            amount_proposed = p.field_maybe_none('amount_proposed')
            if amount_proposed is not None:
                proposals.append([p.id_in_group, amount_proposed])
        return {0: dict(proposals=proposals)}

    @staticmethod
    def error_message(player: Player, values):
        group = player.group
        if not group.is_finished:
            return "Game not finished yet"

    @staticmethod
    def is_displayed(player: Player):
        """Skip this page if a deal has already been made"""
        group = player.group
        deal_price = group.field_maybe_none('deal_price')
        return deal_price is None

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        """Use the new tariff scheme to compute player's payoff."""
        group = player.group
        if player.role == "Importir":
            player.potential_penalty = 1.5 * player.mewah_tariff
        else:
            player.potential_penalty = 0.5 * C.SALARY
        if timeout_happened:
            player.amount_accepted = 0
            player.amount_proposed = 0
            group.deal_price = 0

        # Compute tariff based on whether a 'deal_price' (bribe) was reached.
        # If deal_price == 0 => treat as Barang Mewah
        # If deal_price > 0 => treat as Barang Biasa
        goods_value = group.quantity * C.FIXED_PRICE


        if group.deal_price == 0:
            # Barang Mewah
            player.tariff = player.mewah_tariff
            if player.role == "Importir":
                player.pay = goods_value - player.tariff
            else:
                player.pay = C.SALARY
        else:
            # Barang Biasa
            player.tariff = player.biasa_tariff
            if player.role == "Importir":
                # Importer pays the bribe plus the tariff
                player.pay = goods_value - player.tariff - group.deal_price
            else:
                # Officer receives the bribe, minus cost
                player.pay = C.SALARY + group.deal_price


class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.role == "Petugas Pajak"

    form_model = 'player'
    form_fields = ['bribe', 'category']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if player.category == 0:
            group.category = "Barang Mewah"
        else:
            group.category = "Barang Biasa"
        players = group.get_players()
        bribe = player.field_maybe_none('bribe')
        if bribe is None:
            player.bribe = 0
        if player.bribe == 0:
            player.chance = random.randint(1, 400)
        else:
            if player.role == "Petugas Pajak":
                player.pay = C.SALARY + group.deal_price - player.bribe
            if player.bribe > 180:
                bribe = 180
            rand = random.randint(1, 400)
            player.chance = rand + bribe
        group.chance = player.chance



class ResultsWaitPage(WaitPage):
    pass


class Investigation(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        if group.category == "Barang Biasa":
            player.tariff = player.biasa_tariff
            if group.chance < 200:
                if player.role == "Importir":
                    player.penalty = 1.5 * player.tariff
                else:
                    player.penalty = 0.5 * C.SALARY
            else:
                player.penalty = 0
        else:
            player.tariff = player.mewah_tariff
            player.penalty = 0
        player.payment = player.pay - player.penalty
        if player.payment < 0:
            player.payment = 0

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        import random
        participant = player.participant

        # if it's the last round
        if player.round_number == C.NUM_ROUNDS:
            random_round = random.randint(1, C.NUM_ROUNDS)
            participant.selected_round = random_round
            player.random_round = random_round
            player_in_selected_round = player.in_round(random_round)
            player.payoff = (player.payment*100) + 25000

class MyWaitPage(WaitPage):
    pass

class Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class Results2(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

class payment(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Instructions, ResultsWaitPage, Bargain, Results, ResultsWaitPage, Investigation, MyWaitPage, Results2,payment]