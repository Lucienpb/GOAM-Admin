import pandas as pd


class GOAMRounds:
    """
    Holds all rounds (uploaded + manual) in memory.
    """

    def __init__(self):
        self.rounds = []  # list of DataFrames

    def add_round(self, df, course_name):
        """
        Add a round DataFrame and tag it with the course name.
        df must contain: Name, Strokes, IPS
        """
        df = df.copy()
        df["Course"] = course_name
        self.rounds.append(df)

    def get_all_rounds(self):
        """
        Return a single DataFrame with all rounds combined.
        Columns: Name, Strokes, IPS, Course, (optional) Team
        """
        if not self.rounds:
            return pd.DataFrame(columns=["Name", "Strokes", "IPS", "Course", "Team"])

        combined = pd.concat(self.rounds, ignore_index=True)

        # Ensure Team column exists
        if "Team" not in combined.columns:
            combined["Team"] = None

        return combined
