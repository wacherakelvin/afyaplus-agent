def estimate_monthly_cost(avg_input_tokens, avg_output_tokens,
                          daily_messages, days_per_month=30):
    INPUT_RATE = 0.15 / 1_000_000    # $ per input token
    OUTPUT_RATE = 0.60 / 1_000_000   # $ per output token

    monthly_input_tokens  = avg_input_tokens  * daily_messages * days_per_month
    monthly_output_tokens = avg_output_tokens * daily_messages * days_per_month

    input_cost  = monthly_input_tokens  * INPUT_RATE
    output_cost = monthly_output_tokens * OUTPUT_RATE

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_monthly": input_cost + output_cost,
    }

# Test: 5,000 messages/day, avg 100 input + 150 output tokens
result = estimate_monthly_cost(
    avg_input_tokens=100,
    avg_output_tokens=150,
    daily_messages=5000
)
print(f"Monthly cost estimate: ${result['total_monthly']:.2f}")