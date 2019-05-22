import discord
import config
import datetime
import pytz
import os
import random
import string
import re
import xlsxwriter
from discord.ext import commands


class TimeIn(commands.Cog, name='Time In'):

    #############
    # Constants #
    #############

    MESSAGE_LIMIT = 500;
    INVALID_CHARACTERS = ['{', '}', '[', ']', '*', '?']

    def __init__(self, bot):
        self.bot = bot

    #####################
    # Time in Functions #
    #####################

    def daterange(self, d1, d2):
        return (d1 + datetime.timedelta(days=i) for i in range((d2 - d1).days + 1))

    async def get_timein_hours(self, message):
        time_array = await self.strip_time(message)
        time_sum = 0
        for i in range(0, len(time_array), 2):
            time1 = datetime.datetime.strptime(time_array[i], '%H:%M')
            time2 = datetime.datetime.strptime(time_array[i + 1], '%H:%M')
            diff = time2 - time1
            time_sum += diff.seconds / 3600
        return time_sum

    # Return a dictionary of all time ins for a specified range
    async def timein_dic(self, start_date, end_date):
        output = {}
        timein_users = await self.timein_users()
        # Add all users to dic
        for member in timein_users:
            output[member.display_name] = []

        # Check all messages for a specific date
        count = 0
        for day in self.daterange(start_date, end_date):
            count += 1
            async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
                curr_message = message.content
                # If message contains date
                if (day.strftime("%B %d, %Y") in curr_message) and message.author.bot:
                    # Check all users for each
                    for user in timein_users:
                        # Add total hours to specified user
                        if (user.display_name in curr_message):
                            total = await self.get_timein_hours(message)
                            output[user.display_name].append(total)
            # Add zero hours to user if they have not timed in on this date
            for user in timein_users:
                if len(output[user.display_name]) < count:
                    output[user.display_name].append(0)
            count += 1
        return output

    # Return an array of valid users for time ins
    async def timein_users(self):
        timein_exclude = config.get_timein_exclusions()
        output = []
        for member in self.bot.get_all_members():
            if member.id not in timein_exclude and member.id != self.bot.user.id:
                output.append(member)
        return output

    # Check if any invalid characters are in a message
    async def message_valid(self, message):
        if any(item in message for item in self.INVALID_CHARACTERS):
            return False
        return True

    # Make sure all users have pay rate
    async def check_pay(self):
        for member in self.bot.get_all_members():
            if member.id != self.bot.user.id:
                if (config.get_user_val(member, 'pay_rate') is None) and (member.id not in config.get_timein_exclusions()):
                    return False
        return True

    # Get converted time of user
    async def get_time(self, member, time):
        convert_zone = pytz.timezone(config.get_user_val(member, 'time_zone'))
        return pytz.utc.localize(time, is_dst=None).astimezone(convert_zone)

    # Generate random string
    def random_string(self, length):
        return ''.join(random.choice(string.ascii_letters) for m in range(length))

    # Get a random time in identifier
    async def get_identifier(self, member):
        key = self.random_string(5)
        if key in config.get_user_val(member, 'used_identifiers'):
            await self.get_identifier(member)
        else:
            config.add_indentifier(member, key)
            return key

    # Check if a user is currently timed in
    async def is_timed_in(self, member):
        async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
            curr_message = message.content
            if (member.display_name in curr_message) and message.author.bot:
                if '???}' in curr_message:
                    return True
        return False

    # Return all time ranges from a time in message. Will return an array. Odd indexes are time ins. Even are time outs
    async def strip_time(self, message):
        init_split = message.content.split('{')
        time_range = init_split[1].split('}')[0]
        return time_range.split(' - ')

    # Check if a message is valid to be summed for hours calulation
    async def valid_calc(self, member, message, current_date):
        if member.display_name in message.content:
            date_raw = re.sub('[*]', '', message.content.splitlines()[3])
            check_date = datetime.datetime.strptime(date_raw, "%B %d, %Y")
            current_month = current_date.month

            pay_day = config.get_payday()
            if (check_date.month == (current_month - 1)) and (check_date.day >= pay_day):
                return True
            elif (check_date.month == current_month) and (check_date.day < pay_day):
                return True
        return False

    # Return the message of most recent time in if it is on the same day
    async def check_timein(self, member, date):
        async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
            curr_message = message.content
            if member.display_name in curr_message and message.author.bot:
                if date.strftime("%B %d, %Y") in curr_message:
                    return message
        return None

    # Get the date from a time in
    async def get_timein_date(self, member):
        async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
            curr_message = message.content
            if member.display_name in curr_message and message.author.bot:
                init_split = curr_message.split('*')
                date = init_split[1].split('*')
                return date[0]

    # Get the last time in task
    async def get_timein_task(self, member):
        async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
            curr_message = message.content
            if member.display_name in curr_message and message.author.bot:
                line_split = curr_message.split('\n')
                line_split_len = len(line_split)
                id_split = line_split[line_split_len - 1].split('] ')
                return id_split[1]

    # Edit the message to time out a user
    async def timeout_message(self, member, time):
        async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
            curr_message = message.content
            if member.display_name in curr_message and message.author.bot:
                curr_message = curr_message.replace('???', time)
                await message.edit(content=curr_message)

    # Time in a specified user
    async def time_in(self, member, task, time):
        emote = config.get_user_val(member, 'emote')
        emote_id = await self.get_emote_id(emote)
        emote_display = '<:' + emote + ':' + str(emote_id) + '>'
        if emote_id is None:
            emote_display = ':' + emote + ':'
        last_timein = await self.check_timein(member, time)
        # New time in for the day
        if last_timein is None:
            ti_message = '----------------------- \n'
            ti_message += (emote_display + ' ' + member.display_name + ' ' + emote_display)
            ti_message += '\n----------------------- \n*' + time.strftime("%B %d, %Y") + '*'
            identifier = await self.get_identifier(member)
            task_message = '\n [' + identifier + '] ' + task + ' {' + time.strftime("%H:%M") + ' - ???}'
            await self.bot.get_channel(config.get_timein_channel()).send(ti_message + task_message)
        # Add on to an existing time in
        else:
            identifier = await self.get_identifier(member)
            updated_timein = last_timein.content + '\n [' + identifier + '] ' + task + ' {' + time.strftime(
                "%H:%M") + ' - ???}'
            await last_timein.edit(content=updated_timein)

    # Time out a specified user
    async def time_out(self, member, time):
        # If user is timed in
        if await self.is_timed_in(member):
            # It is the same day
            if await self.get_timein_date(member) == time.strftime("%B %d, %Y"):
                await self.timeout_message(member, time.strftime("%H:%M"))
            # It is a new day
            else:
                await self.timeout_message(member, time.strftime("24:00"))
                task = await self.get_timein_task(member)
                new_day_time = datetime.datetime(time.year, time.month, time.day, 00, 00)
                await self.time_in(member, task, new_day_time)
                await self.time_out(member, time)
        else:
            await member.send('[Error] You are already timed out.')

    # Notify all users on the server
    async def notify_all(self, message):
        for member in self.bot.get_all_members():
            member.send('[Announcement] ' + message)

    # Check if time range is valid
    async def valid_range(self, timein, timeout):
        if timein < timeout:
            return True
        return False

    async def timeout_all(self, time_raw):
        for member in self.bot.get_all_members():
            if member.id not in config.get_timein_exclusions():
                if await self.is_timed_in(member):
                    time = await self.get_time(member, time_raw)
                    await self.time_out(member, time)
                    await member.send('A time in report is being generated. You have been timed out.')

    async def timein_report(self, time):
        pay_day = config.get_payday()

        curr_month = time.month
        curr_day = time.day
        curr_year = time.year

        start_month = 0
        start_year = 0
        start_day = pay_day

        end_month = 0
        end_year = 0
        end_day = pay_day - 1

        timein_users = await self.timein_users()

        # Calculate start/end months and years
        if curr_day >= pay_day:
            start_month = curr_month
            start_year = curr_year

            end_month = curr_month + 1
            end_year = curr_year
            # Account for December
            if curr_month == 12:
                end_year += 1
        else:
            start_month = curr_month - 1
            start_year = curr_year

            end_month = curr_month
            end_year = curr_year

            # Account for January
            if curr_month == 1:
                start_year -= 1

        # Compute start and end date
        start_date = datetime.datetime(start_year, start_month, start_day)
        end_date = datetime.datetime(end_year, end_month, end_day)

        timeins = await self.timein_dic(start_date, end_date)

        # Write file name
        file_name = start_date.strftime("%d-%b-%Y") + '_' + end_date.strftime("%d-%b-%Y")
        file = 'reports/' + file_name + '.xlsx'

        # Create workbook
        workbook = xlsxwriter.Workbook(file)
        worksheet = workbook.add_worksheet()

        # Header format
        header = workbook.add_format({'bold': True, 'border': 2, 'align': 'center'})
        cell = workbook.add_format({'border': 1, 'align': 'center'})

        # Write header
        worksheet.write(0, 0, "DATE", header)
        for i in range(0, len(timein_users)):
            worksheet.write(0, i + 1, timein_users[i].display_name.upper(), header)

        # Write dates in column
        day_row = 1
        for day in self.daterange(start_date, end_date):
            worksheet.write(day_row, 0, day.strftime("%d %b, %Y"), cell)
            day_row += 1

        user_count = 1
        # Add timein hours
        for user in timein_users:
            user_timeins = timeins[user.display_name]
            for i in range(0, len(user_timeins) - 1):
                worksheet.write(i + 1, user_count, str(user_timeins[i])[0:8], cell)
            # Write total hours
            total_time = 0
            for time in user_timeins:
                total_time += time
            worksheet.write(len(user_timeins), user_count, str(total_time)[0:8], header)

            pay_rate = config.get_user_val(user, 'pay_rate')
            worksheet.write(day_row + 1, user_count, pay_rate, header)
            worksheet.write(day_row + 2, user_count, str(pay_rate * total_time)[0:8], header)
            user_count += 1

        # Write footer
        worksheet.write(day_row, 0, 'TOTAL', header)
        worksheet.write(day_row + 1, 0, 'PAY RATE', header)
        worksheet.write(day_row + 2, 0, 'INCOME', header)

        # Set width of first column
        worksheet.set_column(0, 0, 15)

        workbook.close()
        return file

    async def get_emote_id(self, name):
        for emote in self.bot.emojis:
            if emote.name == name:
                return emote.id

    #################
    # User Commands #
    #################

    # Search for a specific timezone
    @commands.command()
    async def ti_search_timezones(self, ctx, *args):
        member = ctx.message.author
        if config.get_timein_channel() is not None and ctx.message.channel.id == config.get_timein_channel():
            zones = pytz.all_timezones

            output = ''
            if len(args) <= 0:
                await member.send('[Error] Please insert keywords.')
                await ctx.message.delete()
            else:
                for zone in zones:
                    if all(arg.lower() in zone.lower() for arg in args):
                        if len(output) > 0:
                            output += ', '
                        output += '[' + str(zones.index(zone)) + '] ' + zone
                await member.send(output)
                await ctx.message.delete()
        else:
            await member.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()

    # Basic time in function
    @commands.command()
    async def timein(self, ctx, *description):
        member = ctx.message.author
        task = ' '.join(description)
        # if there is no description
        if len(description) <= 0:
            await member.send('[Error] Please include a timein description.')
            await ctx.message.delete()
        # If time in channel has not been set
        elif config.get_timein_channel() is None or ctx.message.channel.id != config.get_timein_channel():
            await member.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()
        # If member has not defined a timezone
        elif config.get_user_val(member, 'time_zone') is None:
            await member.send('[Error] Please define your timezone: .set_timezone <zone_num>\n'
                              'Example: .set_timezone 1 \n \n'
                              'To find your timezone: .search_timezone <args>\n'
                              'Example: .search_timezone Pacific US')
            await ctx.message.delete()
        # If member is already timed in
        elif await self.is_timed_in(member):
            await member.send('[Error] You already have an'
                              ' active time in.')
            await ctx.message.delete()
        # Member has invalid characters
        elif not await self.message_valid(task):
            await member.send('[Error] Invalid characters in time in description.')
            await ctx.message.delete()
        # Member can time in
        else:
            time_raw = ctx.message.created_at
            time = await self.get_time(member, time_raw)
            await self.time_in(member, task, time)
            await ctx.message.delete()

    # Basic timeout function
    @commands.command()
    async def timeout(self, ctx):
        member = ctx.message.author
        # If time in channel has not been set
        if config.get_timein_channel() is None or ctx.message.channel.id != config.get_timein_channel():
            await member.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()
        else:
            time_raw = ctx.message.created_at
            time = await self.get_time(member, time_raw)
            await self.time_out(member, time)
            await ctx.message.delete()

    # Manually input timein
    @commands.command()
    async def ti_manual(self, ctx, user, in_date, in_time, out_time, *description):
        member = ctx.message.mentions[0]
        sender = ctx.message.author
        if config.get_timein_channel() is not None and ctx.message.channel.id == config.get_timein_channel():
            date = datetime.datetime.strptime(in_date, '%m-%d-%Y')
            in_time_raw = datetime.datetime.strptime(in_time, '%H:%M')
            out_time_raw = datetime.datetime.strptime(out_time, '%H:%M')
            task = ' '.join(description)

            # if there is no description
            if len(description) <= 0:
                await sender.send('[Error] Please include a timein description.')
                await ctx.message.delete()
            # Member has invalid characters
            elif not await self.message_valid(task):
                await sender.send('[Error] Invalid characters in time in description.')
                await ctx.message.delete()
            # Check if time range is valid
            elif not await self.valid_range(in_time_raw, out_time_raw):
                await sender.send('[Error] Time in time must be before time out time.')
                await ctx.message.delete()
            else:
                # See if time in already exists
                async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
                    curr_message = message.content
                    # User has already timed in on this date
                    if (member.display_name in curr_message) and (
                            date.strftime("%B %d, %Y") in curr_message) and message.author.bot:
                        identifier = await self.get_identifier(member)
                        curr_message += '\n [' + identifier + '] ' + task + ' {' + in_time_raw.strftime(
                            "%H:%M") + ' - ' + out_time_raw.strftime("%H:%M") + '}'
                        await message.edit(content=curr_message)
                        await ctx.message.delete()
                        return
                # User has not timed in on this date
                emote = config.get_user_val(member, 'emote')
                emote_id = await self.get_emote_id(emote)
                emote_display = '<:' + emote + ':' + str(emote_id) + '>'
                if emote_id is None:
                    emote_display = ':' + emote + ':'
                ti_message = '----------------------- \n'
                ti_message += (emote_display + ' ' + member.display_name + ' ' + emote_display)
                ti_message += '\n----------------------- \n*' + date.strftime("%B %d, %Y") + '*'
                identifier = await self.get_identifier(member)
                task_message = '\n [' + identifier + '] ' + task + ' {' + in_time_raw.strftime(
                    "%H:%M") + ' - ' + out_time_raw.strftime("%H:%M") + '}'
                await self.bot.get_channel(config.get_timein_channel()).send(ti_message + task_message)
                await ctx.message.delete()
        else:
            await sender.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()

    # Update an existing time in
    @commands.command()
    async def ti_update(self, ctx, user, id, in_time, out_time, *description):
        member = ctx.message.mentions[0]
        sender = ctx.message.author

        in_time_raw = datetime.datetime.strptime(in_time, '%H:%M')
        out_time_raw = datetime.datetime.strptime(out_time, '%H:%M')
        task = ' '.join(description)

        # if there is no description
        if len(description) <= 0:
            await sender.send('[Error] Please include a timein description.')
            await ctx.message.delete()
        # If time in channel has not been set
        elif config.get_timein_channel() is None or ctx.message.channel.id != config.get_timein_channel():
            await sender.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()
        # Member has invalid characters
        elif not await self.message_valid(task):
            await sender.send('[Error] Invalid characters in time in description.')
            await ctx.message.delete()
        # Check if time range is valid
        elif not await self.valid_range(in_time_raw, out_time_raw):
            await sender.send('[Error] Time in time must be before time out time.')
            await ctx.message.delete()
        else:
            async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
                curr_message = message.content
                if (member.display_name in curr_message) and (id in curr_message) and message.author.bot:
                    lines = message.content.splitlines()
                    for line in lines:
                        if id in line:
                            appended = curr_message.replace(line, ' [' + id + '] ' + task + ' {' + in_time_raw.strftime("%H:%M") + ' - ' + out_time_raw.strftime("%H:%M") + '}')
                            await message.edit(content=appended)
                            await ctx.message.delete()
                            return
            await sender.send('[Error] Cannot find time in ID.')
            await ctx.message.delete()

    # Delete a specified time in
    @commands.command()
    async def ti_delete(self, ctx, user, id):
        member = ctx.message.mentions[0]
        sender = ctx.message.author

        # If time in channel has not been set
        if config.get_timein_channel() is None or ctx.message.channel.id != config.get_timein_channel():
            await sender.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()
        else:
            async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
                curr_message = message.content
                if (member.display_name in curr_message) and (id in curr_message) and message.author.bot:
                    lines = message.content.splitlines()
                    # Delete whole message
                    if len(lines) <= 5:
                        await message.delete()
                        await ctx.message.delete()
                        return
                    else:
                        for line in lines:
                            if id in line:
                                new_message = curr_message.replace(line, "")
                                new_message_clean = os.linesep.join([s for s in new_message.splitlines() if s])
                                await message.edit(content=new_message_clean)
                                await ctx.message.delete()
                                return
            await sender.send('[Error] Cannot find time in ID.')

    # Set timezone of user
    @commands.command()
    async def ti_set_timezone(self, ctx, zone_num):
        member = ctx.message.author
        if config.get_timein_channel() is not None and ctx.message.channel.id == config.get_timein_channel():
            zones = pytz.all_timezones

            # Check if zone is int and is valid
            if zone_num.isdigit():
                zone_num = int(zone_num)
                if zone_num >= 0 and zone_num <= len(zones):
                    config.update_user(member, 'time_zone', zones[zone_num])
                    await member.send('[Success] Updated time zone.')
                    await ctx.message.delete()
                else:
                    await member.send('[Error] Not a valid zone number.')
                    await ctx.message.delete()
            else:
                await member.send('[Error] Please enter a zone number.')
                await ctx.message.delete()
        else:
            await member.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()

    # Set the emote for time in messages
    @commands.command()
    async def ti_set_emote(self, ctx, emote):
        member = ctx.message.author
        if config.get_timein_channel() is not None and ctx.message.channel.id == config.get_timein_channel():
            # Incorrect syntax
            if ':' in emote:
                await member.send('[Error] Please do not include colons (:) with this command.')
            else:
                config.update_user(member, 'emote', emote)
                await member.send('[Success] Time in emote updated.')
            await ctx.message.delete()
        else:
            await member.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()

    ##################
    # Admin Commands #
    ##################

    # Define timein channel
    @commands.command()
    async def ti_set_channel(self, ctx):
        member = ctx.message.author
        channel = ctx.message.channel
        config.set_timein_channel(channel)
        await member.send('[Success] Updated time in channel.')
        await ctx.message.delete()

    # Set pay for a specified user
    @commands.command()
    async def ti_set_pay(self, ctx, user, amount):
        sender = ctx.message.author
        if config.get_timein_channel() is not None and ctx.message.channel.id == config.get_timein_channel():
            member = ctx.message.mentions[0]
            pay = float(amount)
            config.update_user(member, 'pay_rate', pay)
            await sender.send('[Success] Updated pay of ' + member.display_name + ' to: $' + str(pay) + ".")
            await ctx.message.delete()
        else:
            await sender.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()

    # Set the pay date
    @commands.command()
    async def ti_set_payday(self, ctx, day):
        member = ctx.message.author
        if config.get_timein_channel() is not None and ctx.message.channel.id == config.get_timein_channel():
            if day.isdigit():
                if 1 <= int(day) <= 32:
                    config.set_pay_day(int(day))
                    await member.send('[Success] Updated pay date.')
                else:
                    await member.send('[Error] Please enter a valid day of the month.')
            else:
                await member.send('[Error] Please enter a numeric day of the month.')
            await ctx.message.delete()
        else:
            await member.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()

