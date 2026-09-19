import json

 

import pandas as pd

import streamlit as st

 

from engine.loader import load_data

from engine.simulator import run_simulation

 

from engine.account_prioritization import (

    create_priority_accounts

)

 

 

# ---------------------------------------------------------

# PAGE CONFIGURATION

# ---------------------------------------------------------

 

st.set_page_config(

    page_title="Commercial Growth Simulator",

    page_icon="📈",

    layout="wide",

    initial_sidebar_state="expanded"

)

 

 

# ---------------------------------------------------------

# LOAD DATA

# ---------------------------------------------------------

 

@st.cache_data

def load_source_data():

 

    return load_data()

 

 

@st.cache_data

def load_predefined_simulations():

 

    simulation_results = run_simulation()

 

    return pd.DataFrame(

        simulation_results

    )

 

 

# ---------------------------------------------------------

# FORMAT VALUES

# ---------------------------------------------------------

 

def format_currency(value):

 

    if value is None or pd.isna(value):

        return "$0"

 

    value = float(value)

 

    if value >= 1_000_000_000:

        return f"${value / 1_000_000_000:,.2f}B"

 

    if value >= 1_000_000:

        return f"${value / 1_000_000:,.2f}M"

 

    if value >= 1_000:

        return f"${value / 1_000:,.1f}K"

 

    return f"${value:,.0f}"

 

 

def format_percentage(value):

 

    if value is None or pd.isna(value):

        return "0.0%"

 

    return f"{float(value) * 100:.1f}%"

 

 

def format_score(value):

 

    if value is None or pd.isna(value):

        return "0.0/100"

 

    return f"{float(value):.1f}/100"

 

 

# ---------------------------------------------------------

# HELPER FUNCTIONS

# ---------------------------------------------------------

 

def get_scenario_value(

    selected_scenario,

    field_name,

    default_value=0

):

 

    if isinstance(

        selected_scenario,

        pd.Series

    ):

 

        return selected_scenario.get(

            field_name,

            default_value

        )

 

    if isinstance(

        selected_scenario,

        dict

    ):

 

        return selected_scenario.get(

            field_name,

            default_value

        )

 

    return default_value

 

def get_historical_discount_for_selection(

    opportunities,

    industry,

    geography,

    company_size

):

 

    filtered_opportunities = opportunities.copy()

 

    if industry != "All":

 

        filtered_opportunities = filtered_opportunities[

            filtered_opportunities["industry"]

            == industry

        ]

 

    if geography != "All":

 

        filtered_opportunities = filtered_opportunities[

            filtered_opportunities["geography"]

            == geography

        ]

 

    if company_size != "All":

 

        filtered_opportunities = filtered_opportunities[

            filtered_opportunities["company_size"]

            == company_size

        ]

 

    closed_won_opportunities = filtered_opportunities[

        filtered_opportunities["stage"]

        == "Closed Won"

    ].copy()

 

    if len(closed_won_opportunities) == 0:

        return 0

 

    if (

        "discount_pct"

        not in closed_won_opportunities.columns

    ):

        return 0

 

    historical_discount = (

        pd.to_numeric(

            closed_won_opportunities[

                "discount_pct"

            ],

            errors="coerce"

        )

        .dropna()

        .mean()

    )

 

    if pd.isna(historical_discount):

        return 0

 

    historical_discount = max(

        0,

        min(

            0.95,

            float(historical_discount)

        )

    )

 

    return historical_discount

 

def get_product_recommendations(

    selected_scenario

):

 

    recommendation_json = get_scenario_value(

        selected_scenario,

        "product_recommendations_json",

        "[]"

    )

 

    if recommendation_json is None:

        return []

 

    if (

        isinstance(recommendation_json, float)

        and pd.isna(recommendation_json)

    ):

        return []

 

    if isinstance(

        recommendation_json,

        list

    ):

 

        return recommendation_json

 

    if isinstance(

        recommendation_json,

        str

    ):

 

        if recommendation_json.strip() == "":

            return []

 

        try:

 

            recommendations = json.loads(

                recommendation_json

            )

 

            if isinstance(

                recommendations,

                list

            ):

 

                return recommendations

 

        except json.JSONDecodeError:

 

            return []

 

    return []

 

def get_priority_accounts(

    selected_scenario,

    source_data

):

 

    priority_accounts = create_priority_accounts(

        accounts=source_data["accounts"],

 

        scenario_id=get_scenario_value(

            selected_scenario,

            "scenario_id",

            ""

        ),

 

        scenario_name=get_scenario_value(

            selected_scenario,

            "scenario_name",

            ""

        ),

 

        industry=get_scenario_value(

            selected_scenario,

            "industry",

            "All"

        ),

 

        geography=get_scenario_value(

            selected_scenario,

            "geography",

            "All"

        ),

 

        company_size=get_scenario_value(

            selected_scenario,

            "company_size",

            "All"

        ),

 

        propensity_threshold=get_scenario_value(

            selected_scenario,

            "propensity_threshold",

            0

        ),

 

        adjusted_win_rate=get_scenario_value(

            selected_scenario,

            "adjusted_win_rate",

            0

        ),

 

        adjusted_expected_acv=get_scenario_value(

            selected_scenario,

            "adjusted_expected_acv_usd",

            0

        ),

 

        expected_customers_won=get_scenario_value(

            selected_scenario,

            "expected_customers_won",

            0

        ),

 

        projected_revenue=get_scenario_value(

            selected_scenario,

            "projected_revenue_usd",

            0

        ),

 

        product_recommendations=get_scenario_value(

            selected_scenario,

            "product_recommendations_json",

            "[]"

        )

    )

 

    return priority_accounts

 

# ---------------------------------------------------------

# SCENARIO HEADER

# ---------------------------------------------------------

 

def display_scenario_header(

    selected_scenario

):

 

    scenario_name = get_scenario_value(

        selected_scenario,

        "scenario_name",

        "Commercial Scenario"

    )

 

    industry = get_scenario_value(

        selected_scenario,

        "industry",

        "All"

    )

 

    geography = get_scenario_value(

        selected_scenario,

        "geography",

        "All"

    )

 

    company_size = get_scenario_value(

        selected_scenario,

        "company_size",

        "All"

    )

 

    product_strategy = get_scenario_value(

        selected_scenario,

        "product_strategy",

        ""

    )

 

    st.subheader(

        scenario_name

    )

 

    st.caption(

        f"{industry} | "

        f"{geography} | "

        f"{company_size} | "

        f"{product_strategy}"

    )

 

 

# ---------------------------------------------------------

# OVERVIEW PAGE

# ---------------------------------------------------------

 

