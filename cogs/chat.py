import discord
from discord.ext import commands


class Chat(commands.Cog, name='Chat'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def change_status(self, *status):
        status = ' '.join(status)
        await self.bot.change_presence(activity=discord.Game(name=status, type=0))


def setup(bot):
    bot.add_cog(Chat(bot))