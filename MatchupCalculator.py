# NFL Data Import
import nfl_data_py as nfl

# Imports
from math import pi
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
from math import pi
import urllib

# TKinter
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

stats = nfl.import_pbp_data([2023])

# Copy data
new_stats = stats.copy()

# Create Defensive EPA
new_stats['def_epa'] = -stats['epa']

stats = new_stats

# Filter Garbage Time
stats = stats[(stats["wp"] > .25) & (stats["wp"] < .975)]

#REDZONE
redzone = stats[stats["drive_inside20"] == 1.0]
redzone_td = redzone[redzone["touchdown"] == 1.0]

redzone_drives = redzone.groupby("posteam")["drive_real_start_time"].nunique().reset_index()
redzone_tds = redzone_td.groupby("posteam")["touchdown"].size().reset_index()

redzone_tds["redzone_eff"] = redzone_tds["touchdown"] / redzone_drives["drive_real_start_time"] * 100

redzone_tds["redzone_eff_rank"] = redzone_tds["redzone_eff"].rank(method="max", ascending=True).astype(int)
redzone_tds = redzone_tds.sort_values("redzone_eff_rank", ascending=False).reset_index(drop = True)

redzone_tds = redzone_tds.rename(columns={"posteam": "team"})

passing = stats[stats["play_type"] == "pass"]
rushing = stats[stats["play_type"] == "run"]

# OFFENSE
passing_total = passing.groupby("posteam").size().reset_index(name = "pass_plays")
off_passing = passing.groupby("posteam")["epa"].sum().reset_index()

off_passing["off_passing_epa"] = off_passing["epa"] / passing_total["pass_plays"]

rushing_total = rushing.groupby("posteam").size().reset_index(name = "run_plays")
off_rushing = rushing.groupby("posteam")["epa"].sum().reset_index()

off_rushing["off_rush_epa"] = off_rushing["epa"] / rushing_total["run_plays"]


off_passing["off_passing_rank"] = off_passing["off_passing_epa"].rank(method="max", ascending=True).astype(int)
off_passing = off_passing.sort_values("off_passing_rank", ascending=False).reset_index(drop = True)

off_rushing["off_rushing_rank"] = off_rushing["off_rush_epa"].rank(method="max", ascending=True).astype(int)
off_rushing = off_rushing.sort_values("off_rushing_rank", ascending=False).reset_index(drop = True)

off_passing = off_passing.rename(columns={"posteam": "team"})
off_rushing = off_rushing.rename(columns={"posteam": "team"})

# DEFENSE
passing_total = passing.groupby("defteam").size().reset_index(name = "pass_plays")
def_passing = passing.groupby("defteam")["def_epa"].sum().reset_index()

def_passing["def_passing_epa"] = def_passing["def_epa"] / passing_total["pass_plays"]

rushing_total = rushing.groupby("defteam").size().reset_index(name = "run_plays")
def_rushing = rushing.groupby("defteam")["def_epa"].sum().reset_index()

def_rushing["def_rush_epa"] = def_rushing["def_epa"] / rushing_total["run_plays"]

def_passing["def_passing_rank"] = def_passing["def_passing_epa"].rank(method="max", ascending=True).astype(int)
def_passing = def_passing.sort_values("def_passing_rank", ascending=False).reset_index(drop = True)

def_rushing["def_rushing_rank"] = def_rushing["def_rush_epa"].rank(method="max", ascending=True).astype(int)
def_rushing = def_rushing.sort_values("def_rushing_rank", ascending=False).reset_index(drop = True)

def_passing = def_passing.rename(columns={"defteam": "team"})
def_rushing = def_rushing.rename(columns={"defteam": "team"})

# SUCCESS (Not Used)
passing = stats[stats["play_type"] == "pass"]
rushing = stats[stats["play_type"] == "run"]

passing_total = passing.groupby("posteam").size().reset_index(name = "pass_plays")
pass_success = passing.groupby("posteam")["success"].sum().reset_index()

pass_success["pass_success_percent"] = pass_success["success"] / passing_total["pass_plays"] * 100

rushing_total = rushing.groupby("posteam").size().reset_index(name = "run_plays")
rushing_success = rushing.groupby("posteam")["success"].sum().reset_index()

rushing_success["rush_success_percent"] = rushing_success["success"] / rushing_total["run_plays"] * 100

pass_success["pass_success_rank"] = pass_success["pass_success_percent"].rank(method="max", ascending=True).astype(int)
pass_success = pass_success.sort_values("pass_success_rank", ascending=False).reset_index(drop = True)

