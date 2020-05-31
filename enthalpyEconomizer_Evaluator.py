# Specific enthalpy of moist air can be expressed as:
#
# h = ha + x * hw
#
# h = specific enthalpy of moist air (kJ/kg or Btu/lb)
#
# ha = specific enthalpy of dry air (kJ/kg or Btu/lb)
#    = Cpa * t
#    where      Cpa = (specific heat of dry air)                    ------->    (0.24 BTU/lb F)
#               t = air temperature                                             (between -150F and +212F)
#
# x = humidity ratio (kg/kg or lb/lb)                               ------->    (derived from relative humidity)
#
# hw = specific enthalpy of water vapor (kJ/kg or Btu/lb)
#    = Cpw * t + Hwe
#    where      Cpw = (specific heat of water vapor)                ------->    (0.444 BTU/lb F)
#               t = water vapor temperature
#               Hwe = (evaporation heat of water)                   ------->    (1061 BTU/lb)
#
# in Imperial units
# h = (0.240 Btu/lb F) t + x [(0.444 Btu/lb F) t + (1061 Btu/lb)]                            (6)
#
# where
#
# h = enthalpy (Btu/lb)
#
# x = mass of water vapor (lb/lb of dry air)
#
# t = temperature (F)
#
# Calculate the enthalpy of indoor air
# Calculate the enthalpy of outdoor air
# Compare the two values to determine if economizer operation is warranted.
#
from os import path
import csv
import urllib.request
#

print("ECONOMIZER CONTROL WEATHER CONDITIONS EVALUATOR v1.0\n")
#
# URL for current weather observations
rooturl = "http://tgftp.nws.noaa.gov/data/observations/metar/decoded/"
#
# Concatenate rooturl and airport code to obtain full url for decoded current weather observations
ksby = "KSBY.TXT"
url = rooturl + ksby
#
# Retrieve current weather observations from KSBY
print(" *** Retrieving decoded weather observation data from noaa.gov - ")

# Perform http GET request for weather data
req = urllib.request.Request(url)
resp = urllib.request.urlopen(req)
respdata = resp.read()
wxdata = str(respdata)

# Find constant strings in observational weather data text and obtain index numbers to extract substrings

# Observation Date Stamp:
localDateStartIdx = wxdata.find("EDT") - 24
localDateEndIdx = wxdata.find("EDT") - 12
localDate = wxdata[localDateStartIdx:localDateEndIdx]

# Location Header:
headerStartIdx = 2
headerEndIdx = localDateStartIdx - 6
header = wxdata[headerStartIdx:headerEndIdx]

# Observation Time Stamp:
localTimeStartIdx = wxdata.find("EDT") - 9
localTimeEndIdx = wxdata.find("EDT") + 3
localTime = wxdata[localTimeStartIdx:localTimeEndIdx]

# Wind Speed:
windSpeedStartIdx = wxdata.find("Wind: ")
windSpeedEndIdx = wxdata.find("Visibility: ") - 4
windSpeed = wxdata[windSpeedStartIdx:windSpeedEndIdx]

# Visibility:
visibilityStartIdx = wxdata.find("Visibility: ")
visibilityEndIdx = wxdata.find("Sky conditions: ") - 4
visibility = wxdata[visibilityStartIdx:visibilityEndIdx]

# Sky Conditions:
skyCondxStartIdx = wxdata.find("Sky conditions: ")
skyCondxEndIdx = wxdata.find("Temperature: ") - 2
skyCondx = wxdata[skyCondxStartIdx:skyCondxEndIdx]

# Weather?

# Temperature:
temperatureStartIdx = wxdata.find("Temperature: ")
temperatureEndIdx = wxdata.find("Dew Point: ") - 2
temperature = wxdata[temperatureStartIdx:temperatureEndIdx]

# Dew Point:
dewPointStartIdx = wxdata.find("Dew Point: ")
dewPointEndIdx = wxdata.find("Relative Humidity: ") - 2
dewPoint = wxdata[dewPointStartIdx:dewPointEndIdx]

# Relative Humidity:
rhStartIdx = wxdata.find("Relative Humidity: ")
rhEndIdx = wxdata.find("Pressure (altimeter): ") - 2
relativeHumidity = wxdata[rhStartIdx:rhEndIdx]

# Pressure:
pressureStartIdx = wxdata.find("Pressure (altimeter): ")
pressureEndIdx = wxdata.find(" hPa)") + 5
pressure = wxdata[pressureStartIdx:pressureEndIdx]

# Obtain indices for:
# Pressure tendency:
pressureTendencyStartIdx = wxdata.find("Pressure tendency: ")
pressureTendencyEndIdx = wxdata.find("ob: ") - 2
pressureTendency = wxdata[pressureTendencyStartIdx:pressureTendencyEndIdx]

# Uncomment wxdata to debug:
# print("\n")
print(f" *** Retrieved {len(wxdata)} bytes - ")
# print(wxdata)
# print("\n")

print(" *** Parsing outdoor weather data - ")
# print(f"{header}")
# print(f"{localDate}")
# print(f"{localTime}")
# print(f"{windSpeed}")
# print(f"{visibility}")
# print(f"{skyCondx}")
# print(f"{temperature}")
# print(f"{dewPoint}")
# print(f"{relativeHumidity}")
# print(f"{pressure}")
# print(f"{pressureTendency}")
# print("\n")
#

