import pandas as pd
import os
from datetime import datetime


LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'prediction_log.csv')


def log_prediction(product: str, predicted: int,
                   actual: int = None, date: str = None):
    """
    Appends a prediction (and optionally the actual result) to the log CSV.
    Call after each real forecast run with the predicted value.
    Fill in actual value the next day after your shift.
    """
    row = {
        'date': date or datetime.now().strftime('%Y-%m-%d'),
        'product': product,
        'predicted': predicted,
        'actual': actual
    }
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(LOG_PATH, index=False)


def load_log() -> pd.DataFrame:
    """
    Loads the prediction log.
    Returns empty DataFrame if no log exists yet.
    """
    if os.path.exists(LOG_PATH):
        return pd.read_csv(LOG_PATH)
    return pd.DataFrame(columns=['date', 'product', 'predicted', 'actual'])


def calculate_accuracy(log_df: pd.DataFrame) -> dict:
    """
    Calculates MAE and directional accuracy from the prediction log.
    Only uses rows where actual values have been filled in.
    """
    complete = log_df.dropna(subset=['actual']).copy()
    if complete.empty:
        return {
            'mae': None,
            'mae_pct': None,
            'directional_accuracy': None,
            'n': 0
        }

    complete['abs_error'] = abs(complete['predicted'] - complete['actual'])
    mae = complete['abs_error'].mean()
    mean_actual = complete['actual'].mean()
    mae_pct = (mae / mean_actual * 100) if mean_actual > 0 else None

    median_actual = complete['actual'].median()
    complete['correct_direction'] = (
        (complete['predicted'] > median_actual) ==
        (complete['actual'] > median_actual)
    )
    directional_accuracy = complete['correct_direction'].mean()

    return {
        'mae': round(mae, 2),
        'mae_pct': round(mae_pct, 1) if mae_pct else None,
        'directional_accuracy': round(directional_accuracy * 100, 1),
        'n': len(complete)
    }