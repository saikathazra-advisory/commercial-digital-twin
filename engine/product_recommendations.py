import pandas as pd

 

def normalize_column(

    dataframe,

    column_name

):

 

    minimum_value = dataframe[

        column_name

    ].min()

 

    maximum_value = dataframe[

        column_name

    ].max()

 

    if maximum_value == minimum_value:

 

        return pd.Series(

            1.0,

            index=dataframe.index

        )

 

    normalized_values = (

        dataframe[column_name]

        - minimum_value

    ) / (

        maximum_value

        - minimum_value

    )

 

    return normalized_values

 

def filter_product_market_tam(

    product_market_tam,

    industry,

    geography,

    company_size

):

 

    filtered_tam = product_market_tam.copy()

 

    if industry != "All":

 

        filtered_tam = filtered_tam[

            filtered_tam["industry"]

            == industry

        ]

 

    if geography != "All":

 

        filtered_tam = filtered_tam[

            filtered_tam["geography"]

            == geography

        ]

 

    if company_size != "All":

 

        filtered_tam = filtered_tam[

            filtered_tam["company_size"]

            == company_size

        ]

 

    return filtered_tam

 

def filter_historical_opportunities(

    historical_opportunities,

    industry,

    geography,

    company_size

):

 

    filtered_opportunities = (

        historical_opportunities.copy()

    )

 

    if industry != "All":

 

        filtered_opportunities = (

            filtered_opportunities[

                filtered_opportunities["industry"]

                == industry

            ]

        )

 

    if geography != "All":

 

        filtered_opportunities = (

            filtered_opportunities[

                filtered_opportunities["geography"]

                == geography

            ]

        )

 

    if company_size != "All":

 

        filtered_opportunities = (

            filtered_opportunities[

                filtered_opportunities["company_size"]

                == company_size

            ]

        )

 

    return filtered_opportunities

 

def create_product_tam_summary(

    filtered_product_tam

):

 

    if len(filtered_product_tam) == 0:

 

        return pd.DataFrame()

 

    product_tam_summary = (

        filtered_product_tam

        .groupby(

            [

                "product_id",

                "product_name",

                "product_family"

            ],

            as_index=False

        )

        .agg(

            product_tam_value_usd=(

                "product_tam_value_usd",

                "sum"

            ),

 

            product_addressable_accounts_est=(

                "product_addressable_accounts_est",

                "sum"

            ),

 

            average_product_tam_share_pct=(

                "product_tam_share_pct",

                "mean"

            )

        )

    )

 

    return product_tam_summary

 

def create_historical_product_summary(

    filtered_opportunities

):

 

    decided_opportunities = (

        filtered_opportunities[

            filtered_opportunities["stage"].isin(

                [

                    "Closed Won",

                    "Closed Lost"

                ]

            )

        ].copy()

    )

 

    if len(decided_opportunities) == 0:

 

        return pd.DataFrame()

 

    decision_summary = (

        decided_opportunities

        .groupby(

            "product_id",

            as_index=False

        )

        .agg(

            historical_decisions=(

                "opportunity_id",

                "count"

            )

        )

    )

 

    won_opportunities = (

        decided_opportunities[

            decided_opportunities["stage"]

            == "Closed Won"

        ].copy()

    )

 

    if len(won_opportunities) == 0:

 

        decision_summary[

            "historical_wins"

        ] = 0

 

        decision_summary[

            "average_won_acv_usd"

        ] = 0

 

        decision_summary[

            "total_won_acv_usd"

        ] = 0

 

        decision_summary[

            "historical_win_rate"

        ] = 0

 

        return decision_summary

 

    won_summary = (

        won_opportunities

        .groupby(

            "product_id",

            as_index=False

        )

        .agg(

            historical_wins=(

                "opportunity_id",

                "count"

            ),

 

            average_won_acv_usd=(

                "net_acv_usd",

                "mean"

            ),

 

            total_won_acv_usd=(

                "net_acv_usd",

                "sum"

            )

        )

    )

 

    historical_summary = (

        decision_summary.merge(

            won_summary,

            on="product_id",

            how="left"

        )

    )

 

    historical_summary[

        [

            "historical_wins",

            "average_won_acv_usd",

            "total_won_acv_usd"

        ]

    ] = historical_summary[

        [

            "historical_wins",

            "average_won_acv_usd",

            "total_won_acv_usd"

        ]

    ].fillna(0)

 

    historical_summary[

        "historical_win_rate"

    ] = (

        historical_summary[

            "historical_wins"

        ]

        /

        historical_summary[

            "historical_decisions"

        ]

    )

 

    return historical_summary

 

