"""
Manual walk-forward backtest — run this once per session.

Uses the same prompt structure as the production Colab forecast script,
adapted to predict a historical day instead of "tomorrow" — the target
shift's already-logged conditions stand in for the live weather/school API
calls, since those conditions are now known history rather than a forecast.

Each run:
1. Loads tracker, pricing, and FK delivery proxy data.
2. Excludes any dates in EXCLUDED_DATES (verified anomalies only).
3. Finds the next shift (past WALK_FORWARD_START_SHIFT) that still has
   un-backtested products, finishing any partially-completed shift before
   moving to the next one.
4. Re-selects the top-volatile products using ONLY shifts before that date.
5. Calls Gemini once per product using the full production prompt.
6. Appends results to data/backtest_results.csv.

If Gemini's quota is hit mid-run, progress is saved and the next run
picks up exactly where this one left off.

Run: python3 scripts/run_backtest.py
"""

import os
import sys
import re
import time
import pandas as pd
from google import genai

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.data_loader import load_tracker, load_pricing, get_top_volatile_products

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
BACKTEST_PATH = os.path.join(DATA_DIR, 'backtest_results.csv')
FK_PROXY_PATH = os.path.join(DATA_DIR, 'FrenchKorean_Daily_Proxy_Sales.csv')
WALK_FORWARD_START_SHIFT = 20  # backtesting begins at the shift AFTER this index

# Shifts excluded from backtesting: verified anomalies (holidays, closures,
# extreme events) that would distort both training data and MAE if included.
# Document the reason for each — do not add entries based on error size.
EXCLUDED_DATES = {
    # '2026-07-04': 'July 4th — atypical holiday foot traffic pattern',
}

AI_KEY = os.environ.get('AI_KEY')
if not AI_KEY:
    raise RuntimeError("AI_KEY not found in environment. Set it with: export AI_KEY='your-key-here'")

client = genai.Client(api_key=AI_KEY)


def call_with_retry(client, prompt, max_retries=3, base_delay=15):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if '429' in error_str and 'GenerateRequestsPerDayPerProjectPerModel' in error_str:
                raise RuntimeError("Daily Gemini quota exhausted.") from e
            if '503' in error_str or 'UNAVAILABLE' in error_str:
                if attempt < max_retries - 1:
                    wait = base_delay * (attempt + 1)
                    print(f"  Server busy, retrying in {wait}s...")
                    time.sleep(wait)
                    continue
            raise


def find_best_proxy_cols(product_name, proxy_item_cols, top_n=2):
    """Finds the most semantically similar columns in the proxy dataset
    for a given product name using word overlap scoring."""
    product_words = set(product_name.lower().replace('_', ' ').split())
    scored = []
    for col in proxy_item_cols:
        col_words = set(col.lower().replace('_', ' ').split())
        overlap = len(product_words & col_words)
        if overlap > 0:
            scored.append((overlap, col))
    scored.sort(reverse=True)
    return [col for _, col in scored[:top_n]]


def get_shift_to_backtest(tracker_df, pricing_df):
    """Returns (idx, row, products_still_needed) for the next shift that
    still has un-backtested products. Finishes partially-completed shifts
    before moving to the next one."""
    eligible = tracker_df.iloc[WALK_FORWARD_START_SHIFT:]

    if os.path.exists(BACKTEST_PATH) and os.path.getsize(BACKTEST_PATH) > 0:
        existing = pd.read_csv(BACKTEST_PATH)
    else:
        existing = pd.DataFrame(columns=['product', 'date'])

    for idx, row in eligible.iterrows():
        date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
        train_df = tracker_df.iloc[:idx]

        if len(train_df) < 5:
            continue

        vol_df = get_top_volatile_products(train_df, pricing_df, n=12, backtest_path=BACKTEST_PATH)
        needed_products = set(vol_df['product'].tolist())

        done_products = set(existing[existing['date'] == date_str]['product'].tolist())
        still_needed = needed_products - done_products

        if still_needed:
            return idx, row, sorted(still_needed)

    return None, None, None


