import pandas as pd

class GOAMRounds:

    def __init__(self):
        self.rounds = []  # list of DataFrames

    def add_round(self, df, course_name=None):
        """Add a round with optional course tagging."""
        if course_name:
            df["Course"] = course_name
        self.rounds.append(df)

    def load_season(self, season_dict):
        """Load all sheets from a season file."""
        for name, df in season_dict.items():
            df["Course"] = name
            self.rounds.append(df)

    def get_all_rounds(self):
        """Return concatenated DataFrame of all rounds."""
        if not self.rounds:
            return pd.DataFrame()
        return pd.concat(self.rounds, ignore_index=True)
