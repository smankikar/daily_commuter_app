from __future__ import print_function
import requests
import json
import string
import collections
count = 0
SOURCE_PROMPT = "I was unable to find your start station. Can you please say that one more time?"
SOURCE_REPROMPT = "Please say your source station again."
DEST_PROMPT = "I was unable to find your destination station. Can you please say that one more time?" 
DEST_REPROMPT = "Please say your destination station again."

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, speech_output, card_output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': speech_output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': card_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_response_without_card(output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def build_response_only(speechlet_response):
    return {
        'version': '1.0',
        'response': speechlet_response
    }



# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the unofficial commuter app for bart. " \
                    "You can ask me train schedules, check for any delays or get system or elevator status. Here's a sample question that you can ask me. When is the next train from Fremont to Oakland International Airport? You can say help at any time. What would you like to do?" 
                    
                     
     
    reprompt_text = "You can ask me things like trains to, and from any station, schedule of trains between a pair of stations, check for any delays or elevator status. You can say help at any time. What would you like to do? " 
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, reprompt_text, should_end_session))


def help_function():
    

    session_attributes = {}
    card_title = "Help"
    speech_output = "Here are some of the things that I can help you with. " \
                    "Find out about any disruptions to your daily commute by asking for delays. " \
                    "To see if any elevators are out of service, ask for elevator status. " \
                    "You can also ask for the next few trains to your destination. " \
                    "To check for ticket prices, ask for fare between a pair of stations" \
                    "What would you like to do? " 
    card_output = "Sample things to ask : \n\n"\
                    "Get current status. \n"\
                    "Are there any delays? \n"\
                    "Get elevator status. \n"\
                    "Trains from Fremont. \n"\
                    "Trains to Millbrae. \n"\
                    "Trains from Embarcadero to Fruitvale. "
                    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Can I help you with the train schedule? " 
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))



def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the unofficial daily commuter app for bart. " 
                    
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, None, should_end_session))


def status(intent, session):
    card_title = "BART System Status"
    session_attributes = {}
    reprompt_text = None
    should_end_session = True

    status_response = requests.get("http://bart.crudworks.org/api/status")
    data = status_response.json()

    elev_status = requests.get("http://bart.crudworks.org/api/elevatorStatus")
    elev_data = elev_status.json()
    inner_data = elev_data["bsa"]
    str_inner_data = str(inner_data["description"])

    announcements = requests.get("http://bart.crudworks.org/api/serviceAnnouncements")
    announce_data = announcements.json()
    inner_data = announce_data["bsa"]
    parsed_dict = (inner_data[0])
    str_parsed_dict = str(parsed_dict["description"]) + " "

    speech_output = "Currently, there are " + data["traincount"] + " trains running. " + str_parsed_dict + str_inner_data
    card_output = "Currently, there are " + data["traincount"] + " trains running. " + str_parsed_dict + str_inner_data


    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))

    
def elevator_status(intent, session):
    card_title = "BART Elevator Status"
    session_attributes = {}
    reprompt_text = None
    should_end_session = True

    elev_status = requests.get("http://bart.crudworks.org/api/elevatorStatus")
    elev_data = elev_status.json()
    inner_data = elev_data["bsa"]
    
    print ("ELEVATOR DATA --> ", elev_data)
    print ("INNER DATA --> ", inner_data)
    
    speech_output = inner_data["description"]
    card_output = inner_data["description"]

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))

def service_announcements(intent, session):
    card_title = "BART Service Announcements"
    session_attributes = {}
    reprompt_text = None
    should_end_session = True

    announcements = requests.get("http://bart.crudworks.org/api/serviceAnnouncements")
    announcement_data = announcements.json()
    inner_data = announcement_data["bsa"]
    parsed_dict = (inner_data[0])
    speech_output = parsed_dict["description"]
    card_output = parsed_dict["description"]

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))

