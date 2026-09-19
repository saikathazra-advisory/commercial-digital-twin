# ---------------------------------------------------------

# FILTER ACCOUNTS FOR THE SELECTED SCENARIO

# ---------------------------------------------------------
import json

import pandas as pd
 

def filter_scenario_accounts(

    accounts,

    industry,

    geography,

    company_size

):

 

    filtered_accounts = accounts.copy()

 

    if industry != "All":

 

        filtered_accounts = filtered_accounts[

            filtered_accounts["industry"]

            == industry

        ]

 

    if geography != "All":

 

        filtered_accounts = filtered_accounts[

            filtered_accounts["geography"]

            == geography

        ]

 

    if company_size != "All":

 

        filtered_accounts = filtered_accounts[

            filtered_accounts["company_size"]

            == company_size

        ]

 

    return filtered_accounts.copy()

 

# ---------------------------------------------------------

# IDENTIFY FOCUS ACCOUNTS

# ---------------------------------------------------------

 

def get_priority_focus_accounts(

    accounts,

    industry,

    geography,

    company_size,

    propensity_threshold

):

 

    scenario_accounts = filter_scenario_accounts(

        accounts,

        industry,

        geography,

        company_size

    )

 

    focus_accounts = scenario_accounts[

        scenario_accounts["propensity_score"]

        >= propensity_threshold

    ].copy()

 

    return focus_accounts

 

# ---------------------------------------------------------

# CALIBRATE ACCOUNT WIN PROBABILITIES

# ---------------------------------------------------------

 

def calibrate_account_probabilities(

    focus_accounts,

    expected_customers_won,

    maximum_probability=0.95

):

 

    calibrated_accounts = focus_accounts.copy()

 

    number_of_accounts = len(

        calibrated_accounts

    )

 

    if number_of_accounts == 0:

 

        calibrated_accounts[

            "account_win_probability"

        ] = pd.Series(

            dtype=float

        )

 

        return calibrated_accounts

 

    expected_customers_won = max(

        0,

        min(

            float(expected_customers_won),

            number_of_accounts

            * maximum_probability

        )

    )

 

    propensity_values = pd.to_numeric(

        calibrated_accounts[

            "propensity_score"

        ],

        errors="coerce"

    ).fillna(0)

 

    propensity_values = propensity_values.clip(

        lower=0,

        upper=100

    )

 

    account_weights = propensity_values / 100

 

    if account_weights.sum() <= 0:

 

        account_weights = pd.Series(

            1.0,

            index=calibrated_accounts.index

        )

 

    calibrated_accounts[

        "account_probability_weight"

    ] = account_weights

 

    calibrated_accounts[

        "account_win_probability"

    ] = 0.0

 

    remaining_expected_wins = (

        expected_customers_won

    )

 

    active_accounts = pd.Series(

        True,

        index=calibrated_accounts.index

    )

 

    maximum_iterations = (

        number_of_accounts + 5

    )

 

    for _ in range(maximum_iterations):

 

        if remaining_expected_wins <= 0:

            break

 

        active_index = active_accounts[

            active_accounts

        ].index

 

        if len(active_index) == 0:

            break

 

        active_weights = calibrated_accounts.loc[

            active_index,

            "account_probability_weight"

        ]

 

        if active_weights.sum() <= 0:

 

            active_weights = pd.Series(

                1.0,

                index=active_index

            )

 

        proposed_probabilities = (

            remaining_expected_wins

            * active_weights

            / active_weights.sum()

        )

 

        available_probability = (

            maximum_probability

            - calibrated_accounts.loc[

                active_index,

                "account_win_probability"

            ]

        )

 

        allocation = pd.concat(

            [

                proposed_probabilities.rename(

                    "proposed"

                ),

                available_probability.rename(

                    "available"

                )

            ],

            axis=1

        ).min(

            axis=1

        )

 

        calibrated_accounts.loc[

            active_index,

            "account_win_probability"

        ] = (

            calibrated_accounts.loc[

                active_index,

                "account_win_probability"

            ]

            + allocation

        )

 

        amount_allocated = allocation.sum()

 

        remaining_expected_wins = max(

            0,

            remaining_expected_wins

            - amount_allocated

        )

 

        reached_maximum = (

            calibrated_accounts.loc[

                active_index,

                "account_win_probability"

            ]

            >= maximum_probability - 0.0000001

        )

 

        active_accounts.loc[

            reached_maximum[

                reached_maximum

            ].index

        ] = False

 

        if amount_allocated <= 0.0000001:

            break

 

    probability_variance = (

        expected_customers_won

        - calibrated_accounts[

            "account_win_probability"

        ].sum()

    )

 

    if (

        abs(probability_variance) > 0.0000001

        and number_of_accounts > 0

    ):

 

        available_accounts = calibrated_accounts[

            calibrated_accounts[

                "account_win_probability"

            ] < maximum_probability

        ]

 

        if len(available_accounts) > 0:

 

            correction_index = (

                available_accounts.index[0]

            )

 

            corrected_probability = (

                calibrated_accounts.loc[

                    correction_index,

                    "account_win_probability"

                ]

                + probability_variance

            )

 

            calibrated_accounts.loc[

                correction_index,

                "account_win_probability"

            ] = max(

                0,

                min(

                    maximum_probability,

                    corrected_probability

                )

            )

 

    calibrated_accounts[

        "account_win_probability"

    ] = calibrated_accounts[

        "account_win_probability"

    ].clip(

        lower=0,

        upper=maximum_probability

    )

 

    return calibrated_accounts

 

