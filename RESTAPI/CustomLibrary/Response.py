from RESTAPI.ChatBotLibrary import ChatBot


class ChatBotResponse:
    def WeatherResponse(self, text):
        pass

    def BotResponse(self, text):
        result = ChatBot.response(text)
        return result
