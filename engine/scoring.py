def calculate_risk_score(

    win_rate,

    focus_accounts,

    capacity_status

):

 

    risk_score = 50 #starting point for the score as neutral risk

 

    # Win Rate Risk

 

    if win_rate < 0.20:

        risk_score += 20

 

    elif win_rate < 0.30:

        risk_score += 10

 

    else:

        risk_score -= 10

 

    # Focus Account Risk

 

    if focus_accounts < 10: #If one big account slips, revenue changes dramatically

        risk_score += 10

 

    elif focus_accounts > 50: #Less dependency on a few accounts

        risk_score -= 5

 

    # Capacity Risk

 

    if capacity_status == "Capacity Shortfall": #The revenue plan may not be executable

        risk_score += 20

 

    elif capacity_status == "Sufficient Capacity":

        risk_score -= 10

 

    # Keep between 0 and 100

 

    risk_score = max(

        0,

        min(100, risk_score)

    )

 

    return risk_score

 

def calculate_confidence_level(

    risk_score

):

 

    if risk_score <= 30:

        return "High"

 

    elif risk_score <= 60:

        return "Moderate"

 

    else:

        return "Low"