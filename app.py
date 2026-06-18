import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Valuation Engine", layout="wide")
st.title("Stock Valuation Engine")
st.markdown("A tool utilizing both popular and highly accurate financial models to estimate intrinsic value.")

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.header("Select Valuation Model")
model_choice = st.sidebar.radio(
    "Popular Models",
    ["1. NPV via FCFF (WACC)", "2. EV/EBITDA Multiple", "3. P/E Multiple", 
     "4. Adjusted Present Value (APV)", "5. Free Cash Flow to Equity (FCFE)", "6. Certainty Equivalent Method (CEM)"]
)

# ==========================================
# MODEL 1: NPV via FCFF (WACC)
# ==========================================
if model_choice == "1. NPV via FCFF (WACC)":
    st.header("1. Net Present Value (FCFF & WACC)")
    st.markdown("Calculates intrinsic enterprise value using steady-state Free Cash Flow to the Firm.")
    
    col1, col2 = st.columns(2)
    with col1:
        ebit = st.number_input("EBIT", value=100000.0)
        tax_rate = st.slider("Tax Rate (%)", 0.0, 50.0, 27.0) / 100
        depreciation = st.number_input("Depreciation & Amortization", value=20000.0)
    with col2:
        capex = st.number_input("Capital Expenditure (CAPEX)", value=25000.0)
        nwc_change = st.number_input("Change in Net Working Capital", value=5000.0)
        wacc = st.slider("WACC (%)", 1.0, 25.0, 10.0) / 100
        growth_rate = st.slider("Terminal Growth Rate (%)", 0.0, 10.0, 3.0) / 100

    if st.button("Calculate FCFF Value"):
        # Calculate FCFF: EBIT(1-T) + D&A - CAPEX - Change in NWC
        nopat = ebit * (1 - tax_rate)
        fcff = nopat + depreciation - capex - nwc_change
        
        if wacc > growth_rate:
            # Gordon Growth Terminal Value
            enterprise_value = (fcff * (1 + growth_rate)) / (wacc - growth_rate)
            st.success(f"Calculated FCFF: R {fcff:,.2f}")
            st.metric(label="Estimated Enterprise Value", value=f"R {enterprise_value:,.2f}")
        else:
            st.error("WACC must be strictly greater than the Growth Rate.")

# ==========================================
# MODEL 2: EV/EBITDA Multiple
# ==========================================
elif model_choice == "2. EV/EBITDA Multiple":
    st.header("2. Enterprise Value to EBITDA")
    st.markdown("A relative valuation metric widely used to compare companies ignoring capital structure.")
    
    ebitda = st.number_input("Company EBITDA", value=500000.0)
    industry_multiple = st.number_input("Industry Average EV/EBITDA Multiple", value=8.5)
    net_debt = st.number_input("Net Debt (Total Debt - Cash)", value=100000.0)
    
    if st.button("Calculate Relative Value"):
        enterprise_value = ebitda * industry_multiple
        equity_value = enterprise_value - net_debt
        st.metric(label="Implied Enterprise Value", value=f"R {enterprise_value:,.2f}")
        st.metric(label="Implied Equity Value", value=f"R {equity_value:,.2f}")

# ==========================================
# MODEL 3: P/E Multiple
# ==========================================
elif model_choice == "3. P/E Multiple":
    st.header("3. Price-to-Earnings (P/E) Multiple")
    
    eps = st.number_input("Earnings Per Share (EPS)", value=12.50)
    pe_ratio = st.number_input("Target / Peer P/E Ratio", value=15.0)
    
    if st.button("Calculate Target Share Price"):
        target_price = eps * pe_ratio
        st.metric(label="Implied Share Price", value=f"R {target_price:,.2f}")

