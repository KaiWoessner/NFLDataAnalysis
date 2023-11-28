# NFL Data
import nfl_data_py as nfl

# Imports
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# TKinter
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def plot_graph(tm1, tm2, year):

    tm1 = tm1.upper()
    tm2 = tm2.upper()
    years = int(year)

    game_ids = []
    rev_game_ids = []
    for wk in range(1,23):
        print("wk")
        if (wk < 10):
            game_ids.append(f"{year}_0{wk}_{tm1}_{tm2}")
            rev_game_ids.append(f"{year}_0{wk}_{tm2}_{tm1}")

        else:
            game_ids.append(f"{year}_{wk}_{tm1}_{tm2}")
            rev_game_ids.append(f"{year}_{wk}_{tm2}_{tm1}")

    print("HERE2223")
    print(years)
    game = nfl.import_pbp_data([years])
    print(game)

    #pd.set_option('display.max_columns', None)
    gm_stats = game[["game_id", "posteam","play_type", "drive", "qtr", "time", "yardline_100", "ydsnet", "drive_end_transition", "home_score", "away_score"]]

    actual_game = gm_stats[gm_stats["game_id"] == game_ids[0]]

    game_count = 0

    for i in range(0, len(game_ids)):
        print("12")
        temp_game = gm_stats[gm_stats["game_id"] == game_ids[i]]
        if (len(temp_game) != 0):
            actual_game = temp_game
            wk = i+1

            game_count += 1
            div1_wk = i+1
            div1 = game_ids[i]

            home = tm2

        temp_game = gm_stats[gm_stats["game_id"] == rev_game_ids[i]]
        if (len(temp_game) != 0):
            actual_game = temp_game
            wk = i+1

            game_count += 1
            div2_wk = i+1
            div2 = rev_game_ids[i]

            home = tm1

    if ((game_count > 1) & (wk > 18)):
        playoff_choice = input("Those teams played in the regular season and the playoffs. Do you want the playoff game (type 1) or regular season game (type 2): ")
        if (playoff_choice == "1"):
            actual_game = gm_stats[gm_stats["game_id"] == f"{div1}"]

        if (playoff_choice == "2"):
            actual_game = gm_stats[gm_stats["game_id"] == f"{div2}"]
            if (game_count == 3):
                
                # DIVISIONAL
                game_choice = input("Those teams are divisonal opponents and played twice in the regular season. Choose Matchup: Week " + f"{div1_wk}" + "(type 1)" + " or Week " + f"{div2_wk}" + "(type 2): ")
                if (game_choice == "1"):
                    actual_game = gm_stats[gm_stats["game_id"] == f"{div1}"]
                    wk = div1_wk
                    home = tm2
                if (game_choice == "2"):
                    actual_game = gm_stats[gm_stats["game_id"] == f"{div2}"]
                    wk = div2_wk
                    home = tm1
                
        elif (game_count == 2):
            
            # DIVISIONAL
            game_choice = input("Those teams are divisonal opponents and played twice in the regular season. Choose Matchup: Week " + f"{div1_wk}" + "(type 1)" + " or Week " + f"{div2_wk}" + "(type 2): ")
            if (game_choice == "1"):
                actual_game = gm_stats[gm_stats["game_id"] == f"{div1}"]
                wk = div1_wk
                home = tm2
            if (game_choice == "2"):
                actual_game = gm_stats[gm_stats["game_id"] == f"{div2}"]
                wk = div2_wk
                home = tm1

    actual_game = actual_game[actual_game['play_type'] != "kickoff"]
    actual_game = actual_game[actual_game['play_type'] != "extra_point"]

    actual_game = actual_game.sort_values(by = ["qtr","time"], ascending = [True, False]).reset_index(drop = True)

    drive_start = actual_game.groupby('drive').first().reset_index()
    drive_end = actual_game.groupby('drive').last().reset_index()

    drive = pd.merge(drive_start, drive_end, on=['drive'])
    print("HERE11111")
    drive = drive.rename(columns={'qtr_x': 'qtr',
    'posteam_x': 'posteam',
    'yardline_100_y': 'yardline_end',
    'yardline_100_x': 'yardline_start',
    'drive_end_transition_x': 'drive_result',
    'home_score_x' : 'home_score',
    'away_score_x' : 'away_score'})

    drive_final = drive[["drive", "posteam", "qtr", "yardline_start", "yardline_end", "drive_result", "home_score", "away_score"]]

    drive_final.loc[drive_final['drive_result'] == "TOUCHDOWN", ['yardline_end']] = 0

    qtr_drive = drive_final.groupby('qtr').last().reset_index()


    teamcolor = {'ARI':'#97233F','ATL':'#A71930','BAL':'#241773','BUF':'#00338D','CAR':'#0085CA','CHI':'#00143F',
            'CIN':'#FB4F14','CLE':'#FB4F14','DAL':'#B0B7BC','DEN':'#002244','DET':'#046EB4','GB':'#24423C',
            'HOU':'#C9243F','IND':'#003D79','JAX':'#136677','KC':'#CA2430','LA':'#002147','LAC':'#2072BA', 'SD':'#2072BA',
            'LV':'#C4C9CC','MIA':'#0091A0','MIN':'#4F2E84','NE':'#0A2342','NO':'#A08A58','NYG':'#192E6C',
            'NYJ':'#203731','PHI':'#014A53','PIT':'#FFC20E','SEA':'#7AC142','SF':'#C9243F','TB':'#D40909',
            'TEN':'#4095D1','WAS':'#FFC20F'}

    tm_colors = [teamcolor.get(team) for team in drive_final["posteam"]]

    # Create a figure and axis
    fig = Figure(figsize=(12, 4.5))
    ax = fig.add_subplot(1,1,1)

    field_width = (len(drive_final["drive"])) * 4 - 4
    field_length = 100

    # Set the background color to green
    if (len(qtr_drive["drive"]) == 5):
        ax.add_patch(patches.Rectangle((0, -8), 100, qtr_drive["drive"][0]*4+6, color="green", alpha=0.25, zorder=2))
        ax.add_patch(patches.Rectangle((0, qtr_drive["drive"][0]*4-2), 100, (qtr_drive["drive"][1]*4 - qtr_drive["drive"][0]*4), color="green", alpha=0.4, zorder=2))
        ax.add_patch(patches.Rectangle((0, qtr_drive["drive"][1]*4-2), 100, (qtr_drive["drive"][2]*4 - qtr_drive["drive"][1]*4), color="green", alpha=0.55, zorder=2))
        ax.add_patch(patches.Rectangle((0, qtr_drive["drive"][2]*4-2), 100, (qtr_drive["drive"][3]*4 - qtr_drive["drive"][2]*4), color="green", alpha=0.7, zorder=2))
        ax.add_patch(patches.Rectangle((0, qtr_drive["drive"][3]*4-2), 100, qtr_drive["drive"][4]*4+8, color="green", alpha=0.85, zorder=2))

    else:
        ax.add_patch(patches.Rectangle((0, -8), 100, qtr_drive["drive"][0]*4+6, color="green", alpha=0.25, zorder=2))
        ax.add_patch(patches.Rectangle((0, qtr_drive["drive"][0]*4-2), 100, (qtr_drive["drive"][1]*4 - qtr_drive["drive"][0]*4), color="green", alpha=0.4, zorder=2))
        ax.add_patch(patches.Rectangle((0, qtr_drive["drive"][1]*4-2), 100, (qtr_drive["drive"][2]*4 - qtr_drive["drive"][1]*4), color="green", alpha=0.55, zorder=2))
        ax.add_patch(patches.Rectangle((0, qtr_drive["drive"][2]*4-2), 100, qtr_drive["drive"][3]*4+8, color="green", alpha=0.7, zorder=2))

    # Plot the field
    # plt.xlim(0, field_length + 10)
    # plt.ylim(-8, field_width + 8)
    
    ax.set_xlim(0, field_length + 10)
    ax.set_ylim(-8, field_width + 8)

    # Bar height variable
    height = 3.5

    # Creates Bars
    for i in range(len(drive_final["drive"])):
        if drive_final["qtr"][i] % 2 != 0:

            if (drive_final["posteam"][i] == tm1):
                ax.barh(4*i, drive_final["yardline_end"][i]  -  drive_final["yardline_start"][i], left=drive_final["yardline_start"][i], height=height, color=tm_colors[i], zorder = 10)

            if (drive_final["posteam"][i] == tm2):
                ax.barh(4*i, drive_final["yardline_start"][i] -  drive_final["yardline_end"][i], left=(100-drive_final["yardline_start"][i]), height=height, color=tm_colors[i], zorder = 10)

        if drive_final["qtr"][i] % 2 == 0:

            if (drive_final["posteam"][i] == tm1):
                ax.barh(4*i, drive_final["yardline_start"][i] -  drive_final["yardline_end"][i], left=(100-drive_final["yardline_start"][i]), height=height, color=tm_colors[i], zorder = 10)

            if (drive_final["posteam"][i] == tm2):
                ax.barh(4*i, drive_final["yardline_end"][i] -  drive_final["yardline_start"][i], left=drive_final["yardline_start"][i], height=height, color=tm_colors[i], zorder = 10)

    cap_width = 0.5

    # Start Lines
    for i in range(len(drive_final["drive"])):
        bottom = 4 * i - 2 + 0.5

        if drive_final["qtr"][i] % 2 != 0:
            if (drive_final["posteam"][i] == tm1):
                ax.add_patch(patches.Rectangle((drive_final["yardline_start"][i], bottom), cap_width, height, color="0.95", zorder = 20))

            if (drive_final["posteam"][i] == tm2):
                ax.add_patch(patches.Rectangle((100-drive_final["yardline_start"][i], bottom), cap_width, height, color="0.95", zorder = 20))

        if drive_final["qtr"][i] % 2 == 0:

            if (drive_final["posteam"][i] == tm1):
                ax.add_patch(patches.Rectangle((100-drive_final["yardline_start"][i], bottom), cap_width, height, color="0.95", zorder = 20))

            if (drive_final["posteam"][i] == tm2):
                ax.add_patch(patches.Rectangle((drive_final["yardline_start"][i], bottom), cap_width, height, color="0.95", zorder = 20))
    print("HEREsdasd")
    # Scoring
    for i in range(len(drive_final["drive"])):
        bottom = 4 * i - 2 + 0.5

        if (drive_final["drive_result"][i] == "TOUCHDOWN"):
            if drive_final["qtr"][i] % 2 != 0:
                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((0, bottom), cap_width, height, color="orange", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((99.5, bottom), cap_width, height, color="orange", zorder = 25))

            if drive_final["qtr"][i] % 2 == 0:

                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((99.5, bottom), cap_width, height, color="orange", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((0, bottom), cap_width, height, color="orange", zorder = 25))

        if (drive_final["drive_result"][i] == "FIELD_GOAL"):
            if drive_final["qtr"][i] % 2 != 0:
                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((drive_final["yardline_end"][i], bottom), cap_width, height, color="gold", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((100-drive_final["yardline_end"][i], bottom), cap_width, height, color="gold", zorder = 25))

            if drive_final["qtr"][i] % 2 == 0:

                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((100-drive_final["yardline_end"][i], bottom), cap_width, height, color="gold", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((drive_final["yardline_end"][i], bottom), cap_width, height, color="gold", zorder = 25))

        if (drive_final["drive_result"][i] == "PUNT"):

            if drive_final["qtr"][i] % 2 != 0:
                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((drive_final["yardline_end"][i], bottom), cap_width, height, color="brown", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((100-drive_final["yardline_end"][i], bottom), cap_width, height, color="brown", zorder = 25))

            if drive_final["qtr"][i] % 2 == 0:

                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((100-drive_final["yardline_end"][i], bottom), cap_width, height, color="brown", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((drive_final["yardline_end"][i], bottom), cap_width, height, color="brown", zorder = 25))

        if (drive_final["drive_result"][i] in ["INTERCEPTION", "FUMBLE"]):

            if drive_final["qtr"][i] % 2 != 0:
                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((drive_final["yardline_end"][i], bottom), cap_width, height, color="b", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((100-drive_final["yardline_end"][i], bottom), cap_width, height, color="b", zorder = 25))

            if drive_final["qtr"][i] % 2 == 0:

                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((100-drive_final["yardline_end"][i], bottom), cap_width, height, color="b", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((drive_final["yardline_end"][i], bottom), cap_width, height, color="b", zorder = 25))

        if (drive_final["drive_result"][i] == "DOWNS"):

            if drive_final["qtr"][i] % 2 != 0:

                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((drive_final["yardline_end"][i], bottom), cap_width, height, color="purple", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((100 - drive_final["yardline_end"][i], bottom), cap_width, height, color="purple", zorder = 25))

            if drive_final["qtr"][i] % 2 == 0:

                if (drive_final["posteam"][i] == tm1):
                    ax.add_patch(patches.Rectangle((100 - drive_final["yardline_end"][i], bottom), cap_width, height, color="purple", zorder = 25))

                if (drive_final["posteam"][i] == tm2):
                    ax.add_patch(patches.Rectangle((drive_final["yardline_end"][i], bottom), cap_width, height, color="purple", zorder = 25))

    # Yard lines
    for i in range(11):
        line =10 * i
        ax.axvline(line, color='k', linewidth = 2, zorder = 9)

    # Yard lines Numbers
    count = 1
    for i in range(10, 51, 10):
        ax.text(i, -6.5, str(count), fontsize=14, color='k', ha='right')
        ax.text(100-i, -6.5, str(count), fontsize=14, color='k', ha='right')

        ax.text(i, field_width+3, str(count), fontsize=14, color='k', ha='right')
        ax.text(100-i, field_width+3, str(count), fontsize=14, color='k', ha='right')

        count += 1


    for i in range(10, 100, 10):
        ax.text(i, -6.5, str(0), fontsize=14, color='k', ha='left')
        ax.text(i, field_width+3, str(0), fontsize=14, color='k', ha='left')


    # Title
    ax.set_title(tm1 + " vs " + tm2 + " Week " + str(wk) + " " + year, fontsize=14, weight = "bold")

    # LEGENDS
    
    print("HERE")
    fontsize = 10
    
    # Quarters
    if (len(qtr_drive["drive"]) == 5):
        ot = patches.Patch(color='green', alpha = 0.85, label='OT Qtr')
        fourth = patches.Patch(color='green', alpha = 0.7, label='4th Qtr')
        third = patches.Patch(color='green', alpha = 0.55, label='3rd Qtr')
        second = patches.Patch(color='green', alpha = 0.4, label='2nd Qtr')
        first = patches.Patch(color='green', alpha = 0.25, label='1st Qtr')
        quarter = ax.legend(handles=[ot, fourth, third, second, first], loc='center right', prop={'size': fontsize})
        quarter.set_title('Quarter', prop={'size': fontsize})
        ax.add_artist(quarter)

    else:
        fourth = patches.Patch(color='green', alpha = 0.7, label='4th Qtr')
        third = patches.Patch(color='green', alpha = 0.55, label='3rd Qtr')
        second = patches.Patch(color='green', alpha = 0.4, label='2nd Qtr')
        first = patches.Patch(color='green', alpha = 0.25, label='1st Qtr')
        quarter = ax.legend(handles=[fourth, third, second, first], loc='center right', prop={'size': fontsize})
        quarter.set_title('Quarter', prop={'size': fontsize})
        ax.add_artist(quarter)

    # Matchup
    team1_color = teamcolor.get(tm1)
    team2_color = teamcolor.get(tm2)

    team1 = patches.Patch(color=team1_color, label=f"{tm1}     ")
    team2 = patches.Patch(color=team2_color, label=f"{tm2}     ")
    matchup = ax.legend(handles=[team1, team2], bbox_to_anchor=(1, 0.82), loc='upper right', prop={'size': fontsize})
    matchup.set_title('Matchup', prop={'size': fontsize})
    ax.add_artist(matchup)

    # Results
    drive_start = patches.Patch(color='0.95', label='Start')
    punt = patches.Patch(color='brown', label='Punt')
    to = patches.Patch(color='b', label='TO')
    to_on_downs = patches.Patch(color='purple', label='Downs')
    field_goal = patches.Patch(color='gold', label='FG')
    touchdown = patches.Patch(color='orange', label='TD')

    markers = ax.legend(handles=[drive_start, punt, to, to_on_downs, field_goal, touchdown], loc='lower right', prop={'size': fontsize})
    markers.set_title('Results', prop={'size': fontsize})
    ax.add_artist(markers)

    # Final Score
    if (tm1 == home):
        ax.text(105, field_width - 1, "Final Score", fontsize=fontsize, color="k", ha='center', va='center')
        ax.text(103, field_width - 6, str(drive_final["home_score"][0]), fontsize=fontsize+1, color=team1_color, ha='center', va='center')
        ax.text(107, field_width - 6, str(drive_final["away_score"][0]), fontsize=fontsize+1, color=team2_color, ha='center', va='center')
        ax.text(105, field_width - 6, " - ", fontsize=fontsize+1, color="k", ha='center', va='center')

    else:
        ax.text(105, field_width - 1, "Final Score", fontsize=fontsize, color="k", ha='center', va='center')
        ax.text(103, field_width - 6, str(drive_final["away_score"][0]), fontsize=fontsize+1, color=team1_color, ha='center', va='center')
        ax.text(107, field_width - 6, str(drive_final["home_score"][0]), fontsize=fontsize+1, color=team2_color, ha='center', va='center')
        ax.text(105, field_width - 6, " - ", fontsize=fontsize+1, color="k", ha='center', va='center')

    # Border
    border_rect = patches.Rectangle((0, -8), 110, field_width + 16, linewidth=3, edgecolor='black', facecolor='none', zorder=30)
    ax.add_patch(border_rect)

    # Remove x and y ticks
    ax.set_axis_off()
    
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    # Hide the entry widgets and button
    entry1_label.grid_forget()
    entry1.grid_forget()
    entry2_label.grid_forget()
    entry2.grid_forget()
    entry3_label.grid_forget()
    entry3.grid_forget()
    button1.grid_forget()

    # Show the "Return" button
    button2.grid(row=3, column=0, columnspan=2, pady=10)


