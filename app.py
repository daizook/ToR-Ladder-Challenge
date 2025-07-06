import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import numpy as np
import json

# ADMIN PANEL: tracking changes: 5th July, 2025
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

if "admin_variable" not in st.session_state:
    st.session_state.admin_variable = "You shouldn't be seeing this.. Contact Daizook"

TIER_FILE = "tier-config.json"

def load_tier():
    if os.path.exists(TIER_FILE):
        with open(TIER_FILE, 'r') as f:
            return json.load(f).get("TIER", "gen9uu")
    return "gen9uu"

def save_tier(tier):
    with open(TIER_FILE, 'w') as f:
        json.dump({"TIER": tier}, f)

# initializing session state...
if "TIER" not in st.session_state:
    st.session_state["TIER"] = load_tier()

leaderboard_file = 'leaderboard.csv'

def admin_panel():
    st.header("🛠️ Admin Panel")

    with st.expander("Admin Login"):
        st.write("If you're not one of the ToR admins, get your ahhh outta here fam, stop tryna guess the password. -Daizook")
        password = st.text_input("Enter admin password", type="password")
        if password == ADMIN_PASSWORD:
            st.success("Access granted.")

            current_tier = st.session_state.get("TIER", "gen9uu")
            st.write(f"Current tier: `{current_tier}`")

            new_tier = st.text_input("Set a new tier (e.g., gen9ou, gen9randombattle) - if this breaks, lmk -Daizook:", value=current_tier)
            if st.button("Update tier"):
                st.session_state["TIER"] = new_tier
                save_tier(new_tier)  # Persist it!
                st.success(f"Tier updated to: `{new_tier}`")

        elif password != "":
            st.error("Incorrect password. You didn't have enough aura.")

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

def add_custom_css():
    st.markdown("""
        <style>
        /* Style for the leaderboard table */
        .dataframe tbody tr:nth-child(even) {
            background-color: #262730;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: #1C1E22;
        }
        .dataframe thead {
            background-color: #1E90FF;
            color: white;
            font-weight: bold;
        }
        .stButton button {
            background-color: #1E90FF !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)

def reload_page_button():
    if st.button("Reload Page"):
        # Force reloading the leaderboard from CSV
        leaderboard_df = load_leaderboard()
        st.session_state['leaderboard'] = leaderboard_df
        st.experimental_rerun()

def show_leaderboard():
    st.title("🏆 Leaderboard")

    if st.button("🔄 Refresh Leaderboard"):
        refresh()
        st.success("Leaderboard refreshed with updated scores!")

    st.table(st.session_state['leaderboard'].sort_values(by='ELO', ascending=False).reset_index(drop=True))

leaderboard_df = load_leaderboard()

# Keeps track of users
if 'leaderboard' not in st.session_state:
    st.session_state['leaderboard'] = leaderboard_df

def refresh():
    for idx, row in st.session_state['leaderboard'].iterrows():
        username = row['Username']
        ELO, GXE = getELOGXE(tier = st.session_state["TIER"], showdownName=username)
        st.session_state['leaderboard'].at[idx, 'ELO'] = ELO
        st.session_state['leaderboard'].at[idx, 'GXE'] = GXE
    
    st.experimental_rerun()

def user_input_section():
    """
    Handles user inputs; allows them to enter their Showdown username.
    """
    st.header("✍️ Registration")
    st.write("Please make sure you follow the tag format specified by Daizook! 😉 For example, if Daizook wants everyone to use the tag tor9uu, your username should be, for instance, tor9uu DaiBro. Good luck and have fun!!")

    username = st.text_input("Register with your Pokemon Showdown username!")
    ELO, GXE = getELOGXE(showdownName=username, tier=st.session_state["TIER"])

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
                
                leaderboard_df = load_leaderboard()
                st.session_state['leaderboard'] = leaderboard_df
                st.experimental_rerun()

def instructions():
    st.header("📝 Instructions")
    first_paragraph = """
    Hey, welcome to the Treasures of Ruin ladder tournament! This is (what I consider) a pretty standard ladder tournament, in which the goal is to climb as far as you can up the ladder of some chosen tier
    on Pokemon Showdown. This is a pretty fun way to, not only explore other tiers apart from motherfucking OU, but also become a better player, as you get familiar with what other Pokemon can do without frantically 
    looking it up on Smogon during a game.
    """
    st.write(first_paragraph)

    st.subheader("How to sign up")
    sign_up_para = """
    Go to ✍️ Registration, follow the username instructions there (Daizook will probably tell you the tag beforehand), and fill in the form given! Then, press the 'Add me to the leaderboard!' button, and you should 
    be registered and good to go. Yes, I can't believe I have to write this shit.
    """
    st.write(sign_up_para)

    st.subheader("Refreshing the leaderboard")
    refresh_para = """
    The "Refresh leaderboard" button is there so that anyone can see the current leaderboard rankings by the push of a button. For instance, if you're playing a few ladder games and you're tilted as fuck, you can 
    go to this site, press:
    """
    st.write(refresh_para)
    if st.button("ඞ Refresh Leaderboard"):
        st.image("images/amoonguss_gen5.gif")
        st.write("Ha ha you got pranked. Use the button at the top. That's the real one.")
    refresh_para_2 = """
    and you can actually watch your ELO drop 200 points and your GXE fall to 50%! 
    """
    st.write(refresh_para_2)

def credits():
    st.header("✨ Credits")

    credit_para = """
    This web application was coded and designed by Daizook (Discord user: daizook). The open-source code is available here (https://github.com/daizook/ToR-Ladder-Challenge), and you are allowed to use this code 
    if you want to launch your own ladder tournament. However, if you do, please give credit to Daizook in your site somewhere (and, of course, link his GitHub repository :]). ALSO: If your shit is bugging, don't 
    hesitate to contact me and I'll try to see what dumb mistake I (Daizook) made. 'Kay, have fun! Road to top 10 starts now!!
    """
    st.write(credit_para)

    st.image("images/logo.png", caption="Treasures of Ruin Discord: https://discord.gg/MQuHkH48. Logo made by Viz, luv ya bud")


def main():
    st.title("Treasures of Ruin Ladder Challenge")
    st.write(f"(Made with love by Daizook) Hi everyone! This month's tier is {st.session_state['TIER']}")

    # Display leaderboard first
    show_leaderboard()
    
    # Display user input section below the leaderboard
    user_input_section()

    instructions()

    admin_panel()

    credits()

if __name__ == "__main__":
    main()
