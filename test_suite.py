import lc_data_access
import time

lc_access = lc_data_access.LC_Access()


# TODO:
# > Deal with the async aspect if there are too many calls.
# > Cleanup this file for testing.
# > link to the problem on the !get command.
# > don't count duplicates.
# > update recap command to say something if there aren't any users.


start_time = time.time()

# Get a user
# print(lc_access.get_user_most_recent('testuser'))

# print(lc_access.get_users_str())
# print()

# # Users recents:
# print("Testing User's Recents:")
# print(lc_access.users_recents())
# print()

# # Remove a user
# print(lc_access.get_users_str())
# print(lc_access.remove_user("testuser"))
# print("testuser removed, here's who's left:")
# print(lc_access.get_users_str())
# print()

# Weekly Recap
print(lc_access.weekly_recap())


end_time = time.time()
print("Took {} seconds.", end_time - start_time)
