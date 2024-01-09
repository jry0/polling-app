
import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days_after_published):
    time = timezone.now() + datetime.timedelta(days=days_after_published)
    return Question.objects.create(question_text = question_text, pub_date=time)

class QuestionModelTests(TestCase):
    
    def test_was_published_within_day_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_within_day(), False)

    def test_was_published_within_day_older_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_within_day(), False)

    def test_was_published_within_day_recent_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(hours= 23, minutes=59, seconds=59)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_within_day(), True)

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days_after_published=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days_after_published=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days_after_published=-30)
        create_question(question_text="Future question.", days_after_published=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_six_past_questions_only_five_most_recent(self):
        """
        The questions index page may display multiple questions. But only the 5 most recent.
        """
        question1 = create_question(question_text="Past question 1.", days_after_published=-6)
        question2 = create_question(question_text="Past question 2.", days_after_published=-5)
        question3 = create_question(question_text="Past question 3.", days_after_published=-4)
        question4 = create_question(question_text="Past question 4.", days_after_published=-3)
        question5 = create_question(question_text="Past question 5.", days_after_published=-2)
        question6 = create_question(question_text="Past question 6.", days_after_published=-1)
        response = self.client.get(reverse("polls:index"))

        print(response.context["latest_question_list"])
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question6, question5, question4, question3, question2],
        )