import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

PAGE_TITLE = 'Star of the Sprint'
APP_ICON = ':star:'

class Nomination:
    nominator = None
    feedback = None

    def __init__(self, nominator, feedback=None) -> None:
        self.nominator = nominator
        self.feedback = feedback


team_members_dict = {
    '':[],
    'Ava': [Nomination('Richard', 'Amazing work in this sprint')],
    'Richard': [],
    'Lyman': [],
    'Ruth': [Nomination('Claire'), Nomination('Neil', 'Completed all the tasks')],
    'Claire': [],
    'Brandon': [],
    'Caroline': [],
    'Neil': [],
    'Thomas': [],
    'Jane': []
}

def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=APP_ICON)

    st.title(PAGE_TITLE)

    members_list = sorted(list(team_members_dict.keys()))

    star_member = st.selectbox('Nominate a star for this sprint:', members_list)

    if len(star_member):
        feedback = st.text_area('Why are you nominating ' + star_member + '? (optional)')
        members_list.remove(star_member)
        nominator = st.selectbox('Your name:', members_list)

        if nominator:
            if st.button('Submit'):
                team_members_dict[star_member].append(Nomination(nominator, feedback))
                st.info('Your nomination for ' + star_member + ' has been submitted!')

    st.title('Result')

    fig, ax = plt.subplots()
    star_members_dict = {k: v for k, v in sorted(team_members_dict.items(), key=lambda item: len(item[1])) if len(v)}
    start_list = list(star_members_dict.keys())
    votes = [len(v) for _, v in star_members_dict.items()]
    ax.barh(start_list, votes, color='lightcoral')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    st.pyplot(fig)

    i = 1
    star_members_dict = {k: v for k, v in sorted(team_members_dict.items(), key=lambda item: -len(item[1])) if len(v)}
    for name, nominations_list in iter(star_members_dict.items()):
        if len(nominations_list):
            st.markdown(f'### {i}. {name} ({len(nominations_list)})')
            for nomination in nominations_list:
                if nomination.feedback is not None and len(nomination.feedback):
                    st.write(f'- {nomination.feedback} ({nomination.nominator})')
            i += 1
main()