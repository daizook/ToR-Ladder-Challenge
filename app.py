import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

TIER = 'gen9uu'
leaderboard_file = 'leaderboard.csv'

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

def save_leaderboard(df):
    df.to_csv(leaderboard_file, index=False)

def load_leaderboard():
    if os.path.exists(leaderboard_file):
        return pd.read_csv(leaderboard_file)
    else:
        raise ValueError("Leaderboard does not exist!! Contact Daizook and tell his ass to debug this.")

def refresh():
    """
    function refreshes leaderboard such that leaderboard does not stay static
    """
    leaderboard_df = load_leaderboard()

    if len(leaderboard_df) == 0:
        updated_data = {'Username' : [],
                    'ELO' : [],
                    'GXE' : []
                    }
        
        updated_leaderboard_df = pd.DataFrame(updated_data)
        updated_leaderboard_df.to_csv('leaderboard.csv', index = False)
    else:
        updated_data = {'Username' : [],
                        'ELO' : [],
                        'GXE' : []
                        }
        
        for user in leaderboard_df['Username']:
            ELO, GXE = getELOGXE(tier = TIER, showdownName = user)
            updated_data['Username'].append(user)
            updated_data['ELO'].append(ELO)
            updated_data['GXE'].append(GXE)
        
        updated_leaderboard_df = pd.DataFrame(updated_data)
        updated_leaderboard_df.to_csv('leaderboard.csv', index = False)

def show_leaderboard():
    st.title("Leaderboard")

    if st.button("Refresh Leaderboard"):
        st.session_state['leaderboard'] = refresh()
        st.success("Leaderboard refreshed!")

    st.table(st.session_state['leaderboard'].sort_values(by='ELO', ascending=False).reset_index(drop=True))

leaderboard_df = refresh()

#keeps tracks of users (hopefully)
if 'leaderboard' not in st.session_state:
    st.session_state['leaderboard'] = refresh()

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
                global leaderboard_df
                leaderboard_df = pd.concat([leaderboard_df, new_entry], ignore_index=True)
                save_leaderboard(leaderboard_df)  # Save to CSV
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