def fare(intent_request, intent, session):
    card_title = "BART Fare Calculator"
    session_attributes = {}
    reprompt_text = None
    should_end_session = True

    if intent_request['dialogState'] != "COMPLETED":
        print ("DIALOG RUNNING")

        return {  "version": "1.0",  "response": {  "shouldEndSession": False,  "directives": [{  "type": "Dialog.Delegate"  }]}}
    else:
        print ("DIALOG COMPLETE")
        
    if "Source" in intent["slots"] and "Destination" in intent["slots"]:
        sstation = intent["slots"]["Source"]["value"].lower()
        dstation = intent["slots"]["Destination"]["value"].lower()

        if not isStationValid(station_dict, sstation):
            should_end_session = False
            return build_response(session_attributes, build_speechlet_response_without_card(
                SOURCE_PROMPT, SOURCE_REPROMPT, should_end_session))

        elif not isStationValid(station_dict, dstation):
            should_end_session = False
            return build_response(session_attributes, build_speechlet_response_without_card(
                DEST_PROMPT, DEST_REPROMPT, should_end_session))

        start_attributes = create_start_station_attributes(sstation)
        dest_attributes = create_destination_station_attributes(dstation)

        scode = station_dict[sstation]
        dcode = station_dict[dstation]

    route = requests.get("http://bart.crudworks.org/api/tickets/" + scode +"/" + dcode)
    data = route.json()
    fare = (((((data["schedule"])["request"])["trip"])["details"])["fare"])
    
    speech_output = "The fare for your trip from " + str(sstation) + " to " + str(dstation) + " is $" + str(fare) 
    reprompt_text = None 
    return build_response(session_attributes, build_speechlet_response_without_card(
        speech_output, reprompt_text, should_end_session))
        
    
def create_start_station_attributes(sstation):
    return {"StartStation": sstation}
    
def create_destination_station_attributes(dstation):
    return {"DestinationStation": dstation}


station_dict = {
                "twelfth street oakland city center": "12TH",
                "twelfth street": "12TH",
                "oakland city center": "12TH",
                "sixteenth street mission": "16TH",
                "sixteenth street": "16TH",
                "nineteenth street oakland": "19TH",
                "nineteenth street": "19TH",
                "twenty fourth street mission": "24TH",
                "twenty fourth street": "24TH",
                "ashby": "ASHB",
                "balboa park": "BALB",
                "bay fair": "BAYF",
                "castro valley": "CAST",
                "civic center u. n. plaza": "CIVC",
                "civic center": "CIVC",
                "u. n. plaza": "CIVC",
                "coliseum oracle arena": "COLS",
                "coliseum": "COLS",
                "oracle arena": "COLS",
                "oracle": "COLS",
                "colma": "COLM",
                "concord": "CONC",
                "daly city": "DALY",
                "downtown berkeley": "DBRK",
                "dublin pleasanton": "DUBL",
                "el cerrito del norte": "DELN",
                "el cerrito plaza": "PLZA",
                "embarcadero": "EMBR",
                "fremont": "FRMT",
                "fruitvale": "FTVL",
                "glen park": "GLEN",
                "hayward": "HAYW",
                "lafayette": "LAFY",
                "lake merritt": "LAKE",
                "macarthur": "MCAR",
                "millbrae": "MLBR",
                "montgomery street": "MONT",
                "north berkeley": "NBRK",
                "north concord martinez": "NCON",
                "oakland international airport": "OAKL",
                "oakland airport": "OAKL",
                "oakland international": "OAKL",
                "orinda": "ORIN",
                "pittsburg bay point": "PITT",
                "bay point": "PITT",
                "pittsburg": "PITT",
                "pleasant hill contra costa center": "PHIL",
                "pleasant hill": "PHIL",
                "contra costa center": "PHIL",
                "powell street": "POWL",
                "richmond": "RICH",
                "rockridge": "ROCK",
                "san bruno": "SBRN",
                "san francisco international airport": "SFIA",
                "san francisco international": "SFIA",
                "S F international": "SFIA",
                "S. F. international": "SFIA",
                "S F airport": "SFIA",
                "SF airport": "SFIA",
                "sf airport": "SFIA",
                "s f airport": "SFIA",
                "S. F. airport": "SFIA",
                "san francisco airport": "SFIA",
                "san leandro": "SANL",
                "south hayward": "SHAY",
                "south san francisco": "SSAN",
                "union city": "UCTY",
                "walnut creek": "WCRK",
                "warm springs": "WARM",
                "warm springs south fremont": "WARM",
                "south fremont": "WARM",
                "west dublin pleasanton": "WDUB",
                "west dublin": "WDUB",
                "west oakland": "WOAK"
                }            

