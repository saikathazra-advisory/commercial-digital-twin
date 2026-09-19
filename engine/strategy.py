def adjust_win_rate(

    historical_win_rate,

    win_rate_adjustment

):

 

    adjusted_win_rate = (

        historical_win_rate

        + win_rate_adjustment

    )

 

    adjusted_win_rate = max(

        0,

        min(1, adjusted_win_rate)

    )

 

    return adjusted_win_rate

 

def adjust_expected_acv(

    historical_expected_acv,

    acv_adjustment

):

 

    adjusted_expected_acv = (

        historical_expected_acv

        * (1 + acv_adjustment)

    )

 

    adjusted_expected_acv = max(

        0,

        adjusted_expected_acv

    )

 

    return adjusted_expected_acv

 

def calculate_uplift_from_ownership(

    ownership_data,

    maximum_uplift,

    minimum_accounts_per_group

):

 

    if len(ownership_data) == 0:

        return 0, False

 

    account_summary = (

        ownership_data

        .groupby("account_id")

        .agg(

            owned_product_count=(

                "product_id",

                "nunique"

            ),

            total_current_acv_usd=(

                "current_acv_usd",

                "sum"

            )

        )

        .reset_index()

    )

 

    single_product_customers = account_summary[

        account_summary["owned_product_count"] == 1

    ]

 

    multi_product_customers = account_summary[

        account_summary["owned_product_count"] >= 2

    ]

 

    if (

        len(single_product_customers)

        < minimum_accounts_per_group

        or

        len(multi_product_customers)

        < minimum_accounts_per_group

    ):

        return 0, False

 

    average_single_product_acv = (

        single_product_customers[

            "total_current_acv_usd"

        ].mean()

    )

 

    average_multi_product_acv = (

        multi_product_customers[

            "total_current_acv_usd"

        ].mean()

    )

 

    if average_single_product_acv <= 0:

        return 0, False

 

    observed_uplift = (

        average_multi_product_acv

        / average_single_product_acv

        - 1

    )

 

    observed_uplift = max(

        observed_uplift,

        0

    )

 

    observed_uplift = min(

        observed_uplift,

        maximum_uplift

    )

 

    return observed_uplift, True

 

def calculate_bundle_acv_uplift(

    ownership,

    accounts,

    industry,

    geography,

    company_size,

    maximum_uplift=0.25,

    minimum_accounts_per_group=5

):

 

    owned_products = ownership[

        ownership["ownership_status"] == "Owned"

    ].copy()

 

    if len(owned_products) == 0:

        return 0, "No Ownership Evidence"

 

    account_attributes = accounts[

        [

            "account_id",

            "industry",

            "geography",

            "company_size"

        ]

    ].copy()

 

    ownership_with_accounts = owned_products.merge(

        account_attributes,

        on="account_id",

        how="left"

    )

 

    segment_ownership = ownership_with_accounts.copy()

 

    if industry != "All":

        segment_ownership = segment_ownership[

            segment_ownership["industry"] == industry

        ]

 

    if geography != "All":

        segment_ownership = segment_ownership[

            segment_ownership["geography"] == geography

        ]

 

    if company_size != "All":

        segment_ownership = segment_ownership[

            segment_ownership["company_size"]

            == company_size

        ]

 

    segment_uplift, segment_valid = (

        calculate_uplift_from_ownership(

            segment_ownership,

            maximum_uplift,

            minimum_accounts_per_group

        )

    )

 

    if segment_valid:

 

        return (

            segment_uplift,

            "Segment-Specific Evidence"

        )

 

    global_uplift, global_valid = (

        calculate_uplift_from_ownership(

            ownership_with_accounts,

            maximum_uplift,

            minimum_accounts_per_group

        )

    )

 

    if global_valid:

 

        return (

            global_uplift,

            "Global Evidence Fallback"

        )

 

    return (

        0,

        "Insufficient Evidence"

    )

 

def get_effective_acv_adjustment(

    product_strategy,

    scenario_acv_adjustment,

    bundle_acv_uplift

):

 

    if product_strategy == "Bundle":

 

        return bundle_acv_uplift

 

    return scenario_acv_adjustment

 

#discount function

def calculate_historical_discount(

    historical_opportunities

):

 

    closed_won_opportunities = (

        historical_opportunities[

            historical_opportunities["stage"]

            == "Closed Won"

        ]

    )

 

    if len(closed_won_opportunities) == 0:

        return 0

 

    historical_discount = (

        closed_won_opportunities[

            "discount_pct"

        ].mean()

    )

 

    historical_discount = max(

        0,

        min(0.95, historical_discount)

    )

 

    return historical_discount

 

#converts historical net ACV back to an estimated list ACV

def calculate_discount_adjusted_acv(

    historical_expected_acv,

    historical_discount,

    scenario_discount

):

 

    if historical_expected_acv <= 0:

        return 0

 

    historical_discount = max(

        0,

        min(0.95, historical_discount)

    )

 

    scenario_discount = max(

        0,

        min(0.95, scenario_discount)

    )

 

    estimated_list_acv = (

        historical_expected_acv

        / (1 - historical_discount)

    )

 

    discount_adjusted_acv = (

        estimated_list_acv

        * (1 - scenario_discount)

    )

 

    discount_adjusted_acv = max(

        0,

        discount_adjusted_acv

    )

 

    return discount_adjusted_acv

 

#discount impact

def calculate_discount_acv_impact(

    discount_adjusted_acv,

    historical_expected_acv

):

 

    discount_acv_impact = (

        discount_adjusted_acv

        - historical_expected_acv

    )

 

    return discount_acv_impact