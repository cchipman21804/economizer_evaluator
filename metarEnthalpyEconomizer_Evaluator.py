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
import os
import csv
import math
import urllib.request
#

print("ECONOMIZER CONTROL WEATHER CONDITIONS EVALUATOR v1.3\n")
#
# URL for current weather observations
# rooturl = "http://tgftp.nws.noaa.gov/data/observations/metar/decoded/"
rooturl = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/"
#
# Concatenate rooturl and airport code to obtain full url for decoded current weather observations
ksby = "KSBY.TXT" # Wicomico County Regional Airport, Salisbury, MD
kged = "KGED.TXT" # Delaware Coastal Airport, Georgetown, DE
k33n = "K33N.TXT" # Delaware Airpark, Smyrna, DE
kdov = "KDOV.TXT" # Dover Air Force Base, Dover, DE
kilg = "KILG.TXT" # New Castle County Airport, New Castle, DE
kcge = "KCGE.TXT" # Cambridge-Dorchester Regional Airport, Cambridge, MD
koxb = "KOXB.TXT" # Ocean City Municipal Airport, Ocean City, MD
kwal = "KWAL.TXT" # Wallops Island Flight Facility, Wallops Island, VA
#
# humidityratio CSV formatted lookup table
lookupTablePath = "./"
lookupTableFileName = lookupTablePath + "humidityratio.csv"
if not os.path.exists(lookupTableFileName):
    print(" *** FATAL ERROR: The humidity ratio lookup table CSV file does not exist... ***")
    print(" *** Returning to operating system with errorlevel 1.")
    exit(1)
# else: print(" *** Humidity ratio lookup table file found - loading contents into memory - ***")

dbTempSatTable = {}
with open(lookupTableFileName,'r', newline='') as lookupTable:
    reader = csv.reader(lookupTable)
    dbTempSatTable = {rows[0]:rows[1] for rows in reader}
#
# Uncomment to debug:
# print(dbTempSatTable)
#
# Prepare menu selection loop
validInput = False
while validInput == False:
    print("\nLOCAL WEATHER OBSERVATIONS\n")
    print("1 ... Delaware Coastal Airport, Georgetown, Sussex County, DE")
    print("2 ... Wicomico Regional Airport, Salisbury, Wicomico County, MD")
    print("3 ... Wallops Flight Facility, Wallops Island, Accomac County, VA")
    print("4 ... Ocean City Municipal Airport, Ocean City, Worcester County, MD")
    print("5 ... Dover Air Force Base, Dover, Kent County, DE")
    print("6 ... New Castle County Airport, New Castle, New Castle County, DE")
    print("7 ... Delaware Airpark, Smyrna, Kent County, DE")
    print("8 ... Cambridge Dorchester Regional Airport, Cambridge, Dorchester County, MD")
    #    print("n ... Ocean City Municipal Airport, Ocean City, Worcester County, MD")
    airport = input("\nPlease select an area wx forecast or 'e' to EXIT: ")

# Evaluate menu selection
    if airport == '1':
        url = rooturl + kged
        validInput = True  # leave while loop

    elif airport == '2':
        url = rooturl + ksby
        validInput = True  # leave while loop

    elif airport == '3':
        url = rooturl + kwal
        validInput = True  # leave while loop

    elif airport == '4':
        url = rooturl + koxb
        validInput = True  # leave while loop

    elif airport == '5':
        url = rooturl + kdov
        validInput = True  # leave while loop

    elif airport == '6':
        url = rooturl + kilg
        validInput = True  # leave while loop

    elif airport == '7':
        url = rooturl + k33n
        validInput = True  # leave while loop

    elif airport == '8':
        url = rooturl + kcge
        validInput = True  # leave while loop
        
#    elif airport == 'n':
#       url = xxxxurl
#       validInput = True  # leave while loop

    elif airport.lower() == 'e':
        # Exit to Operating System
        print("\n")
        exit(0)

    else: validInput = False
#
# Retrieve current weather observations from airport weather data URL
req = urllib.request.Request(url)
resp = urllib.request.urlopen(req)
respdata = resp.read()
wxdata = str(respdata)
#
# Uncomment wxdata to debug:
# print("\n")
print(f" *** Retrieved {len(wxdata)} bytes from {url} - ")
print(wxdata)
# print("\n")
#
print(" *** Parsing outdoor weather data - ")
#
# Date/Time Stamp:
year = wxdata[2:6]
month = wxdata[7:9]
day = wxdata[10:12]
utchour = wxdata[13:15]
utcminute = wxdata[16:18]
print(f"Date/Time: {month}/{day}/{year} @{utchour}:{utcminute} UTC")
#
# Location Header:
header = wxdata[20:24]
print(f"Location: {header}")
#
# Temperature:
temperatureStartIdx = wxdata.find(" RMK ") - 11
temperatureEndIdx = wxdata.find(" RMK ") - 9
degC = wxdata[temperatureStartIdx:temperatureEndIdx]
# Convert to degrees Fahrenheit
outdoorDBTemp = 9/5*float(degC)+32
print(f"Dry Bulb Temperature: {degC} degrees Celsius ({round(outdoorDBTemp,1)} degrees Fahrenheit)")
# Round temperature float to zero decimal places & convert to string for dictionary key
outdoorDBTempKey = str(round(outdoorDBTemp))
#
# Dew Point:
dewPointStartIdx = wxdata.find(" RMK ") - 8
dewPointEndIdx = wxdata.find(" RMK ") - 6
outdoorDewPointC = wxdata[dewPointStartIdx:dewPointEndIdx]
# Convert to degrees Fahrenheit
dewPoint = 9/5*float(outdoorDewPointC)+32
print(f"Dew Point: {outdoorDewPointC} degrees Celsius ({round(dewPoint,1)} degrees Fahrenheit)")
# Round temperature float to zero decimal places & convert to string for dictionary key
outdoorDewPointKey = str(round(dewPoint))
#
# Relative Humidity:
#print(f"Dew Point Saturation Ratio: {dbTempSatTable[outdoorDewPointKey]}")
#print(f"Air Temp Saturation Ratio: {dbTempSatTable[outdoorDBTempKey]}")
#
# Calculate outdoor relative humidity from saturation ratios of outdoor temperature & outdoor dew point 
rhOutdoor = float(dbTempSatTable[outdoorDewPointKey])/float(dbTempSatTable[outdoorDBTempKey])
print(f"Relative Humidity: {round(rhOutdoor*100,1)}%")
#
# Wind Direction & Wind Speed:
if "AUTO" in wxdata:
    windDir = wxdata[38:41]
    windSpeedKnots = float(wxdata[41:43])
