from otree.api import *

class Constants(BaseConstants):
    name_in_url = 'final_save'
    players_per_group = None
    num_rounds = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    email_address = models.StringField(
        label="Enter your email address if you want to be contacted for the $50 best story award:",
        blank=True,
    )

class FinalSavePage(Page):
    form_model = 'player'
    form_fields = ['email_address']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            "participant_code": player.participant.code,
            "final_story": player.participant.vars.get('final_story', 'No story submitted.'),
            "final_payoff_display": int(player.participant.payoff) if player.participant.payoff else 0,
        }

page_sequence = [FinalSavePage]
