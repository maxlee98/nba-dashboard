import streamlit as st

st.set_page_config(
    page_title="NBA Analytics",
    page_icon="🏀",
)

st.write("# Welcome to NBA Analytics! 🏀")

# st.sidebar.success("Select a demo above.")
st.warning("Do let each page finish loading prior to switching onto other pages")

st.markdown(
    """
    The NBA Analytics App was built specifically for enthusiasts to 
    better understand each team's and players' performance across the various
    games or seasons. \n
    Click on the side bar to begin exploring!
    ## Pages Available
    - Team Demo
        - Allows you to understand each player's impact on the team's performance
    - Player Demo
        - Allows you to compare between Two Player's Performance. (Includes a Shot Chart)
    - Defense Player
        - Allows you to understand a player's defensive capabilities against an offensive player
    - Defense Team
        - Allows you to understand a team's defensive capabilities against a player

    """    

)

st.info("This dashboard is still under-development and may experience performance issues.  If there are any issues with regards to loading a page, do reload the page.")


st.markdown(
    """

    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)