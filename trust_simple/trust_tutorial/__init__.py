from otree.api import *
from openai import OpenAI
import os
import random
import time
import json
from statistics import mean, mode
import math
import random

doc = """
Storytelling app
"""

class Constants(BaseConstants):
    name_in_url = 'feedback_study'
    players_per_group = 2
    num_rounds = 1
    chatgpt_prompt = "Improve the feedback: keep the content constant, improve the delivery to make it more constructive and softened. Max 200 words, try to keep the same length, use minimal punctuation (e.g., no hyphens). The context is the following: you are asked by and undegrad student to improve feedback, your improved version will be directly sent to a peer, don't put anything that could give away that it has been improved by AI."
    images = [
        {'image': f'trust_tutorial/image{i}.png', 'choices': choices, 'correct': correct}
        for i, (choices, correct) in enumerate([
            (['jealous', 'panicked', 'arrogant', 'hateful'], 'panicked'),
            (['playful', 'comforting', 'irritated', 'bored'], 'playful'),
            (['terrified', 'upset', 'arrogant', 'annoyed'], 'upset'),
            (['joking', 'flustered', 'desire', 'convinced'], 'desire'),
            (['joking', 'insisting', 'amused', 'relaxed'], 'insisting'),
            (['irritated', 'sarcastic', 'worried', 'friendly'], 'worried'),
            (['aghast', 'fantasizing', 'impatient', 'alarmed'], 'fantasizing'),
            (['apologetic', 'friendly', 'uneasy', 'dispirited'], 'uneasy'),
            (['despondent', 'relieved', 'shy', 'excited'], 'despondent'),
            (['annoyed', 'hostile', 'horried', 'preoccupied'], 'preoccupied'),
            (['cautious', 'insisting', 'bored', 'aghast'], 'cautious'),
            (['terrified', 'amused', 'regretful', 'flirtatious'], 'regretful'),
            (['indifferent', 'embarrassed', 'skeptical', 'dispirited'], 'skeptical'),
            (['decisive', 'anticipating', 'threatening', 'shy'], 'anticipating'),
            (['irritated', 'disappointed', 'depressed', 'accusing'], 'accusing'),
            (['contemplative', 'flustered', 'encouraging', 'amused'], 'contemplative'),
            (['irritated', 'thoughtful', 'encouraging', 'sympathetic'], 'thoughtful'),
            (['doubtful', 'affectionate', 'playful', 'aghast'], 'doubtful'),
            (['decisive', 'amused', 'aghast', 'bored'], 'decisive'),
            (['arrogant', 'grateful', 'sarcastic', 'tentative'], 'tentative'),
            (['dominant', 'friendly', 'guilty', 'horrified'], 'friendly'),
            (['embarrassed', 'fantasizing', 'confused', 'panicked'], 'fantasizing'),
            (['preoccupied', 'grateful', 'insisting', 'imploring'], 'preoccupied'),
            (['contented', 'apologetic', 'defiant', 'curious'], 'defiant'),
            (['pensive', 'irritated', 'excited', 'hostile'], 'pensive'),
            (['panicked', 'incredulous', 'despondent', 'interested'], 'interested'),
            (['alarmed', 'shy', 'hostile', 'anxious'], 'hostile'),
            (['joking', 'cautious', 'arrogant', 'reassuring'], 'cautious'),
            (['interested', 'joking', 'affectionate', 'contented'], 'interested'),
            (['impatient', 'aghast', 'irritated', 'reflective'], 'reflective'),
            (['grateful', 'flirtatious', 'hostile', 'disappointed'], 'flirtatious'),
            (['ashamed', 'confident', 'joking', 'dispirited'], 'confident'),
            (['serious', 'ashamed', 'bewildered', 'alarmed'], 'serious'),
            (['embarrassed', 'guilty', 'fantasizing', 'concerned'], 'concerned'),
            (['aghast', 'baffled', 'distrustful', 'terrified'], 'distrustful'),
            (['puzzled', 'nervous', 'insisting', 'contemplative'], 'nervous'),
            (['ashamed', 'nervous', 'suspicious', 'indecisive'], 'suspicious'),
        ], start=1)
    ]


class Subsession(BaseSubsession):
    mode_ai_use = models.IntegerField(blank=True)
    mean_willing_to_pay = models.FloatField(blank=True)
    mode_writer_teammate = models.FloatField(blank=True)
    mode_writer_boss = models.FloatField(blank=True)

class Group(BaseGroup):
    story_text = models.LongStringField(label="Write a short story:")
    feedback_text = models.LongStringField(label="Write feedback on the story:")
    improved_feedback = models.LongStringField(blank=True)  # To store ChatGPT's output
    revised_story = models.LongStringField(blank=True, label="Revised story after feedback:")
    display_condition = models.StringField()  # To store raw or improved feedback condition
    feedback_to_show = models.LongStringField(blank=True)  # To store the feedback to be displayed
    #revised_story_complete = models.BooleanField(initial=False)  # Track revision completion

