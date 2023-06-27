
import streamlit as st
import altair as alt
import requests
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import pandas as pd
import numpy as np
from nba_api.stats.static import teams
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamestimatedmetrics

# Team Colours ########################################
team_colors_dict = {
    'Atlanta Hawks': '#E03A3E',
    'Boston Celtics': '#007A33',
    'Brooklyn Nets': '#000000',
    'Charlotte Hornets': '#00788C',
    'Chicago Bulls': '#CE1141',
    'Cleveland Cavaliers': '#6F263D',
    'Dallas Mavericks': '#00538C',
    'Denver Nuggets': '#0E2240',
    'Detroit Pistons': '#C8102E',
    'Golden State Warriors': '#1D428A',
    'Houston Rockets': '#CE1141',
    'Indiana Pacers': '#002D62',
    'LA Clippers': '#C8102E',
    'Los Angeles Lakers': '#552583',
    'Memphis Grizzlies': '#5D76A9',
    'Miami Heat': '#98002E',
    'Milwaukee Bucks': '#00471B',
    'Minnesota Timberwolves': '#0C2340',
    'New Orleans Pelicans': '#0C2340',
    'New York Knicks': '#F58426',
    'Oklahoma City Thunder': '#007AC1',
    'Orlando Magic': '#0077C0',
    'Philadelphia 76ers': '#ED174C',
    'Phoenix Suns': '#1D1160',
    'Portland Trail Blazers': '#E03A3E',
    'Sacramento Kings': '#5A2D81',
    'San Antonio Spurs': '#C4CED4',
    'Toronto Raptors': '#CE1141',
    'Utah Jazz': '#002B5C',
    'Washington Wizards': '#002B5C'
}
########################################




st.set_page_config(page_title="Team Demo", page_icon="📈")
fl_name = __file__.split("\\")[-1].split(".")[0]

st.title('Team vs Team Analytics') 
st.write(
    """
    This demo shows two team's Regular Season ranking pitted against each other.

    """
)

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def getTeamNames():
# Get all the teams and their information
    return pd.DataFrame(teams.get_teams())['full_name']

def getAllTeamMetrics(season_selector):
    teamMetrics = teamestimatedmetrics.TeamEstimatedMetrics(league_id='00', season=season_selector, season_type='Regular Season')
    teamMetrics_df = teamMetrics.get_data_frames()[0]
    teamMetrics_df = teamMetrics_df.drop(['TEAM_ID'], axis=1)
    # teamMetrics_df.set_index(['TEAM_NAME'], inplace=True)
    return teamMetrics_df

def displayTeamVS(data, nba_team1, nba_team2):
    drop_cols = ['GP', 'MIN', 'W', 'L', 'GP_RANK', 'W_RANK', 'L_RANK', 'W_PCT_RANK', 'MIN_RANK', 'E_OFF_RATING_RANK', 'E_DEF_RATING_RANK',
       'E_NET_RATING_RANK', 'E_AST_RATIO_RANK', 'E_OREB_PCT_RANK',
       'E_DREB_PCT_RANK', 'E_REB_PCT_RANK', 'E_TM_TOV_PCT_RANK',
       'E_PACE_RANK']
    chart_data = data.loc[(data['TEAM_NAME'] == nba_team1) | (data['TEAM_NAME'] == nba_team2) , data.columns.drop(drop_cols)]
    # chart_data.reset_index().rename(columns={chart_data.index.name:'TEAM_NAME'})
    df = chart_data.melt(id_vars='TEAM_NAME', var_name='Columns', value_name='Values')
    # Normalize the values
    df['Normalized'] = df.groupby('Columns')['Values'].transform(lambda x: (x) / (x.max() + x.min()))
    df.rename(columns={'Columns':'Metric'}, inplace=True)
    # Create the chart
    colour_domain, colour_range = [nba_team1, nba_team2], [team_colors_dict[nba_team1], team_colors_dict[nba_team2]]
    colors = alt.Color('TEAM_NAME:N', scale=alt.Scale(domain=colour_domain, range=colour_range))


    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Normalized:Q', stack='normalize'),
        y=alt.Y('Metric:N'),
        # color=alt.Color('TEAM_NAME:N', scale=alt.Scale(scheme='category20')),
        color=colors,
        tooltip=['Metric', 'Values']
    ).properties(
        width=600,
        height=500
    )

    # Create the dotted line on the x-axis
    dotted_line = alt.Chart(pd.DataFrame({'x': [0.5]})).mark_rule(
        strokeDash=[3, 3],  # Set the strokeDash property to define the dotted pattern
        color='white'  # Set the color of the dotted line
    ).encode(
        x='x'  # Use the 'x' column to position the line horizontally on the x-axis
    )


    # Combine the bar chart and the dotted line
    combined_chart = alt.layer(chart, dotted_line)

    return combined_chart

try:
    season_selector = st.selectbox('Select Season', ['2022-23', '2021-22', '2020-21', '2019-20', '2018-19', '2017-18', '2008-09'],index = 0, key="team_vs_team_season")

    if not season_selector:
        st.error("Please select at least one season.")
    data = getAllTeamMetrics(season_selector)
    st.write("### Team Roster Statistics", data.sort_values("W", ascending=False).set_index("TEAM_NAME"))

    if len(data) > 0:
        st.download_button('Download Dataframe', convert_df(data), file_name='{}.csv'.format(fl_name), mime='text/csv', key="{}_download".format(fl_name))
    col1, col2 = st.columns(2)
    with col1:
        nba_team1 = st.selectbox(
            "Choose Team", getTeamNames(), index=1, key="team1"
        )

    with col2:
        nba_team2 = st.selectbox(
            "Choose Team", getTeamNames(), index=2, key="team2", 
        )

    if not col1:
        st.error("Please select at least one team for the First Team")
    elif not col2:
        st.error("Please select at least one team for the Second Team")
    else:
        chart = displayTeamVS(data, nba_team1, nba_team2)

        st.altair_chart(chart, use_container_width=True)
        # chart = alt.Chart(chart_data).mark_bar().encode(
        #     x=alt.X('NET_OFF_RATING:Q', stack='normalize'),
        #     y=alt.Y('TEAM_NAME:N'),
        #     color=alt.Color('TEAM_NAME:N', scale=alt.Scale(scheme='category20')),
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