def get_evidence_status(

    historical_decisions,

    minimum_decisions

):

 

    if historical_decisions >= minimum_decisions:

 

        return "Strong Segment Evidence"

 

    if historical_decisions > 0:

 

        return "Limited Segment Evidence"

 

    return "TAM Evidence Only"

 

def calculate_product_recommendations(

    product_market_tam,

    historical_opportunities,

    products,

    industry,

    geography,

    company_size,

    top_n=3,

    minimum_decisions=10

):

 

    filtered_product_tam = (

        filter_product_market_tam(

            product_market_tam,

            industry,

            geography,

            company_size

        )

    )

 

    filtered_opportunities = (

        filter_historical_opportunities(

            historical_opportunities,

            industry,

            geography,

            company_size

        )

    )

 

    product_tam_summary = (

        create_product_tam_summary(

            filtered_product_tam

        )

    )

 

    if len(product_tam_summary) == 0:

 

        return []

 

    historical_summary = (

        create_historical_product_summary(

            filtered_opportunities

        )

    )

 

    product_ranking = (

        product_tam_summary.copy()

    )

 

    if len(historical_summary) > 0:

 

        product_ranking = (

            product_ranking.merge(

                historical_summary,

                on="product_id",

                how="left"

            )

        )

 

    else:

 

        product_ranking[

            "historical_decisions"

        ] = 0

 

        product_ranking[

            "historical_wins"

        ] = 0

 

        product_ranking[

            "historical_win_rate"

        ] = 0

 

        product_ranking[

            "average_won_acv_usd"

        ] = 0

 

        product_ranking[

            "total_won_acv_usd"

        ] = 0

 

    product_attributes = products[

        [

            "product_id",

            "product_category",

            "product_tier",

            "target_persona",

            "base_acv_usd",

            "bundle_eligible_flag"

        ]

    ].copy()

 

    product_ranking = (

        product_ranking.merge(

            product_attributes,

            on="product_id",

            how="left"

        )

    )

 

    historical_columns = [

        "historical_decisions",

        "historical_wins",

        "historical_win_rate",

        "average_won_acv_usd",

        "total_won_acv_usd"

    ]

 

    product_ranking[

        historical_columns

    ] = product_ranking[

        historical_columns

    ].fillna(0)

 

    product_ranking[

        "historical_decisions"

    ] = product_ranking[

        "historical_decisions"

    ].astype(int)

 

    product_ranking[

        "historical_wins"

    ] = product_ranking[

        "historical_wins"

    ].astype(int)

 

    # Normalize each scoring measure between 0 and 1

 

    product_ranking[

        "normalized_tam"

    ] = normalize_column(

        product_ranking,

        "product_tam_value_usd"

    )

 

    product_ranking[

        "normalized_win_rate"

    ] = normalize_column(

        product_ranking,

        "historical_win_rate"

    )

 

    product_ranking[

        "normalized_average_acv"

    ] = normalize_column(

        product_ranking,

        "average_won_acv_usd"

    )

 

    product_ranking[

        "normalized_wins"

    ] = normalize_column(

        product_ranking,

        "historical_wins"

    )

 

    # Calculate the raw product score

 

    product_ranking[

        "raw_recommendation_score"

    ] = (

        product_ranking[

            "normalized_tam"

        ] * 0.40

 

        +

 

        product_ranking[

            "normalized_win_rate"

        ] * 0.25

 

        +

 

        product_ranking[

            "normalized_average_acv"

        ] * 0.20

 

        +

 

        product_ranking[

            "normalized_wins"

        ] * 0.15

    )

 

    # Evidence factor reduces reliance on small samples

 

    product_ranking[

        "historical_evidence_factor"

    ] = (

        product_ranking[

            "historical_decisions"

        ]

        /

        minimum_decisions

    ).clip(

        lower=0,

        upper=1

    )

 

    # Preserve TAM contribution when history is limited.

    # Historical components receive the evidence adjustment.

 

    product_ranking[

        "product_recommendation_score"

    ] = (

 

        product_ranking[

            "normalized_tam"

        ] * 0.40

 

        +

 

        (

            product_ranking[

                "normalized_win_rate"

            ] * 0.25

 

            +

 

            product_ranking[

                "normalized_average_acv"

            ] * 0.20

 

            +

 

            product_ranking[

                "normalized_wins"

            ] * 0.15

        )

 

        *

 

        product_ranking[

            "historical_evidence_factor"

        ]

    )

 

    product_ranking[

        "product_recommendation_score"

    ] = (

        product_ranking[

            "product_recommendation_score"

        ]

        * 100

    )

 

    product_ranking[

        "evidence_status"

    ] = product_ranking.apply(

        lambda row: get_evidence_status(

            row["historical_decisions"],

            minimum_decisions

        ),

        axis=1

    )

 

    product_ranking = (

        product_ranking.sort_values(

            [

                "product_recommendation_score",

                "product_tam_value_usd",

                "historical_decisions"

            ],

            ascending=[

                False,

                False,

                False

            ]

        )

        .reset_index(drop=True)

    )

 

    number_of_recommendations = min(

        top_n,

        len(product_ranking)

    )

 

    recommendations = []

 

    for index in range(

        number_of_recommendations

    ):

 

        product = product_ranking.iloc[

            index

        ]

 

        recommendation_rank = index + 1

 

        if product["historical_decisions"] > 0:

 

            recommendation_reason = (

                f"{product['product_name']} ranks "

                f"number {recommendation_rank} based on "

                f"an estimated product TAM of "

                f"${product['product_tam_value_usd']:,.0f}, "

                f"a historical win rate of "

                f"{product['historical_win_rate'] * 100:.1f}%, "

                f"an average won ACV of "

                f"${product['average_won_acv_usd']:,.0f}, "

                f"and {int(product['historical_wins'])} "

                f"historical wins from "

                f"{int(product['historical_decisions'])} "

                f"decided opportunities."

            )

 

        else:

 

            recommendation_reason = (

                f"{product['product_name']} ranks "

                f"number {recommendation_rank} primarily "

                f"because of an estimated product TAM of "

                f"${product['product_tam_value_usd']:,.0f}. "

                f"No decided historical opportunities "

                f"were available for this product in the "

                f"selected market."

            )

 

        recommendations.append({

 

            "recommendation_rank":

                recommendation_rank,

 

            "product_id":

                product["product_id"],

 

            "product_name":

                product["product_name"],

 

            "product_family":

                product["product_family"],

 

            "product_category":

                product["product_category"],

 

            "product_tier":

                product["product_tier"],

 

            "target_persona":

                product["target_persona"],

 

            "bundle_eligible_flag":

                product["bundle_eligible_flag"],

 

            "product_tam_value_usd":

                round(

                    product[

                        "product_tam_value_usd"

                    ],

                    2

                ),

 

            "product_addressable_accounts_est":

                int(

                    product[

                        "product_addressable_accounts_est"

                    ]

                ),

 

            "average_product_tam_share_pct":

                round(

                    product[

                        "average_product_tam_share_pct"

                    ],

                    4

                ),

 

            "historical_decisions":

                int(

                    product[

                        "historical_decisions"

                    ]

                ),

 

            "historical_wins":

                int(

                    product[

                        "historical_wins"

                    ]

                ),

 

            "historical_win_rate":

                round(

                    product[

                        "historical_win_rate"

                    ],

                    4

                ),

 

            "average_won_acv_usd":

                round(

                    product[

                        "average_won_acv_usd"

                    ],

                    2

                ),

 

            "total_won_acv_usd":

                round(

                    product[

                        "total_won_acv_usd"

                    ],

                    2

                ),

 

            "historical_evidence_factor":

                round(

                    product[

                        "historical_evidence_factor"

                    ],

                    4

                ),

 

            "product_recommendation_score":

                round(

                    product[

                        "product_recommendation_score"

                    ],

                    2

                ),

 

            "evidence_status":

                product[

                    "evidence_status"

                ],

 

            "recommendation_reason":

                recommendation_reason

        })

 

    return recommendations