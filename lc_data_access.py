import requests
import time
import json

USER_FILE = "user_store.txt"

class LC_Access():
        
    def __init__(self):
        self.users = set()
        self.load_users()
        
    def load_users(self):
        """
        Initializes self.users with all the users in USER_FILE.
        """
        with open(USER_FILE, "r") as infile:
            names = infile.readline().strip().split()
            for username in names:
                self.users.add(username)
        return "User List Updated."     

    def save_users(self):
        """
        Writes all the usernames in self.users to USER_FILE separated by a space.
        """
        with open(USER_FILE, "w") as outfile:
            for user in self.users:
                outfile.write(user + " ")
        return "Users saved."
    
    def _get_user_data(self, username):
        """
        Takes a username as input and returns the data from LeetCode on the user.
        Returns: status_code, user_data
        """      
        
        url = 'https://leetcode.com/graphql'
        headers = {'accept': '*/*','accept-encoding': 'gzip','accept-language': 'en-US,en;q=0.9','cache-control': 'no-cache','content-length': '411','content-type': 'application/json', 'origin': 'https://leetcode.com','pragma': 'no-cache','sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'same-origin'}
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

        req = requests.post(url, headers=headers, data=json.dumps(body))
        status_code = req.status_code
        user_data = json.loads(req.text)
        return status_code, user_data


    def _get_user_submission_list(self, username):
        """
        Given a username, returns a list of the user's submissions.
        """
        status_code, user_data = self._get_user_data(username)
        if status_code != 200:
            return 0

        return user_data["data"]["recentSubmissionList"]


    def get_user_most_recent(self, username):
        """
        Gets a users most recent submission, returns it as a pretty-formatted string.
        """
        try:
            status_code, user_data = self._get_user_data(username)
            if status_code != 200:
                return "Server error. @Leadership you might want to check on this."
            elif 'errors' in user_data:
                return "That user does not exist. Please try again."

            return self._format_recent_problem(user_data)                   
        except Exception as identifier:
            return "Fail in query for {}".format(username)


    def get_users_str(self):
        """
        Return a string with a list of all the users.
        """
        return str(self.users)


    def add_user(self, username):
        """
        Adds a user to self.users if they have a leetcode account.
        Returns a result message string.
        """
        if username not in self.users:
            status_code, user_data = self._get_user_data(username)
            if status_code != 200 or 'errors' in user_data:
                return "Unrecognized user. Please try again."

            self.users.add(username)
            self.save_users()
            return "Added {} to the list!".format(username)
        else:
            return "{} is already on the list!".format(username)

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

    def users_recents(self):
        """
        Returns a string of the most recent problem each user solved.
        """
        r_str = ""
        if len(self.users) > 5:
            return "Too many users to print in one message. Please user the  `!get <username>`  command instead."

        for user in self.users:
            problem = self.get_user_most_recent(user)
            r_str += "\n{}'s most recent submission:\n".format(user)
            r_str += problem
            r_str += "\n"

        return r_str


    def weekly_recap(self):
        """
        Gets a count of how many problem's they've solved in the last week for each user.
        """
        data = []
        range_start = time.time() - 604800  # Gets time from epoch 1 week ago
        for user in self.users:
            r = self._get_users_week(user, range_start)
            data.append((r, user))

        data.sort(reverse=True)

        r_str = "Weekly Recap.\n`"
        for count, username in data:
            r_str += "{}:  \t{} problems solved\t\t\n".format(username, count)

        return r_str + '`'

    def _get_users_week(self, username, range_start):
        """
        Given a user, this gets the number of problems a user solved in the last week.
        Params: username of the user, time in unix epoch from one week ago.
        Returns: number of problems the user solved as an int.
        This is a helper method for weekly_recap()
        """
        r = 0
        submission_list = self._get_user_submission_list(username)
        for submission in submission_list:
            timestamp = int(submission["timestamp"])
            time_delta = timestamp - range_start
            if time_delta >= 0:
                r += 1
            else:
                break

        return r


    def _format_recent_problem(self, user_data):
        """
        Given user_data JSON object from LeetCode, return a formatted string of the user's most recent submission.
        """
        problem = user_data["data"]["recentSubmissionList"][0]
        
        timestamp = int(problem["timestamp"])
        readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

        r_str = """
Problem Title:  {}
Submit Time:   {}
Result:              {}     
Language:        {}
""".format(problem["title"], readable_time, problem["statusDisplay"], problem["lang"])

        return r_str