def display_overview(

    selected_scenario

):

 

    display_scenario_header(

        selected_scenario

    )

 

    metric_1, metric_2, metric_3, metric_4 = (

        st.columns(4)

    )

 

    with metric_1:

 

        st.metric(

            label="Total Addressable Market",

            value=format_currency(

                get_scenario_value(

                    selected_scenario,

                    "tam_usd"

                )

            )

        )

 

    with metric_2:

 

        st.metric(

            label="Projected New ACV",

            value=format_currency(

                get_scenario_value(

                    selected_scenario,

                    "projected_revenue_usd"

                )

            )

        )

 

    with metric_3:

 

        st.metric(

            label="Required Pipeline",

            value=format_currency(

                get_scenario_value(

                    selected_scenario,

                    "required_pipeline_usd"

                )

            )

        )

 

    with metric_4:

 

        st.metric(

            label="Confidence Level",

            value=get_scenario_value(

                selected_scenario,

                "confidence_level",

                "Not Available"

            )

        )

 

    metric_5, metric_6, metric_7, metric_8 = (

        st.columns(4)

    )

 

    with metric_5:

 

        st.metric(

            label="Addressable Accounts",

            value=int(

                get_scenario_value(

                    selected_scenario,

                    "addressable_accounts"

                )

            )

        )

 

    with metric_6:

 

        st.metric(

            label="Focus Accounts",

            value=int(

                get_scenario_value(

                    selected_scenario,

                    "focus_accounts"

                )

            )

        )

 

    with metric_7:

 

        st.metric(

            label="Expected Customers Won",

            value=(

                f"{float(get_scenario_value(

                    selected_scenario,

                    'expected_customers_won'

                )):.1f}"

            )

        )

 

    with metric_8:

 

        st.metric(

            label="Adjusted Win Rate",

            value=format_percentage(

                get_scenario_value(

                    selected_scenario,

                    "adjusted_win_rate"

                )

            )

        )

 

    st.divider()

 

    market_column, strategy_column = (

        st.columns(2)

    )

 

    with market_column:

 

        st.markdown(

            "### Selected Market"

        )

 

        market_data = pd.DataFrame({

            "Selection": [

                "Industry",

                "Geography",

                "Company Size",

                "Propensity Threshold"

            ],

            "Value": [

                get_scenario_value(

                    selected_scenario,

                    "industry",

                    "All"

                ),

                get_scenario_value(

                    selected_scenario,

                    "geography",

                    "All"

                ),

                get_scenario_value(

                    selected_scenario,

                    "company_size",

                    "All"

                ),

                int(

                    get_scenario_value(

                        selected_scenario,

                        "propensity_threshold"

                    )

                )

            ]

        })

 

        st.dataframe(

            market_data,

            hide_index=True,

            use_container_width=True

        )

 

    with strategy_column:

 

        st.markdown(

            "### Commercial Strategy"

        )

 

        strategy_data = pd.DataFrame({

        "Selection": [

            "Product Strategy",

            "Sales Motion",

            "Pricing Assumption",

            "Historical Discount",

            "Scenario Discount",

            "Historical Win Rate",

            "Adjusted Win Rate",

            "Historical Expected ACV",

            "Adjusted Expected ACV"

        ],

        "Value": [

            get_scenario_value(

                selected_scenario,

                "product_strategy",

                ""

            ),

 

            get_scenario_value(

                selected_scenario,

                "sales_motion",

                ""

            ),

 

            get_scenario_value(

                selected_scenario,

                "pricing_assumption",

                "Scenario Discount"

            ),

 

            format_percentage(

                get_scenario_value(

                    selected_scenario,

                    "historical_discount_pct"

                )

            ),

 

            format_percentage(

                get_scenario_value(

                    selected_scenario,

                    "scenario_discount_pct"

                )

            ),

 

            format_percentage(

                get_scenario_value(

                    selected_scenario,

                    "historical_win_rate"

                )

            ),

 

            format_percentage(

                get_scenario_value(

                    selected_scenario,

                    "adjusted_win_rate"

                )

            ),

 

            format_currency(

                get_scenario_value(

                    selected_scenario,

                    "historical_expected_acv_usd"

                )

            ),

 

            format_currency(

                get_scenario_value(

                    selected_scenario,

                    "adjusted_expected_acv_usd"

                )

            )

        ]

    })

 

 

        st.dataframe(

            strategy_data,

            hide_index=True,

            use_container_width=True

        )

 

 

# ---------------------------------------------------------

# PRODUCT RECOMMENDATIONS PAGE

# ---------------------------------------------------------

 

def display_product_recommendations(

    selected_scenario

):

 

    display_scenario_header(

        selected_scenario

    )

 

    st.markdown(

        "### Product Recommendations"

    )

 

    st.caption(

        "Products are ranked using estimated product TAM, "

        "historical win rate, average won ACV, historical "

        "wins and supporting evidence."

    )

 

    recommendations = get_product_recommendations(

        selected_scenario

    )

 

    if len(recommendations) == 0:

 

        st.info(

            "No product recommendations are available. "

            "Confirm that product_market_tam.csv is loaded "

            "and that the simulator generates "

            "product_recommendations_json."

        )

 

        return

 

    recommendation_columns = st.columns(

        len(recommendations)

    )

 

    for index, recommendation in enumerate(

        recommendations

    ):

 

        with recommendation_columns[index]:

            recommendation_rank = (

                recommendation.get(

                    "recommendation_rank",

                    index + 1

                )

            )

 

            product_name = recommendation.get(

                "product_name",

                "Product Not Available"

            )

 

            product_family = recommendation.get(

                "product_family",

                ""

            )

 

            recommendation_score = (

                recommendation.get(

                    "product_recommendation_score",

                    0

                )

            )

 

            product_tam = recommendation.get(

                "product_tam_value_usd",

                0

            )

 

            historical_win_rate = (

                recommendation.get(

                    "historical_win_rate",

                    0

                )

            )

 

            average_won_acv = (

                recommendation.get(

                    "average_won_acv_usd",

                    0

                )

            )

 

            historical_wins = recommendation.get(

                "historical_wins",

                0

            )

 

            historical_decisions = (

                recommendation.get(

                    "historical_decisions",

                    0

                )

            )

 

            product_addressable_accounts = (

                recommendation.get(

                    "product_addressable_accounts_est",

                    0

                )

            )

 

            evidence_status = recommendation.get(

                "evidence_status",

                "Evidence Not Available"

            )

 

            st.markdown(

                f"#### Option {recommendation_rank}"

            )

 

            st.markdown(

                f"### {product_name}"

            )

 

            if product_family:

 

                st.caption(

                    product_family

                )

 

            st.metric(

                label="Recommendation Score",

                value=format_score(

                    recommendation_score

                )

            )

 

            st.metric(

                label="Estimated Product TAM",

                value=format_currency(

                    product_tam

                )

            )

 

            supporting_metric_1, supporting_metric_2 = (

                st.columns(2)

            )

 

            with supporting_metric_1:

 

                st.metric(

                    label="Win Rate",

                    value=format_percentage(

                        historical_win_rate

                    )

                )

 

            with supporting_metric_2:

 

                st.metric(

                    label="Average ACV",

                    value=format_currency(

                        average_won_acv

                    )

                )

 

            st.write(

                "**Historical evidence:** "

                f"{int(historical_wins)} wins from "

                f"{int(historical_decisions)} decisions"

            )

 

            st.write(

                "**Product-addressable accounts:** "

                f"{int(product_addressable_accounts)}"

            )

 

            if evidence_status == (

                "Strong Segment Evidence"

            ):

 

                st.success(

                    evidence_status

                )

 

            elif evidence_status == (

                "Limited Segment Evidence"

            ):

 

                st.warning(

                    evidence_status

                )

 

            else:

 

                st.info(

                    evidence_status

                )

 

    st.divider()

 

    explanation_column, ranking_column = (

        st.columns(2)

    )

 

    with explanation_column:

 

        with st.expander(

            "Why Were These Products Recommended?",

            expanded=False

        ):

 

            for recommendation in recommendations:

 

                recommendation_rank = (

                    recommendation.get(

                        "recommendation_rank",

                        ""

                    )

                )

 

                product_name = recommendation.get(

                    "product_name",

                    "Product Not Available"

                )

 

                recommendation_reason = (

                    recommendation.get(

                        "recommendation_reason",

                        "Recommendation explanation "

                        "is not available."

                    )

                )

 

                st.markdown(

                    f"**Option {recommendation_rank}: "

                    f"{product_name}**"

                )

 

                st.write(

                    recommendation_reason

                )

 

    with ranking_column:

 

        with st.expander(

            "View Recommendation Ranking",

            expanded=False

        ):

 

            ranking_data = pd.DataFrame(

                recommendations

            )

 

            ranking_columns = [

                "recommendation_rank",

                "product_name",

                "product_tam_value_usd",

                "historical_decisions",

                "historical_wins",

                "historical_win_rate",

                "average_won_acv_usd",

                "product_recommendation_score",

                "evidence_status"

            ]

 

            available_columns = [

                column

                for column in ranking_columns

                if column in ranking_data.columns

            ]

 

            ranking_display = ranking_data[

                available_columns

            ].copy()

 

            if "product_tam_value_usd" in ranking_display:

 

                ranking_display[

                    "product_tam_value_usd"

                ] = ranking_display[

                    "product_tam_value_usd"

                ].apply(

                    format_currency

                )

 

            if "historical_win_rate" in ranking_display:

 

                ranking_display[

                    "historical_win_rate"

                ] = ranking_display[

                    "historical_win_rate"

                ].apply(

                    format_percentage

                )

 

            if "average_won_acv_usd" in ranking_display:

 

                ranking_display[

                    "average_won_acv_usd"

                ] = ranking_display[

                    "average_won_acv_usd"

                ].apply(

                    format_currency

                )

 

            ranking_display = ranking_display.rename(

                columns={

                    "recommendation_rank":

                        "Rank",

                    "product_name":

                        "Product",

                    "product_tam_value_usd":

                        "Product TAM",

                    "historical_decisions":

                        "Decisions",

                    "historical_wins":

                        "Wins",

                    "historical_win_rate":

                        "Win Rate",

                    "average_won_acv_usd":

                        "Average Won ACV",

                    "product_recommendation_score":

                        "Score",

                    "evidence_status":

                        "Evidence"

                }

            )

 

            st.dataframe(

                ranking_display,

                hide_index=True,

                use_container_width=True

            )

 

