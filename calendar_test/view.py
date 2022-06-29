import datetime
import json
import os
import google_apis_oauth
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect

import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# The url where the google oauth should redirect
# after a successful login.
REDIRECT_URI = 'http://localhost:8000/rest/v1/calendar/redirect/'

# Authorization scopes required
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Path of the "client_id.json" file
JSON_FILEPATH = os.path.join(os.getcwd(), 'client_id.json')
def GoogleCalendarInitView(request):
    oauth_url = google_apis_oauth.get_authorization_url(
        JSON_FILEPATH, SCOPES, REDIRECT_URI)
    return HttpResponseRedirect(oauth_url)

def GoogleCalendarRedirectView(request):
    try:
        # Get user credentials
        credentials = google_apis_oauth.get_crendentials_from_callback(
            request,
            JSON_FILEPATH,
            SCOPES,
            REDIRECT_URI
        )
        
        
        # Stringify credentials for storing them in the DB
        stringified_token = google_apis_oauth.stringify_credentials(
            credentials)
        
        json.dump(stringified_token, open('token.json', 'w'))
        # dump the credentials to the folder
        
        return HttpResponseRedirect('/calendar')
        ...
    except google_apis_oauth.exceptions.InvalidLoginException:
        # Invalid credentials
        ...
        print('invalid')
        return HttpResponseRedirect('/')
        

import google_apis_oauth
from googleapiclient.discovery import build

# Load the stored credentials in a variable say 'stringified_token

# Load the credentials object using the stringified token.
def calendar(request):

    credentials_dict = json.loads(open('token.json', 'r').read())
    creds, refreshed = google_apis_oauth.load_credentials(credentials_dict)

# Using credentials to access Upcoming Events
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print('Getting the upcoming 10 events')
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    res = []
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        res.append("["+start+"   "+event['summary']+"      "+"]")

    return HttpResponse(res if res else 'No upcoming events found.')