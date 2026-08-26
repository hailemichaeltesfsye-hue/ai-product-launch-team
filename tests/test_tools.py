from tools.research import calculate_financial_metrics, perform_market_research


def test_perform_market_research():
    result = perform_market_research("Developer Tools")
    assert result["topic"] == "Developer Tools"
    assert "market_sentiment" in result
    assert len(result["key_competitor_types"]) >= 2
    assert "avg_payback_period_months" in result["industry_benchmarks"]


def test_calculate_financial_metrics():
    result = calculate_financial_metrics(
        setup_cost=50000.0,
        monthly_burn=10000.0,
        target_monthly_revenue=20000.0,
    )
    assert result["initial_investment"] == 50000.0
    assert result["monthly_net_margin"] == 10000.0
    assert result["estimated_months_to_breakeven"] == 5.0
    assert result["annualized_run_rate"] == 240000.0
