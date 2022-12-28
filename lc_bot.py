import discord
from discord.ext import tasks
import lc_data_access

lc_access = lc_data_access.LcAccess("user_store.txt")


class LeetCodeBot(discord.Client):

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):

        # Make sure the message is in the bot-testing channel
        if message.channel.id != 791542249031860245:
            return

        # Don't respond to ourselves.
        if message.author == self.user:
            return

        if message.content[0] == '!':
            message_text = message.content.split()
            if len(message_text) > 2:
                await message.channel.send('Invalid command, please try again.')
                return

            # !get <username>
            if message_text[0] == "!get":
                username = message_text[1]

                if ' ' in username:
                    await message.channel.send('Your entry contains spaces. Instead, enter a valid leetcode username.')
                else:
                    await message.channel.send('Getting {}\'s most recent LeetCode submission:'.format(username))
                    await message.channel.send(lc_access.get_user_most_recent(username))

            # !users
            elif message_text[0] == "!users":
                await message.channel.send(lc_access.get_users_str())

            # !add <username>
            elif message_text[0] == "!add":
                await message.channel.send(lc_access.add_user(message_text[1]))

            # !remove <username>
            elif message_text[0] == "!remove":
                result = lc_access.remove_user(message_text[1])
                if result:
                    await message.channel.send("User removed.")
                else:
                    await message.channel.send(
                        "An error occurred. Please ensure {} is on the list.".format(message_text[1]))

            # !recents
            elif message_text[0] == "!recents":
                await message.channel.send(lc_access.recent_submissions_for_each_user())

            # !recap
            elif message_text[0] == "!recap":
                # TODO: insert wait message for (0.3 * # of users) seconds
                await message.channel.send(lc_access.weekly_recap_leaderboard())

            # !save
            elif message_text[0] == "!save":
                await message.channel.send(lc_access.save_users())

            # !help
            elif message_text[0] == "!help":
                help_str = ("Available Commands:\n"
                            "\t!recap\n"
                            "\t!get <username>\n"
                            "\t!users\n"
                            "\t!add <username>\n"
                            "\t!remove <username>\n")
                await message.channel.send(help_str)

            else:
                # Error message here since no command was run
                await message.channel.send(
                    "That command is unrecognizable. Type  `!help`  for a list of available commands.")

            return

        if message.content == '$abort mission':
            await message.channel.send('Mission Aborted, LC_Tracker will be down until booted up again.')
            await self.close()
            return

        if message.content == 'ping':
            await message.channel.send('pong')
            return


# Get the discord bot token.
with open("token.txt", "r") as infile:
    token = infile.readline().strip()

# bot_channel = 791542249031860245;    # <-- This channel is the hidden bot-testing channel
bot_channel = 799064821517385750;  # <-- This channel is the main leetcode-bot channel


# Send a weekly recap every week
@tasks.loop(hours=168)
async def weekly_message():
    message_channel = client.get_channel(bot_channel)
    print(f"Sending weekly message to: {message_channel}")
    await message_channel.send(lc_access.weekly_recap_leaderboard())
    await message_channel.send("Nice work everyone! Use the `!help` command for more commands.")


@weekly_message.before_loop
async def before():
    await client.wait_until_ready()


client = LeetCodeBot()
weekly_message.start()
client.run(token)
