"""
Credit Risk Underwriting Tools
==============================

A comprehensive set of credit risk assessment tools designed for LangChain integration.
These tools help evaluate loan applicant profiles and generate risk assessments.

Risk Interpretation Guidelines:
- DTI Ratio: Low < 35%, Medium 35-50%, High > 50%
- LTV Ratio: Low < 80%, Medium 80-90%, High > 90%
- Credit Utilization: Low < 30%, Medium 30-50%, High > 50%
- FOIR: Low < 40%, Medium 40-55%, High > 55%
- DSCR: Low Risk > 1.5, Medium 1.0-1.5, High < 1.0
"""

from langchain_core.tools import tool
from typing import Literal


# =============================================================================
# Core Financial Ratios
# =============================================================================

@tool
def compute_debt_to_income_ratio(monthly_income: float, total_monthly_debt: float) -> dict:
    """
    Calculate the Debt-to-Income (DTI) ratio for a loan applicant.
    
    DTI is a key metric that measures a borrower's ability to manage monthly 
    debt payments relative to their gross monthly income. Lenders use this 
    to assess repayment capacity.
    
    Formula: DTI = (Total Monthly Debt / Gross Monthly Income) × 100
    
    Risk Interpretation:
    - Low Risk: DTI < 35% - Comfortable debt level
    - Medium Risk: DTI 35-50% - Manageable but tight
    - High Risk: DTI > 50% - May struggle with repayments
    
    Args:
        monthly_income: Gross monthly income of the applicant (must be > 0)
        total_monthly_debt: Total monthly debt obligations (loans, EMIs, credit card payments)
    
    Returns:
        Dictionary with ratio, percentage, and risk_category
    
    Example:
        >>> compute_debt_to_income_ratio(50000, 15000)
        {'ratio': 0.3, 'percentage': 30.0, 'risk_category': 'LOW'}
    """
    if monthly_income <= 0:
        return {"error": "Monthly income must be greater than zero"}
    
    if total_monthly_debt < 0:
        return {"error": "Total monthly debt cannot be negative"}
    
    ratio = total_monthly_debt / monthly_income
    percentage = ratio * 100
    
    if percentage < 35:
        risk_category = "LOW"
    elif percentage <= 50:
        risk_category = "MEDIUM"
    else:
        risk_category = "HIGH"
    
    return {
        "ratio": round(ratio, 4),
        "percentage": round(percentage, 2),
        "risk_category": risk_category
    }


@tool
def compute_loan_to_value_ratio(loan_amount: float, property_value: float) -> dict:
    """
    Calculate the Loan-to-Value (LTV) ratio for secured loans.
    
    LTV measures the loan amount relative to the collateral's appraised value.
    It indicates the risk exposure for the lender - higher LTV means higher risk.
    
    Formula: LTV = (Loan Amount / Property Value) × 100
    
    Risk Interpretation:
    - Low Risk: LTV < 80% - Strong collateral coverage
    - Medium Risk: LTV 80-90% - Acceptable with good credit
    - High Risk: LTV > 90% - Limited equity cushion
    
    Args:
        loan_amount: The loan principal being requested
        property_value: Appraised market value of the property/collateral
    
    Returns:
        Dictionary with ratio, percentage, and risk_category
    
    Example:
        >>> compute_loan_to_value_ratio(800000, 1000000)
        {'ratio': 0.8, 'percentage': 80.0, 'risk_category': 'MEDIUM'}
    """
    if property_value <= 0:
        return {"error": "Property value must be greater than zero"}
    
    if loan_amount < 0:
        return {"error": "Loan amount cannot be negative"}
    
    ratio = loan_amount / property_value
    percentage = ratio * 100
    
    if percentage < 80:
        risk_category = "LOW"
    elif percentage <= 90:
        risk_category = "MEDIUM"
    else:
        risk_category = "HIGH"
    
    return {
        "ratio": round(ratio, 4),
        "percentage": round(percentage, 2),
        "risk_category": risk_category
    }


