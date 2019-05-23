import discord
import config
from discord.ext import commands
from discord import Status

###########################
# Setup Bot Configuration #
###########################

# Create a config if it does not yet exist
config.initialize()

TOKEN = config.get_token()
COMMAND_PREFIX = config.get_command_prefix()

bot = commands.Bot(command_prefix=COMMAND_PREFIX)

# Define bot extensions
extensions = ['cogs.chat', 'cogs.timein', 'cogs.help']


# Update members in configuration
async def update_members():
    for user in bot.get_all_members():
        if not config.user_in_config(user) and user.id != bot.user.id:
            config.add_user(user)

###############
# Bot Events #
###############

# Log in
@bot.event
async def on_ready():
    await update_members()
    print('Logged in as: ' + bot.user.name + ' (' + str(bot.user.id) + ')')
    print('------')

# Command error handling
@bot.event
async def on_command_error(ctx, error):
    await ctx.message.delete()
    await ctx.message.author.send("[Error] Invalid command or syntax. Use '.help' for assistance.")


# Refresh config when new person joins
@bot.event
async def on_member_join(member):
    await update_members()

# Load available cogs and extensions
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as error:
            print('{} cannot be loaded. [{}]'.format(extension,error))
    bot.run(TOKEN)