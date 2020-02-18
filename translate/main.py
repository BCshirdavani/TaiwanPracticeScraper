import googletrans
from googletrans import Translator
import requests
import json
import datetime
from dateutil import parser
import math
import pandas as pd
from dateutil.tz import gettz


URL = 'http://data.taipower.com.tw/opendata01/apply/file/d006001/001.txt'
translator = Translator()

print(googletrans.LANGCODES)

def percentOfCapacityGenerated(capacity, produced):
    try:
        if math.isnan(float(capacity)) or math.isnan(float(produced)):
            return "N/A"
    except ValueError as e:
        print(e, 'could not convert value to float')
    else:
        percent = float(produced)/float(capacity)
        formattedPercent = str(percent * 100) + '%'
        return formattedPercent

def splitBracketFromString(inputString):
    return inputString.split('(')[0]

response = requests.get(URL)
print(response.status_code)
raw_data = response.content.decode('utf-8')
raw_dict = json.loads(raw_data)
print('request finished')
dateTimeTaiwan = parser.parse(raw_dict[''])

powerTypes = []
unitNames = []
deviceCapacities = []
netPowerGenerations = []
generationPerDeviceCapacityRatios = []
comments = []

for entry in raw_dict['aaData']:
    powerTypes.append(entry[0])
    unitNames.append(entry[1])
    if "(" in entry[2] or "(" in entry[3] or "%" not in entry[4]:
        cleanCapacity = splitBracketFromString(entry[2])
        cleanGeneration = splitBracketFromString(entry[3])
        cleanPercent = percentOfCapacityGenerated(cleanCapacity, cleanGeneration)
        deviceCapacities.append(cleanCapacity)
        netPowerGenerations.append(cleanGeneration)
        generationPerDeviceCapacityRatios.append(cleanPercent)
    else:
        deviceCapacities.append(entry[2])
        netPowerGenerations.append(entry[3])
        generationPerDeviceCapacityRatios.append(entry[4])
    comments.append(entry[5])

# TODO: powerTypes list no longer translates...consider putting characters into a small unique set, and translating that, then map back to list.
powerTypeListEnglish = translator.translate(powerTypes)
# sending blank elements to translation function, breaks the translation
# lastColumnEnglish = translator.translate(comments)

unitNameEnglish = translator.translate(unitNames)


columns = ['Power Type','Unit Name', 'Power Capacity', 'Net Power Generated', 'Ratio Generated','Time Reported (Taiwan CST)']
data = {columns[0]: powerTypeListEnglish,
        columns[1]: unitNameEnglish,
        columns[2]: deviceCapacities,
        columns[3]: netPowerGenerations,
        columns[4]: generationPerDeviceCapacityRatios,
        columns[5]: [dateTimeTaiwan] * len(powerTypeListEnglish)}
dataFrame = pd.DataFrame(data=data)

print(dataFrame.head(5))

print('done')




