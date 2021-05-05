import os
import sys
import traceback

import requests
import datetime
import time


def send_telegram_message(message):
    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/json'
    }
    telegram_bot_url = 'https://api.telegram.org/bot' + telegram_bot_id + '/sendMessage'
    telegram_message = {
        'chat_id': telegram_chat_id,
        'text': message
    }
    requests.post(telegram_bot_url, json=telegram_message, headers=headers)


def hit_api_and_get_data():
    current_date = datetime.date.today()
    current_date_plus_7 = current_date + datetime.timedelta(days=7)
    current_date_plus_14 = current_date + datetime.timedelta(days=14)

    date_format = "%d/%m/%y"
    current_date_formatted = current_date.strftime(date_format)
    current_date_plus_7_formatted = current_date_plus_7.strftime(date_format)
    current_date_plus_14_formatted = current_date_plus_14.strftime(date_format)

    msg_sent = False
    dates = [current_date_formatted, current_date_plus_7_formatted, current_date_plus_14_formatted]
    for date in dates:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.49'
        }
        url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict'
        params = {'district_id': district_id, 'date': date}

        try:
            print("Calling API for date ", date)
            centers_request = requests.get(url, params, headers=headers)
            print('Status Code', centers_request.status_code)
            centers_request_data = centers_request.json()
            centers = centers_request_data['centers']
            filtered_sessions_centers = []
            print("Filtering centers and sessions")
            for center in centers:
                center['sessions'] = [session for session in center['sessions'] if
                                      session['min_age_limit'] < 45
                                      and session['available_capacity'] >= int(min_capacity)
                                      ]
                session_dates = ", ".join(
                    [session['date'] + ': ' + str(session['available_capacity']) for session in center['sessions']])
                center['session_dates'] = session_dates
                if len(center['sessions']) > 0:
                    filtered_sessions_centers.append(center)

            center_pincodes = [center['name'] + ", " + str(center['pincode']) + ", " + center['session_dates'] for
                               center in filtered_sessions_centers]

            print("Available Slots ", len(center_pincodes))
            print("Sending telegram message")
            for center_pincode in center_pincodes:
                send_telegram_message(center_pincode)
                msg_sent = True
            time.sleep(5)

        except Exception as e:
            send_telegram_message('Error ' + str(e))
            traceback.print_exc()
    if not msg_sent:
        send_telegram_message('No center found with available vaccine slots')


if __name__ == "__main__":
    min_capacity = os.getenv("TRACKER_MIN_CAPACITY")
    district_id = os.getenv("TRACKER_DISTRICT_ID")
    telegram_chat_id = os.getenv("TRACKER_TELEGRAM_ID")
    telegram_bot_id = os.getenv("TRACKER_TELEGRAM_BOT_ID")
    print('Min Capacity', min_capacity)
    print('Distt. ', district_id)
    print('telegram_chat_id ', telegram_chat_id)
    print('telegram_bot_id ', telegram_bot_id)
    hit_api_and_get_data()
