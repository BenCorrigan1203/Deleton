# pylint: disable=unused-variable

from unittest.mock import patch

# from helper_functions import get_all_riders_rides, get_city, get_leaderboard, get_daily_rides


def test_get_request(test_client):
    '''Test get request returns the correct HTML.'''
    response = test_client.get("/")

    assert b"<h2>Top Stories</h2>" in response.data

@patch("helper_functions.get_stories")
def test_get_stories_returns_list(mock_get_stories, test_client):
    '''Checks that get_all_stories returns a valid dict'''

    mock_get_stories.return_value = [{"id": 1, "title": "Sometitle", "url": "www.bbc.co.uk", "score": 0 }]

    result = test_client.get("/stories/")
    data = result.json
    print(data)

    assert isinstance(data, dict)
    assert data["success"] is True
    assert data["total_stories"] == 1
    assert result.status_code == 200