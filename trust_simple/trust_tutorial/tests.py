from otree.api import Bot, Submission
import random
import json

from . import pages


class PlayerBot(Bot):
    def play_round(self):
        yield pages.IntroductionPage, {'consent_given': True}
        yield pages.FirstChapterIntroduction
        yield Submission(pages.EyesTask, {
            'responses': json.dumps(['choice1'] * 36)
        }, check_html=False)
        yield pages.Results
        yield pages.SecondChapter
        yield pages.TaskInstructions

        if self.player.id_in_group == 1:
            yield Submission(pages.WriteStory, {
                'story_text': 'This is a test story written by Player 1.'
            }, check_html=False)

        if self.player.id_in_group == 2:
            yield pages.ReadingTime  # If timer-based, omit or simulate timeout
            yield Submission(pages.ProvideFeedback, {
                'feedback_text': 'This is automated feedback from the bot.'
            }, check_html=False)

        if self.player.id_in_group == 1:
            yield pages.ViewFeedback
            yield Submission(pages.ReviseStory, {
                'revised_story': 'This is the revised story.'
            }, check_html=False)

        if self.player.id_in_group == 2:
            yield pages.FeedbackGiverQuestions, {
                "constructive_feedback": 5,
                "relevant_feedback": 5,
                "helpful_communication": 5,
                "agreeable_tone": 5,
                "harsh_feedback": 1,
                "rude_feedback": 1,
                "collaborative_teammate": 5,
                "feedback_incorporation": 5,
                "satisfaction_with_interactions_received": 5,
                "work_with_teammate_again_received": 5,
                "ai_use": 1,
            }
            yield pages.FeedbackGiverQuestions2, {
                "ai_use_beliefs": 4,
                "willing_to_pay_for_ai": 4.50,
            }
            yield pages.FeedbackGiverQuestions3, {
                "beliefs_willing_to_pay_for_ai": 3.50,
                "chatgpt_interpersonal": 4,
                "chatgpt_feedback": 4,
                "chatgpt_cognitive": 4,
                "chatgpt_manual": 3,
                "chatgpt_routine": 3,
                "chatgpt_non_routine": 4,
                "use_ai_frequency": 4,
                "risk_taker": 3,
                "political_stance": 3,
                "charity_volunteer": 1,
                "volunteer_hours": 2,
            }

        if self.player.id_in_group == 1:
            yield pages.WriterFinalQuestions, {
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
            yield pages.WriterFinalQuestions2, {
                "writer_belief_teammate": 3,
                "writer_preference_boss": 2,
            }
            yield pages.WriterFinalQuestions3, {
                "writer_belief_boss": 4,
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

        yield pages.Demographics, {
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

        yield pages.FinalStory
        yield pages.ThankYouPage, {"email_address": "bot@example.com"}
