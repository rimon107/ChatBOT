from RESTAPI.ChatBotLibrary import TestChatBot


class ChatBotResponse:
    def WeatherResponse(self, text):
        pass

    def BotResponse(self, text):
        result = TestChatBot.response(text)
        return result
