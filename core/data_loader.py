import os
import pandas as pd

# Paths to your real tracked data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKER_PATH = os.path.join(BASE_DIR, 'data', 'Personal_Workplace_Shift_Tracker.xlsx')
PRICING_PATH = os.path.join(BASE_DIR, 'data', 'Personal_Workplace_Pricing.xlsx')

MIN_SHIFTS_FOR_CV = 5  # products with fewer logged shifts are excluded from volatility ranking


def load_tracker(use_synthetic=False):
    """Load the real shift tracker. use_synthetic kept for backward compatibility
    with existing call sites but is now ignored — always loads real data."""
    df = pd.read_excel(TRACKER_PATH)
    return df


def load_pricing(use_synthetic=False):
    """Load the real pricing sheet. use_synthetic kept for backward compatibility."""
    df = pd.read_excel(PRICING_PATH)
    return df


def get_product_list(tracker_df):
    """Return product names derived from '<Product>_Waste_Count' columns."""
    waste_cols = [c for c in tracker_df.columns if c.endswith('_Waste_Count')]
    return [c.replace('_Waste_Count', '') for c in waste_cols]

def get_unreliable_products(backtest_path, min_predictions=3, error_threshold_multiplier=2.0):
    """Identifies products whose backtest performance has been
    consistently poor — their mean absolute error is meaningfully higher
    than the typical product's, suggesting Gemini struggles to predict
    them reliably.

    Only flags a product once it has at least min_predictions backtested
    data points, so a single early result doesn't unfairly exclude it.

    Returns a set of product names to exclude from future selection.
    """
    if not os.path.exists(backtest_path) or os.path.getsize(backtest_path) == 0:
        return set()

    bt_df = pd.read_csv(backtest_path)
    product_errors = bt_df.groupby('product').agg(
        n=('abs_error', 'count'),
        mean_error=('abs_error', 'mean')
    )
    product_errors = product_errors[product_errors['n'] >= min_predictions]

    if len(product_errors) == 0:
        return set()

    overall_median_error = product_errors['mean_error'].median()
    threshold = overall_median_error * error_threshold_multiplier

    unreliable = product_errors[product_errors['mean_error'] > threshold]
    return set(unreliable.index)

def get_top_volatile_products(tracker_df, pricing_df, n=12, min_shifts=MIN_SHIFTS_FOR_CV, dollar_floor=1.0, backtest_path=None):
    """Rank products by coefficient of variation, matching the batch
    forecast script's triage logic.

    Applies two filters before ranking:
    - dollar_floor: excludes products whose mean dollar waste per shift is
      too low to matter financially, regardless of how volatile the count
      looks in isolation.
    - reliability filter: excludes products with a demonstrated track
      record of inaccurate backtested predictions, even if they'd
      otherwise rank as volatile enough to qualify.

    Returns a DataFrame with columns ['product', 'cv'], sorted ascending by cv.
    """
    waste_cols = [c for c in tracker_df.columns if c.endswith('_Waste_Count')]
    pricing_dict = dict(zip(pricing_df.columns.tolist(), pricing_df.iloc[0].tolist()))

    unreliable_products = get_unreliable_products(backtest_path) if backtest_path else set()

    stats = {}
    for col in waste_cols:
        product = col.replace('_Waste_Count', '')
        if product in unreliable_products:
            continue

        series = tracker_df[col].dropna()
        if len(series) < min_shifts:
            continue

        mean = series.mean()
        std = series.std()
        cv = std / (mean + 0.1)

        unit_price = pricing_dict.get(product, 0)
        mean_dollar_waste = mean * unit_price

        if mean_dollar_waste >= dollar_floor:
            stats[product] = {'cv': cv, 'mean_dollar_waste': mean_dollar_waste}

    cv_series = pd.Series({p: s['cv'] for p, s in stats.items()}).sort_values(ascending=False)
    top_n = cv_series.head(n)
    return pd.DataFrame({'product': top_n.index, 'cv': top_n.values}).sort_values('cv', ascending=True).reset_index(drop=True)


def get_weekday_weekend_waste(tracker_df):
    """Return (weekday_totals, weekend_totals) as two pandas Series of
    per-shift total waste, split by Day_of_Week."""
    waste_cols = [c for c in tracker_df.columns if c.endswith('_Waste_Count')]
    totals = tracker_df[waste_cols].sum(axis=1)
    is_weekend = tracker_df['Day_of_Week'].isin(['Saturday', 'Sunday'])
    weekday_totals = totals[~is_weekend]
    weekend_totals = totals[is_weekend]
    return weekday_totals, weekend_totals

