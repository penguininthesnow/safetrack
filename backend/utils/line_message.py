import requests
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
# GROUP_ID = os.getenv("LINE_GROUP_ID")
# USER_ID = os.getenv("USER_ID")

def send_line_message(message: str, image_url=None, to_id: str = None):
    """
    發送 LINE 訊息
    :parm message:
    :parm image_url: 可選，圖片 url
    :param to_id: 
    """
    line_api_url = "https://api.line.me/v2/bot/message/push"
    
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    if not to_id:
        print("未提供 to_id，無法發送 LINE 訊息")
        return None

    messages = [
        {
            "type": "text",
            "text": message
        }
    ]

    # 文字訊息
    # messages.append({
    #     "type": "text",
    #     "text": message
    # })

    image_urls = []

    # 加圖片(支援上傳3張圖片)
    if image_url:
        if isinstance(image_url, str):
            image_urls = [u.strip() for u in image_url.split(",") if u.strip()]
        elif isinstance(image_url, list):
            image_urls = [str(u).strip() for u in image_url if str(u).strip()]
        else:
            print("未知的 image_url 型別:", type(image_url))

    for img_url in image_urls:
        if img_url.startswith("https://"):
            messages.append({
                "type": "image",
                "originalContentUrl": img_url,
                "previewImageUrl": img_url
            })
        else:
            print("略過非 https 圖片網址:", img_url)

    # LINE 最多可以上傳5個 messages
    messages = messages[:5]

    payload = {
        "to": to_id,
        "messages": messages
    }

    print("send_line_message image_url type =", type(image_url))
    print("send_line_message image_urls =", image_urls)
    print("送 LINE messages =", messages)

    try:
        response = requests.post(
            line_api_url,
            headers=headers,
            json=payload,
            timeout=(3, 5)
        )

        print("Send to: ", to_id)
        print("LINE API response:", response.status_code)
        print("LINE API body:", response.text)

        if response.status_code != 200:
            print("LINE Notify 發送失敗:", response.text)

        try:
            return response.json()
        except Exception:
            return {"status_code": response.status_code, "text": response.text}
        
    except requests.exceptions.Timeout:
        print("LINE API timeout")
        return {"error": "timeout"}

    except Exception as e:
        print("LINE 發送錯誤:", str(e))
        return {"error": str(e)}
    

     # 選傳送其中一個的寫法
    # data = {
    #     "to": GROUP_ID,
    #     "to": USER_ID,
    #     "messages": messages
    # }

    # targets = [GROUP_ID, USER_ID]

    # for target in targets:
    #     if not target:
    #         continue
        
    #     data = {
    #         "to": to_id,
    #         "messages": messages
    #     }