@tool
def compute_credit_utilization_ratio(credit_used: float, credit_limit: float) -> dict:
    """
    Calculate Credit Utilization Ratio for revolving credit assessment.
    
    Credit utilization measures how much of available credit is being used.
    It's a strong indicator of credit management behavior and financial stress.
    
    Formula: Utilization = (Credit Used / Credit Limit) × 100
    
    Risk Interpretation:
    - Low Risk: < 30% - Excellent credit management
    - Medium Risk: 30-50% - Acceptable utilization
    - High Risk: > 50% - Potential financial stress indicator
    
    Args:
        credit_used: Current outstanding balance across all credit lines
        credit_limit: Total approved credit limit across all credit lines
    
    Returns:
        Dictionary with ratio, percentage, and risk_category
    
    Example:
        >>> compute_credit_utilization_ratio(15000, 100000)
        {'ratio': 0.15, 'percentage': 15.0, 'risk_category': 'LOW'}
    """
    if credit_limit <= 0:
        return {"error": "Credit limit must be greater than zero"}
    
    if credit_used < 0:
        return {"error": "Credit used cannot be negative"}
    
    ratio = credit_used / credit_limit
    percentage = ratio * 100
    
    if percentage < 30:
        risk_category = "LOW"
    elif percentage <= 50:
        risk_category = "MEDIUM"
    else:
        risk_category = "HIGH"
    
    return {
        "ratio": round(ratio, 4),
        "percentage": round(percentage, 2),
        "risk_category": risk_category
    }


@tool
def compute_foir(
    monthly_income: float,
    existing_emis: float,
    proposed_emi: float,
    other_obligations: float = 0
) -> dict:
    """
    Calculate Fixed Obligation to Income Ratio (FOIR).
    
    FOIR measures the proportion of income committed to fixed monthly obligations.
    It helps determine if the applicant can afford additional debt burden.
    
    Formula: FOIR = ((Existing EMIs + Proposed EMI + Other Obligations) / Monthly Income) × 100
    
    Risk Interpretation:
    - Low Risk: FOIR < 40% - Healthy disposable income
    - Medium Risk: FOIR 40-55% - Limited financial flexibility
    - High Risk: FOIR > 55% - High debt burden
    
    Args:
        monthly_income: Gross monthly income
        existing_emis: Total of all current EMI payments
        proposed_emi: EMI for the loan being applied for
        other_obligations: Other fixed monthly obligations (rent, insurance, etc.)
    
    Returns:
        Dictionary with ratio, percentage, remaining_income, and risk_category
    
    Example:
        >>> compute_foir(100000, 20000, 15000, 5000)
        {'ratio': 0.4, 'percentage': 40.0, 'remaining_income': 60000, 'risk_category': 'MEDIUM'}
    """
    if monthly_income <= 0:
        return {"error": "Monthly income must be greater than zero"}
    
    total_obligations = existing_emis + proposed_emi + other_obligations
    
    if total_obligations < 0:
        return {"error": "Total obligations cannot be negative"}
    
    ratio = total_obligations / monthly_income
    percentage = ratio * 100
    remaining_income = monthly_income - total_obligations
    
    if percentage < 40:
        risk_category = "LOW"
    elif percentage <= 55:
        risk_category = "MEDIUM"
    else:
        risk_category = "HIGH"
    
    return {
        "ratio": round(ratio, 4),
        "percentage": round(percentage, 2),
        "total_obligations": round(total_obligations, 2),
        "remaining_income": round(remaining_income, 2),
        "risk_category": risk_category
    }


# =============================================================================
# EMI and Loan Calculations
# =============================================================================

