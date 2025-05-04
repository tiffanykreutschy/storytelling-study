from otree.api import *

class Constants(BaseConstants):
    name_in_url = 'payment_sheet'
    players_per_group = None
    num_rounds = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    pass

class PaymentSheet(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # Get all participants
        participants_data = []
        session = player.session
        for p in session.get_participants():
            participants_data.append({
                'code': p.code,
                'payoff': round(p.payoff_plus_participation_fee(), 2),
            })
        return dict(participants_data=participants_data)

page_sequence = [PaymentSheet]
