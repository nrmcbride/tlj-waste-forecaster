"""
Nightly batch forecast job.

Runs Gemini once per top-12 volatile product using real tracker/pricing
data, tomorrow's weather, and tomorrow's school status. Writes results to
data/latest_forecast.csv, which the Streamlit app reads on next load.

Run manually:
    python scripts/run_nightly_forecast.py

Requires env vars (or Streamlit secrets equivalents passed as env in CI):
    AI_KEY       - Gemini API key
    WEATHER_KEY  - OpenWeather API key
"""
import os
import re
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from google import genai

from core.data_loader import load_tracker, load_pricing, get_top_volatile_products
from core.weather import get_tomorrow_weather
from core.school_calendar import get_school_status
from core.forecast_engine import build_prompt, call_gemini_with_retry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_PATH = os.path.join(DATA_DIR, 'latest_forecast.csv')
BACKTEST_PATH = os.path.join(DATA_DIR, 'backtest_results.csv')


def main():
    AI_KEY = os.getenv("AI_KEY", "")
    WEATHER_KEY = os.getenv("WEATHER_KEY", "")

    if not AI_KEY:
        print("AI_KEY not set. Aborting nightly forecast run.")
        sys.exit(1)

    tracker_df = load_tracker()
    pricing_df = load_pricing()
    pricing_dict = dict(zip(pricing_df.columns.tolist(), pricing_df.iloc[0].tolist()))

    vol_df = get_top_volatile_products(tracker_df, pricing_df, n=12, backtest_path=BACKTEST_PATH)
    products = vol_df['product'].tolist()

    if not products:
        print("No volatile products found — check tracker data. Aborting.")
        sys.exit(1)

    weather_string = (
        get_tomorrow_weather(WEATHER_KEY) if WEATHER_KEY
        else "Weather API key not configured. Defaulting to general averages."
    )
    school_status = get_school_status()

    client = genai.Client(api_key=AI_KEY)

    context_cols = [c for c in tracker_df.columns if '_Waste_Count' not in c]

    rows = []
    for product in products:
        waste_col = f"{product}_Waste_Count"
        if waste_col in tracker_df.columns:
            tracker_extract = tracker_df[context_cols + [waste_col]].to_string(index=False)
            tracker_note = f"'{waste_col}' found. {len(tracker_df)} logged shifts."
        else:
            tracker_extract = tracker_df[context_cols].to_string(index=False)
            tracker_note = "No column found."

        unit_price = pricing_dict.get(product, None)

        prompt = build_prompt(
            target_product=product,
            tracker_extract=tracker_extract,
            tracker_note=tracker_note,
            fk_extract="Not available in nightly batch.",
            fk_note="No proxy data used in nightly batch.",
            weather_string=weather_string,
            school_status=school_status,
            unit_price=unit_price
        )

        predicted_count = None
        financial_risk = None
        strategic_logic = None

        try:
            result = call_gemini_with_retry(client, prompt)
            for line in result.strip().split('\n'):
                if line.startswith("FORECAST:"):
                    nums = re.findall(r'\d+', line)
                    if nums:
                        predicted_count = int(nums[0])
                elif line.startswith("FINANCIAL RISK:"):
                    financial_risk = line.replace("FINANCIAL RISK:", "").strip()
                elif line.startswith("STRATEGIC LOGIC:"):
                    strategic_logic = line.replace("STRATEGIC LOGIC:", "").strip()
        except RuntimeError as e:
            print(f"Stopping early — {e}")
            break
        except Exception as e:
            print(f"Failed on {product}: {e}")
            continue

        if predicted_count is None:
            print(f"No parseable forecast for {product}, skipping.")
            continue

        loss_val = round(predicted_count * unit_price) if unit_price else 0
        price_str = f"${unit_price:.2f}" if unit_price else "price n/a"

        rows.append({
            'Product': f"{product} ({price_str})",
            'Predicted Waste': predicted_count,
            'Loss': f"${loss_val}",
            'Explanation': strategic_logic or "No explanation returned.",
        })

        print(f"  {product:25s} -> {predicted_count} units | {financial_risk or ''}")
        time.sleep(2)

    if not rows:
        print("No forecasts produced — leaving existing latest_forecast.csv untouched.")
        sys.exit(1)

    out_df = pd.DataFrame(rows)
    os.makedirs(DATA_DIR, exist_ok=True)

    eastern_now = datetime.now(ZoneInfo("America/New_York"))
    out_df['Generated'] = eastern_now.strftime('%Y-%m-%d %H:%M:%S')
    out_df['Target Date'] = (eastern_now + timedelta(days=1)).strftime('%Y-%m-%d')

    out_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nWrote {len(out_df)} forecasts to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()