rushing_success["rush_success_rank"] = rushing_success["rush_success_percent"].rank(method="max", ascending=True).astype(int)
rushing_success = rushing_success.sort_values("rush_success_rank", ascending=False).reset_index(drop = True)

pass_success = pass_success.rename(columns={"posteam": "team"})
rushing_success = rushing_success.rename(columns={"posteam": "team"})

#TURNOVERS (Not used)
off_fumble = stats.groupby("posteam")["fumble_lost"].sum().reset_index()
off_int = stats.groupby("posteam")["interception"].sum().reset_index()

def_fumble = stats.groupby("defteam")["fumble_lost"].sum().reset_index()
def_int = stats.groupby("defteam")["interception"].sum().reset_index()

turnovers = pd.DataFrame(off_fumble["posteam"])
turnovers["turnover_diff"] = (def_fumble["fumble_lost"] + def_int["interception"]) - (off_fumble["fumble_lost"] + off_int["interception"])

turnovers["turnover_rank"] = turnovers["turnover_diff"].rank(method="max", ascending=True).astype(int)
turnovers = turnovers.sort_values("turnover_rank", ascending=False).reset_index(drop = True)

turnovers = turnovers.rename(columns={"posteam": "team"})

# Merge rank dataframes
column1 = off_passing
data_frames = [off_rushing, def_passing, def_rushing, turnovers, redzone_tds]

for columns in data_frames:
    column1 = pd.merge(column1, columns, on='team', how='left')

fin_ranks = column1[["team", "off_passing_rank","off_rushing_rank", "def_passing_rank", "def_rushing_rank", "redzone_eff_rank"]]



def plot_graph(inp1, inp2):
    
  inp1 = inp1.upper()
  inp2 = inp2.upper()
    
  matchup = fin_ranks[fin_ranks["team"].isin([inp1, inp2])]

  # Team
  team = nfl.import_team_desc()

  tm1_info = team[team["team_abbr"] == matchup["team"].values[0]]
  tm2_info = team[team["team_abbr"] == matchup["team"].values[1]]

  team_cols = []
  team_cols.append(tm1_info["team_color"].values[0])
  team_cols.append(tm2_info["team_color"].values[0])


  categories = ["off_passing_rank", "off_rushing_rank", "def_passing_rank", "def_rushing_rank", "redzone_eff_rank"]
  data = matchup.loc[:, categories].values

  first_column = data[:, 0]

  # Append the first column to the end
  data = np.hstack((data, first_column.reshape(-1, 1)))

  category_count = len(list(matchup.columns[1:]))

  labels = ['OFF Passing', 'OFF Rushing', 'DEF Passing', 'DEF Rushing', "Redzone Eff"]

  # Create a list of angles for each category
  start_angle = np.pi / 2

  angles = [start_angle + n / float(category_count) * 2 * np.pi for n in range(category_count)]
  angles += angles[:1]


  # Make the plot
  fig, ax = plt.subplots(figsize=(7,4), subplot_kw=dict(polar=True))


  # Plot the data
  for i in range(len(data)):
    ax.fill(angles, data[i], color=team_cols[i], alpha=0.25)
    
  # Add labels
  label_radius = 20
  fsize = 12
  
  for i in range(5):
    angle = 2 * np.pi / 5 * i + np.pi/2
    ax.text(angle, label_radius, labels[i], ha='center', va='center', fontsize = fsize-5, weight = "heavy")

  x = np.pi / 2
  pen_coords = [
      (x, 32),
      (2 * np.pi / 5 + x, 32),
      ( 4*np.pi / 5 + x, 32),
      (6 * np.pi / 5 + x, 32),
      (8 * np.pi / 5 + x, 32)
  ]

  # Add lines connecting the vertices of the hex
  for i in range(len(pen_coords) - 1):
      x1, y1 = pen_coords[i]
      x2, y2 = pen_coords[i + 1]
      ax.plot([x1, x2], [y1, y2], color='k', linewidth=3)

  # Connect the last point to the first point
  x1, y1 = pen_coords[-1]
  x2, y2 = pen_coords[0]
  ax.plot([x1, x2], [y1, y2], color='k', linewidth=3)

  # Set axes
  ax.yaxis.grid(True, linestyle='-', alpha=0.0, color='none')
  ax.xaxis.grid(True, linestyle='-', alpha=0.0, color='none')
  ax.spines['polar'].set_visible(False)
  plt.ylim(0, 40)
  ax.set_yticks(np.arange(0, 40, 2))
  ax.set_yticklabels([])
  ax.set_xticklabels([])

  # Create cartesian axes
  ax2 = plt.axes([0, 0, 1, 1], frameon=False, polar=False)
  ax2.set_xlim(0,100)
  ax2.set_ylim(0,100)
  ax2.set_yticks([])
  ax2.set_xticks([])

  # Box
  rect = patches.Rectangle((18, 20), 64,65, linewidth=1, edgecolor='black', facecolor='none')
  ax2.add_patch(rect)

  # Logo
  tm1_logo_url = tm1_info["team_logo_espn"].values[0]
  tm2_logo_url = tm2_info["team_logo_espn"].values[0]

  tm1_logo_img = Image.open(urllib.request.urlopen(tm1_logo_url))
  tm2_logo_img = Image.open(urllib.request.urlopen(tm2_logo_url))

  ax2.imshow(tm1_logo_img, extent=(18, 33, 53, 83), aspect='auto')
  ax2.imshow(tm2_logo_img, extent=(67, 82, 53, 83), aspect='auto')

  ax2.text(26.5, 50, tm1_info["team_nick"].values[0], ha='center', va='center', fontsize = fsize-3, weight = "bold", color=team_cols[0])
  ax2.text(73.5, 50, tm2_info["team_nick"].values[0], ha='center', va='center', fontsize = fsize-3, weight = "bold", color=team_cols[1])

  # Title
  ax2.text(50, 88, "Team Matchup Comparisons 2023", ha='center', va='center', fontsize = fsize+4, weight = "bold")

  # Physical data
  tm1_ranks = matchup.iloc[0]
  height = 45
  i = 0
  for column_name, column_data, in tm1_ranks.items():
    if column_name == "team":
      continue
    ax2.text(26.5, height, f'{labels[i]}' + " : " + f'{abs(33 - column_data)}', ha='center', va='center', fontsize = fsize-4)
    height -= 4
    i += 1

  tm2_ranks = matchup.iloc[1]
  height = 45
  i = 0
  for column_name, column_data, in tm2_ranks.items():
    if column_name == "team":
      continue
    ax2.text(73.5, height, f'{labels[i]}' + " : " + f'{abs(33 - column_data)}', ha='center', va='center', fontsize = fsize-4)
    height -= 4
    i += 1

  canvas = FigureCanvasTkAgg(fig, master=graph_frame)
  canvas.draw()
  canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
  # Hide the entry widgets and button
  entry1_label.grid_forget()
  entry1.grid_forget()
  entry2_label.grid_forget()
  entry2.grid_forget()
  button1.grid_forget()

  # Show the "Return" button
  button2.grid(row=3, column=0, columnspan=2, pady=10)


