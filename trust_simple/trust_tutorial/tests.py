from otree.api import Bot, Submission
import random
import json
from trust_tutorial import (
    IntroductionPage, WaitAfterConsent, FirstChapterIntroduction, EyesTask,
    Results, SecondChapter, TaskInstructions, WriteStory, ReadingTime,
    WaitForStory, ProvideFeedback, WaitForFeedback, ViewFeedback, ReviseStory,
    FeedbackGiverQuestions, FeedbackGiverQuestions2, FeedbackGiverQuestions3,
    WriterFinalQuestions, WriterFinalQuestions2, WriterFinalQuestions3,
    Demographics, WaitForWriter, FinalStory, WaitForRevision,
    FinalPayoffWaitPage, ThankYouPage
)

class PlayerBot(Bot):
    def play_round(self):

        yield IntroductionPage, {'consent_given': True}
        yield FirstChapterIntroduction

        yield Submission(EyesTask, {
            'responses': json.dumps(['choice1'] * 36)
        }, check_html=False)

        yield Results
        yield SecondChapter
        yield TaskInstructions

        if self.player.id_in_group == 1:
            yield Submission(WriteStory, {'story_text': 'This is a test story written by Player 1'}, check_html=False)
            yield ReadingTime
            

        elif self.player.id_in_group == 2:
            yield
            yield Submission(ProvideFeedback, {'feedback_text': 'This is a test feedback from Player 2'}, check_html=False)
            

        if self.player.id_in_group == 1:
            yield ViewFeedback
            yield Submission(ReviseStory, {'revised_story': 'This is the revised story by Player 1'}, check_html=False)

        if self.player.id_in_group == 2:
            yield FeedbackGiverQuestions, {
                "constructive_feedback": random.randint(1, 5),
                "relevant_feedback": 5,
                "helpful_communication": 5,
                "agreeable_tone": 4,
                "harsh_feedback": 2,
                "rude_feedback": 1,
                "collaborative_teammate": 5,
                "feedback_incorporation": 4,
                "satisfaction_with_interactions_received": 5,
                "work_with_teammate_again_received": 1,
                "ai_use": 1,
            }
            yield FeedbackGiverQuestions2, {
                "ai_use_beliefs": random.randint(1, 5),
                "willing_to_pay_for_ai": round(random.uniform(1, 5), 2),
            }
            yield FeedbackGiverQuestions3, {
                "beliefs_willing_to_pay_for_ai": round(random.uniform(1, 5), 2),
                "chatgpt_interpersonal": 4,
                "chatgpt_feedback": 4,
                "chatgpt_cognitive": 5,
                "chatgpt_manual": 2,
                "chatgpt_routine": 3,
                "chatgpt_non_routine": 4,
                "use_ai_frequency": 3,
                "risk_taker": 4,
                "political_stance": 3,
                "charity_volunteer": 1,
                "volunteer_hours": 5,
            }

        if self.player.id_in_group == 1:
            yield WriterFinalQuestions, {
                "constructive_feedback_received": 4,
                "relevant_feedback_received": 4,
                "helpful_communication_received": 4,
                "agreeable_tone_received": 4,
                "harsh_feedback": 2,
                "rude_feedback": 1,
                "collaborative_teammate": 5,
                "feedback_shaped_final_story": 1,
                "satisfaction_with_interactions_received": 4,
                "work_with_teammate_again_received": 1,
                "writer_preference_teammate": 1,
            }
            yield WriterFinalQuestions2, {
                "writer_belief_teammate": random.randint(1, 5),
                "writer_preference_boss": 2,
            }
            yield WriterFinalQuestions3, {
                "writer_belief_boss": random.randint(1, 5),
                "chatgpt_interpersonal": 4,
                "chatgpt_feedback": 4,
                "chatgpt_cognitive": 5,
                "chatgpt_manual": 2,
                "chatgpt_routine": 3,
                "chatgpt_non_routine": 4,
                "use_ai_frequency": 3,
                "risk_taker": 4,
                "political_stance": 3,
                "charity_volunteer": 1,
                "volunteer_hours": 5,
            }

        yield Demographics, {
            "age": 25,
            "gender": "female",
            "ethnicity": "White",
            "english_level": "Fluent",
            "school_affiliation": "Columbia",
            "program": "PhD",
            "year": "3",
            "participation_satisfaction": 5,
            "comments": "No comments.",
        }

        
        yield FinalStory
        
        yield ThankYouPage, {"email_address": "bot@example.com"}

