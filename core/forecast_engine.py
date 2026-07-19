import time


def build_prompt(target_product, tracker_extract, tracker_note,
                 fk_extract, fk_note, weather_string,
                 school_status, unit_price):
    """
    Builds the structured Gemini prompt for a single product.
    Separated from the API call so it can be tested independently.
    """
    waste_col = f"{target_product}_Waste_Count"
    price_str = f"${unit_price}" if unit_price else "Price not found."

    return f"""You are an inventory analyst for TOUS LES JOURS, a French-Asian artisanal bakery inside H Mart, Cary NC. Hours: 9AM-7:30PM.

TASK: Predict the closing leftover count for '{target_product}' tomorrow. This product was selected because its waste pattern is highly unpredictable historically. Optimize for accuracy. Follow the data exactly.

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
- Compare waste on REGULAR_SCHOOL_DAY vs NO_STUDENT_DAY rows to detect school-status sensitivity
- Find rows whose full context most closely matches tomorrow and weight those waste counts highest
- BOGO deals in Shift_Notes artificially suppress waste — discount those rows if tomorrow has no deal
- Do not invent patterns. Small sample — read numbers exactly

DATA:
1. TRACKER (PRIMARY): {tracker_note}
2. FK DELIVERY PROXY (SUPPLEMENTARY): {fk_note} — item demand direction only, not volume

TOMORROW: Weather: {weather_string} | School: {school_status} | Price: {price_str}

TRACKER DATA:
{tracker_extract}

FK PROXY DATA:
{fk_extract}

Return exactly three lines, no markdown, no extra text:
FORECAST: {target_product} | Predicted Leftover Count at Closing: [whole number]
FINANCIAL RISK: Projected Waste Capital Loss: $[{unit_price if unit_price else 'unit price'} x leftover count]
STRATEGIC LOGIC: [2-3 short reasons separated by " | ", each under 12 words, written in plain everyday language for a store manager — NOT a data analyst. Do not use internal field names, enum values, or technical jargon anywhere in this line (never write things like NO_STUDENT_DAY, REGULAR_SCHOOL_DAY, CaryHigh_ Status, Traffic_Density, BOGO, Shift_Notes, or row/column references). Instead translate them into natural phrasing, for example: NO_STUDENT_DAY -> "school is out", REGULAR_SCHOOL_DAY -> "school is in session", BOGO -> "a buy-one-get-one deal", Traffic_Density 1/2/3 -> "quiet/typical/busy foot traffic", Shift_Notes about rain -> "rainy weather". Each reason should read like a manager explaining their gut call to a coworker, e.g.: "School's out, so fewer walk-in customers" | "Similar warm days sold out completely" | "No promo running, unlike last time"]"""


def call_gemini_with_retry(client, prompt, max_retries=3, base_delay=15):
    """
    Calls Gemini with retry logic.
    Stops immediately on daily quota exhaustion (429 daily limit).
    Retries up to 3 times on temporary server errors (503).
    Wait schedule: 15s → 30s → 45s.
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if '429' in error_str and 'GenerateRequestsPerDayPerProjectPerModel' in error_str:
                raise RuntimeError("Daily Gemini quota exhausted.") from e
            if '503' in error_str or 'UNAVAILABLE' in error_str:
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (attempt + 1))
                    continue
            raise