class Player(BasePlayer):
    assigned_role = models.StringField(blank=True)
    consent_given = models.BooleanField(
        label="I have read the above purpose of the study, and understand my role in participating in the research. I volunteer to take part in this research. I have had a chance to ask questions. If I have questions later, about the research, I can ask the investigator listed above. I understand that I may refuse to participate or withdraw from participation at any time. The investigator may withdraw me at his/her professional discretion. I certify that I am 18 years of age or older and freely give my consent to participate in this study. I will receive a copy of this document for my records.",
        widget=widgets.CheckboxInput,
    )
    responses = models.LongStringField(blank=True)  # Store all responses as a JSON string
    image_responses = models.StringField(blank=True)  # To store participant responses as a JSON string
    correct_answers = models.IntegerField(initial=0)  # To count the number of correct answers
    bonus = models.FloatField(initial=0.0)  # Store the calculated bonus
    email_address = models.StringField(
       label="Enter your email address if you want to be contacted for the $50 best story award:",
        blank=True,
    )

    task_bonus = models.FloatField(initial=0.0)

    #Feedback giver
    mode_bonus = models.FloatField(initial=0.0)
    mean_bonus = models.FloatField(initial=0.0)

    #Writer
    writer_mode_bonus_teammate = models.FloatField(initial=0.0)
    writer_mode_bonus_boss = models.FloatField(initial=0.0)

    ###Questions at the end
    # Feedback giver
    constructive_feedback = models.IntegerField(
        label="How constructive was the feedback you gave?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Very destructive"],
            [2, "Destructive"],
            [3, "Somewhat destructive"],
            [4, "Neutral"],
            [5, "Somewhat constructive"],
            [6, "Constructive"],
            [7, "Very constructive"],
        ],
    )
    relevant_feedback = models.IntegerField(
        label="How relevant was the feedback you gave?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Very irrelevant"],
            [2, "Irrelevant"],
            [3, "Somewhat irrelevant"],
            [4, "Neutral"],
            [5, "Somewhat relevant"],
            [6, "Relevant"],
            [7, "Very relevant"],
        ],
    )
    helpful_communication = models.IntegerField(
        label="To what extent was the feedback you gave communicated in a helpful way?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Very unhelpful"],
            [2, "Unhelpful"],
            [3, "Somewhat unhelpful"],
            [4, "Neutral"],
            [5, "Somewhat helpful"],
            [6, "Helpful"],
            [7, "Very helpful"],
        ],
    )
    agreeable_tone = models.IntegerField(
        label="How agreeable was the tone of the advice you gave?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Very disagreeable"],
            [2, "Disagreeable"],
            [3, "Somewhat disagreeable"],
            [4, "Neutral"],
            [5, "Somewhat agreeable"],
            [6, "Agreeable"],
            [7, "Very agreeable"],
        ],
    )
    harsh_feedback = models.IntegerField(
        label="How harsh was the feedback you gave?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Very soft"],
            [2, "Soft"],
            [3, "Somewhat soft"],
            [4, "Neutral"],
            [5, "Somewhat harsh"],
            [6, "Harsh"],
            [7, "Very harsh"],
        ],
    )
    rude_feedback = models.IntegerField(
        label="How rude was the feedback you gave?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Very polite"],
            [2, "Polite"],
            [3, "Somewhat polite"],
            [4, "Neutral"],
            [5, "Somewhat rude"],
            [6, "Rude"],
            [7, "Very rude"],
        ],
    )
    collaborative_teammate = models.IntegerField(
        label="How collaborative was your teammate?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Very uncooperative"],
            [2, "Uncooperative"],
            [3, "Somewhat uncooperative"],
            [4, "Neutral"],
            [5, "Somewhat collaborative"],
            [6, "Collaborative"],
            [7, "Very collaborative"],
        ],
    )
    feedback_incorporation = models.IntegerField(
        label="To what extent do you believe they incorporated your feedback?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    satisfaction_with_interactions = models.IntegerField(
        label="How satisfied are you with the interactions with your teammate?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    work_with_teammate_again = models.IntegerField(
        label="If paired in another experiment, would you choose to work with this teammate again?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    ai_use = models.IntegerField(
        label="Would you have wanted to use AI to revise your feedback before sending it to your teammate?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    ai_use_beliefs = models.IntegerField(
        label="On average, do you think other participants in your position (advice giver) would have wanted to use AI to revise your feedback before sending it to their teammate? If you choose the most common response (mode), you will get an extra 1$.",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    willing_to_pay_for_ai = models.FloatField(
        label="If given the option, how much would you be willing to pay for an AI revision before sending your advice to your teammate?",
    )
    beliefs_willing_to_pay_for_ai = models.FloatField(
        label="On average, how much do you think other participants in your position would be willing to pay for an AI revision?",
    )
    chatgpt_interpersonal = models.IntegerField(
        label="To what extent do you think ChatGPT can improve outcomes in interpersonal tasks?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    chatgpt_feedback = models.IntegerField(
        label="To what extent do you think ChatGPT can improve outcomes in providing feedback?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    chatgpt_cognitive = models.IntegerField(
        label="To what extent do you think ChatGPT can improve outcomes in cognitive demanding tasks?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    chatgpt_manual = models.IntegerField(
        label="To what extent do you think ChatGPT can improve outcomes in manual tasks?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    chatgpt_routine = models.IntegerField(
        label="To what extent do you think ChatGPT can improve outcomes in routine tasks?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    chatgpt_non_routine = models.IntegerField(
        label="To what extent do you think ChatGPT can improve outcomes in non-routine tasks?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    use_ai_frequency = models.IntegerField(
        label="How often do you use AI (e.g., ChatGPT)?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Never"],
            [2, "Once a month"],
            [3, "Once a week"],
            [4, "Every other day"],
            [5, "Once a day"],
            [6, "Several times a day"],
            [7, "Almost constantly"],
        ],
    )
    risk_taker = models.IntegerField(
        label="How do you see yourself? Are you generally a risk-taker or do you try to avoid risks?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Very risk averse"],
            [2, "Risk averse"],
            [3, "Somewhat risk averse"],
            [4, "Neutral"],
            [5, "Somewhat risk seeking"],
            [6, "Risk seeking"],
            [7, "Very risk seeking"],
        ],
    )
    political_stance = models.IntegerField(
        label="In politics, where do you personally stand?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Very liberal"],
            [2, "Liberal"],
            [3, "Somewhat liberal"],
            [4, "Neutral"],
            [5, "Somewhat conservative"],
            [6, "Conservative"],
            [7, "Very conservative"],
        ],
    )
    charity_donation_frequency = models.IntegerField(
        label="How often do you donate to a charity?",
        choices=[
            [1, "Never"],
            [2, "Once or twice a year"],
            [3, "Three to four times a year"],
            [4, "Five to six times a year"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    charity_volunteer = models.BooleanField(
        label="Do you volunteer for charity?",
        widget=widgets.RadioSelectHorizontal,
    )
    volunteer_hours = models.IntegerField(
        label="If yes, how many hours of charity work do you do annually?",
        choices=[
            [1, "More than 60 hours"],
            [2, "40 to 60 hours"],
            [3, "20 to 40 hours"],
            [4, "10 to 20 hours"],
            [5, "Less than 10 hours"],
            [6, "Zero hours"],
        ],
        blank=True,
        widget=widgets.RadioSelectHorizontal,
    )
    age = models.IntegerField(label="How old are you?")
    gender = models.StringField(
        label="What gender best describes you?",
        choices=["Male", "Female", "Non-binary", "Other", "Prefer not to say"],
    )
    ethnicity = models.StringField(
        label="What is your ethnicity?",
        choices=[
            "American Indian or Alaskan Native",
            "Asian / Pacific Islander",
            "Black or African American",
            "Hispanic",
            "White / Caucasian",
            "Multiple ethnicity/Other",
            "Prefer not to say",
        ],
    )
    english_level = models.StringField(
        label="What is your English level?",
        choices=["Fluent", "C1-C2", "B1-B2"],
    )
    school_affiliation = models.StringField(
        label="What school are you affiliated to?",
        choices=[
            "Architecture, Planning, & Preservation, Graduate School of",
            "Arts and Sciences, Graduate School of",
            "Arts, School of the",
            "Barnard College",
            "Columbia Business School",
            "Columbia Climate School",
            "Columbia College",
            "Columbia Journalism School",
            "Columbia Law School",
            "Dental Medicine, College of",
            "Engineering and Applied Science, Fu Foundation School of",
            "General Studies, School of",
            "International and Public Affairs, School of",
            "Jewish Theological Seminary",
            "Nursing, School of",
            "Physicians and Surgeons, Vagelos College of",
            "Professional Studies, School of",
            "Public Health, Mailman School of",
            "Social Work, School of",
            "Teachers College",
            "Union Theological Seminary",
            "Other",
        ],
    )
    program = models.StringField(
        label="What program are you in?",
        choices=["Undergrad", "Master", "MBA", "Other"],
    )
    year = models.StringField(
        label="What year are you in?",
        choices=["1st", "2nd", "3rd", "Other", "I am not a student"],
    )
    participation_satisfaction = models.IntegerField(
        label="Are you glad you participated in the study?",
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Neutral"],
            [4, "Fairly"],
            [5, "Totally"],
        ],
    )
    comments = models.LongStringField(
        label="If you want to make a comment, feel free here:",
        blank=True,
    )

    # Writer fields
    constructive_feedback_received = models.IntegerField(
        label="How constructive was the feedback you received?",
        choices=[
            [1, "Very destructive"],
            [2, "Destructive"],
            [3, "Somewhat destructive"],
            [4, "Neutral"],
            [5, "Somewhat constructive"],
            [6, "Constructive"],
            [7, "Very constructive"],
        ],
    )
    relevant_feedback_received = models.IntegerField(
        label="How relevant was the feedback you received?",
        choices=[
            [1, "Very irrelevant"],
            [2, "Irrelevant"],
            [3, "Somewhat irrelevant"],
            [4, "Neutral"],
            [5, "Somewhat relevant"],
            [6, "Relevant"],
            [7, "Very relevant"],
        ],
    )
    helpful_communication_received = models.IntegerField(
        label="To what extent was feedback you received communicated in a helpful way?",
        choices=[
            [1, "Very unhelpful"],
            [2, "Unhelpful"],
            [3, "Somewhat unhelpful"],
            [4, "Neutral"],
            [5, "Somewhat helpful"],
            [6, "Helpful"],
            [7, "Very helpful"],
        ],
    )
    agreeable_tone_received = models.IntegerField(
        label="How agreeable was the tone of the advice you received?",
        choices=[
            [1, "Very disagreeable"],
            [2, "Disagreeable"],
            [3, "Somewhat disagreeable"],
            [4, "Neutral"],
            [5, "Somewhat agreeable"],
            [6, "Agreeable"],
            [7, "Very agreeable"],
        ],
    )
    harsh_feedback_received = models.IntegerField(
        label="How harsh was the feedback you received?",
        choices=[
            [1, "Very soft"],
            [2, "Soft"],
            [3, "Somewhat soft"],
            [4, "Neutral"],
            [5, "Somewhat harsh"],
            [6, "Harsh"],
            [7, "Very harsh"],
        ],
    )
    rude_feedback_received = models.IntegerField(
        label="How rude was the feedback you received?",
        choices=[
            [1, "Very polite"],
            [2, "Polite"],
            [3, "Somewhat polite"],
            [4, "Neutral"],
            [5, "Somewhat rude"],
            [6, "Rude"],
            [7, "Very rude"],
        ],
    )
    collaborative_teammate_received = models.IntegerField(
        label="How collaborative was your teammate?",
        choices=[
            [1, "Very uncooperative"],
            [2, "Uncooperative"],
            [3, "Somewhat uncooperative"],
            [4, "Neutral"],
            [5, "Somewhat collaborative"],
            [6, "Collaborative"],
            [7, "Very collaborative"],
        ],
    )

    feedback_shaped_final_story = models.IntegerField(
        label="To what extent do you believe the feedback you received shaped the final story?",
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    satisfaction_with_interactions_received = models.IntegerField(
        label="How satisfied are you with the interactions with your teammate?",
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )
    work_with_teammate_again_received = models.IntegerField(
        label="If paired in another experiment, would you choose to work with this teammate again?",
        choices=[
            [1, "Not at all"],
            [2, "Slightly"],
            [3, "Somewhat"],
            [4, "Neutral"],
            [5, "Fairly"],
            [6, "Very"],
            [7, "Totally"],
        ],
    )

    # Writer preferences: teammate feedback
    writer_preference_teammate = models.StringField(
        choices=["Harsher from non-AI", "Softer with help of AI"],
        label="Would you rather receive harsher feedback from a teammate who doesn’t use AI or less harsh feedback from a teammate who uses AI?",
        widget=widgets.RadioSelect
    )

    writer_belief_teammate = models.StringField(
        choices=["Harsher from non-AI", "Softer with help of AI"],
        label="What do you think most participants would prefer: harsher feedback from a teammate who doesn’t use AI or less harsh feedback from a teammate who uses AI?",
        widget=widgets.RadioSelect
    )

    # Writer preferences: boss feedback
    writer_preference_boss = models.StringField(
        choices=["Harsher from non-AI", "Softer with help of AI"],
        label="Would you rather receive harsher feedback from a boss who doesn’t use AI or less harsh feedback from a boss who uses AI?",
        widget=widgets.RadioSelect
    )

    writer_belief_boss = models.StringField(
        choices=["Harsher from non-AI", "Softer with help of AI"],
        label="What do you think most participants would prefer: harsher feedback from a boss who doesn’t use AI or less harsh feedback from a boss who uses AI?",
        widget=widgets.RadioSelect
    )

class WaitAfterConsent(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        subsession.group_randomly()
        for group in subsession.get_groups():
            group.display_condition = random.choice(["raw", "improved"])
            for p in group.get_players():
                p.assigned_role = "writer" if p.id_in_group == 1 else "feedback_giver"

# FUNCTIONS
def calculate_correct_answers(self):
    """Calculate the number of correct answers and set the bonus."""
    try:
        responses = json.loads(self.responses)  # Parse responses from JSON
        correct_count = sum(
            1 for i, response in enumerate(responses)
            if response == Constants.images[i]['correct']
        )
        self.correct_answers = correct_count
        self.bonus = correct_count * 0.10  # $0.10 per correct answer
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error in calculate_correct_answers: {e}")
        self.correct_answers = 0
        self.bonus = 0.0

def runGPT(messages):
    try:
        # Create OpenAI client
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Set up retry parameters
        max_retries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                # Call the new chat completion endpoint
                response = client.chat.completions.create(
                    messages=messages,
                    #model="gpt-3.5-turbo",  # Update to your preferred model
                    model="gpt-4",
                    temperature=0,  # Adjust temperature as needed
                    max_tokens=200  # Adjust token limit as needed
                )

                # Extract and return the first choice's content
                return response.choices[0].message.content

            except openai.error.RateLimitError:
                if attempt < max_retries - 1:  # Retry if not the last attempt
                    print(f"Rate limit hit. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    # If retries are exhausted
                    print("Exceeded retry attempts due to rate limit.")
                    return "There is a technical issue. Raise your hand."

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "There is a technical issue. Raise your hand."


def generate_improved_feedback(group: Group):
    try:
        print("Generating improved feedback...")  # Debugging
        # Construct the GPT messages
        messages = [
            {"role": "system", "content": Constants.chatgpt_prompt},
            {"role": "user", "content": group.feedback_text},
        ]
        # Call GPT
        improved_feedback = runGPT(messages)

        # Assign the improved feedback to the group field
        group.improved_feedback = improved_feedback

        # Debugging
        print(f"Original Feedback: {group.feedback_text}")
        print(f"Improved Feedback: {group.improved_feedback}")
    except Exception as e:
        print(f"Error generating improved feedback: {e}")
        group.improved_feedback = f"Error: {e}"

# Collect responses for the mode question (feedback giver only)
    ai_revision_responses = [
        p.ai_use_beliefs for p in group.subsession.get_players()
        if p.id_in_group == 2 and p.field_maybe_none('ai_use_beliefs') is not None
    ]

    if ai_revision_responses:
        # Calculate and store the mode
        try:
            mode_value = mode(ai_revision_responses)
        except:
            mode_value = ai_revision_responses[0]  # If only one response exists, use it as mode
        Subsession.mode_ai_revision = mode_value
        print(f"[Debug] Mode for 'use AI revision': {mode_value}")
    else:
        Subsession.mode_ai_revision = 1  # Default to 1 if no responses

    # Collect responses for the mean question (feedback giver only)
    willingness_to_pay_responses = [
        p.willing_to_pay_for_ai for p in group.subsession.get_players()
        if p.id_in_group == 2 and p.field_maybe_none('willing_to_pay_for_ai') is not None
    ]

    if willingness_to_pay_responses:
        # Calculate and store the mean
        mean_value = sum(willingness_to_pay_responses) / len(willingness_to_pay_responses)
        Subsession.mean_willing_to_pay = mean_value
        print(f"[Debug] Mean for 'willing to pay for AI': {mean_value}")
    else:
        Subsession.mean_willing_to_pay = 1.0  # Default to $1 if no responses


def calculate_mode_and_mean(subsession):
    """ Compute the mode of ai_use and the mean of willing_to_pay_for_ai for P2 players. """

    players_p2 = [p for p in subsession.get_players() if p.id_in_group == 2]

    # Mode calculation for AI Use
    ai_use_responses = [p.field_maybe_none("ai_use") for p in players_p2 if p.field_maybe_none("ai_use") is not None]

    if ai_use_responses:
        try:
            subsession.mode_ai_use = mode(ai_use_responses)  # Most common response
        except:
            subsession.mode_ai_use = random.choice(ai_use_responses)  # If there's a tie, pick randomly
    else:
        subsession.mode_ai_use = random.choice(range(1, 8))  # Default to a random value if no responses

    # Mean calculation for Willingness to Pay
    wtp_values = [p.field_maybe_none("willing_to_pay_for_ai") for p in players_p2 if
                  p.field_maybe_none("willing_to_pay_for_ai") is not None]

    if wtp_values:
        subsession.mean_willing_to_pay = sum(wtp_values) / len(wtp_values)
    else:
        subsession.mean_willing_to_pay = 0.0  # Default to 0 if no data

def set_final_payoff(player: Player):
    subsession = player.subsession
    base_payoff = 15.0  # Fixed base payoff

    # Task bonus (everyone)
    player.task_bonus = player.correct_answers * 0.10 if player.correct_answers else 0.0

    # Feedback giver bonuses (Player 2)
    if player.id_in_group == 2:
        mode_val = subsession.field_maybe_none("mode_ai_use")
        mean_val = subsession.field_maybe_none("mean_willing_to_pay") or 0.0
        player.mode_bonus = 1.0 if player.ai_use_beliefs == mode_val else 0.0

        belief = player.field_maybe_none("beliefs_willing_to_pay_for_ai")
        player.mean_bonus = (
            1.0 if belief is not None and mean_val * 0.95 <= belief <= mean_val * 1.05 else 0.0
        )

    # Writer bonuses (Player 1)
    if player.id_in_group == 1:
        teammate_beliefs = [
            p.writer_belief_teammate for p in subsession.get_players()
            if p.id_in_group == 1 and p.writer_belief_teammate is not None
        ]
        boss_beliefs = [
            p.writer_belief_boss for p in subsession.get_players()
            if p.id_in_group == 1 and p.writer_belief_boss is not None
        ]

        try:
            mode_teammate = mode(teammate_beliefs)
        except:
            mode_teammate = teammate_beliefs[0] if teammate_beliefs else None

        try:
            mode_boss = mode(boss_beliefs)
        except:
            mode_boss = boss_beliefs[0] if boss_beliefs else None

        writer_teammate = player.field_maybe_none("writer_belief_teammate")
        writer_boss = player.field_maybe_none("writer_belief_boss")

        player.writer_mode_bonus_teammate = 1.0 if writer_teammate == mode_teammate else 0.0
        player.writer_mode_bonus_boss = 1.0 if writer_boss == mode_boss else 0.0

    # Safely retrieve bonuses (always use stored values)
    mode_bonus = player.mode_bonus or 0.0
    mean_bonus = player.mean_bonus or 0.0
    writer_mode_bonus_teammate = player.writer_mode_bonus_teammate or 0.0
    writer_mode_bonus_boss = player.writer_mode_bonus_boss or 0.0

    # Final payoff (for all)
    unrounded_total = (
        base_payoff +
        player.task_bonus +
        mode_bonus +
        mean_bonus +
        writer_mode_bonus_teammate +
        writer_mode_bonus_boss
    )

    player.payoff = cu(math.ceil(unrounded_total))

def set_final_payoffs(subsession: Subsession):
    for p in subsession.get_players():
        set_final_payoff(p)

# PAGES
class WriteStory(Page):
    form_model = 'group'
    form_fields = ['story_text']
    timeout_seconds = 420  # 600 later

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 1  # Only Player 1 writes the story


class WaitForStory(WaitPage):
    pass


class ProvideFeedback(Page):
    form_model = 'group'
    form_fields = ['feedback_text']
    timeout_seconds = 300 #600 later

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 2  # Only Player 2 provides feedback

    @staticmethod
    def vars_for_template(player):
        return dict(story=player.group.story_text)
# **Wait Page to Ensure Mode and Mean Are Calculated**
class WaitForFeedback(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        # Generate improved feedback only if the condition is "improved"
        if group.display_condition == "improved" and group.field_maybe_none('improved_feedback') is None:
            generate_improved_feedback(group)

        # Assign feedback to be displayed
        group.feedback_to_show = (
            group.feedback_text
            if group.display_condition == "raw"
            else (group.field_maybe_none('improved_feedback') or group.feedback_text)  # Fallback to raw feedback
        )

class ViewFeedback(Page):
    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 1  # Only Player 1 views feedback

    @staticmethod
    def vars_for_template(player):
        group = player.group
        feedback_to_show = (
            group.feedback_text
            if group.display_condition == "raw"
            else group.improved_feedback
        )
        feedback_type = "Raw" if group.display_condition == "raw" else "Improved"

        return dict(
            feedback=feedback_to_show,
            feedback_type=feedback_type,  # Pass feedback type to the template
        )

class ReviseStory(Page):
    form_model = 'group'
    form_fields = ['revised_story']
    timeout_seconds = 300 #600 later

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 1  # Only Player 1 revises the story

    @staticmethod
    def vars_for_template(player):
        group = player.group
        return dict(
            original_story=group.story_text,
            feedback=group.feedback_to_show,  # Use the assigned feedback (raw or improved)
        )


class FinalStory(Page):
    @staticmethod
    def vars_for_template(player):
        group = player.group
        final_story = group.field_maybe_none('revised_story') or group.story_text  # Default to original story
        print(f"[Debug] Final story shown to Player {player.id_in_group}: {final_story}")
        return dict(
            final_story=final_story,
            is_writer=(player.id_in_group == 1),  # Identify if this is the writer
        )

class WaitForRevision(WaitPage):
    title_text = "Waiting for Your Teammate"
    body_text = (
        "Your teammate is revising the story. "
        "You will proceed once they finish submitting the revised version."
    )

    @staticmethod
    def is_displayed(player: Player):
        # This wait page is only displayed to the feedback giver (Player 2)
        return player.id_in_group == 2

    @staticmethod
    def after_all_players_arrive(group: Group):
        # This ensures that the wait ends as soon as the writer (Player 1) submits the revised story
        if not group.field_maybe_none("revised_story"):
            print("[Debug] Feedback giver is waiting for the writer to finish revising.")

class IntroductionPage(Page):
    form_model = 'player'
    form_fields = ['consent_given']

    @staticmethod
    def vars_for_template(player):
        return dict(
            consent_text="""
            STORYTELLING STUDY
            AAAV5817(M00Y01)

            CONSENT FORM
            ... [Text of the consent form from above] ...
            """
        )

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class FirstChapterIntroduction(Page):
    pass

class EyesTask(Page):
    form_model = 'player'
    form_fields = ['responses']
    timeout_seconds = 600

    @staticmethod
    def vars_for_template(player: Player):
        return {'images': Constants.images}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        try:
            # Parse responses from JSON
            responses = json.loads(player.responses)
            correct_count = sum(
                1 for i, response in enumerate(responses)
                if response == Constants.images[i]['correct']
            )
            # Update correct_answers and bonus
            player.correct_answers = correct_count
            player.bonus = correct_count * 0.10  # $0.10 per correct answer
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error calculating correct answers: {e}")
            player.correct_answers = 0
            player.bonus = 0.0


class Results(Page):
    @staticmethod
    def vars_for_template(player):
        return {
            'correct_answers': player.correct_answers,
            'bonus': player.bonus,
        }


class SecondChapter(Page):
    @staticmethod
    def is_displayed(player):
        return True  # Show this page to all players

    @staticmethod
    def vars_for_template(player):
        # Add any dynamic content you want here
        return {}


class TaskInstructions(Page):
    @staticmethod
    def is_displayed(player):
        return True  # Ensure this page is displayed for the players

    @staticmethod
    def vars_for_template(player):
        return {}  # You can add any dynamic variables here if needed

class ReadingTime(Page):
    @staticmethod
    def is_displayed(player):
        # Only display this page to the feedback giver (Player 2)
        return player.id_in_group == 2
    timeout_seconds = 420  # 600 later

class FeedbackGiverQuestions(Page):
    form_model = "player"
    form_fields = [
        "constructive_feedback",
        "relevant_feedback",
        "helpful_communication",
        "agreeable_tone",
        "harsh_feedback",
        "rude_feedback",
        "collaborative_teammate",
        "feedback_incorporation",
        "satisfaction_with_interactions",
        "work_with_teammate_again",
        "ai_use",
    ]

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 2

class FeedbackGiverQuestions2(Page):
    form_model = "player"
    form_fields = [
        "ai_use_beliefs",
        "willing_to_pay_for_ai",
    ]

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 2

class FeedbackGiverQuestions3(Page):
    form_model = "player"
    form_fields = [
        "beliefs_willing_to_pay_for_ai",
        "chatgpt_interpersonal",
        "chatgpt_feedback",
        "chatgpt_cognitive",
        "chatgpt_manual",
        "chatgpt_routine",
        "chatgpt_non_routine",
        "use_ai_frequency",
        "risk_taker",
        "political_stance",
        "charity_volunteer",
        "volunteer_hours",
    ]

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 2

class WriterFinalQuestions(Page):
    form_model = "player"
    form_fields = [
        "constructive_feedback_received",
        "relevant_feedback_received",
        "helpful_communication_received",
        "agreeable_tone_received",
        "harsh_feedback_received",
        "rude_feedback_received",
        "collaborative_teammate_received",
        "feedback_shaped_final_story",
        "satisfaction_with_interactions_received",
        "work_with_teammate_again_received",
        "writer_preference_teammate",
    ]

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 1

class WriterFinalQuestions2(Page):
    form_model = "player"
    form_fields = [
        "writer_belief_teammate",
        "writer_preference_boss",
    ]

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 1

class WriterFinalQuestions3(Page):
    form_model = "player"
    form_fields = [
        "writer_belief_boss",
        "chatgpt_interpersonal",
        "chatgpt_feedback",
        "chatgpt_cognitive",
        "chatgpt_manual",
        "chatgpt_routine",
        "chatgpt_non_routine",
        "use_ai_frequency",
        "risk_taker",
        "political_stance",
        "charity_volunteer",
        "volunteer_hours",
    ]

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 1

class Demographics(Page):
    form_model = "player"
    form_fields = [
        "age",
        "gender",
        "ethnicity",
        "english_level",
        "school_affiliation",
        "program",
        "year",
        "participation_satisfaction",
        "comments",
    ]

    def error_message(player, values):
        if values.get('charity_volunteer') == 'Yes' and values.get('volunteer_hours') is None:
            return "Please tell us how many hours you volunteer annually."

class WaitForWriter(WaitPage):
    after_all_players_arrive = "calculate_mode_and_mean"

    title_text = "Waiting for Your Teammate"
    body_text = (
        "Please wait while your teammate finishes revising their story. "
        "Once they submit their final version, you will proceed to the next step."
    )

    @staticmethod
    def is_displayed(player):
        # Only Feedback Giver (Player 2) sees this page
        return player.id_in_group == 2

    @staticmethod
    def get_timeout_seconds(player):
        # Add a timeout to ensure players are not stuck indefinitely
        return 300  # Timeout in seconds (e.g., 5 minutes)

    @staticmethod
    def after_all_players_arrive(group: Group):
        pass  # No additional actions needed; just let the feedback giver proceed

class WaitForRevision(WaitPage):
    title_text = "Waiting for Your Teammate"
    body_text = (
        "Your teammate is revising the story. "
        "You will be able to proceed to the final page once they submit their revision."
    )

    @staticmethod
    def is_displayed(player: Player):
        # Only display this wait page to the feedback giver (Player 2)
        # if the revised story is not yet submitted
        return player.id_in_group == 2 and not player.group.field_maybe_none("revised_story")

    @staticmethod
    def after_all_players_arrive(group: Group):
        # This method ensures the wait ends as soon as the writer submits their revision
        pass

class ThankYouPage(Page):
    form_model = "player"
    form_fields = ["email_address"]

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        print("Page reached by player:", player.id_in_group, "round:", player.round_number)
        set_final_payoff(player)

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        subsession = player.subsession

        # Pull only stored values — no recomputation
        base_payoff = 15.0
        task_bonus = player.task_bonus or 0.0
        mode_bonus = player.mode_bonus or 0.0
        mean_bonus = player.mean_bonus or 0.0
        writer_mode_bonus_teammate = player.writer_mode_bonus_teammate or 0.0
        writer_mode_bonus_boss = player.writer_mode_bonus_boss or 0.0

        unrounded_total = base_payoff + task_bonus + mode_bonus + mean_bonus + writer_mode_bonus_teammate + writer_mode_bonus_boss
        final_payoff = float(player.payoff)

        # Optional debug assertion (keep this while testing)
        assert final_payoff == math.ceil(unrounded_total), f"[ERROR] Payoff mismatch: stored {final_payoff} vs computed {math.ceil(unrounded_total)}"

        return {
            "final_payoff": round(final_payoff, 2),
            "unrounded_total": round(unrounded_total, 2),
            "task_bonus": round(task_bonus, 2),
            "mode_bonus": mode_bonus,
            "mean_bonus": mean_bonus,
            "writer_mode_bonus_teammate": writer_mode_bonus_teammate,
            "writer_mode_bonus_boss": writer_mode_bonus_boss,
            "mode_ai_use": subsession.field_maybe_none("mode_ai_use") or "N/A",
            "mean_willing_to_pay": round(subsession.field_maybe_none("mean_willing_to_pay") or 0.0, 2),
            "willing_to_pay_for_ai": player.field_maybe_none("willing_to_pay_for_ai") or "N/A",
            "beliefs_willing_to_pay_for_ai": player.field_maybe_none("beliefs_willing_to_pay_for_ai") or "N/A",
            "ai_use": player.field_maybe_none("ai_use") or "N/A",
            "ai_use_beliefs": player.field_maybe_none("ai_use_beliefs") or "N/A",
            "final_story": group.revised_story or group.story_text or "No story was submitted.",
        }

def check_writer_mode_bonus_storage(players):
    results = []
    for p in players:
        result = {
            "participant_id": p.participant.code,
            "role": p.id_in_group,
            "writer_belief_teammate": p.field_maybe_none("writer_belief_teammate"),
            "writer_belief_boss": p.field_maybe_none("writer_belief_boss"),
            "writer_mode_bonus_teammate": p.field_maybe_none("writer_mode_bonus_teammate"),
            "writer_mode_bonus_boss": p.field_maybe_none("writer_mode_bonus_boss"),
            "payoff": float(p.payoff),
        }
        results.append(result)
    import pandas as pd
    df = pd.DataFrame(results)
    import ace_tools as tools; tools.display_dataframe_to_user(name="Writer Bonus Debug", dataframe=df)
    df.head()

class FinalPayoffWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        calculate_mode_and_mean(subsession)
        set_final_payoffs(subsession)

# Display order of the pages
page_sequence = [
    IntroductionPage,
    WaitAfterConsent,
    FirstChapterIntroduction,
    EyesTask,
    Results,
    SecondChapter,
    TaskInstructions,
    WriteStory,
    ReadingTime,
    WaitForStory,
    ProvideFeedback,
    WaitForFeedback,
    ViewFeedback,
    ReviseStory,
    FeedbackGiverQuestions,
    FeedbackGiverQuestions2,
    FeedbackGiverQuestions3,
    WriterFinalQuestions,
    WriterFinalQuestions2,
    WriterFinalQuestions3,
    Demographics,
    WaitForWriter,
    FinalStory,
    WaitForRevision,
    FinalPayoffWaitPage,
    ThankYouPage
]