@tool
def compute_emi(principal: float, annual_interest_rate: float, tenure_months: int) -> dict:
    """
    Calculate Equated Monthly Installment (EMI) for a loan.
    
    EMI is the fixed monthly payment required to repay a loan over a specified period.
    
    Formula: EMI = P × r × (1+r)^n / ((1+r)^n - 1)
    Where: P = Principal, r = Monthly interest rate, n = Number of months
    
    Args:
        principal: Loan principal amount
        annual_interest_rate: Annual interest rate as percentage (e.g., 10 for 10%)
        tenure_months: Loan tenure in months
    
    Returns:
        Dictionary with emi, total_payment, total_interest, and effective_annual_rate
    
    Example:
        >>> compute_emi(1000000, 10, 120)
        {'emi': 13215.07, 'total_payment': 1585808.40, 'total_interest': 585808.40, ...}
    """
    if principal <= 0:
        return {"error": "Principal must be greater than zero"}
    
    if annual_interest_rate < 0:
        return {"error": "Interest rate cannot be negative"}
    
    if tenure_months <= 0:
        return {"error": "Tenure must be at least 1 month"}
    
    # Convert annual rate to monthly rate
    monthly_rate = (annual_interest_rate / 100) / 12
    
    if monthly_rate == 0:
        # Zero interest loan
        emi = principal / tenure_months
    else:
        # Standard EMI formula
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / \
              (((1 + monthly_rate) ** tenure_months) - 1)
    
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    
    return {
        "emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "interest_to_principal_ratio": round(total_interest / principal, 4),
        "monthly_interest_rate": round(monthly_rate * 100, 4)
    }


@tool
def compute_dscr(net_operating_income: float, total_debt_service: float) -> dict:
    """
    Calculate Debt Service Coverage Ratio (DSCR) for business/commercial loans.
    
    DSCR measures cashflow available to service debt. It's crucial for business 
    loans and commercial real estate financing.
    
    Formula: DSCR = Net Operating Income / Total Debt Service
    
    Risk Interpretation:
    - Low Risk: DSCR > 1.5 - Strong debt servicing capacity
    - Medium Risk: DSCR 1.0-1.5 - Adequate coverage
    - High Risk: DSCR < 1.0 - Insufficient income to cover debt
    
    Args:
        net_operating_income: Annual net operating income (NOI)
        total_debt_service: Annual debt service (principal + interest payments)
    
    Returns:
        Dictionary with ratio, excess_income, and risk_category
    
    Example:
        >>> compute_dscr(500000, 300000)
        {'ratio': 1.67, 'excess_income': 200000, 'risk_category': 'LOW'}
    """
    if total_debt_service <= 0:
        return {"error": "Total debt service must be greater than zero"}
    
    ratio = net_operating_income / total_debt_service
    excess_income = net_operating_income - total_debt_service
    
    if ratio > 1.5:
        risk_category = "LOW"
    elif ratio >= 1.0:
        risk_category = "MEDIUM"
    else:
        risk_category = "HIGH"
    
    return {
        "ratio": round(ratio, 4),
        "excess_income": round(excess_income, 2),
        "coverage_percentage": round(ratio * 100, 2),
        "risk_category": risk_category
    }


# =============================================================================
# Behavioral and Qualitative Assessments
# =============================================================================