def display_priority_accounts(

    selected_scenario,

    source_data

):

 

    display_scenario_header(

        selected_scenario

    )

 

    st.markdown(

        "### Priority Accounts"

    )

 

    st.caption(

        "Focus accounts are ranked using propensity-calibrated "

        "win probability and expected ACV contribution. "

        "Account-level expected ACV reconciles to the "

        "scenario-level Projected New ACV."

    )

 

    priority_accounts = get_priority_accounts(

        selected_scenario,

        source_data

    )

 

    if len(priority_accounts) == 0:

 

        st.info(

            "No focus accounts were found for the selected "

            "market and propensity threshold."

        )

 

        return

 

    scenario_projected_acv = float(

        get_scenario_value(

            selected_scenario,

            "projected_revenue_usd",

            0

        )

    )

 

    account_expected_acv = float(

        priority_accounts[

            "expected_acv_contribution_usd"

        ].sum()

    )

 

    reconciliation_variance = (

        account_expected_acv

        - scenario_projected_acv

    )

 

    account_probability_total = float(

        priority_accounts[

            "account_win_probability"

        ].sum()

    )

 

    expected_customers_won = float(

        get_scenario_value(

            selected_scenario,

            "expected_customers_won",

            0

        )

    )

 

    # -----------------------------------------------------

    # SUMMARY METRICS

    # -----------------------------------------------------

 

    metric_1, metric_2, metric_3, metric_4 = (

        st.columns(4)

    )

 

    with metric_1:

 

        st.metric(

            label="Focus Accounts",

            value=len(priority_accounts)

        )

 

    with metric_2:

 

        st.metric(

            label="Expected Customers Won",

            value=f"{account_probability_total:.1f}"

        )

 

    with metric_3:

 

        st.metric(

            label="Account-Level Expected ACV",

            value=format_currency(

                account_expected_acv

            )

        )

 

    with metric_4:

 

        st.metric(

            label="Reconciliation Variance",

            value=format_currency(

                reconciliation_variance

            )

        )

 

    # -----------------------------------------------------

    # RECONCILIATION STATUS

    # -----------------------------------------------------

 

    expected_win_variance = (

        account_probability_total

        - expected_customers_won

    )

 

    if (

        abs(reconciliation_variance) < 0.01

        and abs(expected_win_variance) < 0.01

    ):

 

        st.success(

            "Account-level allocation is fully reconciled. "

            f"The {len(priority_accounts):,} focus accounts "

            f"sum to {format_currency(account_expected_acv)}, "

            "matching the scenario Projected New ACV."

        )

 

    else:

 

        st.warning(

            "The account-level allocation contains a "

            "reconciliation difference. Review the account "

            "allocation logic before using the output."

        )

 

    st.divider()

 

    # -----------------------------------------------------

    # PRIORITY BAND SUMMARY

    # -----------------------------------------------------

 

    st.markdown(

        "#### Priority Distribution"

    )

 

    priority_summary = (

        priority_accounts

        .groupby(

            "priority_band",

            as_index=False

        )

        .agg(

            account_count=(

                "account_id",

                "count"

            ),

 

            expected_customers_won=(

                "account_win_probability",

                "sum"

            ),

 

            expected_acv_contribution_usd=(

                "expected_acv_contribution_usd",

                "sum"

            )

        )

    )

 

    priority_order = {

        "Priority 1": 1,

        "Priority 2": 2,

        "Priority 3": 3

    }

 

    priority_summary[

        "priority_sort"

    ] = priority_summary[

        "priority_band"

    ].map(

        priority_order

    )

 

    priority_summary = (

        priority_summary

        .sort_values(

            "priority_sort"

        )

        .drop(

            columns=[

                "priority_sort"

            ]

        )

    )

 

    priority_summary[

        "expected_acv_share_pct"

    ] = (

        priority_summary[

            "expected_acv_contribution_usd"

        ]

        / account_expected_acv

        if account_expected_acv > 0

        else 0

    )

 

    summary_display = (

        priority_summary.copy()

    )

 

    summary_display[

        "expected_acv_share_pct"

    ] = (

        summary_display[

            "expected_acv_share_pct"

        ]

        * 100

    )

 

    summary_display[

        "expected_customers_won"

    ] = summary_display[

        "expected_customers_won"

    ].round(1)

 

    st.dataframe(

        summary_display,

        hide_index=True,

        use_container_width=True,

        column_config={

            "priority_band":

                st.column_config.TextColumn(

                    "Priority Band"

                ),

 

            "account_count":

                st.column_config.NumberColumn(

                    "Accounts",

                    format="%d"

                ),

 

            "expected_customers_won":

                st.column_config.NumberColumn(

                    "Expected Wins",

                    format="%.1f"

                ),

 

            "expected_acv_contribution_usd":

                st.column_config.NumberColumn(

                    "Expected ACV",

                    format="$%,.0f"

                ),

 

            "expected_acv_share_pct":

                st.column_config.NumberColumn(

                    "ACV Share",

                    format="%.1f%%"

                )

        }

    )

 

    st.divider()

 

    # -----------------------------------------------------

    # ACCOUNT FILTERS

    # -----------------------------------------------------

 

    st.markdown(

        "#### Account-Level Detail"

    )

 

    filter_1, filter_2, filter_3, filter_4 = (

        st.columns(4)

    )

 

    with filter_1:

 

        priority_band_options = [

            "All"

        ] + (

            priority_accounts[

                "priority_band"

            ]

            .dropna()

            .unique()

            .tolist()

        )

 

        selected_priority_band = st.selectbox(

            "Priority Band",

            priority_band_options,

            key=(

                "priority_account_band_filter_"

                + str(

                    get_scenario_value(

                        selected_scenario,

                        "scenario_id",

                        ""

                    )

                )

            )

        )

 

    with filter_2:

 

        customer_options = [

            "All"

        ] + sorted(

            priority_accounts[

                "current_customer_flag"

            ]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

 

        selected_customer_flag = st.selectbox(

            "Current Customer",

            customer_options,

            key=(

                "priority_customer_filter_"

                + str(

                    get_scenario_value(

                        selected_scenario,

                        "scenario_id",

                        ""

                    )

                )

            )

        )

 

    with filter_3:

 

        tier_options = [

            "All"

        ] + sorted(

            priority_accounts[

                "account_tier"

            ]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

 

        selected_account_tier = st.selectbox(

            "Account Tier",

            tier_options,

            key=(

                "priority_tier_filter_"

                + str(

                    get_scenario_value(

                        selected_scenario,

                        "scenario_id",

                        ""

                    )

                )

            )

        )

 

    with filter_4:

 

        owner_options = [

            "All"

        ] + sorted(

            priority_accounts[

                "owner_type"

            ]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )

 

        selected_owner_type = st.selectbox(

            "Owner Type",

            owner_options,

            key=(

                "priority_owner_filter_"

                + str(

                    get_scenario_value(

                        selected_scenario,

                        "scenario_id",

                        ""

                    )

                )

            )

        )

 

    filtered_priority_accounts = (

        priority_accounts.copy()

    )

 

    if selected_priority_band != "All":

 

        filtered_priority_accounts = (

            filtered_priority_accounts[

                filtered_priority_accounts[

                    "priority_band"

                ]

                == selected_priority_band

            ]

        )

 

    if selected_customer_flag != "All":

 

        filtered_priority_accounts = (

            filtered_priority_accounts[

                filtered_priority_accounts[

                    "current_customer_flag"

                ].astype(str)

                == selected_customer_flag

            ]

        )

 

    if selected_account_tier != "All":

 

        filtered_priority_accounts = (

            filtered_priority_accounts[

                filtered_priority_accounts[

                    "account_tier"

                ].astype(str)

                == selected_account_tier

            ]

        )

 

    if selected_owner_type != "All":

 

        filtered_priority_accounts = (

            filtered_priority_accounts[

                filtered_priority_accounts[

                    "owner_type"

                ].astype(str)

                == selected_owner_type

            ]

        )

 

    st.caption(

        f"Showing {len(filtered_priority_accounts):,} "

        f"of {len(priority_accounts):,} focus accounts."

    )

 

    # -----------------------------------------------------

    # ACCOUNT TABLE

    # -----------------------------------------------------

 

    display_columns = [

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

        "account_tier",

        "current_customer_flag",

        "strategic_account_flag",

        "propensity_score",

        "digital_maturity_score",

        "data_intensity_score",

        "sales_coverage_flag",

        "owner_type",

        "account_win_probability",

        "estimated_account_acv_usd",

        "expected_acv_contribution_usd",

        "expected_acv_share_pct",

        "cumulative_expected_acv_pct",

        "recommended_product_1",

        "recommended_product_2",

        "recommended_product_3"

    ]

 

    available_display_columns = [

        column

        for column in display_columns

        if column

        in filtered_priority_accounts.columns

    ]

 

    priority_display = (

        filtered_priority_accounts[

            available_display_columns

        ].copy()

    )

 

    priority_display[

        "account_win_probability"

    ] = (

        priority_display[

            "account_win_probability"

        ]

        * 100

    )

 

    priority_display[

        "expected_acv_share_pct"

    ] = (

        priority_display[

            "expected_acv_share_pct"

        ]

        * 100

    )

 

    priority_display = priority_display.rename(

        columns={

            "priority_rank":

                "Priority Rank",

 

            "priority_band":

                "Priority Band",

 

            "account_id":

                "Account ID",

 

            "account_name":

                "Account Name",

 

            "account_type":

                "Account Type",

 

            "industry":

                "Industry",

 

            "geography":

                "Geography",

 

            "country":

                "Country",

 

            "region":

                "Region",

 

            "company_size":

                "Company Size",

 

            "account_tier":

                "Account Tier",

 

            "current_customer_flag":

                "Current Customer",

 

            "strategic_account_flag":

                "Strategic Account",

 

            "propensity_score":

                "Propensity Score",

 

            "digital_maturity_score":

                "Digital Maturity",

 

            "data_intensity_score":

                "Data Intensity",

 

            "sales_coverage_flag":

                "Sales Coverage",

 

            "owner_type":

                "Owner Type",

 

            "account_win_probability":

                "Win Probability",

 

            "estimated_account_acv_usd":

                "Gross ACV Potential",

 

            "expected_acv_contribution_usd":

                "Expected ACV Contribution",

 

            "expected_acv_share_pct":

                "Expected ACV Share",

 

            "cumulative_expected_acv_pct":

                "Cumulative ACV Share",

 

            "recommended_product_1":

                "Recommended Product 1",

 

            "recommended_product_2":

                "Recommended Product 2",

 

            "recommended_product_3":

                "Recommended Product 3"

        }

    )

 

    st.dataframe(

        priority_display,

        hide_index=True,

        use_container_width=True,

        height=520,

        column_config={

            "Priority Rank":

                st.column_config.NumberColumn(

                    format="%d",

                    width="small"

                ),

 

            "Propensity Score":

                st.column_config.ProgressColumn(

                    min_value=0,

                    max_value=100,

                    format="%d"

                ),

 

            "Win Probability":

                st.column_config.NumberColumn(

                    format="%.1f%%"

                ),

 

            "Gross ACV Potential":

                st.column_config.NumberColumn(

                    format="$%,.0f"

                ),

 

            "Expected ACV Contribution":

                st.column_config.NumberColumn(

                    format="$%,.0f"

                ),

 

            "Expected ACV Share":

                st.column_config.NumberColumn(

                    format="%.2f%%"

                ),

 

            "Cumulative ACV Share":

                st.column_config.ProgressColumn(

                    min_value=0,

                    max_value=1,

                    format="%.1f%%"

                )

        }

    )

 

    # -----------------------------------------------------

    # DOWNLOADS

    # -----------------------------------------------------

 

    download_column_1, download_column_2 = (

        st.columns(2)

    )

 

    full_account_csv = (

        priority_accounts

        .to_csv(

            index=False

        )

        .encode(

            "utf-8"

        )

    )

 

    filtered_account_csv = (

        filtered_priority_accounts

        .to_csv(

            index=False

        )

        .encode(

            "utf-8"

        )

    )

 

    scenario_id = str(

        get_scenario_value(

            selected_scenario,

            "scenario_id",

            "scenario"

        )

    )

 

    with download_column_1:

 

        st.download_button(

            label="Download All Priority Accounts",

            data=full_account_csv,

            file_name=(

                f"{scenario_id}_priority_accounts.csv"

            ),

            mime="text/csv",

            use_container_width=True,

            key=(

                f"download_all_priority_{scenario_id}"

            )

        )

 

    with download_column_2:

 

        st.download_button(

            label="Download Filtered Accounts",

            data=filtered_account_csv,

            file_name=(

                f"{scenario_id}_filtered_priority_accounts.csv"

            ),

            mime="text/csv",

            use_container_width=True,

            key=(

                f"download_filtered_priority_"

                f"{scenario_id}"

            )

        )

 

# ---------------------------------------------------------

# COMMERCIAL PERFORMANCE PAGE

# ---------------------------------------------------------

 

def display_commercial_performance(

    selected_scenario

):

 

    display_scenario_header(

        selected_scenario

    )

 

    st.markdown(

        "### Commercial Performance"

    )

 

    win_rate_column, acv_column = (

        st.columns(2)

    )

 

    with win_rate_column:

 

        st.markdown(

            "#### Win Rate"

        )

 

        win_rate_metric_1, win_rate_metric_2 = (

            st.columns(2)

        )

 

        with win_rate_metric_1:

 

            st.metric(

                label="Historical Win Rate",

                value=format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "historical_win_rate"

                    )

                )

            )

 

        with win_rate_metric_2:

 

            st.metric(

                label="Adjusted Win Rate",

                value=format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "adjusted_win_rate"

                    )

                ),

                delta=format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "effective_win_rate_adjustment"

                    )

                )

            )

 

        win_rate_data = pd.DataFrame({

            "Measure": [

                "Scenario Adjustment",

                "Discount Adjustment",

                "Effective Adjustment"

            ],

            "Value": [

                format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "scenario_win_rate_adjustment"

                    )

                ),

                format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "discount_win_rate_adjustment"

                    )

                ),

                format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "effective_win_rate_adjustment"

                    )

                )

            ]

        })

 

        st.dataframe(

            win_rate_data,

            hide_index=True,

            use_container_width=True

        )

 

    with acv_column:

 

        st.markdown(

            "#### Annual Contract Value"

        )

 

        acv_metric_1, acv_metric_2 = (

            st.columns(2)

        )

 

        with acv_metric_1:

 

            st.metric(

                label="Historical Expected ACV",

                value=format_currency(

                    get_scenario_value(

                        selected_scenario,

                        "historical_expected_acv_usd"

                    )

                )

            )

 

        with acv_metric_2:

 

            st.metric(

                label="Adjusted Expected ACV",

                value=format_currency(

                    get_scenario_value(

                        selected_scenario,

                        "adjusted_expected_acv_usd"

                    )

                )

            )

 

            product_strategy = get_scenario_value(

                selected_scenario,

                "product_strategy",

                ""

            )

 

            pricing_assumption = get_scenario_value(

                selected_scenario,

                "pricing_assumption",

                "Scenario Discount"

            )

 

            historical_discount = get_scenario_value(

                selected_scenario,

                "historical_discount_pct",

                0

            )

 

            scenario_discount = get_scenario_value(

                selected_scenario,

                "scenario_discount_pct",

                0

            )

 

            if (

                str(product_strategy)

                .strip()

                .lower()

                == "bundle"

            ):

 

                bundle_uplift_display = (

                    format_percentage(

                        get_scenario_value(

                            selected_scenario,

                            "observed_bundle_acv_uplift"

                        )

                    )

                )

 

                bundle_status = "Applied"

 

            else:

 

                bundle_uplift_display = (

                    "Not Applied"

                )

 

                bundle_status = (

                    "Single Product Strategy"

                )

 

 

            acv_data = pd.DataFrame({

                "Measure": [

                    "Pricing Assumption",

                    "Historical Discount",

                    "Scenario Discount",

                    "Discount-Adjusted ACV",

                    "Discount ACV Impact",

                    "Bundle ACV Uplift",

                    "Bundle Uplift Status",

                    "Effective ACV Adjustment"

                ],

                "Value": [

                    pricing_assumption,

 

                    format_percentage(

                        historical_discount

                    ),

 

                    format_percentage(

                        scenario_discount

                    ),

 

                    format_currency(

                        get_scenario_value(

                            selected_scenario,

                            "discount_adjusted_acv_usd"

                        )

                    ),

 

                    format_currency(

                        get_scenario_value(

                            selected_scenario,

                            "discount_acv_impact_usd"

                        )

                    ),

 

                    bundle_uplift_display,

 

                    bundle_status,

 

                    format_percentage(

                        get_scenario_value(

                            selected_scenario,

                            "effective_acv_adjustment"

                        )

                    )

                ]

            })

 

        st.dataframe(

            acv_data,

            hide_index=True,

            use_container_width=True

        )

 

    st.divider()

 

    revenue_metric_1, revenue_metric_2, revenue_metric_3 = (

        st.columns(3)

    )

 

    with revenue_metric_1:

 

        st.metric(

            label="Expected Customers Won",

            value=(

                f"{float(get_scenario_value(

                    selected_scenario,

                    'expected_customers_won'

                )):.1f}"

            )

        )

 

    with revenue_metric_2:

 

        st.metric(

            label="Projected New ACV",

            value=format_currency(

                get_scenario_value(

                    selected_scenario,

                    "projected_revenue_usd"

                )

            )

        )

 

    with revenue_metric_3:

 

        st.metric(

            label="Required Pipeline",

            value=format_currency(

                get_scenario_value(

                    selected_scenario,

                    "required_pipeline_usd"

                )

            )

        )

 

 

