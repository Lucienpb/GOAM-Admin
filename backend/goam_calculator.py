import pandas as pd

class GOAMCalculator:

    @staticmethod
    def calculate_player_stats(df):
        """Aggregate strokes + IPS per player across all rounds."""
        if df.empty:
            return pd.DataFrame()

        grouped = df.groupby("Name").agg({
            "Strokes": "mean",
            "IPS": "mean",
            "Course": "count"
        }).reset_index()

        grouped.rename(columns={"Course": "Games Played"}, inplace=True)
        grouped["IPS"] = grouped["IPS"].round(1)
        grouped["Strokes"] = grouped["Strokes"].round(1)

        return grouped.sort_values("IPS", ascending=False)

    @staticmethod
    def calculate_liv(df, team_map):
        """Calculate LIV totals using top 3 IPS per team per course."""
        if df.empty:
            return pd.DataFrame()

        df["Team"] = df["Name"].map(team_map)

        results = []

        for course in df["Course"].unique():
            course_df = df[df["Course"] == course]

            for team in course_df["Team"].unique():
                team_df = course_df[course_df["Team"] == team]
                top3 = team_df.nlargest(3, "IPS")["IPS"].sum()

                results.append({
                    "Team": team,
                    "Course": course,
                    "LIV Points": top3
                })

        return pd.DataFrame(results)