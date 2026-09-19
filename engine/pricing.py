import pandas as pd

 

# ---------------------------------------------------------

# DISCOUNT BAND CONFIGURATION

# ---------------------------------------------------------

 

DISCOUNT_BINS = [

    -0.001,

    0.05,

    0.10,

    0.15,

    0.20,

    1.00

]

 

DISCOUNT_LABELS = [

    "0%-5%",

    "5%-10%",

    "10%-15%",

    "15%-20%",

    "Above 20%"

]

 

# ---------------------------------------------------------

# ADD DISCOUNT BAND TO HISTORICAL OPPORTUNITIES

# ---------------------------------------------------------

 

def add_discount_band(

    historical_opportunities

):

 

    opportunities = (

        historical_opportunities.copy()

    )

 

    if "discount_pct" not in opportunities.columns:

 

        opportunities["discount_band"] = (

            "Discount Data Not Available"

        )

 

        return opportunities

 

    opportunities["discount_pct"] = (

        pd.to_numeric(

            opportunities["discount_pct"],

            errors="coerce"

        )

    )

 

    opportunities["discount_band"] = pd.cut(

        opportunities["discount_pct"],

        bins=DISCOUNT_BINS,

        labels=DISCOUNT_LABELS,

        include_lowest=True

    )

 

    return opportunities

 

# ---------------------------------------------------------

# IDENTIFY THE SCENARIO DISCOUNT BAND

# ---------------------------------------------------------

 

def get_discount_band(

    scenario_discount

):

 

    if scenario_discount is None:

        scenario_discount = 0

 

    scenario_discount = float(

        scenario_discount

    )

 

    scenario_discount = max(

        0,

        min(1, scenario_discount)

    )

 

    if scenario_discount <= 0.05:

 

        return "0%-5%"

 

    elif scenario_discount <= 0.10:

 

        return "5%-10%"

 

    elif scenario_discount <= 0.15:

 

        return "10%-15%"

 

    elif scenario_discount <= 0.20:

 

        return "15%-20%"

 

    else:

 

        return "Above 20%"

 

# ---------------------------------------------------------

# CALCULATE WIN RATE FOR THE SELECTED DISCOUNT BAND

# ---------------------------------------------------------

 

def calculate_discount_band_win_rate(

    historical_opportunities,

    scenario_discount,

    minimum_decisions=20

):

 

    scenario_discount_band = get_discount_band(

        scenario_discount

    )

 

    if historical_opportunities is None:

 

        return (

            0,

            scenario_discount_band,

            0,

            "No Historical Evidence"

        )

 

    if len(historical_opportunities) == 0:

 

        return (

            0,

            scenario_discount_band,

            0,

            "No Historical Evidence"

        )

 

    required_columns = {

        "stage",

        "discount_pct"

    }

 

    if not required_columns.issubset(

        historical_opportunities.columns

    ):

 

        return (

            0,

            scenario_discount_band,

            0,

            "Required Discount Data Not Available"

        )

 

    opportunities = add_discount_band(

        historical_opportunities

    )

 

    closed_opportunities = opportunities[

        opportunities["stage"].isin(

            [

                "Closed Won",

                "Closed Lost"

            ]

        )

    ].copy()

 

    if len(closed_opportunities) == 0:

 

        return (

            0,

            scenario_discount_band,

            0,

            "No Historical Evidence"

        )

 

    total_decisions = len(

        closed_opportunities

    )

 

    total_wins = len(

        closed_opportunities[

            closed_opportunities["stage"]

            == "Closed Won"

        ]

    )

 

    overall_win_rate = (

        total_wins

        / total_decisions

    )

 

    discount_band_opportunities = (

        closed_opportunities[

            closed_opportunities[

                "discount_band"

            ].astype("string")

            == scenario_discount_band

        ]

    )

 

    discount_band_decisions = len(

        discount_band_opportunities

    )

 

    if (

        discount_band_decisions

        < minimum_decisions

    ):

 

        return (

            overall_win_rate,

            scenario_discount_band,

            discount_band_decisions,

            "Insufficient Discount-Band Evidence"

        )

 

    discount_band_wins = len(

        discount_band_opportunities[

            discount_band_opportunities["stage"]

            == "Closed Won"

        ]

    )

 

    discount_band_win_rate = (

        discount_band_wins

        / discount_band_decisions

    )

 

    return (

        discount_band_win_rate,

        scenario_discount_band,

        discount_band_decisions,

        "Segment Discount-Band Evidence"

    )

 

# ---------------------------------------------------------

# CALCULATE DISCOUNT-RELATED WIN-RATE ADJUSTMENT

# ---------------------------------------------------------

 

def calculate_discount_win_rate_adjustment(

    historical_win_rate,

    discount_band_win_rate,

    evidence_status,

    maximum_adjustment=0.05

):

 

    if evidence_status != (

        "Segment Discount-Band Evidence"

    ):

 

        return 0

 

    historical_win_rate = float(

        historical_win_rate

    )

 

    discount_band_win_rate = float(

        discount_band_win_rate

    )

 

    observed_adjustment = (

        discount_band_win_rate

        - historical_win_rate

    )

 

    controlled_adjustment = max(

        -maximum_adjustment,

        min(

            maximum_adjustment,

            observed_adjustment

        )

    )

 

    return controlled_adjustment