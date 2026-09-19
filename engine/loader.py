from pathlib import Path

 

import pandas as pd

 

# ---------------------------------------------------------

# PROJECT PATHS

# ---------------------------------------------------------

 

PROJECT_ROOT = Path(__file__).resolve().parent.parent

 

DATA_DIR = PROJECT_ROOT / "data"

 

# ---------------------------------------------------------

# LOAD SOURCE DATA

# ---------------------------------------------------------

 

def load_data():

 

    required_files = {

        "accounts":

            "accounts.csv",

 

        "products":

            "products.csv",

 

        "ownership":

            "account_product_ownership.csv",

 

        "market":

            "market_tam.csv",

 

        "product_market_tam":

            "product_market_tam.csv",

 

        "opportunities":

            "historical_opportunities.csv",

 

        "capacity":

            "sales_capacity.csv",

 

        "scenarios":

            "scenario_inputs.csv"

    }

 

    missing_files = [

        file_name

        for file_name in required_files.values()

        if not (

            DATA_DIR / file_name

        ).exists()

    ]

 

    if missing_files:

 

        missing_file_list = ", ".join(

            missing_files

        )

 

        raise FileNotFoundError(

            "The following required data files "

            f"were not found in {DATA_DIR}: "

            f"{missing_file_list}"

        )

 

    data = {}

 

    for dataset_name, file_name in (

        required_files.items()

    ):

 

        file_path = (

            DATA_DIR / file_name

        )

 

        data[dataset_name] = pd.read_csv(

            file_path

        )

 

    return data