# ---------------------------------------------------------

# CAPACITY AND RISK PAGE

# ---------------------------------------------------------

 

def display_capacity_and_risk(

    selected_scenario

):

 

    display_scenario_header(

        selected_scenario

    )

 

    capacity_column, risk_column = (

        st.columns(2)

    )

 

    with capacity_column:

 

        st.markdown(

            "### Sales Capacity"

        )

 

        capacity_metric_1, capacity_metric_2 = (

            st.columns(2)

        )

 

        with capacity_metric_1:

 

            st.metric(

                label="Required Hunters",

                value=int(

                    get_scenario_value(

                        selected_scenario,

                        "required_hunters"

                    )

                )

            )

 

        with capacity_metric_2:

 

            st.metric(

                label="Available Hunters",

                value=int(

                    get_scenario_value(

                        selected_scenario,

                        "available_hunters"

                    )

                )

            )

 

        capacity_data = pd.DataFrame({

            "Measure": [

                "Accounts per Hunter",

                "Additional Hunters Required",

                "Surplus Hunters",

                "Capacity Status"

            ],

            "Value": [

                get_scenario_value(

                    selected_scenario,

                    "accounts_per_hunter"

                ),

                int(

                    get_scenario_value(

                        selected_scenario,

                        "additional_hunters_required"

                    )

                ),

                int(

                    get_scenario_value(

                        selected_scenario,

                        "surplus_hunters"

                    )

                ),

                get_scenario_value(

                    selected_scenario,

                    "capacity_status",

                    "Not Available"

                )

            ]

        })

 

        st.dataframe(

            capacity_data,

            hide_index=True,

            use_container_width=True

        )

 

    with risk_column:

 

        st.markdown(

            "### Risk Assessment"

        )

 

        risk_metric_1, risk_metric_2 = (

            st.columns(2)

        )

 

        with risk_metric_1:

 

            st.metric(

                label="Risk Score",

                value=(

                    f"{int(get_scenario_value(

                        selected_scenario,

                        'risk_score'

                    ))}/100"

                )

            )

 

        with risk_metric_2:

 

            st.metric(

                label="Confidence Level",

                value=get_scenario_value(

                    selected_scenario,

                    "confidence_level",

                    "Not Available"

                )

            )

 

        capacity_status = get_scenario_value(

            selected_scenario,

            "capacity_status",

            ""

        )

 

        if capacity_status == "Capacity Shortfall":

 

            st.warning(

                "The selected scenario requires "

                "additional hunter capacity."

            )

 

        elif capacity_status == "Capacity Balanced":

 

            st.info(

                "Available capacity matches the "

                "scenario requirement."

            )

 

        else:

 

            st.success(

                "Existing hunter capacity is sufficient "

                "for the selected scenario."

            )

 

        st.markdown(

            "#### Execution Context"

        )

 

        st.write(

            "Focus accounts: "

            f"**{int(get_scenario_value(

                selected_scenario,

                'focus_accounts'

            ))}**"

        )

 

        st.write(

            "Expected customers won: "

            f"**{float(get_scenario_value(

                selected_scenario,

                'expected_customers_won'

            )):.1f}**"

        )

 

        st.write(

            "Required pipeline: "

            f"**{format_currency(get_scenario_value(

                selected_scenario,

                'required_pipeline_usd'

            ))}**"

        )

 

 