# ==========================================
# MODEL 4: Adjusted Present Value (APV)
# ==========================================
elif model_choice == "4. Adjusted Present Value (APV)":
    st.header("4. Adjusted Present Value (APV)")
    st.markdown("Separates the unlevered firm value from the financing side effects (Tax Shield).")
    
    fcff = st.number_input("Expected FCFF", value=80000.0)
    unlevered_cost = st.slider("Unlevered Cost of Capital (Ku) %", 1.0, 25.0, 12.0) / 100
    growth_rate = st.slider("Growth Rate (%)", 0.0, 10.0, 3.0) / 100
    
    total_debt = st.number_input("Total Debt", value=200000.0)
    cost_of_debt = st.slider("Cost of Debt (%)", 1.0, 20.0, 7.0) / 100
    tax_rate = st.slider("Corporate Tax Rate (%)", 0.0, 50.0, 27.0) / 100
    
    if st.button("Calculate APV"):
        if unlevered_cost > growth_rate:
            # V_unlevered = FCFF / (Ku - g)
            v_unlevered = (fcff * (1 + growth_rate)) / (unlevered_cost - growth_rate)
            # PV of perpetual tax shield = Tc * D
            pv_tax_shield = tax_rate * total_debt
            apv = v_unlevered + pv_tax_shield
            
            st.write(f"Unlevered Value: R {v_unlevered:,.2f}")
            st.write(f"PV of Tax Shield: R {pv_tax_shield:,.2f}")
            st.metric(label="Total Adjusted Present Value (APV)", value=f"R {apv:,.2f}")
        else:
            st.error("Unlevered Cost of Capital must be greater than Growth Rate.")

# ==========================================
# MODEL 5: Free Cash Flow to Equity (FCFE)
# ==========================================
elif model_choice == "5. Free Cash Flow to Equity (FCFE)":
    st.header("5. Free Cash Flow to Equity (FCFE)")
    st.markdown("Values the equity directly by mapping cash available strictly to shareholders.")
    
    net_income = st.number_input("Net Income", value=60000.0)
    depreciation = st.number_input("Depreciation", value=15000.0)
    capex = st.number_input("CAPEX", value=20000.0)
    nwc_change = st.number_input("Change in NWC", value=3000.0)
    net_debt_issued = st.number_input("Net Debt Issued (New Debt - Principal Repaid)", value=5000.0)
    
    cost_of_equity = st.slider("Cost of Equity (Ke) %", 1.0, 30.0, 14.0) / 100
    growth_rate = st.slider("FCFE Growth Rate (%)", 0.0, 10.0, 4.0) / 100
    
    if st.button("Calculate Equity Value via FCFE"):
        # FCFE = NI + Depr - CAPEX - Change NWC + Net Debt Issued
        fcfe = net_income + depreciation - capex - nwc_change + net_debt_issued
        
        if cost_of_equity > growth_rate:
            equity_value = (fcfe * (1 + growth_rate)) / (cost_of_equity - growth_rate)
            st.success(f"Calculated FCFE: R {fcfe:,.2f}")
            st.metric(label="Implied Total Equity Value", value=f"R {equity_value:,.2f}")
        else:
            st.error("Cost of Equity must be greater than the Growth Rate.")

# ==========================================
# MODEL 6: Certainty Equivalent Method (CEM)
# ==========================================
elif model_choice == "6. Certainty Equivalent Method (CEM)":
    st.header("6. Certainty Equivalent Method (CEM)")
    st.markdown("Adjusts for risk in the numerator (cash flows) rather than the discount rate.")
    
    expected_cf = st.number_input("Expected Risky Cash Flow", value=100000.0)
    cash_flow_beta = st.number_input("Cash Flow Beta", value=0.8)
    market_return = st.slider("Expected Market Return (Rm) %", 1.0, 20.0, 12.0) / 100
    risk_free_rate = st.slider("Risk-Free Rate (Rf) %", 1.0, 15.0, 5.0) / 100
    
    if st.button("Calculate Certainty Equivalent PV"):
        # CE = E(CF) - Beta * (Rm - Rf)
        market_risk_premium = market_return - risk_free_rate
        # Note: In practice, CE adjustments can be complex. This uses a simplified continuous adjustment representation.
        certainty_equivalent_cf = expected_cf - (cash_flow_beta * market_risk_premium * expected_cf)
        
        # Discount at Risk Free Rate
        present_value = certainty_equivalent_cf / (1 + risk_free_rate)
        
        st.write(f"Risk-Stripped Certainty Equivalent Cash Flow: R {certainty_equivalent_cf:,.2f}")
        st.metric(label="Present Value (Discounted at Rf)", value=f"R {present_value:,.2f}")