from datetime import datetime

def transform_datetime(dt: datetime) -> str:
    # Format the datetime object into the desired string format
    formatted_datetime = dt.strftime('%Y-%m-%d %H:%M:%S.%f%z')
    return formatted_datetime

# Example usage:
import zoneinfo

dt = datetime(2021, 6, 16, 20, 14, 9, 309735, tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC'))
print(transform_datetime(dt))
