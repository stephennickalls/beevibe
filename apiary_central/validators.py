
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
import re
from datetime import datetime

def validate_datetime():
    pass

def validate_datetime_format(value):
    print(f'####### initial value = {type(value)}')
    # convert value to string
    try:
        datetime_string = value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')  # ISO 8601 format
    except ValueError:
            raise ValidationError('Invalid datetime format, please use YYYY-MM-DDTHH:MM[:ss[.uuuuuu]][TZ] format.')
    print(f'####### date string = {datetime_string}')
    # Regular expression to match zeros in the time component
    if re.match(r"\d{4}-\d{2}-\d{2}T00:00:00\.000000Z", datetime_string):
        print("The time component is all zeros.")
        raise ValidationError('Invalid datetime format, no time value was provided')
    
    return value
    
    
