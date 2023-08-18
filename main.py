from __future__ import print_function

import datetime
import os.path
# These libraries are part of the google cloud console
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Defining a event_Flag as Yes(Y) or No (N)
event_flag = str(input("Do you want to Create an event Y / N\n "))


def get_user_input(prompt):
    """

    prompt str : The string to be given in the input function
    :return:  This Function returns the text entered as in input function
    """
    return input(prompt)


def create_event():
    """
    This Function is used to store the values of required variables which is needed to store create an event on Google Calendar.
    :return:
    """


    global summary, location, description, start_date_str, start_time_str, start_date_time, start_timezone
    global end_date_time, end_timezone, recurrence_count, attendee_emails, reminders_minutes
    summary = get_user_input("Enter event summary: ")
    location = get_user_input("Enter event location: ")
    description = get_user_input("Enter event description: ")

    start_date_str = get_user_input("Enter start date (YYYY-MM-DD): ")
    start_time_str = get_user_input("Enter start time (HH:MM): ")
    start_date_time = f"{start_date_str}T{start_time_str}:00"
    start_timezone = get_user_input("Enter time zone (e.g., America/Toronto): ")

    end_date_str = get_user_input("Enter end date (YYYY-MM-DD): ")
    end_time_str = get_user_input("Enter end time (HH:MM): ")
    end_date_time = f"{end_date_str}T{end_time_str}:00"
    end_timezone = get_user_input("Enter time zone (e.g., America/Toronto): ")

    recurrence_count = int(get_user_input("Enter recurrence count: "))
    attendee_emails = get_user_input("Enter attendee emails (comma-separated): ").split(',')

    reminders_minutes = int(get_user_input("Enter reminder minutes: "))

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if event_flag == 'Y':
            create_event()
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_date_time,
                    'timeZone': start_timezone,
                },
                'end': {
                    'dateTime': end_date_time,
                    'timeZone': end_timezone,
                },
                'recurrence': [f'RRULE:FREQ=DAILY;COUNT={recurrence_count}'],
                'attendees': [{'email': email.strip()} for email in attendee_emails],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': reminders_minutes},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {event.get('htmlLink')}")
        else:
            pass

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