def elicitSlotDirective(intent):
    del intent["slots"]["Destination"]["resolutions"]
    del intent["slots"]["Source"]["value"]
    str1 = '{"version": "1.0","sessionAttributes": {},"response": {"outputSpeech": {"type": "PlainText","text": "What is your start station?"},'
    str2 = '"shouldEndSession": false,"directives": [{"type": "Dialog.ElicitSlot","slotToElicit": "Source"'
    str3 = ', "updatedIntent": ' + json.dumps(intent)
    str4 = '}]}}'
    finalStr = str1 + str2 + str3 + str4
    print("finalStr --> ", finalStr)
    return finalStr

def delegateDirective(intent):
    del intent["slots"]["Destination"]["resolutions"]
    str1 = '{"version": "1.0","sessionAttributes": {},'
    str2 = '"shouldEndSession": false,"directives": [{"type": "Dialog.Delegate"'
    str3 = ', "updatedIntent": ' + json.dumps(intent)
    str4 = '}]}'
    finalStr = str1 + str2 + str3 + str4
    print("finalStr --> ", finalStr)
    return finalStr


def route(intent_request, intent, session):
    print("in function route")
    card_title = "BART Route Departures"
    session_attributes = {}
    reprompt_text = None
    should_end_session = True
    
    if intent_request['dialogState'] != "COMPLETED":
        print ("DIALOG RUNNING")

        return {  "version": "1.0",  "response": {  "shouldEndSession": False,  "directives": [{  "type": "Dialog.Delegate"  }]}}
        #return elicitSlotDirective(intent)
        #return delegateDirective(intent)
    else:
        print ("DIALOG COMPLETE")
    
    if "Source" in intent["slots"] and "Destination" in intent["slots"]:
        sstation = intent["slots"]["Source"]["value"].lower()
        dstation = intent["slots"]["Destination"]["value"].lower()
        print ("SSTATION --> ", sstation)
        print ("DSTATION --> ", dstation)

        if not isStationValid(station_dict, sstation):
            should_end_session = False
            print ("INVALID SOURCE")
            return build_response(session_attributes, build_speechlet_response_without_card(
                SOURCE_PROMPT, SOURCE_REPROMPT, should_end_session))
        elif not isStationValid(station_dict, dstation):
            should_end_session = False
            print ("INVALID DESTINATION")
            return build_response(session_attributes, build_speechlet_response_without_card(
                DEST_PROMPT, DEST_REPROMPT, should_end_session))

        start_attributes = create_start_station_attributes(sstation)
        dest_attributes = create_destination_station_attributes(dstation)

        scode = station_dict[sstation]
        dcode = station_dict[dstation]
        return commonfactor(scode, dcode)

Itinerary = collections.namedtuple('Itinerary', ['sstation', 'sstationName',
    'target', 'duration', 'numSegments', 'segments', 'fare'])

Segment = collections.namedtuple('Segment', ['originName', 'trainHeadStation',
    'trainHeadStationName', 'destinationName', 'origTimeMin'])


def getItinerary(scode, dcode):
    route = requests.get("http://bart.crudworks.org/api/tickets/" + scode +"/" + dcode)
    data = route.json()
    trip = data["schedule"]["request"]["trip"]
    fare = trip["details"]["fare"]
    duration = trip["details"]["duration"]
    inner_data = trip["leg"]
    numSegments = len(inner_data)
    print ("numSegments --> ", numSegments)
    sstation = inner_data[0]["details"]["origin"]
    sstationName = inner_data[0]["details"]["originName"]
    target = inner_data[0]["details"]["trainHeadStationName"]
    
    segments = []
    for i, segment in enumerate(inner_data):
        segments.append(Segment(
        segment["details"]["originName"],
        segment["details"]["trainHeadStation"],
        segment["details"]["trainHeadStationName"],
        segment["details"]["destinationName"],
        segment["details"]["origTimeMin"]
        ))
    return Itinerary(sstation, sstationName, target, duration, numSegments, segments, fare)


def getSpeechOutput(inner_data2, target):
    outer_list = []
    speech_output = ''
    for i in inner_data2:
        inner_tuple = ()
        destination = (i["destination"])
        print ("DESTINATION --> ", destination)
        if (destination==target):
            estimate = (i["estimate"])    
            for j in estimate:
                numOfCars = int(j["length"])
                minutes = (j["minutes"])
                if (minutes == "Leaving"):
                    minutes = 0
                else:
                    minutes = int(minutes)
                
                inner_tuple = (destination, numOfCars, minutes)
                outer_list.append(inner_tuple)

            sorted_outer_list = sorted(outer_list, key= lambda x: x[2])
            for a in sorted_outer_list:
                if (a[2] == 0):
                    speech_output += (str(a[1]) + " car train for " + str(a[0]) + " leaving right now. ")
                elif (a[2] == 1):
                    speech_output += (str(a[1]) + " car train for " + str(a[0]) + " in " + str(a[2]) + " minute. ")
                else:
                    speech_output += (str(a[1]) + " car train for " + str(a[0]) + " in " + str(a[2]) + " minutes. ")
