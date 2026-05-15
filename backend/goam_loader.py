import pandas as pd

class GOAMLoader:

    @staticmethod
    def load_season(file):
        """Load all sheets from a full-season workbook."""
        return pd.read_excel(file, sheet_name=None)

    @staticmethod
    def load_single_round(file):
        """Load a single-round sheet."""
        return pd.read_excel(file)