# humidityratio CSV formatted lookup table
lookupTablePath = "insert path here"
lookupTableFileName = lookupTablePath + "humidityratio.csv"
if not path.exists(lookupTableFileName):
    print(" *** FATAL ERROR: The humidity ratio lookup table file does not exist.")
    print(" *** Returning to operating system with errorlevel 1.")
    exit(1)
else: print(" *** Humidity ratio lookup table file found - loading contents into memory - \n")

dbTempSatTable = {}
with open(lookupTableFileName,'r', newline='') as lookupTable:
    reader = csv.reader(lookupTable)
    dbTempSatTable = {rows[0]:rows[1] for rows in reader}
#
# Uncomment to debug:
# print(dbTempSatTable)
#
# t = input("Enter outdoor dry bulb temperature")
# outdoorDBTemp = float(t)
#
print(f" *** Weather observations for {header}:")
print(f"{localDate}")
print(f"{localTime}")
print(f"{temperature}")
#
# Convert temperature substring to float for calculations
outdoorDBTemp = float(temperature[13:17])
#
# Round temperature float to zero decimal places & convert to string for dictionary key
outdoorDBTempRoundedKey = str(round(outdoorDBTemp))
#
# print(f"Outdoor DB Temp: {outdoorDBTemp} deg F")
#
# rh = input("Enter indoor relative humidity")
# rhIndoor = float(rh)
#
# Calculate indoor humidity ratio from indoor relative humidity and dry bulb temperature saturation lookup table
# rh = input("Enter outdoor relative humidity")
#
# print(f"Outdoor Relative Humidity: {rhOutdoor}%")
#
print(f"{relativeHumidity}")
rhOutdoor = float(relativeHumidity[19:21])
rhOutdoor = rhOutdoor/100
#
# x = input("Enter outdoor humidity ratio")
x = float(dbTempSatTable[outdoorDBTempRoundedKey]) * rhOutdoor
x = float(x)/7000  # convert from gr/LB to LB/LB
#
OutdoorEnthalpy = (0.240 * outdoorDBTemp) + x * (0.444 * outdoorDBTemp + 1061)
print(f"\n *** Outdoor Enthalpy: {round(OutdoorEnthalpy,1)} BTU per lb of dry air\n")
#
# Calculate indoor humidity ratio from indoor relative humidity and dry bulb temperature saturation lookup table
#
# Data entry of indoor conditions
validInput = False
while validInput == False:
    t = input("Enter indoor dry bulb temperature (30-87 deg F): ")
    try:
        indoorDBTemp = round(float(t))
        if indoorDBTemp > 29 & indoorDBTemp < 88:
            validInput = True
        else:
            print("\n *** Temperature must be between 30 & 87 degrees.\n")
    except ValueError:
        print("\n *** Temperature must be a number rounded to the nearest whole degree.\n")
#
# Uncomment to debug:
# print(f"Saturated Specific Humidity: {dbTempSatTable[t]} gr/LB")
#
validInput = False
while validInput == False:
    rh = input("Enter indoor relative humidity (0-100 %): ")
    try:
        rhIndoor = round(float(rh))
        if rhIndoor >= 0 & rhIndoor <= 100:
            validInput = True
        else:
            print("\n *** Relative Humidity must be between 0 & 100.\n")
    except ValueError:
        print("\n *** Relative Humidity must be a number.\n")
#
# Convert percentage to decimal
rhIndoor = rhIndoor/100
#
# x = input("Enter indoor humidity ratio")
#
# Look up saturation specific humidity of indoor dry bulb temperature in dictionary
# Multiply the saturation specific humidity by the relative humidity to obtain the specific humidity
x = float(dbTempSatTable[t]) * rhIndoor
#
# convert from gr/LB to LB/LB for enthalpy formula
x = x/7000
#
IndoorEnthalpy = (0.240 * indoorDBTemp) + x * (0.444 * indoorDBTemp + 1061)
print(f"\n *** Indoor Enthalpy: {round(IndoorEnthalpy,1)} BTU per lb of dry air")
print("\n")
#
# Compare indoor enthalpy to outdoor enthalpy and determine if economizer should be used
#
# Density of air = 0.075 lb/ft^3
#
# Conversion factor: lb/hr to CFM = 60 min/hr * 0.075 lb/ft^3 = 4.5
#
# Enthalpy equation:
# Q = m(h2-h1)
#
# where
# Q = rate of heat added or removed from substance in BTU/hr
# m = mass flow rate of substance in lb/hr
# (h2-h1) = change in enthalpy of substance in BTU/lb
#
validInput = False
while validInput == False:
    m = input("Enter blower air flow rate (CFM): ")
    try:
        m = float(m)
        if m > 0:
            validInput = True
        else:
            print("\n *** Air flow rate must be greater than zero.\n")
    except ValueError:
        print("\n *** Air flow rate must be a number greater than zero.\n")
#
# Convert CFM to lb/hr
m = m/4.5
#
# Calculate heat flow rate in BTU/hr
Q = m * (IndoorEnthalpy - OutdoorEnthalpy)
if Q < 0:
    mode = "heating"
    equiv = Q / 3412.14163  # convert to KW
    unit = "KW"
else:
    mode = "cooling"
    equiv = Q / 12000  # convert to tons of ice
    unit = "tons of ice"
#
# NOTE: Negative values of Q are heating BTUs/hr
print(f"Activating the economizer will provide {round(Q,2)} BTU/hr of {mode}.")
print(f"Equivalent to {round(equiv,2)} {unit}.\n")
#
exit(0)