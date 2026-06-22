"""
generate_synthetic_data.py
Run once from the terminal: python generate_synthetic_data.py
Generates data/synthetic_tracker.csv and data/synthetic_pricing.csv
for the public Streamlit demo. Real TLJ data never touches the live site.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

PRODUCTS = [
    'ChestnutPanBread', 'MorningBread', 'MochaBread', 'MagicMochaBread',
    'CoffeeBun', 'GarlicStick', 'CreamCheeseGarlicBread', 'SaltButterRoll',
    'PlusMilkRoll', 'ButterCreamBread', 'TaroButterCreamBread', 'Soboro',
    'CustardCreamSoboro', 'CustardBun', 'RedBeanBread', 'RedBeanMilkCreamBread',
    'PremiumWalnutRedBeanBread', 'MilkCreamBread', 'TaroCreamBun',
    'HoneyCheeseMochiPancake', 'CornCheeseDonut', 'MilkSoftBread',
    'MilkyPuffyBread', 'StrawberrySoftBread', 'HoneydewSoftBread',
    'BananaSoftBread', 'CreamCheeseWalnutBread', 'CranberryCreamCheeseBun',
    'ChocoDippedWaffle', 'MangoCreamDonut', 'MatchaCreamDonut', 'UbeCreamDonut',
    'VanillaCreamDonut', 'ChocoCreamDonut', 'SweetRiceRedBeanDonut',
    'RedBeanDonut', 'TwistDonut', 'StrawberryCreamCroissant',
    'ChocoHazelnutFillingCroissant', 'ChocoDippedCroissant', 'AlmondCroissant',
    'JalapenoCheeseCroissant', 'PainAuRaisin', 'PainAuChocolat',
    'ChocolateAvalanche', 'MontBlancPastry', 'GuavaDanish',
    'SweetBlueberryCreamCheeseDanish', 'SpinachFetaCheeseDanish',
    'GreekYogurtCherryDanish', 'MixedBerryDanish', 'MushroomOnionCheeseDanish',
    'CaramelApplePie', 'YuzuPie', 'PortugueseEggTart', 'CreamCheeseTart',
    'Croquette', 'KimchiCroquette', 'CurryCroquette', 'ChocoFilledCookie',
    'ChocoShellBread', 'ChocoPretzelPastry', 'CustardAlmondPretzelPastry',
    'PlainCloudBagel', 'EverythingSeasoningCloudBagel'
]

WASTE_RANGES = {
    'CustardBun': (0, 24), 'GuavaDanish': (0, 18),
    'SweetRiceRedBeanDonut': (0, 20), 'ChocoHazelnutFillingCroissant': (0, 11),
    'PainAuChocolat': (0, 13), 'SpinachFetaCheeseDanish': (0, 12),
    'Croquette': (0, 10), 'TwistDonut': (0, 16),
    'CranberryCreamCheeseBun': (0, 9), 'VanillaCreamDonut': (0, 11),
}
DEFAULT_WASTE_RANGE = (0, 5)

WEATHER_OPTIONS = [
    'Clear Sky', 'Scattered Clouds', 'Overcast Clouds',
    'Light Rain', 'Moderate Rain', 'High Humidity'
]
DAYS = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
SCHOOL_STATUSES = ['NO_STUDENT_DAY', 'OPEN']
NOTES_OPTIONS = [
    'Steady flow throughout the day.',
    'BOGO on croissants today, busy morning.',
    'Super slow day, barely any customers.',
    'Rained most of the afternoon, low traffic.',
    'Busy weekend rush, sold out of several items.',
    'Normal day, nothing unusual.',
    None
]

rows = []
start_date = date(2026, 1, 10)

for i in range(40):
    shift_date = start_date + timedelta(days=i * 3)
    day = DAYS[i % len(DAYS)]
    traffic = random.choice([1, 2, 3])
    weather = random.choice(WEATHER_OPTIONS)
    school = 'NO_STUDENT_DAY' if day in ['Saturday', 'Sunday'] else random.choice(SCHOOL_STATUSES)
    temp_high = random.randint(65, 95)
    temp_low = temp_high - random.randint(4, 12)
    humidity = round(random.uniform(0.20, 0.85), 2)
    notes = random.choice(NOTES_OPTIONS)

    row = {
        'Date': shift_date.strftime('%Y-%m-%d'),
        'Day_of_Week': day,
        'High_Low_Temp_From_12PM_to_6PM': f"{temp_high} / {temp_low} degrees Fahrenheit",
        'Humidity_From_12PM_to_6PM': humidity,
        'Weather_Description': weather,
        'CaryHigh_ Status': school,
        'Shift_Notes': notes,
        'Traffic_Density': traffic,
    }

    is_bogo = notes and 'BOGO' in notes
    is_slow = traffic == 1 or 'slow' in (notes or '').lower() or 'Rain' in weather

    for product in PRODUCTS:
        low, high = WASTE_RANGES.get(product, DEFAULT_WASTE_RANGE)
        base = random.randint(low, high)
        if is_slow:
            base = min(int(base * 1.4), high)
        if is_bogo:
            base = max(0, int(base * 0.5))
        row[f"{product}_Waste_Count"] = base

    rows.append(row)

df = pd.DataFrame(rows)
out_path = os.path.join(os.path.dirname(__file__), 'data', 'synthetic_tracker.csv')
df.to_csv(out_path, index=False)
print(f"✅ Synthetic tracker: {len(df)} shifts, {len(PRODUCTS)} products → {out_path}")

pricing_data = {p: round(random.uniform(3.25, 8.50), 2) for p in PRODUCTS}
pricing_df = pd.DataFrame([pricing_data])
pricing_out = os.path.join(os.path.dirname(__file__), 'data', 'synthetic_pricing.csv')
pricing_df.to_csv(pricing_out, index=False)
print(f"✅ Synthetic pricing → {pricing_out}")