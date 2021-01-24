from ..my_sample_crowdsale import MySampleCrowdsale
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class TestMySampleCrowdsale(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(MySampleCrowdsale, self.test_account1)

    def test_hello(self):
        self.assertEqual(self.score.hello(), "Hello")
