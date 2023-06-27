print(__file__.split("\\")[-1].split(".")[0])

import matplotlib.pyplot as plt

# Net offensive ratings
warriors_rating = 120
celtics_rating = 100

# Set the team names
team_names = ['Golden State Warriors', 'Celtics']

# Set the colors for each team
team_colors = ['royalblue', 'green']

# Set up the figure and axis
fig, ax = plt.subplots()

# Set the x-axis limits
ax.set_xlim([0, warriors_rating + celtics_rating])

# Plot the bars
ax.barh([0], [warriors_rating], color=team_colors[0], height=0.2)
ax.barh([0], [celtics_rating], color=team_colors[1], height=0.2, left=warriors_rating)

# Customize the chart
ax.set_yticks([])
ax.invert_yaxis()  # Invert the y-axis

# Add team names at the ends
ax.text(0, 0, team_names[0], color='black', fontweight='bold', ha='right', va='center')
ax.text(warriors_rating + celtics_rating, 0, team_names[1], color='black', fontweight='bold', ha='left', va='center')

# Add net offensive ratings
# ax.text(0, 0, str(warriors_rating), color='white', fontweight='bold', ha='right', va='center')
# ax.text(warriors_rating + celtics_rating, 0, str(celtics_rating), color='white', fontweight='bold', ha='left', va='center')

# Add a title
ax.set_title('Net Offensive Ratings Comparison')

# Remove unnecessary spines
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Show the chart
plt.show()
