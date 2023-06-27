
import streamlit as st
import requests
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonallplayers
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playervsplayer
from nba_api.stats.endpoints import boxscoredefensive
from nba_api.stats.endpoints import boxscoreplayertrackv2
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import playbyplay
from nba_api.stats.endpoints import leagueseasonmatchups

st.set_page_config(page_title="Team Demo", page_icon="📈")
fl_name = __file__.split("\\")[-1].split(".")[0]

st.title('Team Analytics')
st.write(
    """
    This demo shows a team roster's breakdown across N games, to answer questions
    like "Who is the most valuable player within the team?"

    """
)

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def p_addCourt(df):
    if 'vs.' in df['MATCHUP']:
        df['COURT'] = 'HOME'
    else:
        df['COURT'] = 'AWAY'
    return df

@st.cache_data
def getRosterImpact(team_name, season = "2022-23", game_type = "Regular Season", last_n_games = 5):
    # Find the team by its abbreviation
    t_df = pd.DataFrame(teams.get_teams())
    t_abb = t_df.loc[t_df['full_name'] == team_name, 'abbreviation'].item()
    print(t_abb)

    # Find the team by its abbreviation
    t_info = teams.find_team_by_abbreviation(t_abb)
    # Retrieve the team ID
    t_id = t_info['id']

    top_n = 8
    p_stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed='Totals', last_n_games = 82, season_type_all_star = "Playoffs").get_data_frames()[0]
    # player_stats.loc[player_stats['TEAM_ID'] == team_id, :]
    p_mins = p_stats.loc[p_stats['TEAM_ID'] == t_id, ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN']].sort_values('MIN', ascending=False)
    top_mins = p_mins[:top_n]
    top_mins_players = top_mins['PLAYER_NAME']

    dfs = []
    use_cols = ['GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']
    # p = top_mins_players[0]
    for p in top_mins_players:
        print("Processing Player : {}".format(p))
        p_id = players.find_players_by_full_name(p)[0]['id']
        # print("Player : {} \t Player_ID = {}".format(p, player_id))
        try:
            p_log = playergamelog.PlayerGameLog(player_id=p_id, season_type_all_star=game_type, timeout=10).get_data_frames()[0][:last_n_games]
            if len(p_log) > 0:
                p_log_gs = p_log.loc[:, use_cols[1:-1]]
                p_log_gs["GS"] = p_log_gs["PTS"] + 0.4 * p_log_gs["FGM"] - 0.7 * p_log_gs["FGA"] - 0.4 * (p_log_gs["FTA"] - p_log_gs["FTM"])  + 0.7 * p_log_gs["OREB"] + 0.3 * p_log_gs["DREB"] + p_log_gs["STL"] + 0.7 * p_log_gs["AST"] + 0.7 * p_log_gs["BLK"] - 0.4 * p_log_gs["PF"] - p_log_gs["TOV"]
                p_log_gs["GS_MIN"] = round(p_log_gs["GS"] / p_log_gs["MIN"], 3)
                p_log_gs= p_log_gs.apply(p_addCourt, axis=1)
                # print(p_log_gs)
                p_avg = p_log_gs.groupby('COURT').mean(numeric_only=True).round(2).reindex(['HOME', 'AWAY'])
                p_avg.columns.name = p
                dfs.append(p_avg)
        except requests.exceptions.ReadTimeout:
            print("Timeout Occured for Player: {}".format(p))
            continue
    df = pd.concat(dfs, axis=0, keys=top_mins_players)
    df.columns.name = "{} Games Avg".format(last_n_games)
    return df

def getTeamNames():
# Get all the teams and their information
    return pd.DataFrame(teams.get_teams())['full_name']

try:
    nba_teams = st.selectbox(
        "Choose Team", getTeamNames()
    )
    game_type = st.selectbox(
            "Choose Game Type", ["Regular Season", "Pre Season", "Playoffs", "All-Star"], key="gt"
        ) 
    n_games = st.slider("Number of Past Games", 1, 82, 16, help="Takes slider value and perform an analysis for the last N Games")
    if not nba_teams:
        st.error("Please select at least one team.")
    else:
        data = getRosterImpact(nba_teams, game_type=game_type, last_n_games = n_games)
        st.write("### Team Roster Statistics", data)
        if len(data) > 0:
            st.download_button('Download Dataframe', convert_df(data), file_name='{}.csv'.format(fl_name), mime='text/csv', key="{}_download".format(fl_name))

        # data = data.T.reset_index()
        # data = pd.melt(data, id_vars=["index"]).rename(
        #     columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
        # )
        # chart = (
        #     alt.Chart(data)
        #     .mark_area(opacity=0.3)
        #     .encode(
        #         x="year:T",
        #         y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
        #         color="Region:N",
        #     )
        # )
        # st.altair_chart(chart, use_container_width=True)
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