#        else:
#            speech_output += ("Currently, there are no trains running between these stations. ")
    return speech_output    

def commonfactor(scode, dcode):
    card_title = "BART Route Departures"
    session_attributes = {}
    reprompt_text = None
    should_end_session = True
    card_output = ""
    print ("SCODE --> ", scode, ", DCODE --> ", dcode)

    iti = getItinerary(scode, dcode)
    speech_output_1 = "From " + str(iti.sstationName) + " station, take one of the following trains. "
    print ("TARGET --> ", iti.target)
    target = iti.target
    #if (str(target) == "Millbrae"):
    #    target = string.replace(target, "Millbrae", "SFO/Millbrae")
    if (str(iti.target).startswith("Warm Springs")):
        target = string.replace(iti.target, iti.target, "Warm Springs")

    print ("TARGET2 --> ", target)
    departures = requests.get("http://bart.crudworks.org/api/departures/" + iti.sstation)
    data = departures.json()

    inner_data2 = (data["etd"])
    segments = iti.segments

    speech_output_2 = getSpeechOutput(inner_data2, target)
    if not speech_output_2:
        print ("YAY")
        speech_output = "Currently, there are no trains running between these stations. "
    else:
        speech_output = speech_output_1 + speech_output_2
        if (iti.numSegments == 3):
            speech_output += train_transfer_speech(segments[1].originName, segments[1].trainHeadStationName)
            speech_output += train_transfer_speech(segments[2].originName, segments[2].trainHeadStationName)
            speech_output += trip_time_speech(segments[2].destinationName, str(iti.duration))
            card_output = departure_card(segments[0].trainHeadStationName, segments[0].originName, segments[0].origTimeMin) +  train_transfer_speech(segments[1].originName, segments[1].trainHeadStationName) + train_transfer_speech(segments[2].originName, segments[2].trainHeadStationName) + trip_time_speech(segments[2].destinationName, str(iti.duration))
        elif (iti.numSegments == 2):
            speech_output += train_transfer_speech(segments[1].originName, segments[1].trainHeadStationName)
            speech_output += trip_time_speech(segments[1].destinationName, str(iti.duration))
            card_output = departure_card(segments[0].trainHeadStationName, segments[0].originName, segments[0].origTimeMin) + train_transfer_speech(segments[1].originName, segments[1].trainHeadStationName) + trip_time_speech(segments[1].destinationName, str(iti.duration))
        elif (iti.numSegments == 1):
            speech_output += trip_time_speech(segments[0].destinationName, str(iti.duration))
            card_output += departure_card(segments[0].trainHeadStationName, segments[0].originName, segments[0].origTimeMin) + trip_time_speech(segments[0].destinationName, str(iti.duration))
        else:
            speech_output = "Currently, there are no trains running between these stations. "
            card_output = "Currently, there are no trains running between these stations. "

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))

def train_transfer_speech(transferPoint, trainHeader):
    return "At " + transferPoint + " station, transfer to " +  trainHeader + " train . " 
    
def trip_time_speech(dest, duration):
    return "Your total trip time to " + dest + " is " + duration + " minutes"
    
def departure_card(trainHeader, origin, origTimeMin):
    return "Take the " + trainHeader + " train from " + origin + " departing in " + origTimeMin + "."

def isStationValid(stationDict, stationName):
    return (stationDict.get(stationName) is not None)

