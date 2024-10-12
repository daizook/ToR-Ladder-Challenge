import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

TIER = 'gen9uu'

def getELOGXE(tier: str, showdownName: str):
    """
    Returns ELO, GXE for any Pokemon Showdown username
    tier -> example: gen9uu, gen9nationaldex, etc.
    showdownURL example: uu5pi zook

    usage of function: getELOGXE('gen9uu', 'uu5pi zook')
    >> (1499.0, 79.1) -> (ELO, GXE)
    """

    urlName = showdownName.replace(" ", "_")
    url = f'https://pokemonshowdown.com/users/{urlName}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    sample_text = soup.text.replace('\n', ' ')
    try:
        ELO = float(sample_text[sample_text.find(tier) + len(tier) : sample_text.find(tier) + len(tier) + 4])
    except ValueError:
        ELO = 1000
    
    try:
        GXE = float(sample_text[sample_text.find(tier) + len(tier) + 4 : sample_text.find(tier) + len(tier) + 8])
    except ValueError:
        GXE = 0
    
    return ELO, GXE

leaderboard_data = {
    'Username': [],
    'ELO': [],
    'GXE' : []
}

leaderboard_df = pd.DataFrame(leaderboard_data)

#keeps tracks of users (hopefully)
if 'leaderboard' not in st.session_state:
    st.session_state['leaderboard'] = leaderboard_df

def show_leaderboard():
    """
    Displays leaderboard
    """
    st.title("Leaderboard")
    st.table(st.session_state['leaderboard'].sort_values(by='ELO', ascending=False).reset_index(drop=True))

def user_page():
    """
    handles user inputs; allows them to enter their Showdown user.
    """
    st.title("Enter Username")

    username = st.text_input("Enter your username:")
    ELO, GXE = getELOGXE(showdownName=username, tier = TIER)

    #refreshes leaderboard
    if st.button("Add me to the leaderboard!"):
        if username:
            if username in st.session_state['leaderboard']['Username'].values:
                #denies people from entering duplicate users
                st.warning(f"Username '{username}' already registered for ladder challenge. Please choose a different username.")
            else:
                new_entry = pd.DataFrame({'Username': [username], 'ELO': [ELO], 'GXE' : [GXE]})
                st.session_state['leaderboard'] = pd.concat([st.session_state['leaderboard'], new_entry], ignore_index=True)
                st.success(f"{username} added to the leaderboard!")

def main():
    st.sidebar.title(f"Treasures of Ruin Ladder Challenge - {TIER}")
    page = st.sidebar.selectbox("Select a page", ["Leaderboard", "Enter Username"])

    if page == "Leaderboard":
        show_leaderboard()
    elif page == "Enter Username":
        user_page()

if __name__ == "__main__":
    main()


