import pandas as pd
from datetime import datetime


class GOAMCalculator:
    """
    Performs all GOAM calculations:
    - Build long-format rounds from course sheets
    - IPS best six
    - Strokes best six (over par)
    - IPS leaderboard (Excel layout)
    - Strokes leaderboard (Excel layout)
    - LIV team scores + LIV leaderboard
    - Split by course
    - Dynamic course list
    - Output filename
    """

    PAR = 72

    # ---------------------------------------------------------
    # Build long-format table from course sheets
    # ---------------------------------------------------------
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
                    "Team": row["LIV"] if "LIV" in df.columns else None,
                })

        if not rows:
            return pd.DataFrame(columns=["Name", "Course", "Strokes", "IPS", "Team"])

        return pd.DataFrame(rows)

    # ---------------------------------------------------------
    # Dynamic course list
    # ---------------------------------------------------------
    @staticmethod
    def list_courses(df):
        if df.empty:
            return []
        return sorted(df["Course"].dropna().unique().tolist())

    # ---------------------------------------------------------
    # Best 6 IPS (core numbers only)
    # ---------------------------------------------------------
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
                "Rounds_Played": len(group),
            })

        out = pd.DataFrame(results)

        out = out.sort_values(
            by=["Best6_IPS", "Rounds_Played"],
            ascending=[False, False],
        ).reset_index(drop=True)

        return out

    # ---------------------------------------------------------
    # Best 6 Strokes (core numbers only)
    # ---------------------------------------------------------
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
                "Best6_Strokes_Over_Par": best6,
            })

        out = pd.DataFrame(results)

        out = out.sort_values(
            by=["Games_Played", "Best6_Strokes_Over_Par"],
            ascending=[False, True],
        ).reset_index(drop=True)

        return out

    # ---------------------------------------------------------
    # LIV scoring (raw per team per course)
    # ---------------------------------------------------------
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
                "LIV_Points": top3,
            })

        if not results:
            return pd.DataFrame(columns=["Team", "Course", "LIV_Points"])

        out = pd.DataFrame(results)

        out = out.sort_values(
            by=["Course", "LIV_Points"],
            ascending=[True, False],
        ).reset_index(drop=True)

        return out

    # ---------------------------------------------------------
    # LIV Leaderboard (pivoted + strength index + arrows)
    # ---------------------------------------------------------
    @staticmethod
    def build_liv_leaderboard(df):
        """
        Returns LIV leaderboard in Excel/UI format:
        Team | LIV Total | Strength Index | Trend | <courses...>
        """
        liv_raw = GOAMCalculator.calculate_liv(df)

        if liv_raw.empty:
            return pd.DataFrame()

        # Pivot: rows = Team, columns = Course, values = LIV_Points
        pivot = liv_raw.pivot_table(
            index="Team",
            columns="Course",
            values="LIV_Points",
            aggfunc="first",
        ).fillna(0)

        # LIV Total
        pivot["LIV Total"] = pivot.sum(axis=1)

        # Strength Index = average points per course played
        course_cols = [c for c in pivot.columns if c != "LIV Total"]
        played_counts = pivot[course_cols].astype(bool).sum(axis=1)
        pivot["Strength Index"] = (
            pivot[course_cols].sum(axis=1) / played_counts.replace(0, pd.NA)
        ).round(1)

        # Sort by LIV Total
        pivot = pivot.sort_values(by="LIV Total", ascending=False)

        # Ranking arrows (relative to previous row)
        arrows = []
        prev = None
        for total in pivot["LIV Total"]:
            if prev is None:
                arrows.append("–")
            else:
                if total > prev:
                    arrows.append("↑")
                elif total < prev:
                    arrows.append("↓")
                else:
                    arrows.append("→")
            prev = total

        pivot["Trend"] = arrows

        # Final column order
        final_cols = ["LIV Total", "Strength Index", "Trend"] + sorted(course_cols)
        final = pivot[final_cols].reset_index()  # Team becomes a column

        return final

    # ---------------------------------------------------------
    # IPS Leaderboard (Excel layout)
    # ---------------------------------------------------------
    @staticmethod
    def build_ips_leaderboard(df):
        """
        Returns IPS leaderboard in Excel format:
        Rank | Name | Best6_IPS | <courses...> | Rounds_Played
        """
        if df.empty:
            return pd.DataFrame()

        pivot = df.pivot_table(
            index="Name",
            columns="Course",
            values="IPS",
            aggfunc="first",
        ).reset_index()

        best6 = GOAMCalculator.calculate_best_six_ips(df)

        merged = pivot.merge(best6, on="Name", how="left")

        merged = merged.fillna(0)

        # Ensure numeric sorting works
        numeric_cols = merged.columns.drop(["Name"])
        merged[numeric_cols] = merged[numeric_cols].apply(
            pd.to_numeric, errors="coerce"
        ).fillna(0)

        merged = merged.sort_values(
            by=["Best6_IPS", "Rounds_Played"],
            ascending=[False, False],
        ).reset_index(drop=True)

        merged.insert(0, "Rank", merged.index + 1)

        course_cols = sorted(
            [c for c in merged.columns
             if c not in ["Rank", "Name", "Best6_IPS", "Rounds_Played"]]
        )
        final_cols = ["Rank", "Name", "Best6_IPS"] + course_cols + ["Rounds_Played"]

        return merged[final_cols]

    # ---------------------------------------------------------
    # Strokes Leaderboard (Excel layout)
    # ---------------------------------------------------------
    @staticmethod
    def build_strokes_leaderboard(df):
        """
        Returns Strokes leaderboard in Excel format:
        Rank | Name | Best6_Strokes_Over_Par | <courses...> | Games_Played
        """
        if df.empty:
            return pd.DataFrame()

        df = df.copy()
        df["Strokes_Over_Par"] = df["Strokes"] - GOAMCalculator.PAR

        pivot = df.pivot_table(
            index="Name",
            columns="Course",
            values="Strokes_Over_Par",
            aggfunc="first",
        ).reset_index()

        best6 = GOAMCalculator.calculate_strokes(df)

        merged = pivot.merge(best6, on="Name", how="left")

        merged = merged.fillna(0)

        numeric_cols = merged.columns.drop(["Name"])
        merged[numeric_cols] = merged[numeric_cols].apply(
            pd.to_numeric, errors="coerce"
        ).fillna(0)

        merged = merged.sort_values(
            by=["Games_Played", "Best6_Strokes_Over_Par"],
            ascending=[False, True],
        ).reset_index(drop=True)

        merged.insert(0, "Rank", merged.index + 1)

        course_cols = sorted(
            [c for c in merged.columns
             if c not in ["Rank", "Name", "Best6_Strokes_Over_Par", "Games_Played"]]
        )
        final_cols = ["Rank", "Name", "Best6_Strokes_Over_Par"] + course_cols + ["Games_Played"]

        return merged[final_cols]

    # ---------------------------------------------------------
    # Split by course
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Output filename
    # ---------------------------------------------------------
    @staticmethod
    def generate_output_filename():
        """
        GOAM_Scores_2026_MMM_updated.xlsx
        """
        month = datetime.now().strftime("%b")
        return f"GOAM_Scores_2026_{month}_updated.xlsx"
