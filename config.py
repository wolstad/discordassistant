import json
import os
import sys

############################
# Read and Write Functions #
############################


# Create config file if it does not exist
def initialize():
    exists = os.path.isfile('config.json')
    if not exists:
        config = {}
        config['bot'] = []
        config['bot'].append({
            'token': '',
            'command_prefix': '.',
            'pay_day': None,
            'timein_exclusions': [],
            'timein_channel': None
        })

        config['users'] = []

        update(config)


# Update config file
def update(config):
    with open("config.json", "w") as json_file:
        json.dump(config, json_file, indent=4, sort_keys=True)


# Add a user to the config file
def add_user(user):
    config = get_config()
    # User is already in the config
    if user_in_config(user):
        return
    else:
        config['users'].append({
            'name': user.id,
            'emote': 'yum',
            'time_zone': None,
            'pay_rate': None,
            'used_identifiers': []
        })
        update(config)


def update_user(user, param, value):
    config =  get_config()
    for p in config['users']:
        if p['name'] == user.id:
            config['users'][config['users'].index(p)][param] = value
            update(config)

##################
# Set Functions #
##################


def set_timein_channel(channel):
    config = get_config()
    config['bot'][0]['timein_channel'] = channel.id
    update(config)


def set_pay_day(day):
    config = get_config()
    config['bot'][0]['pay_day'] = day
    update(config)


def add_indentifier(user, indentifier):
    indentifiers = get_user_val(user, 'used_identifiers')
    indentifiers.append(indentifier)
    update_user(user, 'used_identifiers', indentifiers)


def add_ti_exclusion(user):
    config = get_config()
    config['bot'][0]['timein_exclusions'].append(user.id)
    update(config)


def del_ti_exclusion(user):
    config = get_config()
    config['bot'][0]['timein_exclusions'].remove(user.id)
    update(config)

####################
# Access Functions #
####################


def get_config():
    with open('config.json') as json_file:
        config = json.load(json_file)
        return config


def get_token():
    config = get_config()
    token = config['bot'][0]['token']
    # Exit bot if token is not defined
    if len(token)<=0:
        print("[Error] Please define a token in config.json")
        sys.exit()
    else:
        return token


def get_user_val(user, param):
    config = get_config()
    for p in config['users']:
        if p['name'] == user.id:
            return p[param]


def get_command_prefix():
    config = get_config()
    return config['bot'][0]['command_prefix']


def get_timein_channel():
    config = get_config()
    return config['bot'][0]['timein_channel']


def get_timein_exclusions():
    config = get_config()
    return config['bot'][0]['timein_exclusions']

def get_payday():
    config = get_config()
    return config['bot'][0]['pay_day']


####################
# Helper Functions #
####################


def user_in_config(user):
    config = get_config()
    for p in config['users']:
        if p['name'] == user.id:
            return True
    return False