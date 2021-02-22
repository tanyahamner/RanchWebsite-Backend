import re

def strip_phone(phone):
    if phone is None or phone == '':
        return ''
         
    return re.sub('[^0-9]+', '', phone)
