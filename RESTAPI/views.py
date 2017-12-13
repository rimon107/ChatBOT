from django.http import JsonResponse
from .CustomLibrary.Response import ChatBotResponse
from RESTAPI.ChatBotLibrary import TestChatBot
from django.views.decorators.csrf import csrf_exempt
from RESTAPI.ChatBotLibrary import weatherApi
from geotext import GeoText
# import goslate
from googletrans import Translator


@csrf_exempt
def GetResponseResult(request):
    query = ""
    query = request.POST.get('query', '')
    # gs = goslate.Goslate()
    #Google Translate API Library
    translator = Translator()


    if query == "" or query is None:
        query = request.GET.get('query', '')

    try:

        # lang = gs.detect(query)
        lang = translator.detect(query).lang
        if lang == 'bn':
            # message = gs.translate(query, 'en')
            message = translator.translate(query, dest='en').text
        if lang == 'en':
            query = query.lower()

            print(query)
            # if find_words('WEATHER', query):
            if 'weather' in query:
                print("in ")
                # places = GeoText(query)
                # print(places)
                # place = places.cities[0]
                # print(place)
                places = query.replace('weather', '').split(" ")
                print(places)
                if places.__len__() == 1 and places[0] == "":
                    places.append('Dhaka')
                print(places)
                des = ''
                for plc in places:
                    cap_plc = plc.title()
                    place = GeoText(cap_plc)
                    print(place)
                    print( place.cities.__len__())
                    if place.cities.__len__() == 1:
                        des = place.cities[0]
                        print(des)
                        url = weatherApi.url_builder(des)
                        raw_data = weatherApi.data_fetch(url)
                        if raw_data is not None:
                            break

                url = weatherApi.url_builder(des)
                raw_data = weatherApi.data_fetch(url)
                print(raw_data)
                data_org = weatherApi.data_organizer(raw_data)
                print(data_org)
                message = weatherApi.data_output(data_org)
                print("message")
                print(message)
            # message = ChatBotResponse.BotResponse(query)
            else:
                print("out")
                message = TestChatBot.response(query)
        status = "success"
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