import time
import streamlit as st
import requests
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import playerdashboardbyshootingsplits

fl_name = __file__.split("\\")[-1].split(".")[0]

st.set_page_config(page_title="Player Demo", page_icon="📊")

st.title('Player Analytics')
st.write(
    """
    This page would allow you to compare between Players' Boxscore, Shooting percentages 
    or 
    even understand if a player has improved after a period of N games.

    """
)

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


@st.cache_data
def getPlayerBoxScore(player_name, last_n_games, season = "2022-23", game_type = "Regular Season", ):
    use_cols = ['GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']

    print("Processing Player : {}".format(player_name))
    time.sleep(1)
    p_id = players.find_players_by_full_name(player_name)[0]['id']
    # print("Player : {} \t Player_ID = {}".format(p, player_id))
    try:
        time.sleep(1)
        p_log = playergamelog.PlayerGameLog(player_id=p_id, season_type_all_star=game_type, timeout=10).get_data_frames()[0][:last_n_games]
        print(len(p_log))
        if len(p_log) > 0:
            p_log_gs = p_log.loc[:, use_cols]
            p_log_gs["GS"] = p_log_gs["PTS"] + 0.4 * p_log_gs["FGM"] - 0.7 * p_log_gs["FGA"] - 0.4 * (p_log_gs["FTA"] - p_log_gs["FTM"])  + 0.7 * p_log_gs["OREB"] + 0.3 * p_log_gs["DREB"] + p_log_gs["STL"] + 0.7 * p_log_gs["AST"] + 0.7 * p_log_gs["BLK"] - 0.4 * p_log_gs["PF"] - p_log_gs["TOV"]
            p_log_gs["GS_MIN"] = round(p_log_gs["GS"] / p_log_gs["MIN"], 3)

    except requests.exceptions.ReadTimeout:
        print("Timeout Occured for Player: {}".format(player_name))
        st.write("Player does not have any box score")

    return p_log_gs

def getPlayerShootingChart(player_name, last_n_games, season="2022-23", game_type="Regular Season"):
    time.sleep(1)
    p_id = players.find_players_by_full_name(player_name)[0]['id']
    time.sleep(1)
    playerShootingSplits = playerdashboardbyshootingsplits.PlayerDashboardByShootingSplits(last_n_games=last_n_games, measure_type_detailed="Base", month=0, opponent_team_id=0, pace_adjust="N", 
                                            per_mode_detailed="PerGame", period=0, player_id=p_id, plus_minus="N", rank="N", season=season, season_type_playoffs=game_type,
                                            vs_division_nullable=None, vs_conference_nullable=None, season_segment_nullable=None, outcome_nullable=None,
                                            location_nullable=None, game_segment_nullable	=None, date_to_nullable=None, date_from_nullable=None
                                            )
    
    playerShootingSplits_df = playerShootingSplits.shot_area_player_dashboard.get_data_frame()
    return playerShootingSplits_df


def getTeamNames():
# Get all the teams and their information
    time.sleep(1)
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
    plt.ylim(0,1)
    plt.xticks(theta[:-1], df['GROUP_VALUE'], color='grey', size=12)
    ax.tick_params(direction='out', pad=30) # to increase the distance of the labels to the plot
    # fill the area of the polygon with green and some transparency
    ax.fill(theta, values, 'green', alpha=0.1)
    # plt.legend() # shows the legend, using the label of the line plot (useful when there is more than 1 polygon)
    plt.title("Shot Type Percentages")
    st.pyplot(fig)
    # plt.show()


try:
    col1, col2 = st.columns(2)
    with col1:
        nba_team1 = st.selectbox(
            "Choose Team", getTeamNames(), key="team1"
        )
        player_name1 = st.selectbox(
            "Choose Player", getPlayersName(nba_team1), key="player1"
        ) 
        game_type1 = st.selectbox(
            "Choose Game Type", ["Regular Season", "Pre Season", "Playoffs", "All-Star"], key="gt1"
        ) 
        n_games1 = st.slider("Number of Past Games", 1, 82, 16, key="ngame1", help="Takes slider value and perform an analysis for the last N Games")
        if not nba_team1:
            st.error("Please select at least one team.")
        else:
            data1 = getPlayerBoxScore(player_name1, game_type=game_type1, last_n_games = n_games1)
            st.write("### {} BoxScore".format(player_name1), data1)
            if len(data1) > 0:
                st.download_button('Download Dataframe', convert_df(data1), file_name='{}_1.csv'.format(fl_name), mime='text/csv', key="{}_1_download".format(fl_name))

    with col2:
        nba_team2 = st.selectbox(
            "Choose Team", getTeamNames(), key="team2"
        )
        player_name2 = st.selectbox(
            "Choose Player", getPlayersName(nba_team2), key="player2"
        ) 
        game_type2 = st.selectbox(
            "Choose Game Type", ["Regular Season", "Pre Season", "Playoffs", "All-Star"], key="gt2"
        ) 
        n_games2 = st.slider("Number of Past Games", 1, 82, 16, key="ngames2", help="Takes slider value and perform an analysis for the last N Games")
        if not nba_team2:
            st.error("Please select at least one team.")
        else:
            data2 = getPlayerBoxScore(player_name2, game_type=game_type2, last_n_games = n_games2)
            st.write("### {} BoxScore".format(player_name2), data2)
            if len(data2) > 0:
                st.download_button('Download Dataframe', convert_df(data2), file_name='{}_2.csv'.format(fl_name), mime='text/csv', key="{}_2_download".format(fl_name))


# Shot Charts for the different players
    with col1:
        shotChart1 = getPlayerShootingChart(player_name1, n_games1, season="2022-23", game_type=game_type1)
        # st.write("### Player ShotChart", shotChart1)
        make_shot_spider(shotChart1)
    with col2:
        shotChart2 = getPlayerShootingChart(player_name2, n_games2, season="2022-23", game_type=game_type2)
        # st.write("### Player ShotChart", shotChart2)
        make_shot_spider(shotChart2)



except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