def main():
    tracker_df = load_tracker()
    pricing_df = load_pricing()
    pricing_dict = dict(zip(pricing_df.columns.tolist(), pricing_df.iloc[0].tolist()))

    if os.path.exists(FK_PROXY_PATH):
        delivery_proxy = pd.read_csv(FK_PROXY_PATH)
        fk_date_col = [c for c in delivery_proxy.columns if 'unnamed' in c.lower() or 'date' in c.lower()]
        fk_item_cols = [c for c in delivery_proxy.columns if c not in fk_date_col]
    else:
        delivery_proxy = None
        fk_date_col = []
        fk_item_cols = []

    if EXCLUDED_DATES:
        before_count = len(tracker_df)
        tracker_df = tracker_df[~tracker_df['Date'].astype(str).isin(EXCLUDED_DATES.keys())].reset_index(drop=True)
        excluded_count = before_count - len(tracker_df)
        if excluded_count:
            print(f"Excluded {excluded_count} anomaly date(s): {list(EXCLUDED_DATES.values())}")
            print("=" * 65)

    target_idx, target_row, product_list = get_shift_to_backtest(tracker_df, pricing_df)

    if target_row is None:
        print(f"All eligible shifts (past shift {WALK_FORWARD_START_SHIFT}) are fully backtested.")
        print("Log more shifts and re-run to continue building the backtest.")
        return

    target_date = target_row['Date']
    print(f"Backtesting shift dated {target_date} — {len(product_list)} products still needed...")
    print("=" * 65)

    train_df = tracker_df.iloc[:target_idx]
    context_cols = [c for c in tracker_df.columns if not c.endswith('_Waste_Count')]

    # Target shift's already-known conditions stand in for the live
    # weather/school API calls — this day already happened, so its actual
    # recorded weather and school status ARE the "forecast" being tested.
    weather_desc = target_row.get('Weather_Description', 'Unknown')
    temp = target_row.get('High_Low_Temp_From_12PM_to_6PM', 'Unknown')
    humidity = target_row.get('Humidity_From_12PM_to_6PM', 'Unknown')
    tomorrow_weather_string = f"{weather_desc}, Temp: {temp}, Humidity: {humidity}"
    school_status = target_row.get('CaryHigh_ Status', 'Unknown')

    results = []
    quota_exhausted = False

    for i, target_product in enumerate(product_list):
        if quota_exhausted:
            break

        waste_col = f"{target_product}_Waste_Count"
        if waste_col not in tracker_df.columns:
            continue

        actual_value = target_row.get(waste_col)
        if pd.isna(actual_value):
            print(f"  Skipping {target_product} — no actual value logged for this shift.")
            continue

        # Compute stats for this product from TRAINING data only (no future leakage)
        train_series = train_df[waste_col].dropna()
        mean_waste = train_series.mean()
        max_waste = train_series.max()
        std_waste = train_series.std()
        cv_waste = std_waste / (mean_waste + 0.1) if pd.notna(std_waste) else 0

        tracker_extract = train_df[context_cols + [waste_col]].to_string(index=False)
        tracker_note = (f"'{waste_col}' found. {len(train_df)} shifts. "
                        f"Mean waste: {mean_waste:.1f}, max: {max_waste:.0f}, std: {std_waste:.1f}, "
                        f"coefficient of variation: {cv_waste:.2f} (selected for high unpredictability).")

        unit_price = pricing_dict.get(target_product, None)
        price_str = f"${unit_price}" if unit_price else "Price not found."

        if delivery_proxy is not None:
            fk_matched = find_best_proxy_cols(target_product, fk_item_cols, top_n=2)
            if fk_matched:
                fk_extract = delivery_proxy[fk_date_col + fk_matched].head(10).to_string(index=False)
                fk_note = f"Matched: {fk_matched}. Delivery sales — use for item demand direction only, not volume."
            else:
                fk_extract = "No match."
                fk_note = "No match — rely on tracker only."
        else:
            fk_extract = "Not available."
            fk_note = "No proxy data available."

        master_prompt = f"""You are an inventory analyst for TOUS LES JOURS, a French-Asian artisanal bakery inside H Mart, Cary NC. Hours: 9AM-7:30PM.

TASK: Predict the closing leftover count for '{target_product}' tomorrow. This product was selected because its waste pattern is highly unpredictable historically — optimize for accuracy. Follow the data exactly.

TRACKER COLUMNS:
- Date, Day_of_Week: shift date and day
- High_Low_Temp_From_12PM_to_6PM: temperature during peak hours
- Humidity_From_12PM_to_6PM: humidity during peak hours
- Weather_Description: observed weather that shift
- CaryHigh_ Status: school status (REGULAR_SCHOOL_DAY or NO_STUDENT_DAY)
- Traffic_Density: H Mart foot traffic (1=low, 2=medium, 3=high)
- Shift_Notes: BOGO deals, rushes, unusual events — read carefully
- {waste_col}: actual closing leftover count

HOW TO USE THE TRACKER:
- Cross-reference each row's waste count against ALL context columns
- Compare waste on REGULAR_SCHOOL_DAY vs NO_STUDENT_DAY rows to detect school-status sensitivity for this item
- Find rows whose full context most closely matches tomorrow and weight those waste counts highest
- BOGO deals in Shift_Notes artificially suppress waste — discount those rows if tomorrow has no deal
- Do not invent patterns. {len(train_df)} shifts is a small sample — read numbers exactly

DATA:
1. TRACKER (PRIMARY): {tracker_note}
2. FK DELIVERY PROXY (SUPPLEMENTARY): {fk_note} — item demand direction only, not volume

TOMORROW: Weather: {tomorrow_weather_string} | School: {school_status} | Price: {price_str}

TRACKER DATA:
{tracker_extract}

FK PROXY DATA:
{fk_extract}

Return exactly three lines, no markdown, no extra text:
FORECAST: {target_product} | Predicted Leftover Count at Closing: [whole number]
FINANCIAL RISK: Projected Waste Capital Loss: $[{unit_price if unit_price else 'unit price'} x leftover count]
STRATEGIC LOGIC: [One sentence: which tracker rows drove the prediction, how CaryHigh_ Status correlated with waste for this item, and how Shift_Notes affected the estimate]"""

        try:
            result = call_with_retry(client, master_prompt)

            predicted_value = None
            strategic_logic = ""
            for line in result.strip().split('\n'):
                if line.startswith("FORECAST:"):
                    nums = re.findall(r'\d+', line)
                    if nums:
                        predicted_value = int(nums[0])
                elif line.startswith("STRATEGIC LOGIC:"):
                    strategic_logic = line.replace("STRATEGIC LOGIC:", "").strip()

            if predicted_value is not None:
                abs_error = abs(predicted_value - actual_value)
                results.append({
                    'product': target_product,
                    'date': pd.to_datetime(target_date).strftime('%Y-%m-%d'),
                    'actual': actual_value,
                    'predicted': predicted_value,
                    'abs_error': abs_error,
                    'unit_price': unit_price if unit_price else 0,
                    'strategic_logic': strategic_logic
                })
                print(f"  {target_product}: actual={actual_value}, predicted={predicted_value}, error={abs_error}")
            else:
                print(f"  {target_product}: could not parse prediction from response")
                print(f"    Raw response: {result}")

        except RuntimeError:
            print(f"\n  Quota exhausted after {i} products. Saving progress.")
            quota_exhausted = True
        except Exception as e:
            print(f"  {target_product}: FAILED — {e}")

        if i < len(product_list) - 1 and not quota_exhausted:
            time.sleep(2)

    if results:
        new_df = pd.DataFrame(results)
        if os.path.exists(BACKTEST_PATH) and os.path.getsize(BACKTEST_PATH) > 0:
            existing_df = pd.read_csv(BACKTEST_PATH)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df
        combined_df.to_csv(BACKTEST_PATH, index=False)
        print("=" * 65)
        print(f"Saved {len(results)} predictions for shift {target_date}.")
        print(f"Total backtested predictions so far: {len(combined_df)}")
    else:
        print("No results generated this run.")

    if quota_exhausted:
        print("\nRun again (same or next day) to finish this shift before moving to the next.")


if __name__ == '__main__':
    main()