else:
    windDir = wxdata[33:36]
    windSpeedKnots = float(wxdata[36:38])
#
# Convert wind speed to MPH for display
windSpeedMph = round(windSpeedKnots / 0.868976)
print(f"Wind: {windDir} degrees @{windSpeedKnots} Knots ({windSpeedMph} MPH)")
if windDir == 'VRB':
    print("*** Wind is too variable for effective economizer operation...\n")
    exit(0)
#
if windSpeedKnots == 0:
    print("*** Wind is calm --- ineffective for economizer operation...\n")
    exit(0)
#
# Convert wind direction to float for energy calculations
windDir = float(windDir)
# Convert wind speed to feet per minute for energy calculations
windSpeedFpm = windSpeedKnots * 101.27
#
# Pressure:
#pressureStartIdx = wxdata.find("Pressure (altimeter): ")
#pressureEndIdx = wxdata.find(" hPa)") + 5
#pressure = wxdata[pressureStartIdx:pressureEndIdx]
#
# Pressure tendency:
#pressureTendencyStartIdx = wxdata.find("Pressure tendency: ")
#pressureTendencyEndIdx = wxdata.find("ob: ") - 2
#pressureTendency = wxdata[pressureTendencyStartIdx:pressureTendencyEndIdx]
#
# x = input("Enter outdoor humidity ratio")
x = float(dbTempSatTable[outdoorDBTempKey]) * rhOutdoor
x = x / 7000  # convert from gr/LB to LB/LB
#
OutdoorEnthalpy = (0.240 * outdoorDBTemp) + x * (0.444 * outdoorDBTemp + 1061)
print(f"\n *** Outdoor Enthalpy: {round(OutdoorEnthalpy,1)} BTU per lb of dry air\n")
#
# Calculate indoor humidity ratio from indoor relative humidity and dry bulb temperature saturation lookup table
#
# Data entry of indoor conditions
validInput = False
while validInput == False:
    t = input("Enter indoor dry bulb temperature (0-120 deg F): ")
    try:
        indoorDBTemp = round(float(t))
        if indoorDBTemp >= 0 & indoorDBTemp <= 120:
            validInput = True
        else:
            print("\n *** Temperature must be between 0 & 120 degrees (inclusive).\n")
    except ValueError:
        print("\n *** Temperature must be a number within the specified limits. ***\n")
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
            print("\n *** Relative Humidity must be between 0 & 100 (inclusive).\n")
    except ValueError:
        print("\n *** Relative Humidity must be a number within the specified limits. ***\n")
#
# Convert relative humidity percentage to decimal
rhIndoor = rhIndoor/100
#
# x = input("Enter indoor humidity ratio")
#
# Look up saturation specific humidity of indoor dry bulb temperature in dictionary
# Multiply the saturation specific humidity by the relative humidity to obtain the specific humidity
x = float(dbTempSatTable[str(indoorDBTemp)]) * rhIndoor
#
# convert from gr/LB to LB/LB for enthalpy formula
x = x/7000
#
IndoorEnthalpy = (0.240 * indoorDBTemp) + x * (0.444 * indoorDBTemp + 1061)
print(f"\n *** Indoor Enthalpy: {round(IndoorEnthalpy,1)} BTU per lb of dry air")
print("\n")
#
# Obtain window opening dimensions in inches
validInput = False
while validInput == False:
    windowWidthInches = input("Enter window opening width in inches (20-60): ")
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
    windowHeightInches = input("Enter window opening height in inches (1-30): ")
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
# Obtain quantity of window openings
validInput = False
while validInput == False:
    windowQuantity = input("Enter quantity of window openings (1-9): ")
    try:
        windowQuantity = int(windowQuantity)
        if windowQuantity < 1 or windowQuantity > 9:
            print("\n")
        else:
            validInput = True
    except:
        print("\n")
#
# Obtain window opening area in sqft
windowOpeningArea = windowWidthFeet * windowHeightFeet * windowQuantity
#
# Obtain window facing direction in compass degrees
validInput = False
while validInput == False:
    windowOpeningDir = input("Enter compass direction of window openings (in degrees from True North) (0 - 359): ")
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
      massFlowRate = massFlowRate / 4.5                          # Convert CFM to lb/hr
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
# Calculate heat flow rate in BTU/hr
Q = massFlowRate * (IndoorEnthalpy - OutdoorEnthalpy)
if Q < 0:
    mode = "heating"
    equiv = Q / 3412.14163  # convert to KW
    unit = "KW"
else:
    mode = "cooling"
    equiv = Q / 12000  # convert to tons
    unit = "tons"
#
# NOTE: Negative values of Q are heating BTUs/hr
print(f"\nOpening the windows will provide {round(Q,2)} BTU/hr of {mode}.")
print(f"Equivalent to {round(equiv,2)} {unit}.\n")
#
# exit(0)