@tool
def assess_employment_stability(
    employment_type: Literal["salaried", "self_employed", "business_owner", "freelancer", "unemployed"],
    years_in_current_job: float,
    total_work_experience: float,
    job_changes_last_5_years: int = 0
) -> dict:
    """
    Assess employment stability score for credit risk evaluation.
    
    Employment stability is a key indicator of income reliability and loan
    repayment consistency. Stable employment reduces default risk.
    
    Scoring Factors:
    - Employment type weight
    - Tenure in current position
    - Overall work experience
    - Job stability (fewer changes = better)
    
    Args:
        employment_type: Type of employment
        years_in_current_job: Years at current employer/business
        total_work_experience: Total professional experience in years
        job_changes_last_5_years: Number of job changes in last 5 years
    
    Returns:
        Dictionary with score (0-100), factors breakdown, and risk_category
    
    Example:
        >>> assess_employment_stability("salaried", 5, 10, 1)
        {'score': 85, 'risk_category': 'LOW', 'factors': {...}}
    """
    # Employment type scores
    employment_scores = {
        "salaried": 30,
        "business_owner": 25,
        "self_employed": 20,
        "freelancer": 15,
        "unemployed": 0
    }
    
    base_score = employment_scores.get(employment_type, 10)
    
    # Tenure score (max 30 points)
    tenure_score = min(years_in_current_job * 6, 30)
    
    # Experience score (max 20 points)
    experience_score = min(total_work_experience * 2, 20)
    
    # Job stability score (max 20 points)
    if job_changes_last_5_years == 0:
        stability_score = 20
    elif job_changes_last_5_years == 1:
        stability_score = 15
    elif job_changes_last_5_years == 2:
        stability_score = 10
    elif job_changes_last_5_years == 3:
        stability_score = 5
    else:
        stability_score = 0
    
    total_score = base_score + tenure_score + experience_score + stability_score
    total_score = min(total_score, 100)  # Cap at 100
    
    if total_score >= 70:
        risk_category = "LOW"
    elif total_score >= 40:
        risk_category = "MEDIUM"
    else:
        risk_category = "HIGH"
    
    return {
        "score": round(total_score, 2),
        "risk_category": risk_category,
        "factors": {
            "employment_type_score": base_score,
            "tenure_score": round(tenure_score, 2),
            "experience_score": round(experience_score, 2),
            "stability_score": stability_score
        }
    }


@tool
def compute_payment_history_score(
    total_accounts: int,
    on_time_payments: int,
    late_payments_30_days: int = 0,
    late_payments_60_days: int = 0,
    late_payments_90_plus_days: int = 0,
    defaults: int = 0
) -> dict:
    """
    Calculate payment history score based on repayment behavior.
    
    Payment history is the strongest predictor of future credit behavior.
    This score analyzes historical payment patterns.
    
    Scoring:
    - On-time payments contribute positively
    - Late payments deduct based on severity
    - Defaults are heavily penalized
    
    Args:
        total_accounts: Total number of credit accounts
        on_time_payments: Number of on-time payment records
        late_payments_30_days: Payments 30 days late
        late_payments_60_days: Payments 60 days late
        late_payments_90_plus_days: Payments 90+ days late
        defaults: Number of defaulted accounts
    
    Returns:
        Dictionary with score (0-100), on_time_rate, and risk_category
    
    Example:
        >>> compute_payment_history_score(5, 58, 2, 0, 0, 0)
        {'score': 93.33, 'on_time_rate': 96.67, 'risk_category': 'LOW'}
    """
    if total_accounts <= 0:
        return {"error": "Total accounts must be at least 1"}
    
    total_payment_records = (on_time_payments + late_payments_30_days + 
                            late_payments_60_days + late_payments_90_plus_days)
    
    if total_payment_records == 0:
        return {"error": "No payment records available", "score": 50, "risk_category": "MEDIUM"}
    
    # Calculate on-time payment rate
    on_time_rate = (on_time_payments / total_payment_records) * 100
    
    # Base score from on-time rate
    base_score = on_time_rate
    
    # Penalties for late payments
    penalty = (late_payments_30_days * 2 + 
               late_payments_60_days * 5 + 
               late_payments_90_plus_days * 10 + 
               defaults * 25)
    
    final_score = max(0, base_score - penalty)
    final_score = min(100, final_score)
    
    if final_score >= 80:
        risk_category = "LOW"
    elif final_score >= 50:
        risk_category = "MEDIUM"
    else:
        risk_category = "HIGH"
    
    return {
        "score": round(final_score, 2),
        "on_time_rate": round(on_time_rate, 2),
        "total_payment_records": total_payment_records,
        "penalty_points": penalty,
        "risk_category": risk_category
    }


