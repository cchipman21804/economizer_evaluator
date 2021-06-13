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
import math
import urllib.request
#

print("ECONOMIZER CONTROL WEATHER CONDITIONS EVALUATOR v1.2\n")
#
# URL for current weather observations
rooturl = "http://tgftp.nws.noaa.gov/data/observations/metar/decoded/"
#
# Concatenate rooturl and airport code to obtain full url for decoded current weather observations
ksby = "KSBY.TXT"
kged = "KGED.TXT"
k33n = "K33N.TXT"
url = rooturl + k33n
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
windStartIdx = wxdata.find("Wind: ")
windEndIdx = wxdata.find("Visibility: ") - 4
wind = wxdata[windStartIdx:windEndIdx]
windSpeedStartIdx = wxdata.find("ob: ") + 25
windSpeedEndIdx = wxdata.find("ob: ") + 27
windSpeedKnots = wxdata[windSpeedStartIdx:windSpeedEndIdx]
windSpeedMph = round(float(windSpeedKnots) / 0.868976)
windSpeedFpm = float(windSpeedKnots) * 101.27
windDirStartIdx = wxdata.find("ob: ") + 22
windDirEndIdx =  wxdata.find("ob: ") + 25
windDir = wxdata[windDirStartIdx:windDirEndIdx]

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
# print(f"{wind}")
# print(f"{windDir} degrees")
# print(f"{windSpeedKnots} KT")
# print(f"{windSpeedMph} MPH")
# print(f"{windSpeedFpm} FPM")
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
lookupTablePath = "./"
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
print(f" *** Weather observations for [{header}]:")
print(f"{localDate} @{localTime}")
# print(f"{localTime}")
print(f"{temperature}")
print(f"Wind Direction: {windDir} degrees")
print(f"Wind Speed: {windSpeedMph} MPH")
# print(f"{windSpeedFpm} FPM")
#
# Convert wind direction string to float for calculations
windDir = float(windDir)
#
# Convert temperature substring to float for calculations
outdoorDBTemp = float(temperature[13:16])
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
# try:
x = float(dbTempSatTable[str(indoorDBTemp)]) * rhIndoor
# except KeyError:
#     indoorDBTemp = indoorDBTemp + 1
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
#validInput = False
#while validInput == False:
#    m = input("Enter blower air flow rate (CFM): ")
#    try:
#        m = float(m)
#        if m > 0:
#            validInput = True
#        else:
#            print("\n *** Air flow rate must be greater than zero.\n")
#    except ValueError:
#        print("\n *** Air flow rate must be a number greater than zero.\n")
#
# Obtain window opening dimensions in inches
validInput = False
while validInput == False:
    windowWidthInches = input("Enter window opening width in inches ( >=20 & <= 60 ): ")
    try:
        windowWidthInches = float(windowWidthInches)
        if windowWidthInches < 20:
            print("Window width must be greater than or equal to 20 inches.\n")
        elif windowWidthInches > 60:
            print("Window width must be less than or equal to 60 inches.\n")
        else:
            windowWidthFeet = windowWidthInches / 12 # convert inches to feet
            validInput = True
    except:
        print("Window width must be from 20 - 60 inches.\n")
#
validInput = False
while validInput == False:
    windowHeightInches = input("Enter window opening height in inches ( >=1 & <= 30 ): ")
    try:
        windowHeightInches = float(windowHeightInches)
        if windowHeightInches < 1:
            print("Window height must be greater than or equal to 1 inch.\n")
        elif windowHeightInches > 30:
            print("Window height must be less than or equal to 30 inches.\n")
        else:
            windowHeightFeet = windowHeightInches / 12 # convert inches to feet
            validInput = True
    except:
        print("Window height must be from 1 - 30 inches.\n")
#
# Obtain window opening area in sqft
windowOpeningArea = windowWidthFeet * windowHeightFeet
#
# Obtain window facing direction in compass degrees
validInput = False
while validInput == False:
    windowOpeningDir = input("Enter compass direction (in degrees from True North) of window opening (0 - 359): ")
    try:
        windowOpeningDir = float(windowOpeningDir)
        if windowOpeningDir < 0 or windowOpeningDir > 359:
            print("\n")
        else:
            validInput = True
    except:
        print("\n")
#
# Obtain air flow through window (in CFM) from outdoor wind speed & direction
# relative to window opening direction & dimensions
#
windDirOffset = abs(windDir - windowOpeningDir)
#
if windDirOffset >= 90:
      massFlowRate = 0 # airMassFlowRate = 0
else:
      massFlowRate = windSpeedFpm                                # massFlowRate = windSpeed in fpm
      massFlowRate = massFlowRate * abs(math.cos(windDirOffset)) # compensate for wind direction relative to window opening direction
      massFlowRate = massFlowRate * windowOpeningArea            # convert fpm to CFM based on size of window opening (in sqft)
#
# Convert CFM to lb/hr
massFlowRate = massFlowRate / 4.5
#
# Calculate heat flow rate in BTU/hr
Q = massFlowRate * (IndoorEnthalpy - OutdoorEnthalpy)
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
print(f"\nActivating the economizer will provide {round(Q,2)} BTU/hr of {mode}.")
print(f"Equivalent to {round(equiv,2)} {unit}.\n")
#
# exit(0)
