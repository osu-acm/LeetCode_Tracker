import grequests
import time
import json


class LcAccess:
    """
    Class that holds a set of usernames (backed-up by a text file) and provides functions
    for getting recent problem submission data from LeetCode.
    """

    # Functions for manipulating our list of usernames:

    def __init__(self, users_filepath):
        self.users_filepath = users_filepath  # a filepath to the text file that holds space-separated usernames
        self.users = set()
        self.load_users()

    def load_users(self):
        """
        Initializes self.users with all the users in users_filepath.
        """
        with open(self.users_filepath, "r") as infile:
            names = infile.readline().strip().split()
            for username in names:
                self.users.add(username)
        return "User List Updated."

    def save_users(self):
        """
        Writes all the usernames in self.users to users_filepath separated by a space.
        """
        with open(self.users_filepath, "w") as outfile:
            for user in self.users:
                outfile.write(user + " ")
        return "Users saved."

    def remove_user(self, username):
        """
        Removes a user from self.users.
        returns 1 if the user is removed, else returns 0 if the user is not in the list
        """
        if username in self.users:
            self.users.remove(username)
            self.save_users()
            return 1
        else:
            return 0

    def add_user(self, username):
        """
        Adds a user to self.users if they have a leetcode account.
        Returns a result message string.
        """
        if username not in self.users:
            try:
                status_code, user_data = self._fetch_single_user_data(username)
            except Exception:
                return "Exception caught in fetching data."

            if status_code != 200 or 'errors' in user_data:
                return "Unrecognized user. Please try again."

            self.users.add(username)
            self.save_users()
            return "Added {} to the list!".format(username)
        else:
            return "{} is already on the list!".format(username)

    def get_users_str(self):
        """
        Return a string with a list of all the users.
        """
        return str(self.users)

    # Functions for getting users data from LeetCode:

    def _format_post_request(self, username):
        url = 'https://leetcode.com/graphql'
        headers = {'accept': '*/*', 'accept-encoding': 'gzip', 'accept-language': 'en-US,en;q=0.9',
                   'cache-control': 'no-cache', 'content-length': '411', 'content-type': 'application/json'}
        body = {
            "operationName": "getRecentSubmissionList",
            "variables": {
                "username": username
            },
            "query": """query getRecentSubmissionList($username: String!, $limit: Int) {
            recentSubmissionList(username: $username, limit: $limit) {
            title
            titleSlug
            timestamp
            statusDisplay
            lang
            __typename
            }
            languageList {
            id
            name
            verboseName
            __typename
            }
        }
        """
        }
        return grequests.post(url, headers=headers, data=json.dumps(body))

    def _fetch_multiple_users_data(self, usernames):
        """Calls LeetCode API for user data with multiple requests in parallel."""
        reqs = [self._format_post_request(username) for username in usernames]
        results = grequests.map(reqs, size=10)
        return results

    def _fetch_single_user_data(self, username):
        """
        Takes a username as input and returns the data from LeetCode on the user.
        Returns: status_code, user_data
        """

        req = self._format_post_request(username)
        result = grequests.map([req])[0]
        status_code = result.status_code
        user_data = json.loads(result.text)
        return status_code, user_data

    def _get_user_submission_data_from_json(self, user_result):
        """
        Given a json string result for a user, validates and returns their recent submissions.
        """
        status_code, user_data = user_result.status_code, json.loads(user_result.text)
        if status_code != 200:
            return None

        return user_data["data"]["recentSubmissionList"]

    def _format_recent_problem(self, submissions):
        """
        Given a list of submissions to LeetCode, return a formatted string of the user's most recent submission.
        """
        problem = submissions[0]
        timestamp = int(problem["timestamp"])
        readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

        r_str = """
Problem Title:  {}
Submit Time:   {}
Result:              {}     
Language:        {}
""".format(problem["title"], readable_time, problem["statusDisplay"], problem["lang"])

        return r_str

    def get_user_most_recent(self, username):
        """
        Gets a users most recent submission, returns it as a pretty-formatted string.
        """
        try:
            status_code, user_data = self._fetch_single_user_data(username)
            if status_code != 200:
                return "Server error. @Leadership you might want to check on this."
            elif 'errors' in user_data:
                return "That user does not exist. Please try again."

            return self._format_recent_problem(user_data["data"]["recentSubmissionList"])
        except Exception as identifier:
            return "Fail in query for {}".format(username)

    def recent_submissions_for_each_user(self):
        """
        Returns a string of the most recent problem each user solved.
        """
        r_str = ""
        if len(self.users) > 5:
            return "Too many users to print in one message. Please user the  `!get <username>`  command instead."

        try:
            results = self._fetch_multiple_users_data(self.users)
        except Exception:
            return "Exception caught in fetching data."

        for username, user_result in zip(self.users, results):
            submissions = self._get_user_submission_data_from_json(user_result)
            if not submissions:
                pass
            else:
                problem = self._format_recent_problem(submissions)
                r_str += "\n{}'s most recent submission:\n".format(username)
                r_str += problem
                r_str += "\n"

        return r_str

    def _calculate_num_user_submissions_in_last_week(self, user_result, range_start):
        """
        Given a user, this gets the number of problems a user solved in the last week.
        Params:
            user_result: the result of the fetch for data on the user
            range_start: time in unix epoch from one week ago.
        Returns: number of problems the user solved as an int.
        This is a helper method for weekly_recap()
        """
        uniq_solved = set()

        submission_list = self._get_user_submission_data_from_json(user_result)
        if not submission_list:
            return 0

        for submission in submission_list:
            timestamp = int(submission["timestamp"])
            time_delta = timestamp - range_start
            if time_delta >= 0:
                if (submission["statusDisplay"] == "Accepted") and (submission["title"] not in uniq_solved):
                    uniq_solved.add(submission["title"])
            else:
                break

        return len(uniq_solved)

    def weekly_recap_leaderboard(self):
        """
        Gets a count of how many problems each user has solved in the last week.
        """
        data = []
        range_start = time.time() - 604800  # Gets time from epoch 1 week ago

        try:
            results = self._fetch_multiple_users_data(self.users)
        except Exception:
            return "Exception caught in fetching data."

        for username, user_result in zip(self.users, results):
            r = self._calculate_num_user_submissions_in_last_week(user_result, range_start)
            data.append((r, username))

        data.sort(reverse=True)

        r_str = "Weekly Recap:\n`"
        for count, username in data:
            r_str += username.ljust(15)
            r_str += "{} problems solved.".format(count)
            r_str += "\n"
        return r_str + '`'
