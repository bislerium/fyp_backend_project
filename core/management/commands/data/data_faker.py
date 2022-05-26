import enum
import random as rand
import datetime
import exrex
from core.models import FIELD_OF_WORK
from data_provider import DataProvider, EGender
from dateutil.relativedelta import relativedelta


class EContactNumber(enum.Enum):
    PHONE_NUMBER = 0
    NTC_PHONE_NUMBER = 1
    NCELL_PHONE_NUMBER = 2
    SMART_CELL_PHONE_NUMBER = 3
    LAND_LINE_NUMBER = 4
    LOCAL_LAND_LINE_NUMBER = 5

class Name:
    def __init__(self) -> None:
        self.data_provider = DataProvider()

    def randFirstName(self, gender: EGender = EGender.ANY) -> str:
        return rand.choice(self.data_provider.first_names(gender=gender))
    
    def randLastName(self) -> str:
        return rand.choice(self.data_provider.last_names)

    def randFullName(self, gender: EGender = EGender.ANY) -> str:
        return f'{self.randFirstName(gender=gender)} {self.randLastName()}'

class ContactNumber:
    def __init__(self) -> None:
        phone_number_regex = (r'^9[678][01234568]\d{7}$', r'^\+9[678][01234568] \d{3}\-\d{4}$')
        ntc_phone_number_regex = (r'^98[456]\d{7}$', r'^\+98[456] \d{3}\-\d{4}$')
        ncell_phone_number_regex = (r'^98[012]\d{7}$', r'^\+98[012] \d{3}\-\d{4}$')
        smart_cell_phone_number_regex = (r'^9[68][18]\d{7}$', r'^\+9[68][18] \d{3}\-\d{4}$')
        land_line_number_regex = (r'^0[1-9][0-9](4|5|6)\d{5}$', r'^0[1-9][0-9]\-(4|5|6)\d{5}$')
        local_land_line_number_regex = (r'^01(4|5|6)\d{6}$', r'^01\-(4|5|6)\d{6}$')
        self.contact_number_regex = {
            'PHONE_NUMBER' : phone_number_regex, 
            'NTC_PHONE_NUMBER': ntc_phone_number_regex,
            'NCELL_PHONE_NUMBER': ncell_phone_number_regex,
            'SMART_CELL_PHONE_NUMBER': smart_cell_phone_number_regex,
            'LAND_LINE_NUMBER': land_line_number_regex,
            'LOCAL_LAND_LINE_NUMBER': local_land_line_number_regex,
        }

    def random(self, type: EContactNumber = EContactNumber.PHONE_NUMBER, is_formatted: bool = False) -> str:
        return exrex.getone(self.contact_number_regex[type.name][is_formatted.bit_count()])

class RelatedField:
    def __init__(self) -> None:
        self.related_fields = [a[0] for a in FIELD_OF_WORK]
    
    def random(self, min: int = 1, max: int = 8) -> list[str]:
        return rand.choices(self.related_fields, k=rand.randint(min, max))

def randBool() -> bool:
    return bool(rand.randint(0,1))

def randDate(start_datetime: datetime = datetime.datetime.now() - relativedelta(years=100), end_datetime: datetime = datetime.datetime.now(), has_time: bool = False) -> datetime:
    start_date_orand_time = start_datetime if has_time else start_datetime.date()
    end_date_orand_time = end_datetime if has_time else end_datetime.date()
    datetime_difference = end_date_orand_time - start_date_orand_time
    difference = (datetime_difference.days * 24 * 60 * 60) if has_time else datetime_difference.days
    random_from_difference = rand.randrange(difference)
    return start_date_orand_time + (datetime.timedelta(seconds=random_from_difference) if has_time else datetime.timedelta(days=random_from_difference))

def randEmail(name: str):
    _ = ('\.' if randBool() else '').join(name.split())
    regex = fr'{_}\d{{{rand.randint(0,4)}}}@(gmail|hotmail|msn|yahoo|outlook|aol)\.com'
    return exrex.getone(regex)



    


