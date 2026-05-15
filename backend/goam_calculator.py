import pandas as pd
from datetime import datetime

class GOAMCalculator:
    """
    Performs all GOAM calculations:
    - IPS best six
    - Strokes best six (over par)
    - LIV team scores
    - Splitting by course
    """

    PAR = 72

    @staticmethod
    def build_from_course_sheets(sheets_dict):
        """
        Build long-format DataFrame from course sheets.
        Only sheets with {Name, Strokes, IPS} are treated as course sheets.
        """
        rows = []

        for sheet_name, df in sheets_dict.items():
            if not {"Name", "Strokes", "IPS"}.issubset(df.columns):
                continue

            for _, row in df.iterrows():
                rows.append({
                    "Name": row["Name"],
                    "Course": sheet_name,
                    "Strokes": row["Strokes"],
                    "IPS": row["IPS"],
                    "Team": row["LIV"] if "LIV" in df.columns else None
                })

        if not rows:
            return pd.DataFrame(columns=["Name", "Course", "Strokes", "IPS", "Team"])

        return pd.DataFrame(rows)

    @staticmethod
    def calculate_best_six_ips(df):
        """
        IPS leaderboard: best six IPS scores per player.
        """
        if df.empty:
            return pd.DataFrame(columns=["Name", "Best6_IPS", "Rounds_Played"])

        results = []

        for name, group in df.groupby("Name"):
            best6 = group["IPS"].nlargest(6).sum()
            results.append({
                "Name": name,
                "Best6_IPS": best6,
                "Rounds_Played": len(group)
            })

        out = pd.DataFrame(results)
        return out.sort_values(
            by=["Best6_IPS", "Rounds_Played"],
            ascending=[False, False]
        ).reset_index(drop=True)

    @staticmethod
    def calculate_strokes(df):
        """
        Strokes leaderboard: best six rounds by strokes over par.
        Lower is better.
        """
        if df.empty:
            return pd.DataFrame(columns=["Name", "Games_Played", "Best6_Strokes_Over_Par"])

        df = df.copy()
        df["Strokes_Over_Par"] = df["Strokes"] - GOAMCalculator.PAR

        results = []

        for name, group in df.groupby("Name"):
            games = len(group)
            best6 = group["Strokes_Over_Par"].nsmallest(6).sum()
            results.append({
                "Name": name,
                "Games_Played": games,
                "Best6_Strokes_Over_Par": best6
            })

        out = pd.DataFrame(results)
        return out.sort_values(
            by=["Games_Played", "Best6_Strokes_Over_Par"],
            ascending=[False, True]
        ).reset_index(drop=True)

    @staticmethod
    def calculate_liv(df):
        """
        LIV scoring: top 3 IPS per team per course.
        """
        if df.empty or "Team" not in df.columns:
            return pd.DataFrame(columns=["Team", "Course", "LIV_Points"])

        results = []

        for (course, team), group in df.groupby(["Course", "Team"]):
            if team is None:
                continue
            top3 = group["IPS"].nlargest(3).sum()
            results.append({
                "Team": team,
                "Course": course,
                "LIV_Points": top3
            })

        if not results:
            return pd.DataFrame(columns=["Team", "Course", "LIV_Points"])

        out = pd.DataFrame(results)
        return out.sort_values(
            by=["Course", "LIV_Points"],
            ascending=[True, False]
        ).reset_index(drop=True)

    @staticmethod
    def split_by_course(df):
        """
        Return dict: {course_name: DataFrame}
        """
        if df.empty:
            return {}

        result = {}
        for course, group in df.groupby("Course"):
            result[course] = group[["Name", "Strokes", "IPS", "Team"]].reset_index(drop=True)
        return result

    @staticmethod
    def generate_output_filename():
        """
        GOAM_Scores_2026_MMM_updated.xlsx
        """
        month = datetime.now().strftime("%b")
        return f"GOAM_Scores_2026_{month}_updated.xlsx"

@staticmethod
def build_ips_leaderboard(df):
    """
    Returns IPS leaderboard in Excel format:
    Name | Best6_IPS | Akasia | PGC | Kyalami | Copperleaf | Services | Rounds_Played
    """
    if df.empty:
        return pd.DataFrame()

    # Pivot IPS per course
    pivot = df.pivot_table(
        index="Name",
        columns="Course",
        values="IPS",
        aggfunc="first"
    ).reset_index()

    # Calculate Best 6 and Rounds Played
    best6 = GOAMCalculator.calculate_best_six_ips(df)

    # Merge
    merged = pivot.merge(best6, on="Name", how="left")

    # Order columns
    course_cols = sorted([c for c in merged.columns if c not in ["Name", "Best6_IPS", "Rounds_Played"]])
    final_cols = ["Name", "Best6_IPS"] + course_cols + ["Rounds_Played"]

    return merged[final_cols]
