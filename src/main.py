import os

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from scraping import get_reservable_info_as_text

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = "H8uf7m0QRWdAQ7SnjYruob/MPQfDtMmp5K4tYudxMK2E5K12zg4/DFIbhI9C+jCniXDsP20v9TmwsHLTTP9rBHCj54X2u/xVSPG2X7CwBly6VcwntYTQZSDb138onzlu7XbuWYLzRA6Zbie9q6P5pAdB04t89/1O/w1cDnyilFU="
YOUR_CHANNEL_SECRET = "69928433508679b4dc564a8834cb25d2"

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


# ルーティングの設定、POSTリクエストが来たらcallback関数を返す
@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# メッセージを受け取った後にどんな処理を行うかを記述
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "界の予約情報を教えてください":
        reservable_info = get_reservable_info_as_text()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reservable_info))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="何を言っているのかわかりません"),
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
