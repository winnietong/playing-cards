from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.test import TestCase
from models import Card, Player
from utils import create_deck
from forms import EmailUserCreationForm
from test_utils import run_pep8_for_package, run_pyflakes_for_package


# class BasicMathTestCase(TestCase):
#     def test_math(self):
#         a = 1
#         b = 1
#         self.assertEqual(a+b, 2)
#
#     # def test_failing_case(self):
#     #     a = 1
#     #     b = 1
#     #     self.assertAlmostEquals(a+b, 1)
#     #


class UtilTestCase(TestCase):
    def test_create_deck_count(self):
        """Test that we created 52 cards"""
        create_deck()
        self.assertEqual(Card.objects.count(), 52)


class ModelTestCase(TestCase):
    def setUp(self):
        self.card = Card.objects.create(suit=Card.CLUB, rank="jack")

    def test_get_ranking(self):
        """Test that we get the proper ranking for a card"""
        card = Card.objects.create(suit=Card.CLUB, rank="jack")
        self.assertEqual(card.get_ranking(), 11)

    def test_get_war_result_smaller_than(self):
        card1 = Card.objects.create(suit=Card.CLUB, rank="jack")
        card2 = Card.objects.create(suit=Card.CLUB, rank="queen")
        result = card1.get_war_result(card2)
        self.assertEqual(result, -1)

    def test_get_war_result_equal(self):
        card1 = Card.objects.create(suit=Card.CLUB, rank="jack")
        card2 = Card.objects.create(suit=Card.CLUB, rank="jack")
        result = card1.get_war_result(card2)
        self.assertEqual(result, 0)

    def test_get_war_result_greater_than(self):
        card1 = Card.objects.create(suit=Card.CLUB, rank="king")
        card2 = Card.objects.create(suit=Card.CLUB, rank="jack")
        result = card1.get_war_result(card2)
        self.assertEqual(result, 1)


class FormTestCase(TestCase):
    def test_clean_username_exception(self):
        # Create a player so that this username we're testing is already taken
        Player.objects.create_user(username='test-user')

        # set up the form for testing
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test-user'}

        # use a context manager to watch for the validation error being raised
        with self.assertRaises(ValidationError):
            form.clean_username()

    def test_clean_username_pass(self):

        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test-user'}

        self.assertEqual(form.clean_username(), 'test-user')


class ViewTestCase(TestCase):
    def setUp(self):
        create_deck()

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertIn('<p>Suit: spade, Rank: two</p>', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_faq_page(self):
        response = self.client.get(reverse('faq'))
        self.assertIn('<p>Q: Can I win real money on this website?</p>', response.content)

    def test_filters_page(self):
        response = self.client.get(reverse('filters'))
        self.assertIn('We have 52 cards!', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_login_page(self):
        # Create user
        password = 'passsword'
        username = 'username'
        Player.objects.create_user(username=username, password=password)

        # Check that We can log them in
        response = self.client.post(reverse('login'), {'username': username, 'password': password})

        # Check that the user is in the database
        self.assertTrue(Player.objects.filter(username=username).exists())

        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    def test_register_page(self):
        username = 'new-user'
        data = {
            'username': username,
            'email': 'test@test.com',
            'password1': 'test',
            'password2': 'test'
        }
        response = self.client.post(reverse('register'), data)

        # Check this user was created in the database
        self.assertTrue(Player.objects.filter(username=username).exists())

        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('profile')))


class SyntaxTest(TestCase):
    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        packages = ['cards']
        warnings = []
        # Eventually should use flake8 instead so we can ignore specific lines via a comment
        for package in packages:
            warnings.extend(run_pyflakes_for_package(package, extra_ignore=("_settings",)))
            warnings.extend(run_pep8_for_package(package, extra_ignore=("_settings",)))
        if warnings:
            self.fail("{0} Syntax warnings!\n\n{1}".format(len(warnings), "\n".join(warnings)))
