
## Discord Productivity Bot
This bot is designed to increase the productivity for small teams by handling tasks such as time tracking. This bot gives teams the ability to:

 - Specify a channel for time ins on a discord server.
 - Allow users in different time zones to punch in and out with a simple command.
 - Set a pay rate and pay day for users.
 - Generate a report for the given time in period and calculate the total hours logged.

Installation is quick and easy. User specifics are stored in a JSON configuration file, but time ins are recorded and calculated using discord Discord messages.

## Installation

 1. Ensure the latest version of Discord.py is installed on the server, and install the requirements.txt.
 2. Run bot.py. The first time the bot is run, it will terminate and ask you to input the token in the config.json.
 3. Set a time in channel using `.ti_set_channel`
 4. Set the pay date using `.ti_set_payday <date>`
 5. Set the pay rate for each user `.ti_set_pay <user> <rate>` or exclude them from time in calculations using `.ti_exclude <user>`
 6. Start using time ins!

## Commands
Use '.help <command>' for specific usage for a particular command. 
- **Find the code for your timezone.**
`.ti_search_timezones` 
Usage: `.ti_search_timezones <keywords>` 
Ex: `.ti_search_timezones pacific`
- **Create a time in.**
`.timein`
Usage: `.timein <description> ...`
Ex: `.timein beta testing`
- **Time out for a current time in.**
`.timeout`
Usage: `.timeout`
Ex: `timeout`
- **Create a time in for a specified time and date.**
`.ti_manual`
Usage: `.ti_manual <user> <date> <in time> <out time> <description> ...`
Ex: `.ti_manual @User#1234 1-29-2019 4:00 13:00 beta testing`
- **Edit an existing time in.**
`.ti_manual`
Usage: `.ti_update <user> <time in identifier> <in time> <out time> <description> ...`
Ex: `.ti_update @User#1234 QMiDS 3:00 13:00 beta testing`
- **Delete an existing time in.**
`.ti_delete`
Usage: `.ti_delete <user> <time in identifier>`
Ex: `.ti_delete @User#1234 QMiDS`
- **Set your timezone. Use `.ti_search_timezones` to get the timezone ID.**
Usage: `.ti_set_timezone <timezone id>`
Ex: `.ti_set_timezone 585`
- **Set your time in emoji.**
Usage: `.ti_set_emote <emoji>`
Ex: `.ti_set_emote tongue`
- **Update the server time in channel.**
Usage: `.ti_set_channel`
Ex: `.ti_set_channel`
- **Set the pay rate of a specified user**
Usage: `.ti_set_pay <user> <amount>`
Ex: `.ti_set_pay @User#1234 12`
- **Specify a day of the month as the pay day.**
Usage: `.ti_set_payday <day>`
Ex: `.ti_set_payday 15`
- **Get the hours of a user for the current pay period.**
Usage: `.ti_gethours <user>`
Ex: `.ti_gethours @User#1234`
- **Generate an Excel spreadsheet for the current pay period.**
Usage: `.ti_report`
Ex: `.ti_report`
- **Exclude a user for time in calculations.**
Usage: `.ti_exclude <user>`
Ex: `.ti_exclude @User#1234`
- **Change the status message of the bot.**
Usage: `.change_status <status> ...`
Ex: `.change_status hardly working`

## Note
The time in identifier is a unique 5 character string associated with each time in. Time in identifiers are used when updating and deleting existing time ins.