def trainHeader(intent_request, intent, session):
    print("in function trainHeader")
    card_title = "BART Route Departures"
    session_attributes = {}
    reprompt_text = None
    should_end_session = True
    
    if intent_request['dialogState'] != "COMPLETED":
        print ("DIALOG RUNNING")
        return {  "version": "1.0",  "response": {  "shouldEndSession": False,  "directives": [{  "type": "Dialog.Delegate"  }]}}
    else:
        print ("DIALOG COMPLETE")
        
    print ("INTENT [SLOTS] --> ", intent["slots"])
    if "Source" in intent["slots"] and "FinalDestination" in intent["slots"]:
        sstation = intent["slots"]["Source"]["value"].lower()
        dstation = intent["slots"]["FinalDestination"]["value"].lower()
        print ("SSTATION --> ", sstation)
        print ("DSTATION --> ", dstation)

        if not isStationValid(station_dict, sstation):
            should_end_session = False
            print ("INVALID SOURCE")
            return build_response(session_attributes, build_speechlet_response_without_card(
                SOURCE_PROMPT, SOURCE_REPROMPT, should_end_session))
        elif not isStationValid(station_dict, dstation):
            should_end_session = False
            print ("INVALID DESTINATION")
            return build_response(session_attributes, build_speechlet_response_without_card(
                DEST_PROMPT, DEST_REPROMPT, should_end_session))
            
        start_attributes = create_start_station_attributes(sstation)
        dest_attributes = create_destination_station_attributes(dstation)

        scode = station_dict[sstation]
        dcode = station_dict[dstation]

        return commonfactortwo(scode, dcode)
        
def commonfactortwo(scode, dcode):
    card_title = "BART Route Departures"
    session_attributes = {}
    reprompt_text = None
    should_end_session = True
    card_output = ""
    print ("SCODE --> ", scode, ", DCODE --> ", dcode)

    iti = getItinerary(scode, dcode)
    thcode =  iti.segments[0].trainHeadStation
    print ("THCODE --> ", thcode)
    if (str(dcode) != str(thcode)):
        print ("NOT DIRECT")
        speech_output_1 = "Currently, there is no direct train to " + iti.segments[iti.numSegments-1].trainHeadStationName + " ."

    speech_output_1 += "From " + str(iti.sstationName) + " station, take one of the following trains. "
    print ("TARGET --> ", iti.target)
    target = iti.target
    #if (str(target) == "Millbrae"):
    #    target = string.replace(target, "Millbrae", "SFO/Millbrae")
    if (str(iti.target).startswith("Warm Springs")):
        target = string.replace(iti.target, iti.target, "Warm Springs")

    print ("TARGET2 --> ", target)
    departures = requests.get("http://bart.crudworks.org/api/departures/" + iti.sstation)
    data = departures.json()

    inner_data2 = (data["etd"])
    segments = iti.segments

    speech_output = speech_output_1 + getSpeechOutput(inner_data2, target)
    if (iti.numSegments == 3):
        speech_output += train_transfer_speech(segments[1].originName, segments[1].trainHeadStationName)
        speech_output += train_transfer_speech(segments[2].originName, segments[2].trainHeadStationName)
        card_output = departure_card(segments[0].trainHeadStationName, segments[0].originName, segments[0].origTimeMin) +  train_transfer_speech(segments[1].originName, segments[1].trainHeadStationName) + train_transfer_speech(segments[2].originName, segments[2].trainHeadStationName)
    elif (iti.numSegments == 2):
        speech_output += train_transfer_speech(segments[1].originName, segments[1].trainHeadStationName)
        card_output = departure_card(segments[0].trainHeadStationName, segments[0].originName, segments[0].origTimeMin) + train_transfer_speech(segments[1].originName, segments[1].trainHeadStationName)
    elif (iti.numSegments == 1):
        card_output += departure_card(segments[0].trainHeadStationName, segments[0].originName, segments[0].origTimeMin)
    else:
        speech_output = "Currently, there are no trains running between these stations. "
        card_output = "Currently, there are no trains running between these stations. "

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetStatus":
        return status(intent, session)
    elif intent_name == "GetElevatorStatus":
        return elevator_status(intent, session)
    elif intent_name == "GetServiceAnnouncements":
        return service_announcements(intent, session)
    elif intent_name == "GetTrainHeader":
        return trainHeader(intent_request, intent, session)
    elif intent_name == "GetRouteDepartures":
        return route(intent_request, intent, session)
    elif intent_name == "GetFare":
        return fare(intent_request, intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return help_function()
#    elif intent_name == "AMAZON.YesIntent":
#        return repeat_request(intent, session)
#    elif intent_name == "AMAZON.NoIntent":
#        return handle_session_end_request()
    elif intent_name == "AMAZON.StartOverIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.RepeatIntent":
        return handle_repeat_request(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event-->", event)
    
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
