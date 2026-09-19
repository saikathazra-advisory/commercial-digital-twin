import json

 

from engine.loader import load_data

 

from engine.product_recommendations import (

    calculate_product_recommendations

)

 

from engine.strategy import (

    adjust_win_rate,

    adjust_expected_acv,

    calculate_bundle_acv_uplift,

    get_effective_acv_adjustment,

    calculate_historical_discount,

    calculate_discount_adjusted_acv,

    calculate_discount_acv_impact

)

 

from engine.pricing import (

    calculate_discount_band_win_rate,

    calculate_discount_win_rate_adjustment

)

 

from engine.scoring import (

    calculate_risk_score,

    calculate_confidence_level

)

 

from engine.calculations import (

    calculate_tam,

    get_addressable_accounts,

    get_focus_accounts,

    get_scenario_opportunities,

    calculate_win_rate,

    calculate_expected_acv,

    calculate_projected_revenue,

    calculate_required_pipeline,

    calculate_required_hunters,

    get_available_hunters,

    calculate_capacity_gap,

    get_accounts_per_hunter

)

 

def run_simulation(custom_scenarios=None):

 

    data = load_data()

 

    results = []

 

    if custom_scenarios is None:

        scenarios = data["scenarios"]

    else:

        scenarios = custom_scenarios

 

    for _, scenario in scenarios.iterrows():

 

        # Scenario identity

 

        scenario_id = scenario["scenario_id"]

        scenario_name = scenario["scenario_name"]

 

        # Market selections

 

        industry = scenario["industry"]

        geography = scenario["geography"]

        company_size = scenario["company_size"]

 

        product_recommendations = (

            calculate_product_recommendations(

                data["product_market_tam"],

                data["opportunities"],

                data["products"],

                industry,

                geography,

                company_size,

                top_n=3

            )

        )

 

        # Commercial strategy selections

 

        product_strategy = scenario[

            "product_strategy"

        ]

 

        sales_motion = scenario[

            "sales_motion"

        ]

 

        pricing_assumption = scenario.get(

            "pricing_assumption",

            "Set Custom Discount"

        )

 

        discount_pct = float(

            scenario["discount_pct"]

        )

 

        investment_amount = float(

            scenario["investment_amount_usd"]

        )

 

        # Scenario assumptions

 

        win_rate_adjustment = float(

            scenario["target_win_rate_adjustment"]

        )

 

        scenario_acv_adjustment = float(

            scenario["target_acv_adjustment"]

        )

 

        propensity_threshold = int(

            scenario["propensity_threshold"]

        )

 

        # Calculate TAM

 

        tam = calculate_tam(

            data["market"],

            industry,

            geography,

            company_size

        )

 

        # Calculate addressable accounts

 

        addressable_accounts = (

            get_addressable_accounts(

                data["accounts"],

                industry,

                geography,

                company_size

            )

        )

 

        # Calculate focus accounts

 

        focus_accounts = get_focus_accounts(

            addressable_accounts,

            propensity_threshold

        )

 

        # Filter historical opportunities

 

        historical_opportunities = (

            get_scenario_opportunities(

                data["opportunities"],

                industry,

                geography,

                company_size

            )

        )

 

        # Historical win rate

 

        # ---------------------------------------------------------

        # HISTORICAL PERFORMANCE BASELINE

        # ---------------------------------------------------------

 

        historical_win_rate = calculate_win_rate(

            historical_opportunities

        )

 

        historical_expected_acv = calculate_expected_acv(

            historical_opportunities

        )

 

        historical_discount = calculate_historical_discount(

            historical_opportunities

        )

 

        # ---------------------------------------------------------

        # DISCOUNT-BAND WIN-RATE EVIDENCE

        # ---------------------------------------------------------

 

        (

            discount_band_win_rate,

            scenario_discount_band,

            discount_band_decisions,

            discount_evidence_status

        ) = calculate_discount_band_win_rate(

            historical_opportunities,

            discount_pct

        )

 

        # ---------------------------------------------------------

        # DISCOUNT-RELATED WIN-RATE ADJUSTMENT

        # ---------------------------------------------------------

 

        discount_win_rate_adjustment = (

            calculate_discount_win_rate_adjustment(

                historical_win_rate,

                discount_band_win_rate,

                discount_evidence_status

            )

        )

 

        # If historical pricing is explicitly selected,

        # no discount-related win-rate adjustment should apply.

        if (

            pricing_assumption

            == "Use Historical Discount"

        ):

 

            discount_win_rate_adjustment = 0.0

 

        # Secondary safeguard:

        # if scenario discount is effectively equal to historical

        # discount, do not apply a discount-related adjustment.

        elif abs(

            float(discount_pct)

            - float(historical_discount)

        ) < 0.0005:

 

            discount_win_rate_adjustment = 0.0

 

        # ---------------------------------------------------------

        # FINAL WIN-RATE ADJUSTMENT

        # ---------------------------------------------------------

 

        effective_win_rate_adjustment = (

            win_rate_adjustment

            + discount_win_rate_adjustment

        )

 

        adjusted_win_rate = adjust_win_rate(

            historical_win_rate,

            effective_win_rate_adjustment

        )

 

        # Historical expected ACV

 

        historical_expected_acv = (

            calculate_expected_acv(

                historical_opportunities

            )

        )

 

        # Historical discount

 

        historical_discount = (

            calculate_historical_discount(

                historical_opportunities

            )

        )

 

        # Apply scenario discount to ACV

 

        discount_adjusted_acv = (

            calculate_discount_adjusted_acv(

                historical_expected_acv,

                historical_discount,

                discount_pct

            )

        )

 

        discount_acv_impact = (

            calculate_discount_acv_impact(

                discount_adjusted_acv,

                historical_expected_acv

            )

        )

 

        # Calculate scenario-specific bundle uplift

 

        (

            bundle_acv_uplift,

            bundle_uplift_evidence

        ) = calculate_bundle_acv_uplift(

            data["ownership"],

            data["accounts"],

            industry,

            geography,

            company_size

        )

 

        # Select bundle uplift or manual ACV adjustment

 

        effective_acv_adjustment = (

            get_effective_acv_adjustment(

                product_strategy,

                scenario_acv_adjustment,

                bundle_acv_uplift

            )

        )

 

        # Final adjusted expected ACV

 

        adjusted_expected_acv = (

            adjust_expected_acv(

                discount_adjusted_acv,

                effective_acv_adjustment

            )

        )

 

        # Expected customers won

 

        expected_customers_won = (

            len(focus_accounts)

            * adjusted_win_rate

        )

 

        # Projected revenue

 

        projected_revenue = (

            calculate_projected_revenue(

                len(focus_accounts),

                adjusted_win_rate,

                adjusted_expected_acv

            )

        )

 

        # Required pipeline

 

        required_pipeline = (

            calculate_required_pipeline(

                projected_revenue,

                adjusted_win_rate

            )

        )

 

        # Hunter productivity

 

        accounts_per_hunter = (

            get_accounts_per_hunter(

                data["capacity"],

                geography

            )

        )

 

        # Required hunters

 

        required_hunters = (

            calculate_required_hunters(

                len(focus_accounts),

                accounts_per_hunter

            )

        )

 

        # Available hunters

 

        available_hunters = (

            get_available_hunters(

                data["capacity"],

                geography

            )

        )

 

        # Capacity output

 

        (

            additional_hunters_required,

            surplus_hunters,

            capacity_status

        ) = calculate_capacity_gap(

            required_hunters,

            available_hunters

        )

 

        # Risk score

 

        risk_score = calculate_risk_score(

            adjusted_win_rate,

            len(focus_accounts),

            capacity_status

        )

 

        confidence_level = (

            calculate_confidence_level(

                risk_score

            )

        )

 

        # Store scenario summary

 

        results.append({

 

            "scenario_id":

                scenario_id,

 

            "scenario_name":

                scenario_name,

 

            "industry":

                industry,

 

            "geography":

                geography,

 

            "company_size":

                company_size,

 

            "product_strategy":

                product_strategy,

 

            "sales_motion":

                sales_motion,

 

            "pricing_assumption":

                pricing_assumption,

 

            "propensity_threshold":

                propensity_threshold,

 

            "tam_usd":

                round(tam, 2),

 

            "addressable_accounts":

                len(addressable_accounts),

 

            "focus_accounts":

                len(focus_accounts),

 

            "historical_opportunities":

                len(historical_opportunities),

 

            "historical_win_rate":

                round(historical_win_rate, 4),

 

            "scenario_win_rate_adjustment":

                round(win_rate_adjustment, 4),

 

            "scenario_discount_pct":

                round(discount_pct, 4),

 

            "scenario_discount_band":

                scenario_discount_band,

 

            "discount_band_win_rate":

                round(discount_band_win_rate, 4),

 

            "discount_band_decisions":

                discount_band_decisions,

 

            "discount_evidence_status":

                discount_evidence_status,

 

            "discount_win_rate_adjustment":

                round(

                    discount_win_rate_adjustment,

                    4

                ),

 

            "effective_win_rate_adjustment":

                round(

                    effective_win_rate_adjustment,

                    4

                ),

 

            "adjusted_win_rate":

                round(adjusted_win_rate, 4),

 

            "historical_expected_acv_usd":

                round(

                    historical_expected_acv,

                    2

                ),

 

            "historical_discount_pct":

                round(historical_discount, 4),

 

            "discount_adjusted_acv_usd":

                round(discount_adjusted_acv, 2),

 

            "discount_acv_impact_usd":

                round(discount_acv_impact, 2),

 

            "scenario_acv_adjustment":

                round(

                    scenario_acv_adjustment,

                    4

                ),

 

            "observed_bundle_acv_uplift":

                round(bundle_acv_uplift, 4),

 

            "bundle_uplift_evidence":

                bundle_uplift_evidence,

 

            "effective_acv_adjustment":

                round(

                    effective_acv_adjustment,

                    4

                ),

 

            "adjusted_expected_acv_usd":

                round(adjusted_expected_acv, 2),

 

            "expected_customers_won":

                round(expected_customers_won, 2),

 

            "projected_revenue_usd":

                round(projected_revenue, 2),

 

            "required_pipeline_usd":

                round(required_pipeline, 2),

 

            "investment_amount_usd":

                round(investment_amount, 2),

 

            "accounts_per_hunter":

                accounts_per_hunter,

 

            "required_hunters":

                required_hunters,

 

            "available_hunters":

                available_hunters,

 

            "additional_hunters_required":

                additional_hunters_required,

 

            "surplus_hunters":

                surplus_hunters,

 

            "capacity_status":

                capacity_status,

 

            "risk_score":

                risk_score,

 

            "confidence_level":

                confidence_level,

 

            "product_recommendation_count":

                len(product_recommendations),

 

            "product_recommendations_json":

                json.dumps(

                    product_recommendations,

                    default=str

                )

 

        })

 

    return results