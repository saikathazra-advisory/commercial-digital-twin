def calculate_tam(

    market,

    industry,

    geography,

    company_size

):

 

    filtered_market = market.copy()

 

    if industry != "All":

        filtered_market = filtered_market[

            filtered_market["industry"] == industry

        ]

 

    if geography != "All":

        filtered_market = filtered_market[

            filtered_market["geography"] == geography

        ]

 

    if company_size != "All":

        filtered_market = filtered_market[

            filtered_market["company_size"] == company_size

    ]

 

    tam = filtered_market["tam_value_usd"].sum()

 

    return tam

 

# get list of addresable accounts based on selection

def get_addressable_accounts(

    accounts,

    industry,

    geography,

    company_size

):

 

    filtered_accounts = accounts.copy()

 

    if industry != "All":

        filtered_accounts = filtered_accounts[

            filtered_accounts["industry"] == industry

        ]

 

    if geography != "All":

        filtered_accounts = filtered_accounts[

            filtered_accounts["geography"] == geography

        ]

 

    if company_size != "All":

        filtered_accounts = filtered_accounts[

            filtered_accounts["company_size"] == company_size

        ]

 

    return filtered_accounts

 

# get list of accounts which should be focused first

def get_focus_accounts(accounts, propensity_threshold):

 

    focus = accounts[

        accounts["propensity_score"] >= propensity_threshold

    ]

 

    return focus

 

# win rate calculation

def calculate_win_rate(opportunities):

 

    wins = len(

        opportunities[

            opportunities["stage"] == "Closed Won"

        ]

    )

 

    losses = len(

        opportunities[

            opportunities["stage"] == "Closed Lost"

        ]

    )

 

    total_decisions = wins + losses

 

    if total_decisions == 0:

        return 0

 

    return wins / total_decisions

 

# filter opportunites based on selection

def get_scenario_opportunities(

    historical_opportunities,

    industry,

    geography,

    company_size

):

 

    filtered_opportunities = historical_opportunities.copy()

 

    if industry != "All":

        filtered_opportunities = filtered_opportunities[

            filtered_opportunities["industry"] == industry

        ]

 

    if geography != "All":

        filtered_opportunities = filtered_opportunities[

            filtered_opportunities["geography"] == geography

        ]

 

    if company_size != "All":

        filtered_opportunities = filtered_opportunities[

            filtered_opportunities["company_size"] == company_size

        ]

 

    return filtered_opportunities

 

# calculate expected ACV based on average ACV for closed won

def calculate_expected_acv(historical_opportunities):

 

    closed_won = historical_opportunities[

        historical_opportunities["stage"] == "Closed Won"

    ]

 

    if len(closed_won) == 0:

        return 0

 

    expected_acv = closed_won["net_acv_usd"].mean()

 

    return expected_acv

 

#prjected Revenue

def calculate_projected_revenue(

    number_of_focus_accounts,

    win_rate,

    expected_acv

):

 

    projected_revenue = (

        number_of_focus_accounts

        * win_rate

        * expected_acv

    )

 

    return projected_revenue

 

# calculate required pipeline (projected rev/win rate)

def calculate_required_pipeline(

    projected_revenue,

    win_rate

):

 

    if win_rate == 0:

        return 0

 

    required_pipeline = (

        projected_revenue

        / win_rate

    )

 

    return required_pipeline

 

#check how many sales rep we need

import math

 

def calculate_required_hunters(

    focus_accounts,

    accounts_per_hunter

):

 

    required_hunters = math.ceil(

        focus_accounts / accounts_per_hunter

    )

 

    return required_hunters

 

def get_available_hunters(

    capacity,

    geography

):

 

    hunter_data = capacity[

        capacity["seller_type"] == "Hunter"

    ]

 

    if geography != "All":

        hunter_data = hunter_data[

            hunter_data["geography"] == geography

        ]

 

    if len(hunter_data) == 0:

        return 0

 

    available_hunters = hunter_data[

        "seller_count"

    ].sum()

 

    return int(available_hunters)

 

def calculate_capacity_gap(

    required_hunters,

    available_hunters

):

 

    additional_hunters_required = max(

        required_hunters - available_hunters,

        0

    )

 

    surplus_hunters = max(

        available_hunters - required_hunters,

        0

    )

 

    if additional_hunters_required > 0:

        capacity_status = "Capacity Shortfall"

 

    elif surplus_hunters > 0:

        capacity_status = "Sufficient Capacity"

 

    else:

        capacity_status = "Capacity Balanced"

 

    return (

        additional_hunters_required,

        surplus_hunters,

        capacity_status

    )

 

#account per hunter

def get_accounts_per_hunter(

    capacity,

    geography

):

 

    hunter_data = capacity[

        capacity["seller_type"] == "Hunter"

    ].copy()

 

    if geography != "All":

        hunter_data = hunter_data[

            hunter_data["geography"] == geography

        ]

 

    if len(hunter_data) == 0:

        return 25

 

    total_hunters = hunter_data[

        "seller_count"

    ].sum()

 

    if total_hunters == 0:

        return 25

 

    weighted_capacity = (

        hunter_data["seller_count"]

        *

        hunter_data[

            "avg_active_opportunities_per_seller"

        ]

    ).sum()

 

    accounts_per_hunter = (

        weighted_capacity / total_hunters

    )

 

    return round(accounts_per_hunter, 2)