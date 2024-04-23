from flask import Flask, render_template, request
import requests
import threading

app = Flask(__name__)

TOKEN = None
CHANNEL_POST = None
CHANNEL_LAPORAN = None
MESSAGE = None
DELAY_POST = None
stop_flag = threading.Event()

Count_Success_Message = 0
Count_Failed_Message = 0

def send_message_channel(channel_id, message):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    header = {
        "Authorization": TOKEN
    }
    payload = {
        "content": message + """
\n**===================================**
 ----- **Auto Message Made By Here** -----
**===================================**"""
    }
    response = requests.post(url, json=payload, headers=header)
    return response

def send_message():
    global stop_flag
    global TOKEN
    global CHANNEL_POST
    global CHANNEL_LAPORAN
    global MESSAGE
    global DELAY_POST
    global Count_Success_Message
    global Count_Failed_Message

    while not stop_flag.is_set():
        response = send_message_channel(CHANNEL_POST, MESSAGE)
        send_report(response.status_code)
        stop_flag.wait(DELAY_POST)

def send_report(status_code):
    global Count_Success_Message
    global Count_Failed_Message
    if status_code == 200:
        Count_Success_Message += 1
        message = f"""
### --->> AUTO POST LOGS <<---
> *** • Successfully Send Message in Channel : <#{CHANNEL_POST}>
> • Successfully Send Message : {Count_Success_Message} Times
> • Delay Auto Post : {DELAY_POST} Second ***
"""
    else:
        Count_Failed_Message += 1
        message = f"""
### --->> AUTO POST LOGS <<---
> *** • Failed Send Message in Channel : <#{CHANNEL_POST}>
> • Failed Send Message : {Count_Failed_Message} Times
> • Delay Auto Post : {DELAY_POST} Second ***
"""
    send_message_channel(CHANNEL_LAPORAN, message)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def start_send_message():
    global stop_flag
    global TOKEN
    global CHANNEL_POST
    global CHANNEL_LAPORAN
    global MESSAGE
    global DELAY_POST
    global Count_Success_Message
    global Count_Failed_Message

    TOKEN = request.form['token']
    CHANNEL_POST = request.form['channel_post']
    CHANNEL_LAPORAN = request.form['channel_laporan']
    MESSAGE = request.form['message']
    DELAY_POST = int(request.form['delay'])

    Count_Success_Message = 0
    Count_Failed_Message = 0

    header = {
        "Authorization": TOKEN
    }
    response = requests.get('https://discord.com/api/v9/users/@me', headers=header)
    if response.status_code == 200:
        user_data = response.json()
        username = user_data['username']
        print(f'{username} Successfully Connect To Auto Post')

        stop_flag.clear()
        threading.Thread(target=send_message).start()

        return "<h1>Pengiriman pesan dimulai!<h1>"
    else:
        return "<h1>Token Invalid<h1>"

@app.route('/stop-message', methods=['POST'])
def stop_send_message():
    global stop_flag
    stop_flag.set()
    return "<h1>Pengiriman pesan dihentikan!<h1>"

if __name__ == '__main__':
    app.run(debug=True)