# ---------------------------------------------------------

# MODEL DETAILS PAGE

# ---------------------------------------------------------

 

def display_model_details(

    selected_scenario

):

 

    display_scenario_header(

        selected_scenario

    )

 

    evidence_column, assumption_column = (

        st.columns(2)

    )

 

    with evidence_column:

 

        st.markdown(

            "### Model Evidence"

        )

 

        evidence_data = pd.DataFrame({

            "Measure": [

                "Bundle Evidence",

                "Discount Band",

                "Discount Evidence",

                "Historical Opportunities",

                "Product Recommendation Count"

            ],

            "Value": [

                get_scenario_value(

                    selected_scenario,

                    "bundle_uplift_evidence",

                    "Not Available"

                ),

                get_scenario_value(

                    selected_scenario,

                    "scenario_discount_band",

                    "Not Available"

                ),

                get_scenario_value(

                    selected_scenario,

                    "discount_evidence_status",

                    "Not Available"

                ),

                int(

                    get_scenario_value(

                        selected_scenario,

                        "historical_opportunities"

                    )

                ),

                int(

                    get_scenario_value(

                        selected_scenario,

                        "product_recommendation_count"

                    )

                )

            ]

        })

 

        st.dataframe(

            evidence_data,

            hide_index=True,

            use_container_width=True

        )

 

    with assumption_column:

 

        st.markdown(

            "### Model Assumptions"

        )

 

        assumptions_data = pd.DataFrame({

            "Measure": [

                "Propensity Threshold",

                "Scenario Discount",

                "Scenario Win Rate Adjustment",

                "Observed Bundle Uplift",

                "Effective ACV Adjustment",

                "Investment Amount"

            ],

            "Value": [

                int(

                    get_scenario_value(

                        selected_scenario,

                        "propensity_threshold"

                    )

                ),

                format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "scenario_discount_pct"

                    )

                ),

                format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "scenario_win_rate_adjustment"

                    )

                ),

                format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "observed_bundle_acv_uplift"

                    )

                ),

                format_percentage(

                    get_scenario_value(

                        selected_scenario,

                        "effective_acv_adjustment"

                    )

                ),

                format_currency(

                    get_scenario_value(

                        selected_scenario,

                        "investment_amount_usd"

                    )

                )

            ]

        })

 

        st.dataframe(

            assumptions_data,

            hide_index=True,

            use_container_width=True

        )

 

    with st.expander(

        "View Complete Simulation Output",

        expanded=False

    ):

 

        complete_output = pd.DataFrame(

            [dict(selected_scenario)]

        )

 

        st.dataframe(

            complete_output,

            hide_index=True,

            use_container_width=True

        )

 

 

