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
# Fatal Errors:
#
#    print("\n *** FATAL ERROR: The humidity ratio lookup table CSV file does not exist... ***")
#    print(" *** Returning to operating system with errorlevel 1.")
#    exit(1)
#
#    print(f"\n *** FATAL ERROR: Invalid weather data [{degC}] ***")
#    print(" *** Returning to operating system with errorlevel 2.")
#    exit(2)
#
def getweather(url):
# Retrieve current weather observations from airport weather data URL
    req = urllib.request.Request(url)
    try:
        resp = urllib.request.urlopen(req)
    except:
        print(f"\n *** Error... WEATHER OBSERVATION FILE [{airport}] NOT FOUND ON SERVER ***")
        return None
    respdata = resp.read()
    return str(respdata)
#
# Title Screen
swVersion = '  v1.3.1'
creationDate = 'June 2021'
dashes = '----'
print(f"\n\tECONOMIZER CONTROL WEATHER CONDITIONS EVALUATOR {dashes}\t{swVersion}\n")
print(f"\tWritten by, Clifford A. Chipman, EMIT \t{dashes}{dashes}{dashes}\t{creationDate}")
#
# URL for current weather observations
# rooturl = "https://tgftp.nws.noaa.gov/data/observations/metar/decoded/"
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
kesn = "KESN.TXT" # Easton Airport/Newman Field, Easton, MD
#
# humidityratio CSV formatted lookup table
lookupTablePath = "./"
lookupTableFileName = lookupTablePath + "humidityratio.csv"
if not os.path.exists(lookupTableFileName):
    print("\n *** FATAL ERROR: The humidity ratio lookup table CSV file does not exist... ***")
    print(" *** Returning to operating system with errorlevel 1.")
    exit(1)
# else: print(" *** Humidity ratio lookup table file found - loading contents into memory - ***")
#
# Create a dictionary of temperatures in degF with corresponding saturated humidity ratios in grains per pound
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
    print("\n\tLOCAL WEATHER OBSERVATION STATIONS:\n")
    print(" [1] ... [KGED] Delaware Coastal Airport, Georgetown, Sussex County, DE")
    print(" [2] ... [KSBY] Wicomico Regional Airport, Salisbury, Wicomico County, MD")
    print(" [3] ... [KWAL] Wallops Flight Facility, Wallops Island, Accomac County, VA")
    print(" [4] ... [KOXB] Ocean City Municipal Airport, Ocean City, Worcester County, MD")
    print(" [5] ... [KDOV] Dover Air Force Base, Dover, Kent County, DE")
    print(" [6] ... [KILG] New Castle County Airport, New Castle, New Castle County, DE")
    print(" [7] ... [K33N] Delaware Airpark, Smyrna, Kent County, DE")
    print(" [8] ... [KCGE] Cambridge Dorchester Regional Airport, Cambridge, Dorchester County, MD")
    print(" [9] ... [KESN] Easton Airport/Newman Field, Easton, Talbot County, MD")
#    print(" [n] ... [KOXB] Ocean City Municipal Airport, Ocean City, Worcester County, MD")
    airport = input("\nType any airport code, select an airport number, or 'e' to EXIT: ")

# Evaluate menu selection
    if airport.lower() == 'e':
        # Exit to Operating System
        print("\n *** Returning to operating system...\n")
        exit(0)

    elif len(airport) == 4:
        airport = airport.upper() + '.TXT'

    elif airport == '1':
        airport = kged

    elif airport == '2':
        airport = ksby

    elif airport == '3':
        airport = kwal

    elif airport == '4':
        airport = koxb

    elif airport == '5':
        airport = kdov

    elif airport == '6':
        airport = kilg

    elif airport == '7':
        airport = k33n

    elif airport == '8':
        airport = kcge

    elif airport == '9':
        airport = kesn
        
#    elif airport == 'n':
#       airport = xxxx

    else: validInput = False
#
# Concatenate rooturl and airport for full weather observation file URL
    wxdata = getweather(rooturl + airport)
    if wxdata == None:
        validInput = False # Weather file not on server. Get another selection from user
    else:
        validInput = True  # leave while loop
#
# Uncomment print(wxdata) to debug:
# print("\n")
print(f"\n *** Retrieved {len(wxdata)} bytes from {rooturl}{airport} - \n")
print(wxdata)
# print("\n")
#
print("\n *** Parsing outdoor weather data - \n")
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
#
# Find last '/' in wxdata for temperature
startIdx = wxdata.rindex('/') - 2
endIdx = wxdata.rindex('/')
degC = wxdata[startIdx:endIdx]
#
# Convert to degrees Fahrenheit
try:
    outdoorDBTemp = 9/5*float(degC)+32
except:
    print(f"\n *** FATAL ERROR: Invalid weather data [{degC}] ***")
    print(" *** Returning to operating system with errorlevel 2.")
    exit(2)
