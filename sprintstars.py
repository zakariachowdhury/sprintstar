import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import time

PAGE_TITLE = 'The Stars of the Sprint'
APP_ICON = ':star:'

OPTION_NOMINATE_STAR = 'Nominate a star'
OPTION_HOST_POLL = 'Host the poll'
OPTION_SETTINGS = 'Settings'

LABEL_PARTICIPATING = 'Participating'
LABEL_NOT_PARTICIPATING = 'Not participating today'

class Nomination:
    nominator = None
    feedback = None
    is_anonymous = False

    def __init__(self, nominator, feedback=None, is_anonymous=False) -> None:
        self.nominator = nominator
        self.feedback = feedback
        self.is_anonymous = is_anonymous


team_members_dict = {
    'Ava': [Nomination('Richard', 'Amazing work in this sprint')],
    'Richard': [],
    'Lyman': [],
    'Ruth': [],
    'Claire': [],
    'Brandon': [],
    'Caroline': [Nomination('Neil', None, True), Nomination('Ruth')],
    'Neil': [],
    'Thomas': [Nomination('Claire'), Nomination('Brandon'), Nomination('Lyman', 'Completed all the tasks', True)],
    'Jane': []
}

def get_star_members_dict(reverse = False):
    return {k: v for k, v in sorted(team_members_dict.items(), key=lambda item: len(item[1]) if not reverse else -len(item[1])) if len(v)}

def get_total_participants():
    return sum([len(v) for _, v in team_members_dict.items()])

def display_nomination_form():
    members_list = ['']
    feedback = None
    members_list.extend(list(team_members_dict.keys()))
    members_list = sorted(members_list)

    nominator = st.selectbox('Your name:', members_list)
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
                    team_members_dict[star_member].append(Nomination(nominator, feedback, is_anonymous))
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
        ax.barh(start_list, votes, color='lightcoral')
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
        for name, nominations_list in iter(star_members_dict.items()):
            if i == 1:
                top_votes = len(nominations_list)

            if len(nominations_list):
                st.markdown(f'### {i}. {name} ({len(nominations_list)} {"votes" if len(nominations_list) > 1 else "vote"}) {":star:" if len(nominations_list) == top_votes else ""}')
                for nomination in nominations_list:
                    if nomination.feedback is not None and len(nomination.feedback):
                        st.markdown(f'- {nomination.feedback}' + (f' *-{nomination.nominator}*' if not nomination.is_anonymous else ''))
                i += 1
        st.balloons()

def display_progress(reveal_result):
    total_participated = get_total_participants()
    total_members = len(team_members_dict)
    if not reveal_result:
        st.info('The poll is in progress, please wait...')
        st.progress(total_participated / total_members)
    
        if total_participated == total_members:
            st.markdown(f'*Yay, we have full house today, everyone participated!*')
        else:
            st.markdown(f'*{total_participated} out of {total_members}*')

    return reveal_result

def option_host_poll():
    sprint_name = st.text_input('Sprint Name:')
    if sprint_name:
        open_poll = st.checkbox('Open the poll', False)
        if open_poll:
            reveal_result = False

            star_members_dict = get_star_members_dict()
            if len(star_members_dict.keys()):
                reveal_result = st.checkbox('Close the poll / Reveal names', get_total_participants() == len(team_members_dict))

            reveal_result = display_progress(reveal_result)

            display_result(reveal_result)


def option_nominate_star():
    submitted = False
    reveal_result = False
    
    if not reveal_result:
        submitted = display_nomination_form()
    
    if reveal_result or submitted:
        reveal_result = display_progress(reveal_result)
        if reveal_result:
            display_result(reveal_result)

def option_settings():
    #st.write(list(team_members_dict.keys()))
    team_members = ', '.join(list(team_members_dict.keys()))
    st.text_area('Participant Names (comma separated):', team_members)
    st.button('Save')

def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=APP_ICON)

    st.title(PAGE_TITLE)

    option = st.sidebar.radio('Select an option:', [
        OPTION_NOMINATE_STAR,
        OPTION_HOST_POLL,
        OPTION_SETTINGS
    ], 1)

    if option == OPTION_HOST_POLL:
        option_host_poll()
    elif option == OPTION_NOMINATE_STAR:
        option_nominate_star()
    elif option == OPTION_SETTINGS:
        option_settings()
main()