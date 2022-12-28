import lc_data_access
import pytest
from unittest.mock import Mock
import json

# To run these tests, simply run `pytest` in the terminal.


@pytest.fixture
def mock_post(mocker):
    mock = [Mock()]
    mocker.patch('grequests.map', return_value=mock)
    return mock


@pytest.fixture
def lc_access(tmpdir):
    print("\nsetting up")
    fake_user_store_filepath = tmpdir.join("fake_user_store.txt")
    fake_user_store_filepath.write("fake_user ")

    lc_access = lc_data_access.LcAccess(fake_user_store_filepath)
    yield lc_access
    print("\ntearing down")


def test_lc_access_intialization(lc_access):
    assert len(lc_access.users) == 1
    assert 'fake_user' in lc_access.users


def test_add_duplicate_user(lc_access):
    username = "fake_user"
    assert lc_access.add_user(username) == "{} is already on the list!".format(username)


def test_add_new_user(lc_access):
    username = "new_user"
    assert lc_access.add_user(username) == "Added {} to the list!".format(username)
    assert sorted(lc_access.users_filepath.read().split()) == ['fake_user', 'new_user']


def test_remove_user(lc_access):
    username = "new_user"
    lc_access.add_user(username)
    assert lc_access.remove_user(username) == 1
    assert lc_access.users_filepath.read() == "fake_user "


def test_remove_missing_user(lc_access):
    username = "user_not_in_our_list"
    lc_access.add_user(username)
    assert lc_access.remove_user(username) == 0
    assert lc_access.users_filepath.read() == "fake_user "


def test_get_user_most_recent(lc_access, mock_post):
    mock_post[0].status_code = 200
    mock_post[0].text = json.dumps(fake_lc_api_response)

    # Test getting a user's most recent submission
    recent = lc_access.get_user_most_recent('fake_user')
    assert type(recent) == str
    assert 'Fail' not in recent
    # print(recent)

    assert recent == """
Problem Title:  Complement of Base 10 Integer
Submit Time:   2022-09-16 13:09:05
Result:              Accepted     
Language:        python3
"""


def test_users_recents(lc_access, mock_post):
    mock_post[0].status_code = 200
    mock_post[0].text = json.dumps(fake_lc_api_response)

    recents = lc_access.recent_submissions_for_each_user()
    assert recents == """
fake_user's most recent submission:

Problem Title:  Complement of Base 10 Integer
Submit Time:   2022-09-16 13:09:05
Result:              Accepted     
Language:        python3

"""


def test_weekly_recap(lc_access, mock_post):
    mock_post[0].status_code = 200
    mock_post[0].text = json.dumps(fake_lc_api_response)

    recents = lc_access.weekly_recap_leaderboard()

    assert recents == """Weekly Recap:
`fake_user      0 problems solved.
`"""


fake_lc_api_response = {
  "data": {
    "recentSubmissionList": [
      {
        "title": "Complement of Base 10 Integer",
        "titleSlug": "complement-of-base-10-integer",
        "timestamp": "1663358945",
        "statusDisplay": "Accepted",
        "lang": "python3",
        "__typename": "SubmissionDumpNode"
      },
      {
        "title": "Partition Equal Subset Sum",
        "titleSlug": "partition-equal-subset-sum",
        "timestamp": "1663350477",
        "statusDisplay": "Accepted",
        "lang": "python3",
        "__typename": "SubmissionDumpNode"
      },
      {
        "title": "Letter Combinations of a Phone Number",
        "titleSlug": "letter-combinations-of-a-phone-number",
        "timestamp": "1663350348",
        "statusDisplay": "Accepted",
        "lang": "python3",
        "__typename": "SubmissionDumpNode"
      }
    ],
    "languageList": [
      {
        "id": 0,
        "name": "cpp",
        "verboseName": "C++",
        "__typename": "LanguageNode"
      }
    ]
  }
}
