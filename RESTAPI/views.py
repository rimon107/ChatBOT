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
    select = 'BusinessName'
    group = 'BusinessName'

    context = {
        'select':select,
        'group':group
    }

    status , res = GetResultFromDatabase(context, False, True)

    print(status)
    print(res)

    if status:
        result = str(res)
    else:
        result = res
    return result


def GetResultFromDatabase(context, condition=False, group=False ):

    select = context['select']

    database = " [dbo].[SalesInfo] "

    sql = "SELECT  "+select+ " FROM "+ database # + " WHERE " + + "patterns = '" + text + "'"

    sql += "WHERE "+ context['condition'] if condition==True else " "

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

        try:
            response = results[1][select]
        except Exception:
            response = ""

        print(response)
        if response == "":
            return False, response
        else:
            return True, response
    except ConnectionError:
        return False, "Database Connecttion Error"