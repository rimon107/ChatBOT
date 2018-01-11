from django.http import JsonResponse
from .CustomLibrary import Response
from RESTAPI.ChatBotLibrary import ChatBot
from django.views.decorators.csrf import csrf_exempt
from RESTAPI.ChatBotLibrary import weatherApi
from geotext import GeoText
# import goslate
from googletrans import Translator
from ipware.ip import get_ip
import re
import pymssql


m = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12
}

@csrf_exempt
def GetResponseResult(request):
    message = ""
    query = ""
    query = request.POST.get('query', '')
    # gs = goslate.Goslate()
    #Google Translate API Library
    translator = Translator()


    if query == "" or query is None:
        query = request.GET.get('query', '')

    print(query)
    try:
        # lang = gs.detect(query)
        lang = translator.detect(query).lang
        if lang == 'bn':
            # message = gs.translate(query, 'en')
            transMessage = translator.translate(query, dest='en').text
            print(transMessage)
            response = ChatBot.response(transMessage)
            print(response)
            message = translator.translate(response, dest='bn').text
        else:
            query = query.lower()

            print(query)
            # if find_words('WEATHER', query):

            if 'sale' in query:
                message = SalesInfo(query)

            elif 'weather' in query:

                places = query.replace('weather', '').split(" ")
                print(places)
                if places.__len__() == 1 and places[0] == "":
                    places.append('Dhaka')

                des = ''
                for plc in places:
                    cap_plc = plc.title()
                    place = GeoText(cap_plc)

                    if place.cities.__len__() == 1:
                        des = place.cities[0]

                        url = weatherApi.url_builder(des)
                        raw_data = weatherApi.data_fetch(url)
                        if raw_data is not None:
                            break

                url = weatherApi.url_builder(des)
                raw_data = weatherApi.data_fetch(url)

                data_org = weatherApi.data_organizer(raw_data)

                message = weatherApi.data_output(data_org)

            # message = ChatBotResponse.BotResponse(query)
            else:
                message = ChatBot.response(query)

        if message is None:
            message = "No Result Found"
        else:
            if type(message) == list:
                message = message[0]

        status = "success"
        print(message)
        print(status)
    except :
        message = ""
        status = "fail"

    data = {
        'status': status,
        'message' : message
    }
    return JsonResponse(data,safe=False)

def isInt(value):
    try:
        int(value)
        return True
    except:
        return False

def parseIntegers(mixedList):
    return [x for x in mixedList if (isInt(x))]

def find_words(text, search):
    """Find exact words"""
    dText   = text.split()
    dSearch = search.split()

    found_word = 0

    for text_word in dText:
        for search_word in dSearch:
            if search_word == text_word:
                found_word += 1

    if found_word == len(dSearch):
        return True
    else:
        return False



def SalesInfo(query):
    # context = {}
    queryList = re.findall(r'\w+', query)
    status = False
    month = 0
    res = ''
    if queryList.__len__() == 1:
        status, res = SalesOnly(query)
    else:
        for q in queryList:
            print(q)
            status, month = month_string_to_number(q)
            if status == True:
                print(month)
                status, res = SalesInPeriod(queryList)
                break

        if status == False:
            yearList = parseIntegers(queryList)
            if yearList.__len__() != 0:
                print("1")
                status, res = SalesInPeriod(queryList)


    print(status)


    if status:
        result = str(res)
    else:
        result = res
    return result

def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return True, out
    except:
        return False, 0

def SalesOnly(query):
    tag = 'NSI'
    select = ' Sum(NSI) NSI '
    condition = " currentPeriod = 'Current Month'"

    context = {
        'tag': tag,
        'select': select,
        'condition': condition
    }

    status, res = GetResultFromDatabase(context, True, False)
    if status:
        result = str(res[0])
    else:
        result = res

    return status, result

def SalesInPeriod(query):
    print(query)
    yearList = parseIntegers(query)

    tag = 'NSI'
    status = False
    month = 0
    for q in query:
        status, month = month_string_to_number(q)
        if status == True:
            break

    import datetime
    today = datetime.datetime.now()

    if yearList.__len__() != 0:
        year = yearList[0]
    else:
        year = today.year


    if status == False:
        month = today.month
        print(today.year)
        if str(today.year) == str(year):
            status, res = SalesOnly(query)
            return status,res

    print(month)
    if month < 10:
        period = str(year) + '0' + str(month)
    else:
        period = str(year) +  str(month)

    select = ' Sum(NSI) NSI '
    condition = " currentPeriod = '"+ period + "'"

    context = {
        'tag': tag,
        'select': select,
        'condition': condition
    }

    status, res = GetResultFromDatabase(context, True, False)
    if status:
        result = str(res[0])
    else:
        result = res

    return status, result

def getBusiness(query):
    select = 'BusinessName'
    group = 'BusinessName'

    context = {
        'select': select,
        'group': group
    }

    status, res = GetResultFromDatabase(context, False, True)


def GetResultFromDatabase(context, condition=False, group=False ):

    select = context['select']
    tag = context['tag']
    database = " [dbo].[SalesInfo] "

    sql = "SELECT  "+select+ " FROM "+ database # + " WHERE " + + "patterns = '" + text + "'"

    sql += "WHERE "+ context['condition']  if condition==True else " "

    sql += "GROUP BY " + context['group'] if group == True else " "

    print(sql)
    try:
        conn = pymssql.connect(host='MIS-RIMON', user='sa', password='dataport', database='ChatBot')
        cursor = conn.cursor()

        cursor.execute(sql)

        dataset = cursor.fetchall()

        columns = [col[0] for col in cursor.description]

        results = [
            dict(zip(columns, row))
            for row in dataset
        ]

        res = []

        try:
            response = [ res.append( results[i][tag]) for i in  range(dataset.__len__())]
            response = res
        except Exception:
            response = ""

        print(response)
        if response == "":
            return False, response
        else:
            return True, response
    except ConnectionError:
        return False, "Database Connecttion Error"