# ---------------------------------------------------------

# EXTRACT PRODUCT RECOMMENDATIONS

# ---------------------------------------------------------

 

def extract_recommended_products(

    product_recommendations

):

 

    if product_recommendations is None:

 

        recommendations = []

 

    elif isinstance(

        product_recommendations,

        str

    ):

 

        try:

 

            recommendations = json.loads(

                product_recommendations

            )

 

        except json.JSONDecodeError:

 

            recommendations = []

 

    elif isinstance(

        product_recommendations,

        list

    ):

 

        recommendations = (

            product_recommendations

        )

 

    else:

 

        recommendations = []

 

    recommended_products = []

 

    for recommendation in recommendations[:3]:

 

        recommended_products.append(

            recommendation.get(

                "product_name",

                ""

            )

        )

 

    while len(recommended_products) < 3:

 

        recommended_products.append(

            ""

        )

 

    return recommended_products

 

# ---------------------------------------------------------

# ASSIGN PRIORITY BAND

# ---------------------------------------------------------

 

def assign_priority_band(

    priority_percentile

):

 

    if priority_percentile <= 0.10:

 

        return "Priority 1"

 

    elif priority_percentile <= 0.30:

 

        return "Priority 2"

 

    else:

 

        return "Priority 3"

 

# ---------------------------------------------------------

# CREATE ACCOUNT-LEVEL PRIORITY OUTPUT

# ---------------------------------------------------------

 

