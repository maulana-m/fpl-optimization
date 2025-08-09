import requests
import pandas as pd
from datetime import datetime


SUMMARY_URL = "https://fantasy.premierleague.com/api/bootstrap-static"


def get_summary_data():
	response = requests.get(SUMMARY_URL)
	if response.status_code != 200:
		return None

	data = response.json()

	players = pd.json_normalize(data["elements"])
	teams = pd.json_normalize(data["teams"])
	positions = pd.json_normalize(data["element_types"])

	teams_cols = [ "id", "code", "name", "short_name",
		"strength_overall_home", "strength_overall_away", "strength_attack_home",
		"strength_attack_away", "strength_defence_home", "strength_defence_away"
	]

	teams_ = teams[teams_cols]
	teams_ = teams.rename(columns={
	    "code": "team_code",
	    "name": "team_name"
	})

	players["name"] = players["first_name"] + " " + players["second_name"]
	players_cols = [
	    "id", "code", "element_type", "now_cost", "name", "team", "team_code", 
	    "goals_scored", "assists", "own_goals", "penalties_missed", "total_points",
	    "points_per_game"
	]
	players_ = players[players_cols]

	positions = positions[["singular_name_short", "id"]]
	positions = positions.rename(columns={
	    "id": "element_type",
	    "singular_name_short": "position"
	})

	all_players = pd.merge(players_, teams_[["team_code", "team_name"]], on="team_code")
	all_players = pd.merge(all_players, positions, on="element_type")
	all_players["now_cost"] = all_players["now_cost"]/10
	all_players["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	all_players.to_csv("all_players_fpl.csv", index=0)


if __name__ == "__main__":
	get_summary_data()