def return_click():
    # Show the entry widgets and "Plot Graph" button
    entry1_label.grid(row=0, column=0, padx=10, pady=10)
    entry1.grid(row=0, column=1, padx=10, pady=10)
    entry2_label.grid(row=1, column=0, padx=10, pady=10)
    entry2.grid(row=1, column=1, padx=10, pady=10)
    entry3_label.grid(row=2, column=0, padx=10, pady=10)
    entry3.grid(row=2, column=1, padx=10, pady=10)
    button1.grid(row=3, column=0, columnspan=2, pady=10)

    # Hide the "Return" button
    button2.grid_forget()

    # Clear the graph
    for widget in graph_frame.winfo_children():
        widget.destroy()

# Create the main Tkinter window
root = tk.Tk()
root.title("NFL Game Visualizer")

# Create and place entry widgets
entry1_label = ttk.Label(root, text="Team 1")
entry1_label.grid(row=0, column=0, padx=10, pady=10)
entry1 = ttk.Entry(root)
entry1.grid(row=0, column=1, padx=10, pady=10)

entry2_label = ttk.Label(root, text="Team 2")
entry2_label.grid(row=1, column=0, padx=10, pady=10)
entry2 = ttk.Entry(root)
entry2.grid(row=1, column=1, padx=10, pady=10)

entry3_label = ttk.Label(root, text="Year")
entry3_label.grid(row=2, column=0, padx=10, pady=10)
entry3 = ttk.Entry(root)
entry3.grid(row=2, column=1, padx=10, pady=10)

# Create and place the "Plot Graph" button
button1 = ttk.Button(root, text="Plot Game", command=lambda: plot_graph(entry1.get(), entry2.get(), entry3.get()))
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