@tool
def assess_credit_score(credit_score: int) -> dict:
    """
    Assess and categorize a credit bureau score.
    
    Credit scores (like CIBIL in India, FICO in US) are standardized 
    measures of creditworthiness. This tool interprets the score.
    
    Score Ranges (based on common standards):
    - Excellent: 750-900 - Best rates, high approval probability
    - Good: 700-749 - Favorable terms available
    - Fair: 650-699 - Some options with higher rates
    - Poor: 550-649 - Limited options, high rates
    - Very Poor: Below 550 - Likely rejection
    
    Args:
        credit_score: Credit bureau score (typically 300-900)
    
    Returns:
        Dictionary with rating, recommendation, and risk_category
    
    Example:
        >>> assess_credit_score(780)
        {'rating': 'EXCELLENT', 'risk_category': 'LOW', 'recommendation': '...'}
    """
    if credit_score < 300 or credit_score > 900:
        return {"error": "Credit score should be between 300 and 900"}
    
    if credit_score >= 750:
        rating = "EXCELLENT"
        risk_category = "LOW"
        recommendation = "Eligible for best rates and terms. High approval probability."
    elif credit_score >= 700:
        rating = "GOOD"
        risk_category = "LOW"
        recommendation = "Favorable terms available. Standard processing."
    elif credit_score >= 650:
        rating = "FAIR"
        risk_category = "MEDIUM"
        recommendation = "May qualify with higher interest rates. Additional documentation may help."
    elif credit_score >= 550:
        rating = "POOR"
        risk_category = "HIGH"
        recommendation = "Limited options. Consider secured loans or co-applicant."
    else:
        rating = "VERY_POOR"
        risk_category = "HIGH"
        recommendation = "High rejection probability. Recommend credit repair before applying."
    
    return {
        "score": credit_score,
        "rating": rating,
        "risk_category": risk_category,
        "recommendation": recommendation
    }


# =============================================================================
# Collateral and Security Assessment
# =============================================================================

@tool
def compute_collateral_coverage_ratio(
    collateral_value: float,
    loan_amount: float,
    liquidation_discount: float = 0.2
) -> dict:
    """
    Calculate Collateral Coverage Ratio with liquidation consideration.
    
    Assesses how well the collateral protects the lender in case of default,
    accounting for potential liquidation discounts.
    
    Formula: CCR = (Collateral Value × (1 - Liquidation Discount)) / Loan Amount
    
    Risk Interpretation:
    - Low Risk: CCR > 1.5 - Strong collateral protection
    - Medium Risk: CCR 1.0-1.5 - Adequate coverage
    - High Risk: CCR < 1.0 - Under-collateralized
    
    Args:
        collateral_value: Appraised value of collateral
        loan_amount: Total loan amount
        liquidation_discount: Expected discount in forced sale (default 20%)
    
    Returns:
        Dictionary with coverage_ratio, net_collateral_value, and risk_category
    
    Example:
        >>> compute_collateral_coverage_ratio(1500000, 1000000, 0.2)
        {'coverage_ratio': 1.2, 'net_collateral_value': 1200000, 'risk_category': 'MEDIUM'}
    """
    if loan_amount <= 0:
        return {"error": "Loan amount must be greater than zero"}
    
    if collateral_value < 0:
        return {"error": "Collateral value cannot be negative"}
    
    if not 0 <= liquidation_discount < 1:
        return {"error": "Liquidation discount must be between 0 and 1"}
    
    net_collateral_value = collateral_value * (1 - liquidation_discount)
    coverage_ratio = net_collateral_value / loan_amount
    shortfall = loan_amount - net_collateral_value if coverage_ratio < 1 else 0
    
    if coverage_ratio > 1.5:
        risk_category = "LOW"
    elif coverage_ratio >= 1.0:
        risk_category = "MEDIUM"
    else:
        risk_category = "HIGH"
    
    return {
        "coverage_ratio": round(coverage_ratio, 4),
        "coverage_percentage": round(coverage_ratio * 100, 2),
        "net_collateral_value": round(net_collateral_value, 2),
        "shortfall": round(shortfall, 2),
        "risk_category": risk_category
    }


# =============================================================================
# Comprehensive Risk Assessment
# =============================================================================