# ---------------------------------------------------------

# SCENARIO COMPARISON PAGE

# ---------------------------------------------------------

 

def display_scenario_comparison(

    predefined_results

):

 

    st.subheader(

        "Scenario Comparison"

    )

 

    comparison_summary = predefined_results[

        [

            "scenario_name",

            "projected_revenue_usd"

        ]

    ].copy()

 

    comparison_summary = comparison_summary.set_index(

        "scenario_name"

    )

 

    st.bar_chart(

        comparison_summary,

        y="projected_revenue_usd",

        use_container_width=True

    )

 

    comparison_columns = [

        "scenario_id",

        "scenario_name",

        "industry",

        "geography",

        "company_size",

        "product_strategy",

        "propensity_threshold",

        "focus_accounts",

        "adjusted_win_rate",

        "adjusted_expected_acv_usd",

        "projected_revenue_usd",

        "required_pipeline_usd",

        "capacity_status",

        "risk_score",

        "confidence_level"

    ]

 

    available_columns = [

        column

        for column in comparison_columns

        if column in predefined_results.columns

    ]

 

    comparison_display = predefined_results[

        available_columns

    ].copy()

 

    if "adjusted_win_rate" in comparison_display:

 

        comparison_display[

            "adjusted_win_rate"

        ] = comparison_display[

            "adjusted_win_rate"

        ].apply(

            format_percentage

        )

 

    if "adjusted_expected_acv_usd" in comparison_display:

 

        comparison_display[

            "adjusted_expected_acv_usd"

        ] = comparison_display[

            "adjusted_expected_acv_usd"

        ].apply(

            format_currency

        )

 

    if "projected_revenue_usd" in comparison_display:

 

        comparison_display[

            "projected_revenue_usd"

        ] = comparison_display[

            "projected_revenue_usd"

        ].apply(

            format_currency

        )

 

    if "required_pipeline_usd" in comparison_display:

 

        comparison_display[

            "required_pipeline_usd"

        ] = comparison_display[

            "required_pipeline_usd"

        ].apply(

            format_currency

        )

 

    st.dataframe(

        comparison_display,

        hide_index=True,

        use_container_width=True

    )

 

    csv_output = predefined_results.to_csv(

        index=False

    ).encode(

        "utf-8"

    )

 

    st.download_button(

        label="Download All Scenario Results",

        data=csv_output,

        file_name="simulation_outputs.csv",

        mime="text/csv",

        use_container_width=True

    )

 

 

# ---------------------------------------------------------

# CUSTOM SCENARIO FORM

# ---------------------------------------------------------

 

def display_custom_scenario_form(

    source_data

):

 

    account_data = source_data[

        "accounts"

    ]

 

    industry_options = sorted(

        account_data["industry"]

        .dropna()

        .unique()

        .tolist()

    )

 

    geography_options = sorted(

        account_data["geography"]

        .dropna()

        .unique()

        .tolist()

    )

 

    company_size_options = sorted(

        account_data["company_size"]

        .dropna()

        .unique()

        .tolist()

    )

 

    industry_options.insert(

        0,

        "All"

    )

 

    geography_options.insert(

        0,

        "All"

    )

 

    company_size_options.insert(

        0,

        "All"

    )

 

    st.sidebar.header(

        "Build Custom Scenario"

    )

 

    st.sidebar.caption(

        "Select the market and commercial assumptions, "

        "then run the simulation."

    )

 

    # -----------------------------------------------------

    # MARKET AND STRATEGY FORM

    # -----------------------------------------------------

 

    with st.sidebar.form(

        "custom_scenario_form"

    ):

 

        scenario_name = st.text_input(

            "Scenario Name",

            value="My Custom Growth Scenario"

        )

 

        st.markdown(

            "#### Market Selection"

        )

 

        industry = st.selectbox(

            "Industry",

            industry_options

        )

 

        geography = st.selectbox(

            "Geography",

            geography_options

        )

 

        company_size = st.selectbox(

            "Company Size",

            company_size_options

        )

 

        propensity_threshold = st.slider(

            "Minimum Propensity Score",

            min_value=40,

            max_value=95,

            value=70,

            step=5

        )

 

        st.markdown(

            "#### Commercial Strategy"

        )

 

        product_strategy = st.selectbox(

            "Product Strategy",

            [

                "Single Product",

                "Bundle"

            ]

        )

 

        sales_motion = st.selectbox(

            "Sales Motion",

            [

                "Direct",

                "Partner",

                "Inside Sales"

            ]

        )

 

        investment_amount = st.number_input(

            "Investment Amount ($)",

            min_value=0,

            value=1_000_000,

            step=100_000

        )

 

        st.markdown(

            "#### Scenario Adjustments"

        )

 

        win_rate_adjustment = st.slider(

            "Manual Win Rate Adjustment",

            min_value=-10,

            max_value=10,

            value=0,

            step=1,

            help=(

                "Percentage-point adjustment applied "

                "manually to the historical win rate."

            )

        )

 

        acv_adjustment = st.slider(

            "Manual ACV Adjustment",

            min_value=-20,

            max_value=25,

            value=0,

            step=1,

            help=(

                "Used mainly for Single Product scenarios. "

                "Bundle scenarios use the observed bundle "

                "uplift calculated from ownership data."

            )

        )

 

        save_scenario_inputs = st.form_submit_button(

            "Apply Scenario Inputs",

            use_container_width=True

        )

 

    # -----------------------------------------------------

    # SAVE FORM INPUTS IN SESSION STATE

    # -----------------------------------------------------

 

    if save_scenario_inputs:

 

        st.session_state[

            "custom_scenario_inputs"

        ] = {

            "scenario_name":

                scenario_name,

 

            "industry":

                industry,

 

            "geography":

                geography,

 

            "company_size":

                company_size,

 

            "propensity_threshold":

                propensity_threshold,

 

            "product_strategy":

                product_strategy,

 

            "sales_motion":

                sales_motion,

 

            "investment_amount":

                investment_amount,

 

            "win_rate_adjustment":

                win_rate_adjustment,

 

            "acv_adjustment":

                acv_adjustment

        }

 

    # -----------------------------------------------------

    # USE CURRENT OR SAVED FORM INPUTS

    # -----------------------------------------------------

 

    if (

        "custom_scenario_inputs"

        not in st.session_state

    ):

 

        st.session_state[

            "custom_scenario_inputs"

        ] = {

            "scenario_name":

                scenario_name,

 

            "industry":

                industry,

 

            "geography":

                geography,

 

            "company_size":

                company_size,

 

            "propensity_threshold":

                propensity_threshold,

 

            "product_strategy":

                product_strategy,

 

            "sales_motion":

                sales_motion,

 

            "investment_amount":

                investment_amount,

 

            "win_rate_adjustment":

                win_rate_adjustment,

 

            "acv_adjustment":

                acv_adjustment

        }

 

    scenario_inputs = st.session_state[

        "custom_scenario_inputs"

    ]

 

    # -----------------------------------------------------

    # PRICING CONTROLS OUTSIDE THE FORM

    # -----------------------------------------------------

 

    st.sidebar.markdown(

        "#### Pricing Strategy"

    )

 

    pricing_assumption = st.sidebar.selectbox(

        "Pricing Assumption",

        [

            "Use Historical Discount",

            "Set Custom Discount"

        ],

        key="custom_pricing_assumption",

        help=(

            "Use Historical Discount keeps pricing equal "

            "to the historical average for the selected "

            "market. Set Custom Discount lets you test a "

            "different customer discount."

        )

    )

 

    custom_discount_pct = st.sidebar.slider(

        "Custom Discount Percentage",

        min_value=0,

        max_value=35,

        value=10,

        step=1,

        key="custom_discount_percentage",

        disabled=(

            pricing_assumption

            == "Use Historical Discount"

        ),

        help=(

            "Available only when Set Custom Discount is "

            "selected. Zero means no customer discount."

        )

    )

 

    if (

        pricing_assumption

        == "Use Historical Discount"

    ):

 

        historical_segment_discount = (

            get_historical_discount_for_selection(

                source_data["opportunities"],

                scenario_inputs["industry"],

                scenario_inputs["geography"],

                scenario_inputs["company_size"]

            )

        )

 

        st.sidebar.caption(

            "Historical discount for selected market: "

            f"{format_percentage(

                historical_segment_discount

            )}"

        )

 

    else:

 

        historical_segment_discount = (

            get_historical_discount_for_selection(

                source_data["opportunities"],

                scenario_inputs["industry"],

                scenario_inputs["geography"],

                scenario_inputs["company_size"]

            )

        )

 

        st.sidebar.caption(

            "Selected custom discount: "

            f"{custom_discount_pct:.1f}%"

        )

 

    # -----------------------------------------------------

    # RUN SIMULATION BUTTON OUTSIDE THE FORM

    # -----------------------------------------------------

 

    run_scenario = st.sidebar.button(

        "Run Simulation",

        use_container_width=True,

        type="primary"

    )

 

    # -----------------------------------------------------

    # RUN CUSTOM SCENARIO

    # -----------------------------------------------------

 

    if run_scenario:

 

        if (

            pricing_assumption

            == "Use Historical Discount"

        ):

 

            scenario_discount = (

                historical_segment_discount

            )

 

        else:

 

            scenario_discount = (

                custom_discount_pct / 100

            )

 

        custom_scenario = pd.DataFrame([

            {

                "scenario_id":

                    "CUSTOM001",

 

                "scenario_name":

                    scenario_inputs[

                        "scenario_name"

                    ],

 

                "industry":

                    scenario_inputs[

                        "industry"

                    ],

 

                "geography":

                    scenario_inputs[

                        "geography"

                    ],

 

                "company_size":

                    scenario_inputs[

                        "company_size"

                    ],

 

                "buyer_persona":

                    "All",

 

                "product_strategy":

                    scenario_inputs[

                        "product_strategy"

                    ],

 

                "sales_motion":

                    scenario_inputs[

                        "sales_motion"

                    ],

 

                "pricing_assumption":

                    pricing_assumption,

 

                "discount_pct":

                    scenario_discount,

 

                "investment_amount_usd":

                    scenario_inputs[

                        "investment_amount"

                    ],

 

                "hunter_capacity":

                    0,

 

                "farmer_capacity":

                    0,

 

                "target_win_rate_adjustment":

                    scenario_inputs[

                        "win_rate_adjustment"

                    ] / 100,

 

                "target_acv_adjustment":

                    scenario_inputs[

                        "acv_adjustment"

                    ] / 100,

 

                "pipeline_coverage_ratio":

                    3.5,

 

                "propensity_threshold":

                    scenario_inputs[

                        "propensity_threshold"

                    ]

            }

        ])

 

        custom_results = run_simulation(

            custom_scenarios=custom_scenario

        )

 

        if len(custom_results) > 0:

 

            custom_result = custom_results[0]

 

            custom_result[

                "pricing_assumption"

            ] = pricing_assumption

 

            custom_result[

                "historical_segment_discount"

            ] = historical_segment_discount

 

            st.session_state[

                "custom_result"

            ] = custom_result

 

            st.session_state[

                "custom_simulation_completed"

            ] = True

 

        else:

 

            st.sidebar.error(

                "The simulation did not return a result. "

                "Please review the selected assumptions."

            )

 

