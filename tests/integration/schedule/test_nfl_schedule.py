import mock
import os
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY, REGULAR_SEASON, WIN
from sportsreference.nfl.constants import SCHEDULE_URL
from sportsreference.nfl.schedule import Schedule


MONTH = 9
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 19


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nfl', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if 'playoff' in div.lower():
                return read_file('playoff_table.html')
            return read_file('table.html')

    schedule = read_file('gamelog')
    return MockPQ(schedule)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNFLSchedule:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'week': 2,
            'day': 'Sun',
            'date': 'September 17',
            'type': REGULAR_SEASON,
            'datetime': datetime(2017, 9, 17, 0, 0),
            'result': WIN,
            'overtime': 0,
            'location': AWAY,
            'opponent_abbr': 'NOR',
            'opponent_name': 'New Orleans Saints',
            'points_scored': 36,
            'points_allowed': 20
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.schedule = Schedule('NWE')

    def test_nfl_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_nfl_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nfl_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2017, 9, 17))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value