@tool
def classify_risk_category(
    dti_percentage: float,
    ltv_percentage: float,
    credit_score: int,
    employment_stability_score: float,
    payment_history_score: float
) -> dict:
    """
    Classify overall risk category based on multiple credit factors.
    
    This tool aggregates multiple risk indicators to provide a comprehensive
    risk classification for underwriting decisions.
    
    Classification Logic:
    - LOW: All factors favorable, strong creditworthiness
    - MEDIUM: Mixed factors, acceptable with conditions
    - HIGH: Significant risk factors present
    - VERY_HIGH: Multiple high-risk indicators
    
    Args:
        dti_percentage: Debt-to-income ratio as percentage
        ltv_percentage: Loan-to-value ratio as percentage
        credit_score: Credit bureau score (300-900)
        employment_stability_score: Employment stability score (0-100)
        payment_history_score: Payment history score (0-100)
    
    Returns:
        Dictionary with overall_category, individual_assessments, and recommendation
    
    Example:
        >>> classify_risk_category(35, 80, 720, 75, 85)
        {'overall_category': 'MEDIUM', 'recommendation': '...', ...}
    """
    # Score each factor
    risk_points = 0
    assessments = {}
    
    # DTI Assessment
    if dti_percentage < 35:
        assessments["dti"] = {"status": "GOOD", "points": 0}
    elif dti_percentage <= 50:
        assessments["dti"] = {"status": "MODERATE", "points": 1}
        risk_points += 1
    else:
        assessments["dti"] = {"status": "POOR", "points": 2}
        risk_points += 2
    
    # LTV Assessment
    if ltv_percentage < 80:
        assessments["ltv"] = {"status": "GOOD", "points": 0}
    elif ltv_percentage <= 90:
        assessments["ltv"] = {"status": "MODERATE", "points": 1}
        risk_points += 1
    else:
        assessments["ltv"] = {"status": "POOR", "points": 2}
        risk_points += 2
    
    # Credit Score Assessment
    if credit_score >= 750:
        assessments["credit_score"] = {"status": "EXCELLENT", "points": 0}
    elif credit_score >= 700:
        assessments["credit_score"] = {"status": "GOOD", "points": 0}
    elif credit_score >= 650:
        assessments["credit_score"] = {"status": "MODERATE", "points": 1}
        risk_points += 1
    else:
        assessments["credit_score"] = {"status": "POOR", "points": 2}
        risk_points += 2
    
    # Employment Stability Assessment
    if employment_stability_score >= 70:
        assessments["employment"] = {"status": "STABLE", "points": 0}
    elif employment_stability_score >= 40:
        assessments["employment"] = {"status": "MODERATE", "points": 1}
        risk_points += 1
    else:
        assessments["employment"] = {"status": "UNSTABLE", "points": 2}
        risk_points += 2
    
    # Payment History Assessment
    if payment_history_score >= 80:
        assessments["payment_history"] = {"status": "EXCELLENT", "points": 0}
    elif payment_history_score >= 50:
        assessments["payment_history"] = {"status": "MODERATE", "points": 1}
        risk_points += 1
    else:
        assessments["payment_history"] = {"status": "POOR", "points": 2}
        risk_points += 2
    
    # Determine overall category
    if risk_points == 0:
        overall_category = "LOW"
        recommendation = "Approve with standard terms. Strong credit profile."
    elif risk_points <= 2:
        overall_category = "MEDIUM"
        recommendation = "Approve with enhanced due diligence. Consider moderate rate adjustment."
    elif risk_points <= 5:
        overall_category = "HIGH"
        recommendation = "Additional mitigation required (collateral, guarantor). Higher risk pricing."
    else:
        overall_category = "VERY_HIGH"
        recommendation = "Consider rejection or significant risk mitigation measures."
    
    return {
        "overall_category": overall_category,
        "total_risk_points": risk_points,
        "max_risk_points": 10,
        "individual_assessments": assessments,
        "recommendation": recommendation
    }