#
print(f"Dry Bulb Temperature: {degC} degrees Celsius ({round(outdoorDBTemp,1)} degrees Fahrenheit)")
#
# Round temperature float to zero decimal places & convert to string for dictionary key
outdoorDBTempKey = str(round(outdoorDBTemp))
#
# Dew Point:
#
# Find last '/' in wxdata for dew point
startIdx = wxdata.rindex('/') + 1
endIdx = wxdata.rindex('/') + 3
outdoorDewPointC = wxdata[startIdx:endIdx]
#
# Convert to degrees Fahrenheit
try:
    dewPoint = 9/5*float(outdoorDewPointC)+32
except:
    print("\n *** FATAL ERROR: Invalid weather data [{outdoorDewPointC}] ***")
    print(" *** Returning to operating system with errorlevel 2.")
    exit(2)
#
print(f"Dew Point: {outdoorDewPointC} degrees Celsius ({round(dewPoint,1)} degrees Fahrenheit)")
#
# Round temperature float to zero decimal places & convert to string for dictionary key
outdoorDewPointKey = str(round(dewPoint))
#
# Calculate outdoor relative humidity from saturation ratios of outdoor temperature & outdoor dew point 
#
#print(f"Dew Point Saturation Ratio: {dbTempSatTable[outdoorDewPointKey]}")
#print(f"Air Temp Saturation Ratio: {dbTempSatTable[outdoorDBTempKey]}")
#
rhOutdoor = float(dbTempSatTable[outdoorDewPointKey])/float(dbTempSatTable[outdoorDBTempKey])
print(f"Relative Humidity: {round(rhOutdoor*100,1)}%")
#
# Wind Direction:
if "AUTO" in wxdata:
    startIdx = 38
    endIdx = 41
else:
    startIdx = 33
    endIdx = 36
#
windDir = wxdata[startIdx:endIdx]
#
if windDir == 'VRB':
    print("\n *** Wind is too variable --- ineffective for economizer operation...\n")
    exit(0)
#
# Convert wind direction to float for energy calculations
try:
    windDir = float(windDir)
except:
    print("\n *** FATAL ERROR: Invalid weather data [{windDir}] ***")
    print(" *** Returning to operating system with errorlevel 2.")
    exit(2)
#
# Wind Speed:
if "AUTO" in wxdata:
    startIdx = 41
    endIdx = 43
else:
    startIdx = 36
    endIdx = 38
#
# Check for gusts
if wxdata[endIdx] == 'G':
    gust = wxdata[endIdx + 1:endIdx + 3]
else:
    gust = ''
#
windSpeedKnots = wxdata[startIdx:endIdx]
#
# Convert wind speed to float for energy calculations
try:
    windSpeedKnots = float(windSpeedKnots)
except:
    print("\n *** FATAL ERROR: Invalid weather data [{windSpeedKnots}] ***")
    print(" *** Returning to operating system with errorlevel 2.")
    exit(2)
#
if windSpeedKnots == 0:
    print("\n *** Wind is calm --- ineffective for economizer operation...\n")
    exit(0)
#
# Convert wind speed to MPH for display
windSpeedMph = round(windSpeedKnots / 0.868976)
#
print(f"Wind: {windDir} degrees @{windSpeedKnots} Knots ({windSpeedMph} MPH)")
while not gust == '':
    try:
        gustKnots = float(gust)
    except:
        break # Just ignore errors & move on -- gust values are for display only...
    gustMph = round(gustKnots / 0.868976)
    print(f"Gusting to {gustKnots} Knots ({gustMph} MPH)")
#
# Convert wind speed to feet per minute for energy calculations
windSpeedFpm = windSpeedKnots * 101.27
#
# x = input("Enter outdoor humidity ratio")
x = float(dbTempSatTable[outdoorDBTempKey]) * rhOutdoor
#
# convert from gr/LB to LB/LB
x = x / 7000
#
# Calculate enthalpy of outdoor air
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
            print("\n *** Temperature must be between 0 & 120 degrees (inclusive). ***\n")
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
            print("\n *** Relative Humidity must be between 0 & 100 (inclusive). ***\n")
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
            print("\n *** Window width must be greater than or equal to 20 inches. ***\n")
        elif windowWidthInches > 60:
            print("\n *** Window width must be less than or equal to 60 inches. ***\n")
        else:
            windowWidthFeet = windowWidthInches / 12 # convert inches to feet
            validInput = True
    except:
        print("Window width must be a number within the specified limits. ***")
#
validInput = False
while validInput == False:
    windowHeightInches = input("Enter window opening height in inches (1-30): ")
    try:
        windowHeightInches = float(windowHeightInches)
        if windowHeightInches < 1:
            print("\n *** Window height must be greater than or equal to 1 inch. ***\n")
        elif windowHeightInches > 30:
            print("\n *** Window height must be less than or equal to 30 inches. ***\n")
        else:
            windowHeightFeet = windowHeightInches / 12 # convert inches to feet
            validInput = True
    except:
        print("\n *** Window height must be a number within the specified limits. ***")
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
      print("\n *** The wind is blowing from an ineffective direction. ***")
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
print(f"\nOpening the windows will provide {abs(round(Q,2))} BTU/hr of {mode}.")
print(f"Equivalent to {abs(round(equiv,2))} {unit}.\n")
#
print("\n *** Returning to operating system...\n")
exit(0)
