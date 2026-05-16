import pandas as pd

class GOAMRounds:
    """
    Stores all rounds (uploaded + manual) in memory.
    Tracks position history for position change calculations.
    """

    def __init__(self):
        self.rounds = []  # list of DataFrames
        self.position_history = {}  # {player_name: [position_per_course]}

    def add_round(self, df, course_name=None):
        """
        Add a round DataFrame.
        If course_name is provided, tag it.
        """
        df = df.copy()
        if course_name:  # only tag if provided
            df["Course"] = course_name
        self.rounds.append(df)

    def get_all_rounds(self):
        """
        Return a single DataFrame with all rounds combined.
        """
        if not self.rounds:
            return pd.DataFrame(columns=["Name", "Strokes", "IPS", "Course", "Team"])

        combined = pd.concat(self.rounds, ignore_index=True)

        if "Team" not in combined.columns:
            combined["Team"] = None

        return combined

    def update_position_history(self, ips_leaderboard):
        """
        Update position history from current IPS leaderboard.
        This tracks each player's rank after each course.
        """
        if ips_leaderboard.empty:
            return
        
        for idx, row in ips_leaderboard.iterrows():
            name = row["Name"]
            rank = row["Rank"]
            
            if name not in self.position_history:
                self.position_history[name] = []
            
            self.position_history[name].append(rank)

    def get_position_change(self, name):
        """
        Get position change for a player.
        Returns: +N (moved up), -N (moved down), or "–" (no change/first appearance)
        """
        if name not in self.position_history or len(self.position_history[name]) < 2:
            return "–"
        
        history = self.position_history[name]
        previous_pos = history[-2]  # Second to last position
        current_pos = history[-1]   # Last position
        
        change = previous_pos - current_pos  # Positive = moved up, negative = moved down
        
        if change == 0:
            return "–"
        elif change > 0:
            return f"+{change}"
        else:
            return str(change)