# ---------------------------------------------------------

# APPLICATION DATA

# ---------------------------------------------------------

 

source_data = load_source_data()

 

predefined_results = (

    load_predefined_simulations()

)

 

 

# ---------------------------------------------------------

# APPLICATION HEADER

# ---------------------------------------------------------

 

st.title(

    "Commercial Growth Simulator"

)

 

st.caption(

    "Commercial Digital Twin for forward-looking market, "

    "pricing, product, revenue and capacity decisions"

)

 

 

# ---------------------------------------------------------

# SIDEBAR

# ---------------------------------------------------------

 

simulation_mode = st.sidebar.radio(

    "Simulation Mode",

    [

        "Predefined Scenario",

        "Custom Scenario"

    ]

)

 

 

# ---------------------------------------------------------

# PREDEFINED SCENARIO MODE

# ---------------------------------------------------------

 

if simulation_mode == "Predefined Scenario":

 

    # -----------------------------------------------------

    # SCENARIO SELECTION

    # -----------------------------------------------------

 

    st.sidebar.header(

        "Scenario Selection"

    )

 

    selected_scenario_name = st.sidebar.selectbox(

        "Select a Scenario",

        predefined_results[

            "scenario_name"

        ].tolist()

    )

 

    selected_scenario = predefined_results[

        predefined_results["scenario_name"]

        == selected_scenario_name

    ].iloc[0]

 

    # -----------------------------------------------------

    # SIDEBAR SCENARIO ASSUMPTIONS

    # -----------------------------------------------------

 

    st.sidebar.divider()

 

    st.sidebar.subheader(

        "Scenario Assumptions"

    )

 

    st.sidebar.write(

        f"**Industry:** "

        f"{get_scenario_value(

            selected_scenario,

            'industry',

            'All'

        )}"

    )

 

    st.sidebar.write(

        f"**Geography:** "

        f"{get_scenario_value(

            selected_scenario,

            'geography',

            'All'

        )}"

    )

 

    st.sidebar.write(

        f"**Company Size:** "

        f"{get_scenario_value(

            selected_scenario,

            'company_size',

            'All'

        )}"

    )

 

    st.sidebar.write(

        f"**Product Strategy:** "

        f"{get_scenario_value(

            selected_scenario,

            'product_strategy',

            'Not Available'

        )}"

    )

 

    st.sidebar.write(

        f"**Sales Motion:** "

        f"{get_scenario_value(

            selected_scenario,

            'sales_motion',

            'Not Available'

        )}"

    )

 

    st.sidebar.write(

        f"**Propensity Threshold:** "

        f"{int(

            get_scenario_value(

                selected_scenario,

                'propensity_threshold',

                0

            )

        )}"

    )

 

    st.sidebar.write(

        f"**Scenario Discount:** "

        f"{format_percentage(

            get_scenario_value(

                selected_scenario,

                'scenario_discount_pct',

                0

            )

        )}"

    )

 

    # -----------------------------------------------------

    # SIDEBAR MARKET SUMMARY

    # -----------------------------------------------------

 

    st.sidebar.divider()

 

    st.sidebar.subheader(

        "Market Summary"

    )

 

    st.sidebar.write(

        f"**TAM:** "

        f"{format_currency(

            get_scenario_value(

                selected_scenario,

                'tam_usd',

                0

            )

        )}"

    )

 

    st.sidebar.write(

        f"**Addressable Accounts:** "

        f"{int(

            get_scenario_value(

                selected_scenario,

                'addressable_accounts',

                0

            )

        )}"

    )

 

    st.sidebar.write(

        f"**Focus Accounts:** "

        f"{int(

            get_scenario_value(

                selected_scenario,

                'focus_accounts',

                0

            )

        )}"

    )

 

    st.sidebar.write(

        f"**Projected New ACV:** "

        f"{format_currency(

            get_scenario_value(

                selected_scenario,

                'projected_revenue_usd',

                0

            )

        )}"

    )

 

    st.sidebar.write(

        f"**Confidence:** "

        f"{get_scenario_value(

            selected_scenario,

            'confidence_level',

            'Not Available'

        )}"

    )

 

    # -----------------------------------------------------

    # PREDEFINED SCENARIO TABS

    # -----------------------------------------------------

 

    (

        executive_tab,

        product_tab,

        priority_accounts_tab,

        capacity_tab,

        revenue_tab,

        comparison_tab,

        evidence_tab

    ) = st.tabs(

        [

            "Executive Summary",

            "Product Recommendations",

            "Priority Accounts",

            "Capacity & Risk",

            "Revenue Model",

            "Scenario Comparison",

            "Model Evidence"

        ]

    )

 

    with executive_tab:

 

        display_overview(

            selected_scenario

        )

 

    with product_tab:

 

        display_product_recommendations(

            selected_scenario

        )

 

    with priority_accounts_tab:

 

        display_priority_accounts(

            selected_scenario,

            source_data

        )

 

    with capacity_tab:

   

        display_capacity_and_risk(

            selected_scenario

        )

 

    with revenue_tab:

 

        display_commercial_performance(

            selected_scenario

        )

 

 

    with comparison_tab:

 

        display_scenario_comparison(

            predefined_results

        )

 

    with evidence_tab:

 

        display_model_details(

            selected_scenario

        )

 

 