def compute_daily_confidence(tracker_df, is_weekend_tomorrow, tomorrow_day_name=None, school_status_tomorrow=None, weather_forecast_tomorrow=None):
    """Compute a 0-100 confidence score for tomorrow's batch of predictions,
    based purely on historical data coverage — no LLM involved.

    Factors (25 + 20 + 20 + 20 + 15 = 100 points):
    - Historical sample size (25 pts): more logged shifts overall = more
      reliable predictions in general.
    - Day type (20 pts): weekends are historically more volatile than
      weekdays, so weekend predictions carry inherently more uncertainty.
    - Day-specific coverage (20 pts): how many historical shifts share
      tomorrow's exact day name (e.g., specifically Tuesdays), a tighter
      signal than the weekday/weekend binary alone.
    - School calendar match (20 pts): how many historical shifts share
      tomorrow's school-in-session status.
    - Weather similarity (15 pts): placeholder until the Weather API is
      integrated — currently a neutral fixed value.

    Returns a dict: {'score': int, 'breakdown': list of factor dicts}
    """
    n_shifts = len(tracker_df)

    # ---- Factor 1: historical sample size (0-25 points) ----
    sample_size_score = min(n_shifts / 30, 1.0) * 25

    # ---- Factor 2: day type — weekday vs weekend (0-20 points) ----
    weekday_totals, weekend_totals = get_weekday_weekend_waste(tracker_df)
    weekday_std = weekday_totals.std()
    weekend_std = weekend_totals.std()

    if weekday_std and weekday_std > 0 and pd.notna(weekend_std):
        vol_ratio = weekend_std / weekday_std
    else:
        vol_ratio = 1.0

    if is_weekend_tomorrow:
        weekend_penalty = min(max((vol_ratio - 1) / 3, 0.0), 1.0)
        day_type_score = 20 * (1 - weekend_penalty)
    else:
        day_type_score = 20

    # ---- Factor 3: specific day-of-week coverage (0-20 points) ----
    if tomorrow_day_name and 'Day_of_Week' in tracker_df.columns:
        same_day_shifts = tracker_df[tracker_df['Day_of_Week'] == tomorrow_day_name]
        n_same_day = len(same_day_shifts)
        # scale up to full marks at 5+ shifts sharing this exact day
        day_specific_score = min(n_same_day / 5, 1.0) * 20
    else:
        n_same_day = None
        day_specific_score = 10  # neutral if we can't check

    # ---- Factor 4: school calendar match (0-20 points) ----
    school_col_candidates = [c for c in tracker_df.columns if 'caryhigh' in c.lower().replace(' ', '').replace('_', '')]
    if school_status_tomorrow and school_col_candidates:
        school_col = school_col_candidates[0]
        matching_shifts = tracker_df[tracker_df[school_col] == school_status_tomorrow]
        coverage_ratio = min(len(matching_shifts) / 10, 1.0)
        school_score = coverage_ratio * 20
        n_school_matches = len(matching_shifts)
    else:
        school_score = 10  # neutral placeholder
        n_school_matches = None

    # ---- Factor 5: weather similarity (0-15 points) — placeholder until Weather API integrated ----
    # TODO: implement real weather-similarity matching once WEATHER_KEY is integrated
    weather_score = 7.5  # neutral placeholder
    n_weather_matches = None

    # ---- Combine and clamp — hard safety net against NaN/inf from any factor ----
    raw_score = sample_size_score + day_type_score + day_specific_score + school_score + weather_score
    if raw_score != raw_score or raw_score in (float('inf'), float('-inf')):
        raw_score = 50
    total_score = max(0, min(100, round(raw_score)))

    # ---- Build rubric-style breakdown ----
    breakdown = [
        {
            'factor': 'Historical Sample Size',
            'points': round(sample_size_score, 1),
            'max_points': 25,
            'detail': f"{n_shifts} shifts logged — more data generally means more reliable predictions"
        },
        {
            'factor': 'Day Type (Weekday/Weekend)',
            'points': round(day_type_score, 1),
            'max_points': 20,
            'detail': (f"Weekend tomorrow — historically {vol_ratio:.1f}× more volatile than weekdays" if is_weekend_tomorrow
                       else "Weekday tomorrow — the most stable, best-covered pattern")
        },
        {
            'factor': f'{tomorrow_day_name or "Day"}-Specific History',
            'points': round(day_specific_score, 1),
            'max_points': 20,
            'detail': (f"{n_same_day} historical {tomorrow_day_name} shifts logged" if n_same_day is not None
                       else "Day-specific data not available")
        },
        {
            'factor': 'School Calendar Match',
            'points': round(school_score, 1),
            'max_points': 20,
            'detail': (f"{n_school_matches} shifts match tomorrow's school status" if n_school_matches is not None
                       else "School status not yet integrated")
        },
        {
            'factor': 'Weather Similarity',
            'points': round(weather_score, 1),
            'max_points': 15,
            'detail': "Weather matching not yet integrated"
        },
    ]

    return {
        'score': total_score,
        'breakdown': breakdown
    }