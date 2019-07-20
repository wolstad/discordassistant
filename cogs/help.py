import discord
from discord.ext import commands

commands_list = {}

commands_list['ti_search_timezones'] = ['Find the code for your timezone.',
                                        '<keywords>',
                                        'pacific']
commands_list['timein'] = ['Create a time in.',
                           '<description> ...',
                           'beta testing']
commands_list['timeout'] = ['Time out for a current time in.',
                            '',
                            '']
commands_list['switch'] = ['Switch your current task. (Must currently be timed in)',
                           '<description> ...',
                           'beta testing']
commands_list['ti_manual'] = ['Create a time in for a specified time and date.',
                              '<user> <date> <in time> <out time> <description> ...',
                              '@User#1234 1-29-2019 4:00 13:00 beta testing']
commands_list['ti_update'] = ['Edit an existing time in.',
                              '<user> <time in identifier> <in time> <out time> <description> ...',
                              '@User#1234 QMiDS 3:00 13:00 beta testing']
commands_list['ti_delete'] = ['Delete an existing time in.',
                              '<user> <time in identifier>',
                              '@User#1234 QMiDS']
commands_list['ti_cont'] = ['Time in again for your most recent task.',
                            '',
                            '']
commands_list['ti_set_timezone'] = ['Set your timezone. Use \'.ti_search_timezones\' to get the timezone ID.',
                                    '<user> <timezone id>',
                                    '.ti_set_timezone @User#1234 585']
commands_list['ti_set_emote'] = ['Set your time in emoji.',
                                 '<user> <emoji>',
                                 '@User#1234 tongue']
commands_list['ti_set_channel'] = ['Update the server time in channel.',
                                   '',
                                   '']
commands_list['ti_set_pay'] = ['Set the pay rate of a specified user',
                               '<user> <amount>',
                               '@User#1234 12']
commands_list['ti_set_payday'] = ['Specify a day of the month as the pay day.',
                                  '<day>',
                                  '15']
commands_list['ti_gethours'] = ['Get the hours of a user for the current pay period.',
                                '<user>',
                                '@User#1234']
commands_list['ti_report'] = ['Generate an Excel spreadsheet for the current pay period.',
                              '',
                              '']
commands_list['ti_exclude'] = ['Exclude a user for time in calculations.',
                               '<user>',
                               '@User#1234']
commands_list['ti_message_limit'] = ['Set the number of messages time in functions iterate through.',
                                     '<num>',
                                     '500']
commands_list['change_status'] = ['Change the status message of the bot.',
                                  '<status> ...',
                                  'hardly working']

class Help(commands.Cog, name='Help'):

    @commands.command()
    async def help(self, ctx, *command):
        # List all commands
        if len(command) <= 0:
            output = '```\n'
            output += 'Use \'.help <command>\' for specific usage for a particular command.\n----------\n'
            for key in commands_list:
                curr_line = '.' + key + '   ' + commands_list[key][0] + '\n'
                output += curr_line
            output += '\n```'
            await ctx.message.author.send(output)
            await ctx.message.delete()
        # Print out specifics for a single command
        elif len(command) == 1:
            for key in commands_list:
                if ''.join(command) in key or key in ''.join(command):
                    output = '```\n'
                    curr_line = '.' + key + '   ' + commands_list[key][0] + '\n'
                    curr_line += '\n Usage: .' + key + ' ' + commands_list[key][1]
                    curr_line += '\n Ex: .' + key + ' ' + commands_list[key][2]
                    output += curr_line
                    output += '\n```'
                    await ctx.message.author.send(output)
            await ctx.message.delete()
        else:
            ctx.message.author.send('[Error] Help page for specified command not found.')
            await ctx.message.delete()


def setup(bot):
    # Remove existing help command
    bot.remove_command("help")
    bot.add_cog(Help(bot))