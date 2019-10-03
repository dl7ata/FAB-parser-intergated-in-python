APRS_SERVER_HOST = 'euro.aprs2.net'
APRS_SERVER_PORT = 14580
APRS_USER = "DB0TGO-15"
APRS_PASSCODE = "*****"
MY_LAT = 52.5692293
MY_LON = 13.2312943
MY_HOME = (52.5692293, 13.2312943)
MY_FILTER = 'm/1000'

# Check that APRS_USER and APRS_PASSCODE are set
assert len(APRS_USER) > 3 and len(APRS_PASSCODE) > 0, 'Please set APRS_USER and APRS_PASSCODE in settings.py.'

PAK = ['LOCATION', 'OBJECT', 'ITEM', 'MICE', 'NMEA', 'WX',
       'MESSAGE', 'CAPABILITIES', 'STATUS', 'TELEMETRY',
       'TELEMETRY_MESSAGE', 'DX_SPOT', 'EXPERIMENTAL', 'ERROR']
