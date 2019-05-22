import discord
from discord.ext import commands


class Chat(commands.Cog, name='Chat'):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Chat(bot))