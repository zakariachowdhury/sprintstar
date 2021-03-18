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
except:
    pass

PAGE_TITLE = 'The Stars of the Sprint'
APP_ICON = ':star:'

OPTION_NOMINATE_STAR = 'Nominate a star'
OPTION_HOST_POLL = 'Host the poll'
OPTION_SETTINGS = 'Settings'

LABEL_PARTICIPATING = 'Participating'
LABEL_NOT_PARTICIPATING = 'Not participating today'

CONFIG_DIR = 'config/'
SPRINT_CONFIG_FILENAME = CONFIG_DIR + 'sprint.py'
TODAY = str(datetime.now().date())

class Nomination:
    nominator = None
    feedback = None
    is_anonymous = False

    def __init__(self, nominator, feedback=None, is_anonymous=False) -> None:
        self.nominator = nominator
        self.feedback = feedback
        self.is_anonymous = is_anonymous


team_members_dict = {
    'Ava': [Nomination('Richard', 'Amazing work in this sprint').__dict__],
    'Richard': [],
    'Lyman': [],
    'Ruth': [],
    'Claire': [],
    'Brandon': [],
    'Caroline': [Nomination('Neil', None, True).__dict__, Nomination('Ruth').__dict__],
    'Neil': [],
    'Thomas': [Nomination('Claire').__dict__, Nomination('Brandon').__dict__, Nomination('Lyman', 'Completed all the tasks', True).__dict__],
    'Jane': []
}

SPRINT_DEFAULT_VALUES = {
        'name': '',
        'members': {},
        'is_poll_open': False,
        'is_poll_closed': False
    }

sprint_config = {}

def set_sprint_default_values(force=False):
    global sprint_config
    if TODAY not in sprint_config.keys() or force:
        sprint_config[TODAY] = SPRINT_DEFAULT_VALUES

def save_sprint_configs_into_file():
    global sprint_config
    with open(SPRINT_CONFIG_FILENAME, 'w') as f:
        f.write(str(sprint_config))

def load_spring_configs_from_file():
    global sprint_config
    if not os.path.exists(SPRINT_CONFIG_FILENAME):
        save_sprint_configs_into_file()
        from config import sprint # to force auto refresh page on file change

    try:
        with open(SPRINT_CONFIG_FILENAME) as f:
            sprint_config = eval(f.read())
    except Exception as e:
        print(e)
        pass
    return None

def get_sprint_config(key, default=None):
    global sprint_config
    return sprint_config[TODAY][key] if TODAY in sprint_config.keys() and key in sprint_config[TODAY].keys() else default

def set_sprint_config(key, value):
    global sprint_config
    if TODAY in sprint_config.keys() and key in sprint_config[TODAY].keys():
        sprint_config[TODAY][key] = value

def get_star_members_dict(reverse = False):
    return {k: v for k, v in sorted(team_members_dict.items(), key=lambda item: len(item[1]) if not reverse else -len(item[1])) if len(v)}

def get_total_participants():
    return sum([len(v) for _, v in team_members_dict.items()])

def display_github_source_button():
    st.markdown('<iframe src="https://ghbtns.com/github-btn.html?user=zakariachowdhury&repo=sprintstars&type=star&count=true" frameborder="0" scrolling="0" width="150" height="20" title="GitHub"></iframe>', unsafe_allow_html=True)

def display_nomination_form():
    global team_members_dict
    sprint_name = get_sprint_config('name', '')
    is_poll_open = get_sprint_config('is_poll_open', False)
    is_poll_closed = get_sprint_config('is_poll_closed', False)

    if not is_poll_open or len(sprint_name) == 0:
        st.info('Please wait for the host to open the poll')
    elif is_poll_closed:
        st.info('The poll has been closed')
    else:
        members_list = ['']
        feedback = None
        members_list.extend(list(team_members_dict.keys()))
        members_list = sorted(members_list)

        nominator = st.selectbox('Select your name:', members_list)
        if nominator:
            is_not_participating = st.checkbox(LABEL_NOT_PARTICIPATING)

            if not is_not_participating:
                is_anonymous = st.checkbox('Nominate anonymously')
                members_list.remove(nominator)
                star_member = st.selectbox('Nominate a star for this sprint:', members_list)

                if len(star_member):
                    feedback = st.text_area('What are the reasons for nominating ' + star_member + '? (optional)')
                    members_list.remove(star_member)
                
                    if st.checkbox('Submit'):
                        team_members_dict[star_member].append(Nomination(nominator, feedback, is_anonymous).__dict__)
                        return True
            else:
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
    total_participated = get_total_participants()
    total_members = len(team_members_dict)
    if not reveal_result:
        st.info('The poll is in progress...')
        st.progress(total_participated / total_members)
    
        if total_participated == total_members:
            st.markdown(f'*Yay, we have full house today, everyone participated!*')
        else:
            st.markdown(f'*{total_participated} out of {total_members}*')

def option_host_poll():
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
            is_poll_open = st.button('Open the poll for nominations', is_poll_open)
            set_sprint_config('is_poll_open', is_poll_open)

        if is_poll_open:
            display_progress(is_poll_closed)
            display_result(is_poll_closed)

            if not is_poll_closed:
                if st.button('Close the poll / Reveal names'):
                    set_sprint_config('is_poll_closed', True)
                    is_poll_closed = True
            
            #star_members_dict = get_star_members_dict()
            #if len(star_members_dict.keys()):
                #get_total_participants() == len(team_members_dict)

            if is_poll_closed:
                st.markdown('---')
                if st.button(f'Delete the poll'):
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

def option_settings():
    display_github_source_button()
    st.subheader('Settings')    
    team_members = ', '.join(list(team_members_dict.keys()))
    st.text_area('Participant Names (comma separated):', team_members)
    st.button('Save')

def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=APP_ICON)
    st.title(PAGE_TITLE)
    
    load_spring_configs_from_file()

    # global sprint_config
    # st.write(sprint_config)

    option = st.sidebar.radio('Select an option:', [
        OPTION_NOMINATE_STAR,
        OPTION_HOST_POLL,
        OPTION_SETTINGS
    ])

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