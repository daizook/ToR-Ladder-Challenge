import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import numpy as np

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
        ELO = int(sample_text[sample_text.find(tier) + len(tier) : sample_text.find(tier) + len(tier) + 4])
    except ValueError:
        ELO = 1000
    
    try:
        GXE = float(sample_text[sample_text.find(tier) + len(tier) + 4 : sample_text.find(tier) + len(tier) + 8])
        GXE = np.round(GXE, 1)
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

def show_leaderboard():
    # Add custom CSS for dark theme and table styles
    add_custom_css()

    # Title for the leaderboard
    st.title("🏆 Leaderboard")
    
    # Add a button to refresh the leaderboard
    if st.button("🔄 Refresh Leaderboard"):
        refresh()  # Assuming you have this function to refresh the leaderboard
        st.success("Leaderboard refreshed with updated scores!")

    # Sort leaderboard by ELO in descending order and reset the index
    leaderboard_df = st.session_state['leaderboard'].sort_values(by='ELO', ascending=False).reset_index(drop=True)

    # Format the ELO column for better readability
    leaderboard_df['ELO'] = leaderboard_df['ELO'].map('{:,.2f}'.format)

    # Display the styled leaderboard
    st.dataframe(leaderboard_df)

leaderboard_df = load_leaderboard()

# Keeps track of users
if 'leaderboard' not in st.session_state:
    st.session_state['leaderboard'] = leaderboard_df

def refresh():
    for idx, row in st.session_state['leaderboard'].iterrows():
        username = row['Username']
        ELO, GXE = getELOGXE(tier = TIER, showdownName=username)
        st.session_state['leaderboard'].at[idx, 'ELO'] = ELO
        st.session_state['leaderboard'].at[idx, 'GXE'] = GXE
    
    st.experimental_rerun()

def user_input_section():
    """
    Handles user inputs; allows them to enter their Showdown username.
    """
    st.header("Enter Username")

    username = st.text_input("Enter your username:")
    ELO, GXE = getELOGXE(showdownName=username, tier=TIER)

    # Refreshes leaderboard
    if st.button("Add me to the leaderboard!"):
        if username:
            if username in st.session_state['leaderboard']['Username'].values:
                # Denies duplicate users
                st.warning(f"Username '{username}' already registered for ladder challenge. Please choose a different username.")
            else:
                new_entry = pd.DataFrame({'Username': [username], 'ELO': [ELO], 'GXE': [GXE]})
                global leaderboard_df
                leaderboard_df = pd.concat([leaderboard_df, new_entry], ignore_index=True)
                save_leaderboard(leaderboard_df)  # Save to CSV
                st.success(f"{username} added to the leaderboard!")

                st.experimental_rerun()

def main():
    st.title("Treasures of Ruin Ladder Challenge")
    st.write(f"Hi everyone! This month's tier is {TIER}")
    
    # Display leaderboard first
    show_leaderboard()
    
    # Display user input section below the leaderboard
    user_input_section()

if __name__ == "__main__":
    main()
