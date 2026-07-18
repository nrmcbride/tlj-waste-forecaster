import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def get_tomorrow_weather(api_key: str) -> str:
    """
    Fetches a 3-point weather forecast for tomorrow (9AM, 2PM, 7PM)
    for Cary, NC using the OpenWeather 5-day/3-hour forecast API.
    Returns a formatted string ready to pass into the Gemini prompt.
    """
    LATITUDE = "35.791538"
    LONGITUDE = "-78.781120"

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={LATITUDE}&lon={LONGITUDE}&appid={api_key}&units=imperial"
    )
    response = requests.get(url)

    if response.status_code != 200:
        return "Weather API unreachable. Defaulting to general averages."

    w_data = response.json()

    eastern_now = datetime.now(ZoneInfo("America/New_York"))
    tomorrow_date = eastern_now + timedelta(days=1)
    tomorrow_str = tomorrow_date.strftime('%Y-%m-%d')
    target_day_name = tomorrow_date.strftime('%A, %B %d')

    target_hours = {'morning': 9, 'midday': 14, 'evening': 19}
    chunks = {}

    for chunk in w_data['list']:
        chunk_dt = datetime.strptime(chunk['dt_txt'], '%Y-%m-%d %H:%M:%S')
        if chunk_dt.strftime('%Y-%m-%d') == tomorrow_str:
            for label, hour in target_hours.items():
                if chunk_dt.hour == hour and label not in chunks:
                    chunks[label] = chunk

    tomorrow_chunks = [
        c for c in w_data['list']
        if datetime.strptime(c['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') == tomorrow_str
    ]
    for label, hour in target_hours.items():
        if label not in chunks and tomorrow_chunks:
            chunks[label] = min(
                tomorrow_chunks,
                key=lambda c, h=hour: abs(
                    datetime.strptime(c['dt_txt'], '%Y-%m-%d %H:%M:%S').hour - h
                )
            )

    if not chunks:
        return "Weather data unavailable for tomorrow."

    morning_temp = chunks['morning']['main']['temp']
    morning_cond = chunks['morning']['weather'][0]['description']
    midday_temp = chunks['midday']['main']['temp']
    midday_cond = chunks['midday']['weather'][0]['description']
    evening_temp = chunks['evening']['main']['temp']
    evening_cond = chunks['evening']['weather'][0]['description']

    return (
        f"Forecast for {target_day_name} -> "
        f"Open (9:00 AM): {morning_temp}°F, {morning_cond.title()} | "
        f"Midday (2:00 PM): {midday_temp}°F, {midday_cond.title()} | "
        f"Close (7:30 PM): {evening_temp}°F, {evening_cond.title()}"
    )