def create_priority_accounts(

    accounts,

    scenario_id,

    scenario_name,

    industry,

    geography,

    company_size,

    propensity_threshold,

    adjusted_win_rate,

    adjusted_expected_acv,

    expected_customers_won,

    projected_revenue,

    product_recommendations=None

):

 

    focus_accounts = get_priority_focus_accounts(

        accounts,

        industry,

        geography,

        company_size,

        propensity_threshold

    )

 

    output_columns = [

        "scenario_id",

        "scenario_name",

        "priority_rank",

        "priority_band",

        "account_id",

        "account_name",

        "account_type",

        "industry",

        "geography",

        "country",

        "region",

        "company_size",

        "employee_band",

        "revenue_band",

        "buyer_persona_primary",

        "buyer_persona_secondary",

        "account_tier",

        "current_customer_flag",

        "strategic_account_flag",

        "digital_maturity_score",

        "data_intensity_score",

        "propensity_score",

        "sales_coverage_flag",

        "owner_type",

        "account_probability_weight",

        "account_win_probability",

        "estimated_account_acv_usd",

        "initial_expected_acv_usd",

        "expected_acv_contribution_usd",

        "expected_acv_share_pct",

        "cumulative_expected_acv_usd",

        "cumulative_expected_acv_pct",

        "recommended_product_1",

        "recommended_product_2",

        "recommended_product_3",

        "scenario_adjusted_win_rate",

        "scenario_adjusted_expected_acv_usd",

        "allocation_method",

        "reconciliation_factor"

    ]

 

    if len(focus_accounts) == 0:

 

        return pd.DataFrame(

            columns=output_columns

        )

 

    priority_accounts = (

        calibrate_account_probabilities(

            focus_accounts,

            expected_customers_won

        )

    )

 

    priority_accounts[

        "estimated_account_acv_usd"

    ] = float(

        adjusted_expected_acv

    )

 

    priority_accounts[

        "initial_expected_acv_usd"

    ] = (

        priority_accounts[

            "account_win_probability"

        ]

        * priority_accounts[

            "estimated_account_acv_usd"

        ]

    )

 

    initial_expected_acv_total = (

        priority_accounts[

            "initial_expected_acv_usd"

        ].sum()

    )

 

    if initial_expected_acv_total > 0:

 

        reconciliation_factor = (

            float(projected_revenue)

            / initial_expected_acv_total

        )

 

    else:

 

        reconciliation_factor = 0

 

    priority_accounts[

        "reconciliation_factor"

    ] = reconciliation_factor

 

    priority_accounts[

        "expected_acv_contribution_usd"

    ] = (

        priority_accounts[

            "initial_expected_acv_usd"

        ]

        * reconciliation_factor

    )

 

    priority_accounts = (

        priority_accounts.sort_values(

            [

                "expected_acv_contribution_usd",

                "propensity_score",

                "account_id"

            ],

            ascending=[

                False,

                False,

                True

            ]

        )

        .reset_index(

            drop=True

        )

    )

 

    priority_accounts[

        "priority_rank"

    ] = range(

        1,

        len(priority_accounts) + 1

    )

 

    priority_accounts[

        "priority_percentile"

    ] = (

        priority_accounts[

            "priority_rank"

        ]

        / len(priority_accounts)

    )

 

    priority_accounts[

        "priority_band"

    ] = priority_accounts[

        "priority_percentile"

    ].apply(

        assign_priority_band

    )

 

    total_expected_acv = (

        priority_accounts[

            "expected_acv_contribution_usd"

        ].sum()

    )

 

    if total_expected_acv > 0:

 

        priority_accounts[

            "expected_acv_share_pct"

        ] = (

            priority_accounts[

                "expected_acv_contribution_usd"

            ]

            / total_expected_acv

        )

 

    else:

 

        priority_accounts[

            "expected_acv_share_pct"

        ] = 0

 

    priority_accounts[

        "cumulative_expected_acv_usd"

    ] = priority_accounts[

        "expected_acv_contribution_usd"

    ].cumsum()

 

    priority_accounts[

        "cumulative_expected_acv_pct"

    ] = priority_accounts[

        "expected_acv_share_pct"

    ].cumsum()

 

    final_variance = (

        float(projected_revenue)

        - priority_accounts[

            "expected_acv_contribution_usd"

        ].sum()

    )

 

    if (

        len(priority_accounts) > 0

        and abs(final_variance) > 0

    ):

 

        final_row_index = (

            priority_accounts.index[-1]

        )

 

        priority_accounts.loc[

            final_row_index,

            "expected_acv_contribution_usd"

        ] = (

            priority_accounts.loc[

                final_row_index,

                "expected_acv_contribution_usd"

            ]

            + final_variance

        )

 

        priority_accounts[

            "cumulative_expected_acv_usd"

        ] = priority_accounts[

            "expected_acv_contribution_usd"

        ].cumsum()

 

        if projected_revenue > 0:

 

            priority_accounts[

                "expected_acv_share_pct"

            ] = (

                priority_accounts[

                    "expected_acv_contribution_usd"

                ]

                / float(projected_revenue)

            )

 

            priority_accounts[

                "cumulative_expected_acv_pct"

            ] = priority_accounts[

                "expected_acv_share_pct"

            ].cumsum()

 

    recommended_products = (

        extract_recommended_products(

            product_recommendations

        )

    )

 

    priority_accounts[

        "recommended_product_1"

    ] = recommended_products[0]

 

    priority_accounts[

        "recommended_product_2"

    ] = recommended_products[1]

 

    priority_accounts[

        "recommended_product_3"

    ] = recommended_products[2]

 

    priority_accounts[

        "scenario_id"

    ] = scenario_id

 

    priority_accounts[

        "scenario_name"

    ] = scenario_name

 

    priority_accounts[

        "scenario_adjusted_win_rate"

    ] = float(

        adjusted_win_rate

    )

 

    priority_accounts[

        "scenario_adjusted_expected_acv_usd"

    ] = float(

        adjusted_expected_acv

    )

 

    priority_accounts[

        "allocation_method"

    ] = (

        "Propensity-calibrated win probability "

        "with scenario-level ACV reconciliation"

    )

 

    return priority_accounts[

        output_columns

    ]