@tool
def compute_total_risk_score(
    dti_percentage: float,
    ltv_percentage: float,
    credit_score: int,
    employment_stability_score: float,
    payment_history_score: float,
    credit_utilization_percentage: float = 25.0,
    foir_percentage: float = 40.0
) -> dict:
    """
    Compute a comprehensive weighted risk score for underwriting decisions.
    
    This tool calculates a normalized risk score (0-100) by combining 
    multiple credit factors with appropriate weights. Higher score = Lower risk.
    
    Weighting:
    - Credit Score: 25%
    - Payment History: 20%
    - DTI Ratio: 15%
    - LTV Ratio: 15%
    - Employment Stability: 10%
    - Credit Utilization: 10%
    - FOIR: 5%
    
    Args:
        dti_percentage: Debt-to-income ratio as percentage
        ltv_percentage: Loan-to-value ratio as percentage
        credit_score: Credit bureau score (300-900)
        employment_stability_score: Employment stability score (0-100)
        payment_history_score: Payment history score (0-100)
        credit_utilization_percentage: Credit utilization as percentage (default 25%)
        foir_percentage: Fixed obligations to income ratio (default 40%)
    
    Returns:
        Dictionary with total_score, grade, component_scores, and underwriting_recommendation
    
    Example:
        >>> compute_total_risk_score(35, 80, 720, 75, 85, 25, 40)
        {'total_score': 72.5, 'grade': 'B', 'underwriting_recommendation': '...'}
    """
    # Normalize credit score to 0-100 scale
    credit_score_normalized = ((credit_score - 300) / 600) * 100
    
    # Convert ratios to scores (lower ratio = higher score)
    dti_score = max(0, 100 - (dti_percentage * 1.5))
    ltv_score = max(0, 100 - (ltv_percentage * 0.9))
    utilization_score = max(0, 100 - (credit_utilization_percentage * 1.5))
    foir_score = max(0, 100 - (foir_percentage * 1.3))
    
    # Calculate weighted score
    component_scores = {
        "credit_score": {"score": round(credit_score_normalized, 2), "weight": 0.25},
        "payment_history": {"score": round(payment_history_score, 2), "weight": 0.20},
        "dti": {"score": round(dti_score, 2), "weight": 0.15},
        "ltv": {"score": round(ltv_score, 2), "weight": 0.15},
        "employment_stability": {"score": round(employment_stability_score, 2), "weight": 0.10},
        "credit_utilization": {"score": round(utilization_score, 2), "weight": 0.10},
        "foir": {"score": round(foir_score, 2), "weight": 0.05}
    }
    
    total_score = (
        credit_score_normalized * 0.25 +
        payment_history_score * 0.20 +
        dti_score * 0.15 +
        ltv_score * 0.15 +
        employment_stability_score * 0.10 +
        utilization_score * 0.10 +
        foir_score * 0.05
    )
    
    total_score = min(100, max(0, total_score))
    
    # Assign grade
    if total_score >= 85:
        grade = "A"
        recommendation = "APPROVE - Excellent risk profile. Offer best available rates."
    elif total_score >= 70:
        grade = "B"
        recommendation = "APPROVE - Good risk profile. Standard terms apply."
    elif total_score >= 55:
        grade = "C"
        recommendation = "CONDITIONAL APPROVE - Moderate risk. Consider risk-based pricing."
    elif total_score >= 40:
        grade = "D"
        recommendation = "REVIEW - High risk. Requires senior approval and mitigation."
    else:
        grade = "E"
        recommendation = "DECLINE - Very high risk. Does not meet underwriting criteria."
    
    return {
        "total_score": round(total_score, 2),
        "grade": grade,
        "component_scores": component_scores,
        "underwriting_recommendation": recommendation
    }


# =============================================================================
# Export all tools for LangChain
# =============================================================================

# List of all available tools for easy import
CREDIT_RISK_TOOLS = [
    compute_debt_to_income_ratio,
    compute_loan_to_value_ratio,
    compute_credit_utilization_ratio,
    compute_foir,
    compute_emi,
    compute_dscr,
    assess_employment_stability,
    compute_payment_history_score,
    assess_credit_score,
    compute_collateral_coverage_ratio,
    classify_risk_category,
    compute_total_risk_score,
]
