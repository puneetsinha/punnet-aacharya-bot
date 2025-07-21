import requests
import time
import sys
sys.path.append('punnet_aacharya')
from config import BOT_TOKEN

# Fill in your test chat_id here
CHAT_ID = '2333324234'
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'


def send_message(text):
    url = f'{BASE_URL}/sendMessage'
    resp = requests.post(url, json={
        'chat_id': CHAT_ID,
        'text': text
    })
    return resp.json()

def get_updates(offset=None):
    url = f'{BASE_URL}/getUpdates'
    params = {'timeout': 10}
    if offset:
        params['offset'] = offset
    resp = requests.get(url, params=params)
    return resp.json()

def print_new_bot_replies(last_update_id):
    updates = get_updates(last_update_id)
    if not updates.get('ok'):
        return last_update_id
    for update in updates['result']:
        last_update_id = update['update_id'] + 1
        msg = update.get('message') or update.get('edited_message')
        if msg and str(msg.get('chat', {}).get('id')) == str(CHAT_ID):
            if 'text' in msg and msg.get('from', {}).get('is_bot'):
                print(f"Bot: {msg['text']}")
    return last_update_id

def run_test():
    print('Starting Telegram bot live test...')
    last_update_id = None
    # Step 1: /start
    send_message('/start')
    time.sleep(2)
    last_update_id = print_new_bot_replies(last_update_id)
    # Step 2: User concern
    send_message('Guruji, paisa nahi tikta, kya karun?')
    time.sleep(2)
    last_update_id = print_new_bot_replies(last_update_id)
    # Step 3: Birth details
    send_message('Naam: divya\nDin: 12/12/2005\nSamay: 05:00 PM\nSthan: delhi')
    time.sleep(3)
    last_update_id = print_new_bot_replies(last_update_id)
    # Wait for final bot reply
    time.sleep(5)
    last_update_id = print_new_bot_replies(last_update_id)
    print('Test complete.')

if __name__ == '__main__':
    run_test() 