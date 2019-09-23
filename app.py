from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ButtonsTemplate, PostbackAction, TemplateSendMessage, PostbackEvent
)
import os

from my_functions import scraping, other_scraping

app = Flask(__name__)

#LINE Access Token
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
#LINE Channel Secret
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text

    # result = scraping(input_text)
    #
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=result))

    result = other_scraping(input_text)

    if result == 'error':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='お探しのキーワードに一致する結果はありませんでした')
        )
    else:
        my_actions = []
        for song_name in result:
            my_actions.append( PostbackAction(label=song_name, data=result[song_name], display_text=song_name) )

        buttons_template = ButtonsTemplate(
            title='{}の検索結果です！'.format(input_text), text='キーを知りたい曲を選んでください！', actions=my_actions
        )
        template_message = TemplateSendMessage(alt_text='{}の検索結果です！\nキーを知りたい曲を選んでください！'.format(input_text), template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)


@handler.add(PostbackEvent)
def handle_postback(event):
    #
    # success_message = 'キーを判別します！しばらくお待ち下さい。'
    #
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=success_message)
    # )

    result = scraping(event.postback.data)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result)
    )


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
