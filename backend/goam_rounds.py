import pandas as pd

class GOAMRounds:
    """
    Stores all rounds (uploaded + manual) in memory.
    """

    def __init__(self):
        self.rounds = []  # list of DataFrames

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