# Get hours for a specified user for a given pay period
    @commands.command()
    async def ti_gethours(self, ctx, user):
        member = ctx.message.mentions[0]
        sender = ctx.message.author
        if config.get_timein_channel() is not None and ctx.message.channel.id == config.get_timein_channel():
            if (config.get_payday() is None) or (config.get_user_val(member, 'pay_rate') is None):
                await sender.send('[Error] Please define a pay day and a pay rate for the user.')
            else:
                time_raw = ctx.message.created_at
                time = await self.get_time(member, time_raw)
                time_sum = 0
                async for message in self.bot.get_channel(config.get_timein_channel()).history(limit=self.MESSAGE_LIMIT):
                    if await self.valid_calc(member, message, time):
                        time_array = await self.strip_time(message)
                        for i in range(0, len(time_array), 2):
                            time1 = datetime.datetime.strptime(time_array[i], '%H:%M')
                            time2 = datetime.datetime.strptime(time_array[i + 1], '%H:%M')
                            diff = time2 - time1
                            time_sum += diff.seconds / 3600

                await sender.send(member.display_name + ' has timed in: ' + str(time_sum) + ' hours and has earned: $' + str(config.get_user_val(member, 'pay_rate') * time_sum) + ' this pay period.')
                await member.send('[Announcement] A time in report is being generated. Please notify an admin if you are currently timed in or your time ins are incorrect.')
            await ctx.message.delete()
        else:
            await sender.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()

    # Generate a time in report for the current pay period
    @commands.command()
    async def ti_report(self, ctx):
        member = ctx.message.author
        if config.get_timein_channel() is not None and ctx.message.channel.id == config.get_timein_channel():
            if not await self.check_pay():
                await member.send("[Error] Not all users have pay rates defined.")
                await ctx.message.delete()
            elif config.get_payday() is None:
                await member.send("[Error] No pay date has been defined.")
                await ctx.message.delete()
            else:
                await self.timeout_all(ctx.message.created_at)
                await ctx.message.delete()
                output_file = await self.timein_report(ctx.message.created_at)
                await member.send(file=discord.File(output_file))
        else:
            await member.send('[Error] Time in commands can only be run in the time in channel.')
            await ctx.message.delete()

    # Exclude a user from time ins
    @commands.command()
    async def ti_exclude(self, ctx, user):
        member = ctx.message.mentions[0]
        sender = ctx.message.author
        if member.id not in config.get_timein_exclusions():
            config.add_ti_exclusion(member)
            await sender.send('[Success] Added ' + member.display_name + ' to timein exclusions.')
            await ctx.message.delete()
        else:
            config.del_ti_exclusion(member)
            await sender.send('[Success] Removed ' + member.display_name + ' to timein exclusions.')
            await ctx.message.delete()

def setup(bot):
    bot.add_cog(TimeIn(bot))