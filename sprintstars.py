import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime
import time
import json
import os
import ast
from threading import Lock
import st_state_patch

import sys
sys.path = list(set(['config'] + sys.path))

try:
    from config import sprint
    from config import members
except:
    pass

PAGE_TITLE = 'The Stars of the Sprint'
APP_ICON = ':star:'

OPTION_NOMINATE_STAR = 'Nominate stars'
OPTION_HOST_POLL = 'Host the poll'
OPTION_SETTINGS = 'Settings'

LABEL_PARTICIPATING = 'Participating'
LABEL_NOT_PARTICIPATING = 'Not participating today'

CONFIG_DIR = 'config/'
SPRINT_CONFIG_FILENAME = CONFIG_DIR + 'sprint.py'
MEMBERS_CONFIG_FILENAME = CONFIG_DIR + 'members.py'
TODAY = str(datetime.now().date())

MAX_NOMINATIONS = 3

class Nomination:
    nominator = None
    feedback = None
    is_anonymous = False

    def __init__(self, nominator, feedback=None, is_anonymous=False) -> None:
        self.nominator = nominator
        self.feedback = feedback
        self.is_anonymous = is_anonymous

SPRINT_DEFAULT_VALUES = {
        'name': '',
        'members': {},
        'is_poll_open': False,
        'is_poll_closed': False
    }

sprint_config = {}
members_list = []

def set_sprint_default_values(force=False):
    global sprint_config
    if TODAY not in sprint_config.keys() or force:
        sprint_config[TODAY] = SPRINT_DEFAULT_VALUES

def save_obj_into_file(config_dict, filename):
    with open(filename, 'w') as f:
        f.write(str(config_dict))

def load_obj_from_file(filename, default={}):
    if not os.path.exists(filename):
        save_obj_into_file(default, filename)

    try:
        with open(filename) as f:
            return eval(f.read())
    except Exception as e:
        print(e)
        pass
    return default

def save_sprint_configs_into_file():
    global sprint_config
    save_obj_into_file(sprint_config, SPRINT_CONFIG_FILENAME)
    from config import sprint # to force auto refresh page on file change

def load_sprint_configs_from_file():
    global sprint_config
    sprint_config = load_obj_from_file(SPRINT_CONFIG_FILENAME)
    from config import sprint

def get_sprint_config(key, default=None):
    global sprint_config
    return sprint_config[TODAY][key] if TODAY in sprint_config.keys() and key in sprint_config[TODAY].keys() else default

def set_sprint_config(key, value):
    global sprint_config
    if TODAY in sprint_config.keys() and key in sprint_config[TODAY].keys():
        sprint_config[TODAY][key] = value

def save_members_list_into_file():
    global members_list
    save_obj_into_file(sorted(members_list), MEMBERS_CONFIG_FILENAME)
    from config import members

def load_members_list_from_file():
    global members_list
    members_list = load_obj_from_file(MEMBERS_CONFIG_FILENAME, [])
    from config import members

def get_team_members_default_dict():
    return {m:[] for m in members_list}

def get_star_members_dict(reverse = False):
    return {k: v for k, v in sorted(get_sprint_config('members').items(), key=lambda item: len(item[1]) if not reverse else -len(item[1])) if len(v)}

def is_already_nominated(member_name):
    for member, nomination_list in get_sprint_config('members').items():
        for nomination in nomination_list:
            if nomination['nominator'] == member_name:
                return True
    return False

def already_participated_members_list():
    already_participated = []
    for _, nomination_list in get_sprint_config('members').items():
        for nomination in nomination_list:
            already_participated.append(nomination['nominator'])
    return list(set(already_participated))

def get_total_participants():
    return len(already_participated_members_list())

def get_waiting_for_members_list():
    global members_list
    return list(set(members_list) - set(already_participated_members_list()))

def display_empty_team_members_names_warning():
    st.warning('Please save team members names to get started')

def display_github_source_button():
    st.markdown('<iframe src="https://ghbtns.com/github-btn.html?user=zakariachowdhury&repo=sprintstars&type=star&count=true" frameborder="0" scrolling="0" width="150" height="20" title="GitHub"></iframe>', unsafe_allow_html=True)

def display_nomination_form():
    global members_list
    sprint_name = get_sprint_config('name', '')
    is_poll_open = get_sprint_config('is_poll_open', False)
    is_poll_closed = get_sprint_config('is_poll_closed', False)

    if not is_poll_open or len(sprint_name) == 0:
        st.info('Please wait for the host to open the poll')
    elif is_poll_closed:
        st.info('The poll has been closed')
    else:
        members_dropdown_list = ['']
        feedback = None
        members_dropdown_list.extend(members_list)

        nominator = st.selectbox('Select your name:', members_dropdown_list)
        if nominator:
            if is_already_nominated(nominator):
                return True
            else:
                members_dropdown_list.remove(nominator)
                star_members = st.multiselect(f'Nominate stars for this sprint (max {MAX_NOMINATIONS}):', members_dropdown_list)

                if len(star_members) > 0:
                    feedbacks = []
                    for star_member in star_members:
                        feedbacks.append(st.text_area('Reasons for nominating ' + star_member + ' (optional):'))
                    is_anonymous = st.checkbox('Nominate anonymously')

                    if len(star_members) > MAX_NOMINATIONS:
                        st.warning(f'You can nominate up to {MAX_NOMINATIONS} stars.')
                    elif st.button('Submit') and not is_already_nominated(nominator):
                        team_nominations_dict = get_sprint_config('members')
                        for i, star_member in enumerate(star_members):
                            team_nominations_dict[star_member].append(Nomination(nominator, feedbacks[i], is_anonymous).__dict__)
                        set_sprint_config('members', team_nominations_dict)
                        save_sprint_configs_into_file()
                        return True
    return False

