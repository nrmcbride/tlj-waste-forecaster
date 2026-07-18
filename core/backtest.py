import pandas as pd
import time
from datetime import datetime


def run_backtest(tracker_df: pd.DataFrame,
                 products: list,
                 client,
                 min_history: int = 5) -> pd.DataFrame:
    """
    Walk-forward backtest across the provided product list.
    For each shift (after min_history prior shifts exist), the model
    sees only shifts BEFORE that date and predicts the waste count.
    The prediction is compared to the actual recorded value.

    CAVEAT: This is in-sample backtesting on a small dataset.
    Early predictions are based on very little history.
    Treat results as directional, not a validated performance guarantee.
    """
    from core.forecast_engine import build_prompt, call_gemini_with_retry

    tracker_sorted = tracker_df.sort_values('Date').reset_index(drop=True)
    context_cols = [c for c in tracker_df.columns if '_Waste_Count' not in c]
    results = []

    for product in products:
        waste_col = f"{product}_Waste_Count"
        if waste_col not in tracker_sorted.columns:
            continue

        for idx in range(min_history, len(tracker_sorted)):
            history = tracker_sorted.iloc[:idx]
            actual_row = tracker_sorted.iloc[idx]
            actual_value = actual_row[waste_col]
            target_date = str(actual_row['Date'])[:10]

            tracker_extract = history[context_cols + [waste_col]].to_string(index=False)
            tracker_note = f"'{waste_col}' found. {len(history)} prior shifts available."

            # Construct a weather-like string from the actual row's conditions
            weather_string = (
                f"Temp: {actual_row.get('High_Low_Temp_From_12PM_to_6PM', 'N/A')}, "
                f"Humidity: {actual_row.get('Humidity_From_12PM_to_6PM', 'N/A')}, "
                f"Conditions: {actual_row.get('Weather_Description', 'N/A')}"
            )
            school_status = str(actual_row.get('CaryHigh_ Status', 'Unknown'))

            prompt = build_prompt(
                target_product=product,
                tracker_extract=tracker_extract,
                tracker_note=tracker_note,
                fk_extract="Not used in backtest.",
                fk_note="Not used in backtest.",
                weather_string=weather_string,
                school_status=school_status,
                unit_price=None
            )

            # Append instruction to return only a number
            prompt += "\n\nFor this backtest, return ONLY the predicted whole number on the first line."

            try:
                result = call_gemini_with_retry(client, prompt)
                first_line = result.strip().split('\n')[0]
                digits = ''.join(filter(str.isdigit, first_line))
                predicted_value = int(digits) if digits else 0

                results.append({
                    'product': product,
                    'date': target_date,
                    'history_size': idx,
                    'predicted': predicted_value,
                    'actual': int(actual_value),
                    'abs_error': abs(predicted_value - int(actual_value))
                })

                print(
                    f"  {product:30s} {target_date} | "
                    f"Predicted: {predicted_value:3d} | "
                    f"Actual: {int(actual_value):3d} | "
                    f"Error: {abs(predicted_value - int(actual_value)):3d} | "
                    f"History: {idx} shifts"
                )

            except RuntimeError as e:
                print(f"\n🛑 {e}")
                return pd.DataFrame(results)
            except Exception as e:
                print(f"  ❌ Failed: {product} {target_date} | {e}")

            time.sleep(2)

    return pd.DataFrame(results)


def summarize_backtest(results_df: pd.DataFrame) -> dict:
    """
    Calculates summary accuracy metrics from backtest results.
    """
    if results_df.empty:
        return {}

    mae = results_df['abs_error'].mean()
    mean_actual = results_df['actual'].mean()
    mae_pct = (mae / mean_actual * 100) if mean_actual > 0 else None

    return {
        'n_predictions': len(results_df),
        'n_products': results_df['product'].nunique(),
        'mae': round(mae, 2),
        'mae_pct': round(mae_pct, 1) if mae_pct else None,
        'mean_actual': round(mean_actual, 2),
    }