def return_click():
    # Show the entry widgets and "Plot Graph" button
    entry1_label.grid(row=0, column=0, padx=10, pady=10)
    entry1.grid(row=0, column=1, padx=10, pady=10)
    entry2_label.grid(row=1, column=0, padx=10, pady=10)
    entry2.grid(row=1, column=1, padx=10, pady=10)
    button1.grid(row=3, column=0, columnspan=2, pady=10)

    # Hide the "Return" button
    button2.grid_forget()

    # Clear the graph
    for widget in graph_frame.winfo_children():
        widget.destroy()

# Create the main Tkinter window
root = tk.Tk()
root.title("NFL Matchup Calculator")

# Create and place entry widgets
entry1_label = ttk.Label(root, text="Team 1")
entry1_label.grid(row=0, column=0, padx=10, pady=10)
entry1 = ttk.Entry(root)
entry1.grid(row=0, column=1, padx=10, pady=10)

entry2_label = ttk.Label(root, text="Team 2")
entry2_label.grid(row=1, column=0, padx=10, pady=10)
entry2 = ttk.Entry(root)
entry2.grid(row=1, column=1, padx=10, pady=10)

# Create and place the "Plot Graph" button
button1 = ttk.Button(root, text="Plot Matchup", command=lambda: plot_graph(entry1.get(), entry2.get()))
button1.grid(row=3, column=0, columnspan=2, pady=10)

# Create and place the "Return" button (initially hidden)
button2 = ttk.Button(root, text="Return", command=return_click)
button2.grid(row=3, column=0, columnspan=2, pady=10)
button2.grid_forget()

# Create a new frame for the graph within the main window
graph_frame = ttk.Frame(root)
graph_frame.grid(row=4, column=0, columnspan=2, pady=10)

# Start the Tkinter event loop
root.mainloop()