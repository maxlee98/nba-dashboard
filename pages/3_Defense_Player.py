
import streamlit as st
import time
from urllib.error import URLError
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import leagueseasonmatchups


st.set_page_config(page_title="Player Demo", page_icon="📊")
fl_name = __file__.split("\\")[-1].split(".")[0]

st.title('Player vs Player Defense Analytics')
st.write(
    """
    This page would allow you to compare a Players' Statistics when being placed against someone as a defender.

    """
)

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def getTeamNames():
# Get all the teams and their information
    return pd.DataFrame(teams.get_teams())['full_name']

def getPlayersName(team, season='2022-23'):
    time.sleep(1)
    all_teams = teams.get_teams()
    all_teams_df = pd.DataFrame(all_teams)
    abb_t = all_teams_df.loc[all_teams_df['full_name'] == team, 'abbreviation'].item()
    # Find the team by its abbreviation
    time.sleep(1)
    team_info = teams.find_team_by_abbreviation(abb_t)

    # Retrieve the team ID
    team_id = team_info['id']
    time.sleep(1)
    roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
    roster = roster.get_data_frames()[0]['PLAYER']

    time.sleep(1)
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed='Totals', last_n_games = 82, season_type_all_star = "Playoffs").get_data_frames()[0]
    player_mins = player_stats.loc[(player_stats['TEAM_ID'] == team_id) & (player_stats['MIN'] > 0), ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN']].sort_values('MIN', ascending=False)
    
    return list(player_mins.PLAYER_NAME)


def getDefenderList(player_name, season = "2022-23", game_type = "Regular Season"):
    time.sleep(1)
    p_id = players.find_players_by_full_name(player_name)[0]['id']
    time.sleep(1)
    matchups = leagueseasonmatchups.LeagueSeasonMatchups(league_id = "00", 	per_mode_simple = "PerGame", season = season, season_type_playoffs = game_type, off_player_id_nullable = p_id).get_data_frames()[0]
    return matchups['DEF_PLAYER_NAME']

@st.cache_data
def getDefenseBoxScore(player_name1, player_name2, seasons = ['2022-23'], game_type="Regular Season"):
    time.sleep(1)
    p_id1, p_id2 = players.find_players_by_full_name(player_name1)[0]['id'], players.find_players_by_full_name(player_name2)[0]['id']
    cat_pvp = []
    for s in seasons:
        try:
            time.sleep(1)
            pvp_s = leagueseasonmatchups.LeagueSeasonMatchups(league_id = "00", per_mode_simple = "PerGame", season = s, season_type_playoffs = game_type, off_player_id_nullable = p_id1, def_player_id_nullable = p_id2).get_data_frames()[0]
            pvp_s['SEASON_ID'] = s
            cat_pvp.append(pvp_s)
        except Exception as e:
            print("Season = {}, there was an exception".format(s))

    cat_s = pd.concat(cat_pvp)
    cat_s = cat_s.drop(['OFF_PLAYER_ID', 'DEF_PLAYER_ID'], axis=1)
    cat_s = cat_s.sort_values('SEASON_ID', ascending=False)
    

    return cat_s


def make_shot_spider(df):
    data = df[['GROUP_VALUE', 'FG_PCT']]

    # number of variable
    N = len(data)
    

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="polar")

    # theta has 5 different angles, and the first one repeated
    theta = np.arange(len(df) + 1) / float(len(df)) * 2 * np.pi
    # values has the 5 values from 'Col B', with the first element repeated
    values = df['FG_PCT'].values
    values = np.append(values, values[0])

    # draw the polygon and the mark the points for each angle/value combination
    l1, = ax.plot(theta, values, color="C2", marker="o", label="FG_PCT")
    plt.xticks(theta[:-1], df['GROUP_VALUE'], color='grey', size=12)
    ax.tick_params(direction='out', pad=30) # to increase the distance of the labels to the plot
    # fill the area of the polygon with green and some transparency
    ax.fill(theta, values, 'green', alpha=0.1)

    # plt.legend() # shows the legend, using the label of the line plot (useful when there is more than 1 polygon)
    plt.title("Shot Type Percentages")
    st.pyplot(fig)
    # plt.show()


try:
        nba_team1 = st.selectbox(
            "Choose Team", getTeamNames(), key="team1"
        )
        player_name1 = st.selectbox(
            "Choose Player", getPlayersName(nba_team1), key="player1"
        ) 
        game_type1 = st.selectbox(
            "Choose Game Type", ["Regular Season", "Pre Season", "Playoffs", "All-Star"], key="gt1"
        ) 
        defender_name1 = st.selectbox(
            "Choose Defender", getDefenderList(player_name1, game_type=game_type1), key="defender1"
        ) 
        season_selector = st.multiselect('Select Seasons', ['2022-23', '2021-22', '2020-21', '2019-20', '2018-19', '2017-18', '2008-09'])
        if not season_selector:
            st.error("Please select at least one season.")
        else:
            data1 = getDefenseBoxScore(player_name1, defender_name1, season_selector, game_type1)
            st.write("### {} vs {} Matchup".format(player_name1, defender_name1), data1)
            if len(data1) > 0:
                st.download_button('Download Dataframe', convert_df(data1), file_name='{}.csv'.format(fl_name), mime='text/csv', key="{}_download".format(fl_name))




except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