def display_result(reveal_result = False):
    fig, ax = plt.subplots()
    star_members_dict = get_star_members_dict()
    start_list = list(star_members_dict.keys())

    if len(start_list) >= 2:
        if not reveal_result:
            start_list = ['Star ' + str(len(start_list) - i) for i, _ in enumerate(start_list)]

        votes = [len(v) for _, v in star_members_dict.items()]
        ax.barh(start_list, votes, color='lightcoral' if reveal_result else 'teal')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel('Total votes')
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(color='#eeeeee')
        st.pyplot(fig)

    if reveal_result:
        i = 1
        top_votes = 0
        star_members_dict = get_star_members_dict(True)
        if len(star_members_dict.items()):
            for name, nominations_list in iter(star_members_dict.items()):
                if i == 1:
                    top_votes = len(nominations_list)

                if len(nominations_list):
                    st.markdown(f'**{i}. {name}** *- {len(nominations_list)} {"votes" if len(nominations_list) > 1 else "vote"}* {":star:" if len(nominations_list) == top_votes else ""}')
                    for nomination in nominations_list:
                        if nomination['feedback'] is not None and len(nomination['feedback']):
                            st.markdown(f'- *{nomination["feedback"]}*' + (f' *-{nomination["nominator"]}*' if not nomination["is_anonymous"] else ''))
                    i += 1
        else:
            st.warning('No one participated today')

def display_progress(reveal_result):
    global members_list
    total_participated = get_total_participants()
    total_members = len(members_list)
    if not reveal_result:
        st.info('The poll is in progress...')
        st.progress(total_participated / total_members)
    
        if total_participated == total_members:
            st.markdown(f'*Yay, we have full house today, everyone participated!*')
        else:
            st.markdown(f'*{total_participated} out of {total_members}*')
            if total_participated / total_members > 0.5:
                waiting_for_list = ', '.join(get_waiting_for_members_list())
                if len(waiting_for_list):
                    st.markdown(f'*Waiting for {waiting_for_list}...*')

def option_host_poll():
    global team_nominations_dict
    sprint_name = get_sprint_config('name', '')

    is_poll_open = get_sprint_config('is_poll_open', False)
    is_poll_closed = get_sprint_config('is_poll_closed', False)
    
    if not is_poll_closed:
        sprint_name = st.text_input('Sprint Name:', sprint_name)
    elif len(sprint_name):
        st.subheader(sprint_name)

    if sprint_name:
        set_sprint_default_values()
        set_sprint_config('name', sprint_name)
        if not is_poll_open:
            if st.button('Open the poll for nominations', is_poll_open):
                is_poll_open = True
                set_sprint_config('is_poll_open', is_poll_open)
                set_sprint_config('members', get_team_members_default_dict())

        if is_poll_open:
            display_progress(is_poll_closed)
            display_result(is_poll_closed)

            if not is_poll_closed and get_total_participants():
                if st.button('Close the poll / Reveal names') or len(get_waiting_for_members_list()) == 0:
                    st.balloons()
                    set_sprint_config('is_poll_closed', True)
                    is_poll_closed = True

            if is_poll_closed:
                st.markdown('---')
                if st.button(f'Delete the poll to start over'):
                    set_sprint_default_values(True)
        save_sprint_configs_into_file()


def option_nominate_star():
    st.subheader(get_sprint_config('name', ''))
    
    submitted = False
    is_poll_closed = get_sprint_config('is_poll_closed', False)
    
    if not is_poll_closed:
        submitted = display_nomination_form()
    
    if is_poll_closed or submitted:
        display_progress(is_poll_closed)
        if is_poll_closed:
            display_result(is_poll_closed)
            st.info('The poll has been closed for this sprint')            

def option_settings():
    global members_list
    display_github_source_button()
    st.subheader('Settings')
    if len(members_list) == 0:
        display_empty_team_members_names_warning()
    members_str = ', '.join(members_list)
    members_str = st.text_area('Team Members Names (comma separated):', members_str)
    if st.button('Save') and len(members_str):
        members_list = [m.strip() for m in members_str.split(',')]
        save_members_list_into_file()

def main():
    global members_list
    st.set_page_config(page_title=PAGE_TITLE, page_icon=APP_ICON)
    st.title(PAGE_TITLE)
    
    load_sprint_configs_from_file()
    load_members_list_from_file()

    option_list = []

    if len(members_list):
        option_list = [
            OPTION_NOMINATE_STAR,
            OPTION_HOST_POLL,
            OPTION_SETTINGS
        ]
    else:
        option_list = [OPTION_SETTINGS]

    option = st.sidebar.radio('Select an option:', option_list)

    if option == OPTION_HOST_POLL:
        option_host_poll()
    elif option == OPTION_NOMINATE_STAR:
        option_nominate_star()
    elif option == OPTION_SETTINGS:
        option_settings()


s = st.GlobalState(key="mySate")
if not s:
    s.lock = Lock()

with s.lock:
    main()