# ---------------------------------------------------------

# CUSTOM SCENARIO MODE

# ---------------------------------------------------------

 

else:

 

    # -----------------------------------------------------

    # CUSTOM SCENARIO INPUTS IN SIDEBAR

    # -----------------------------------------------------

 

    display_custom_scenario_form(

        source_data

    )

 

    # -----------------------------------------------------

    # CUSTOM SCENARIO RESULT TABS

    # -----------------------------------------------------

 

    (

        results_tab,

        product_tab,

        priority_accounts_tab,

        capacity_tab,

        revenue_tab,

        evidence_tab

    ) = st.tabs(

        [

            "Executive Summary",

            "Product Recommendations",

            "Priority Accounts",

            "Capacity & Risk",

            "Revenue Model",

            "Model Evidence"

        ]

    )

 

    custom_result_available = (

        "custom_result"

        in st.session_state

    )

 

    # -----------------------------------------------------

    # EXECUTIVE SUMMARY TAB

    # -----------------------------------------------------

 

    with results_tab:

 

        if custom_result_available:

 

            custom_result = st.session_state[

                "custom_result"

            ]

 

            display_overview(

                custom_result

            )

 

            st.divider()

 

            custom_output = pd.DataFrame(

                [custom_result]

            )

 

            custom_csv = custom_output.to_csv(

                index=False

            ).encode(

                "utf-8"

            )

 

            st.download_button(

                label="Download Custom Scenario Result",

                data=custom_csv,

                file_name="custom_scenario_result.csv",

                mime="text/csv",

                use_container_width=True

            )

 

        else:

 

            st.info(

                "Select the custom scenario assumptions "

                "in the left sidebar and click "

                "Run Simulation to view the executive summary."

            )

 

    # -----------------------------------------------------

    # PRODUCT RECOMMENDATIONS TAB

    # -----------------------------------------------------

 

    with product_tab:

 

        if custom_result_available:

 

            display_product_recommendations(

                st.session_state[

                    "custom_result"

                ]

            )

 

        else:

 

            st.info(

                "Select the custom scenario assumptions "

                "in the left sidebar and click "

                "Run Simulation to view product recommendations."

            )

 

    # -----------------------------------------------------

    # EXECUTIVE SUMMARY TAB

    # -----------------------------------------------------

 

    with priority_accounts_tab:

 

        if custom_result_available:

 

            display_priority_accounts(

                st.session_state[

                    "custom_result"

                ],

                source_data

            )

 

        else:

 

            st.info(

                "Select the custom scenario assumptions "

                "in the left sidebar and click "

                "Run Simulation to view priority accounts."

            )

 

    # -----------------------------------------------------

        # CAPACITY AND RISK TAB

        # -----------------------------------------------------

   

        with capacity_tab:

   

            if custom_result_available:

   

                display_capacity_and_risk(

                    st.session_state[

                        "custom_result"

                    ]

                )

   

            else:

   

                st.info(

                    "Select the custom scenario assumptions "

                    "in the left sidebar and click "

                    "Run Simulation to view capacity and risk."

                )

 

    # -----------------------------------------------------

    # REVENUE MODEL TAB

    # -----------------------------------------------------

 

    with revenue_tab:

 

        if custom_result_available:

 

            display_commercial_performance(

                st.session_state[

                    "custom_result"

                ]

            )

 

        else:

 

            st.info(

                "Select the custom scenario assumptions "

                "in the left sidebar and click "

                "Run Simulation to view the revenue model."

            )

 

   

 

    # -----------------------------------------------------

    # MODEL EVIDENCE TAB

    # -----------------------------------------------------

 

    with evidence_tab:

 

        if custom_result_available:

 

            display_model_details(

                st.session_state[

                    "custom_result"

                ]

            )

 

        else:

 

            st.info(

                "Select the custom scenario assumptions "

                "in the left sidebar and click "

                "Run Simulation to view model evidence."

            )

 

    # -----------------------------------------------------

    # CUSTOM SCENARIO SIDEBAR SUMMARY

    # -----------------------------------------------------

 

    if custom_result_available:

 

        custom_result = st.session_state[

            "custom_result"

        ]

 

        st.sidebar.divider()

 

        st.sidebar.subheader(

            "Latest Simulation"

        )

 

        st.sidebar.write(

            f"**Scenario:** "

            f"{get_scenario_value(

                custom_result,

                'scenario_name',

                'Custom Scenario'

            )}"

        )

 

        st.sidebar.write(

            f"**Industry:** "

            f"{get_scenario_value(

                custom_result,

                'industry',

                'All'

            )}"

        )

 

        st.sidebar.write(

            f"**Geography:** "

            f"{get_scenario_value(

                custom_result,

                'geography',

                'All'

            )}"

        )

 

        st.sidebar.write(

            f"**Company Size:** "

            f"{get_scenario_value(

                custom_result,

                'company_size',

                'All'

            )}"

        )

 

        st.sidebar.write(

            f"**Product Strategy:** "

            f"{get_scenario_value(

                custom_result,

                'product_strategy',

                'Not Available'

            )}"

        )

 

        st.sidebar.write(

            f"**Propensity Threshold:** "

            f"{int(

                get_scenario_value(

                    custom_result,

                    'propensity_threshold',

                    0

                )

            )}"

        )

 

        st.sidebar.write(

            f"**Scenario Discount:** "

            f"{format_percentage(

                get_scenario_value(

                    custom_result,

                    'scenario_discount_pct',

                    0

                )

            )}"

        )

 

        st.sidebar.divider()

 

        st.sidebar.subheader(

            "Simulation Summary"

        )

 

        st.sidebar.write(

            f"**TAM:** "

            f"{format_currency(

                get_scenario_value(

                    custom_result,

                    'tam_usd',

                    0

                )

            )}"

        )

 

        st.sidebar.write(

            f"**Focus Accounts:** "

            f"{int(

                get_scenario_value(

                    custom_result,

                    'focus_accounts',

                    0

                )

            )}"

        )

 

        st.sidebar.write(

            f"**Projected New ACV:** "

            f"{format_currency(

                get_scenario_value(

                    custom_result,

                    'projected_revenue_usd',

                    0

                )

            )}"

        )

 

        st.sidebar.write(

            f"**Required Pipeline:** "

            f"{format_currency(

                get_scenario_value(

                    custom_result,

                    'required_pipeline_usd',

                    0

                )

            )}"

        )

 

        st.sidebar.write(

            f"**Confidence:** "

            f"{get_scenario_value(

                custom_result,

                'confidence_level',

                'Not Available'

            )}"

        )

 

        st.sidebar.divider()

 

        if st.sidebar.button(

            "Clear Simulation Result",

            use_container_width=True

        ):

 

            del st.session_state[

                "custom_result"

            ]

 

            if (

                "custom_simulation_completed"

                in st.session_state

            ):

 

                del st.session_state[

                    "custom_simulation_completed"

                ]

 

            st.rerun()