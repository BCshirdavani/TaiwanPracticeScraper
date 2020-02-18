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
        formattedPercent = str(round(percent * 100, 3)) + '%'
        return formattedPercent

def splitBracketFromString(inputString):
    return inputString.split('(')[0]

localTranslationDict = {}
with open('chineseEnglishDictionary.txt') as json_file:
    localTranslationDict = json.load(json_file)


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

columns = ['Power Type','Unit Name', 'Power Capacity', 'Net Power Generated', 'Ratio Generated','Time Reported (Taiwan CST)']
dataChinese = {columns[0]: powerTypes,
        columns[1]: unitNames,
        columns[2]: deviceCapacities,
        columns[3]: netPowerGenerations,
        columns[4]: generationPerDeviceCapacityRatios,
        columns[5]: [dateTimeTaiwan] * len(powerTypes)}
dataFrameChinese = pd.DataFrame(data=dataChinese)
print(dataFrameChinese.head(5))

englishRowsList = []
for index, row in dataFrameChinese.iterrows():
    powType_CH = row['Power Type']
    name_CH = row['Unit Name']
    powerTypeEnglish = localTranslationDict[powType_CH] if powType_CH in localTranslationDict else translator.translate(powType_CH).text
    unitNameEnglish = localTranslationDict[name_CH] if name_CH in localTranslationDict else translator.translate(name_CH).text
    englishRowsList.append({columns[0]: powerTypeEnglish,
                            columns[1]: unitNameEnglish,
                            columns[2]: row['Power Capacity'],
                            columns[3]: row['Net Power Generated'],
                            columns[4]: row['Ratio Generated'],
                            columns[5]: row['Time Reported (Taiwan CST)']})



dataFrameEnglish = pd.DataFrame(data=englishRowsList, columns=columns)
print(dataFrameEnglish.head(10))
print(dataFrameEnglish.tail(10))

print('done')




