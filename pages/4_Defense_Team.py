
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

st.title('Player vs Team: Defense Analytics')
st.write(
    """
    This page would allow you to compare a Players' Statistics when being placed against another Team's Roster.

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
    all_teams = teams.get_teams()
    all_teams_df = pd.DataFrame(all_teams)
    abb_t = all_teams_df.loc[all_teams_df['full_name'] == team, 'abbreviation'].item()
    # Find the team by its abbreviation
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
def getTeamDefenseBoxScore(player_name1, def_team, seasons = ['2022-23'], game_type="Regular Season"):
    team_df = pd.DataFrame(teams.get_teams())
    team_row = team_df.loc[team_df['full_name'].str.strip() == def_team, :]
    def_team_id = team_row.id.item()

    p_id1 = players.find_players_by_full_name(player_name1)[0]['id'], 
    cat_pvp = []
    for s in seasons:
        try:
            time.sleep(1)
            pvp_s = leagueseasonmatchups.LeagueSeasonMatchups(league_id='00', per_mode_simple = "PerGame", season = '2022-23', season_type_playoffs = "Playoffs", off_player_id_nullable = p_id1, def_team_id_nullable = def_team_id).get_data_frames()[0]
            pvp_s['SEASON_ID'] = s
            cat_pvp.append(pvp_s)
        except Exception as e:
            print("Season = {}, there was an exception".format(s))

    cat_s = pd.concat(cat_pvp)
    cat_s = cat_s.drop(['OFF_PLAYER_ID', 'DEF_PLAYER_ID'], axis=1)
    cat_s['TOTAL_PTS'] = cat_s['PLAYER_PTS'] + cat_s['TEAM_PTS']
    cat_s['POINTS_PER_POSS'] = cat_s['TOTAL_PTS'] / cat_s['PARTIAL_POSS']
    cat_s.insert(8, 'TOTAL_PTS', cat_s.pop('TOTAL_PTS'))
    cat_s.insert(4, 'POINTS_PER_POSS', cat_s.pop('POINTS_PER_POSS'))
    cat_s = cat_s.sort_values('SEASON_ID', ascending=False)
    

    return cat_s



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
        defender_team1 = st.selectbox(
            "Choose Team Defending", getTeamNames(), key="defender-team1"
        ) 
        season_selector = st.multiselect('Select Seasons', ['2022-23', '2021-22', '2020-21', '2019-20', '2018-19', '2017-18', '2008-09'])
        if not season_selector:
            st.error("Please select at least one season.")
        else:
            data1 = getTeamDefenseBoxScore(player_name1, defender_team1, season_selector, game_type1)
            st.write("### {} vs {} Matchup".format(player_name1, defender_team1), data1)
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
