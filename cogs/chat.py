import discord
from discord.ext import commands


class Chat(commands.Cog, name='Chat'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def change_status(self, ctx, *args):
        status = ' '.join(args)
        if 0 < len(status) <= 100:
            await self.bot.change_presence(activity=discord.Game(name=status, type=0))
            await ctx.message.delete()
        else:
            await ctx.message.author.send('[Error] Invalid status message.')
            await ctx.message.delete()


def setup(bot):
    bot.add_cog(Chat(bot))
