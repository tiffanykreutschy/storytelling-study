from otree.api import Bot, Submission
import random
import json

from . import IntroductionPage, FirstChapterIntroduction, EyesTask, Results, SecondChapter, TaskInstructions, WriteStory, ReadingTime, ProvideFeedback, ViewFeedback, ReviseStory, FeedbackGiverQuestions, FeedbackGiverQuestions2, FeedbackGiverQuestions3, WriterFinalQuestions, WriterFinalQuestions2, WriterFinalQuestions3, Demographics, FinalStory, ThankYouPage
from final_save import FinalSavePage

class PlayerBot(Bot):
    def play_round(self):
        yield IntroductionPage, {'consent_given': True}
        yield FirstChapterIntroduction
        yield Submission(EyesTask, {
            'responses': json.dumps([random.choice(['choice1', 'choice2', 'choice3', 'choice4']) for _ in range(36)])
        }, check_html=False)
        yield Results
        yield SecondChapter
        yield TaskInstructions

        if self.player.id_in_group == 1:
            yield Submission(WriteStory, {
                'story_text': 'This is a test story written by Player 1.'
            }, check_html=False)

        if self.player.id_in_group == 2:
            yield ReadingTime
            yield Submission(ProvideFeedback, {
                'feedback_text': 'This is automated feedback from the bot.'
            }, check_html=False)

        if self.player.id_in_group == 1:
            yield ViewFeedback
            yield Submission(ReviseStory, {
                'revised_story': 'This is the revised story.'
            }, check_html=False)

        if self.player.id_in_group == 2:
            yield FeedbackGiverQuestions, {
                "constructive_feedback": random.randint(1, 7),
                "relevant_feedback": random.randint(1, 7),
                "helpful_communication": random.randint(1, 7),
                "agreeable_tone": random.randint(1, 7),
                "harsh_feedback": random.randint(1, 7),
                "rude_feedback": random.randint(1, 7),
                "collaborative_teammate": random.randint(1, 7),
                "feedback_incorporation": random.randint(1, 7),
                "satisfaction_with_interactions": random.randint(1, 7),
                "work_with_teammate_again": random.randint(1, 7),
                "ai_use": random.randint(1, 7),
            }
            yield FeedbackGiverQuestions2, {
                "ai_use_beliefs": random.randint(1, 7),
                "willing_to_pay_for_ai": random.randint(1, 10),
            }
            yield FeedbackGiverQuestions3, {
                "beliefs_willing_to_pay_for_ai": random.randint(1, 10),
                "chatgpt_interpersonal": random.randint(1, 7),
                "chatgpt_feedback": random.randint(1, 7),
                "chatgpt_cognitive": random.randint(1, 7),
                "chatgpt_manual": random.randint(1, 7),
                "chatgpt_routine": random.randint(1, 7),
                "chatgpt_non_routine": random.randint(1, 7),
                "use_ai_frequency": random.randint(1, 7),
                "risk_taker": random.randint(1, 7),
                "political_stance": random.randint(1, 7),
                "charity_volunteer": random.choice([1, 2]),
                "volunteer_hours": random.choice([1, 2, 3, 4, 5, 6]),
            }

        if self.player.id_in_group == 1:
            yield WriterFinalQuestions, {
                "constructive_feedback_received": random.randint(1, 7),
                "relevant_feedback_received": random.randint(1, 7),
                "helpful_communication_received": random.randint(1, 7),
                "agreeable_tone_received": random.randint(1, 7),
                "harsh_feedback_received": random.randint(1, 7),
                "rude_feedback_received": random.randint(1, 7),
                "collaborative_teammate_received": random.randint(1, 7),
                "feedback_shaped_final_story": random.randint(1, 7),
                "satisfaction_with_interactions_received": random.randint(1, 7),
                "work_with_teammate_again_received": random.randint(1, 7),
                "writer_preference_teammate": random.choice([1, 2]),
            }
            yield WriterFinalQuestions2, {
                "writer_belief_teammate": random.choice([1, 2]),
                "writer_preference_boss": random.choice([1, 2]),
            }
            yield WriterFinalQuestions3, {
                "writer_belief_boss": random.choice([1, 2]),
                "chatgpt_interpersonal": random.randint(1, 7),
                "chatgpt_feedback": random.randint(1, 7),
                "chatgpt_cognitive": random.randint(1, 7),
                "chatgpt_manual": random.randint(1, 7),
                "chatgpt_routine": random.randint(1, 7),
                "chatgpt_non_routine": random.randint(1, 7),
                "use_ai_frequency": random.randint(1, 7),
                "risk_taker": random.randint(1, 7),
                "political_stance": random.randint(1, 7),
                "charity_volunteer": random.choice([1, 2]),
                "volunteer_hours": random.choice([1, 2, 3, 4, 5, 6]),
            }

        yield Demographics, {
            "age": random.choice([18, 24, 24, 26, 27, 28, 35]),
            "gender": random.choice(["Female", "Male", "Other"]),
            "ethnicity": random.choice(["Black or African American", "Black or African American", "Hispanic"]),
            "english_level": "Fluent",
            "school_affiliation": "Columbia Business School",
            "program": random.choice(["Undergrad", "MBA"]),
            "year": random.choice(["1st", "2nd", "3rd"]),
            "participation_satisfaction": random.randint(1, 5),
            "comments": "Bot test run.",
        }

        yield FinalStory
        yield ThankYouPage
        yield FinalSavePage, {"email_address": f"bot_{self.player.id_in_group}@example.com"}
