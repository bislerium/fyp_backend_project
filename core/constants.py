import re

phone_number_regex = (re.compile('^9[678][01234568]\d{7}$'), re.compile('^\+9[678][01234568] \d{3}\-\d{4}$'))
ntc_phone_number_regex = (re.compile('^98[456]\d{7}$'), re.compile('^\+98[456] \d{3}\-\d{4}$'))
ncell_phone_number_regex = (re.compile('^98[012]\d{7}$'), re.compile('^\+98[012] \d{3}\-\d{4}$'))
smart_cell_phone_number_regex = (re.compile('^9[68][18]\d{7}$'), re.compile('^\+9[68][18] \d{3}\-\d{4}$'))
land_line_number_regex = (re.compile('^0[1-9][0-9](4|5|6)\d{5}$'), re.compile('^0[1-9][0-9]\-(4|5|6)\d{5}$'))
local_land_line_number_regex = (re.compile('^01(4|5|6)\d{6}$'), re.compile('^01\-(4|5|6)\d{6}$'))

contact_number_regex = (phone_number_regex, ntc_phone_number_regex, ncell_phone_number_regex, smart_cell_phone_number_regex, land_line_number_regex, local_land_line_number_regex)