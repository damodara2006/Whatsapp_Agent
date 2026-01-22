from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
import requests
import os
import json
import pprint
from dotenv import load_dotenv
from fastapi import FastAPI, Request, requests
from fastapi.responses import PlainTextResponse
load_dotenv()
app = FastAPI()
llm = init_chat_model("groq:llama-3.1-8b-instant", temperature=0.2)
token = os.getenv("WA_ACCESS_TOKEN")

@tool
def send_whatsapp_text_message(to : str, message:str):
    """Send whatsapp text messages 
    Args:
    to (Number type string ) ex : 919043402788
    message (Text Body string) ex : What are you doing
    """
    url = "https://graph.facebook.com/v23.0/962571180271822/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization" : f"Bearer {token}"
    }
    payload = {
        "messaging_product": "whatsapp",
              "recipient_type": "individual",
              "to": to,
              "type": "text",
              "text": {
                "body": message
              }

    }
    res = requests.post(url=url, headers=headers, json=payload)
    if res.status_code == 200:
        return "Message sent ✅"
    else :
        return "Error"
    

toolKit = [send_whatsapp_text_message]
agent = create_agent(
    model = llm,
    tools=toolKit
)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# example_query = "send a whatsapp message to 919043402788 as a message 'This is from agent'"
# for mode , event in agent.stream(
#     {"messages": [("user", example_query)]},
#     stream_mode=["updates"],
# ):
#     if "tools" in event:
#         tool_msgs = event["tools"]["messages"]
#         if tool_msgs:
#             tool_res = tool_msgs[-1].content
# # print(response)
# print("tool_res =", tool_res)

@app.api_route("/webhook", methods=["GET", "POST"])
async def webhook(request: Request):

   
    if request.method == "GET":
        params = request.query_params
        if params.get("hub.verify_token") == VERIFY_TOKEN:
            return PlainTextResponse(content=params.get("hub.challenge"), status_code=200)
        return PlainTextResponse(content="Invalid token", status_code=403)

   
    body = await request.body()
    print("✅ WEBHOOK HIT:", body.decode("utf-8"))

    return PlainTextResponse(content="OK", status_code=200)

@app.get("/privacy")
def privacy():
    return """
    <html>
      <head><title>Privacy Policy</title></head>
      <body>
        <h1>Privacy Policy</h1>
        <p>This app uses WhatsApp Cloud API to receive and send messages.</p>
        <p>We may temporarily process message content to generate automated replies.</p>
        <p>We do not sell or share user data with third parties.</p>
        <p>Data is used only to provide support responses and improve the service.</p>

        <h2>Data Retention</h2>
        <p>Messages may be stored for debugging and support purposes.</p>

        <h2>User Rights</h2>
        <p>Users can request deletion of their data using the delete-data page.</p>

        <h2>Contact</h2>
        <p>Email: damodara2006@gmail.com</p>
      </body>
    </html>
    """, 200


@app.get("/terms")
def terms():
    return "Terms of Service - Test App", 200

@app.get("/delete-data")
def delete_data():
    return "To delete your data, contact: damodara2006@gmail.com", 200


@app.get("/")
def home(request : Request):
    print(request.get("method"))
    return "Running", 200