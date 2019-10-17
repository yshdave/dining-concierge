import json
import logging
import boto3

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def process_user_request(intent_request):
    print("in process_user_req")
    user_intended_location = get_slots(intent_request)["location"]
    user_intended_cuisine = get_slots(intent_request)["cuisine"]
    user_phone_number = get_slots(intent_request)["phonenumber"]
    source = intent_request['invocationSource']

    if source == 'FulfillmentCodeHook':
        slots = get_slots(intent_request)

        validation_result = validate_user_input(user_intended_cuisine,
                                                user_phone_number)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        output_session_attributes = intent_request['sessionAttributes'] if intent_request[
                                                                               'sessionAttributes'] is not None else {}

        push_details_to_sqs(user_intended_location, user_intended_cuisine,
                            user_phone_number)
        # return delegate(output_session_attributes, get_slots(intent_request))

        return close(intent_request['sessionAttributes'],
                     'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': "Recommendations are on their way "
                        })


def validate_user_input(user_intended_cuisine,
                        user_phone_number):
    allowed_cuisines = ['indian', 'chinese', 'mexican', 'middle eastern', 'italian']
    if user_intended_cuisine is not None and user_intended_cuisine.lower() not in allowed_cuisines:
        return build_validation_result(False,
                                       'Cuisine',
                                       'We do not have {}, would you like a different type of cuisine?'
                                       .format(user_intended_cuisine))

    return build_validation_result(True, None, None)


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def push_details_to_sqs(user_intended_location, user_intended_cuisine, user_phone_number):
    sqs = boto3.resource('sqs')
    q1 = sqs.get_queue_by_name(QueueName='Q1')
    user_message = {"location" : user_intended_location}
    user_message["cuisine"] = user_intended_cuisine
    user_message["user_contact"] = user_phone_number
    response = q1.send_message(MessageBody=json.dumps(user_message))
    print(response)

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    return response
def dispatch(intent_request):
    print("*****",intent_request)
    intent_name = intent_request['currentIntent']['name']
    if intent_name == 'diningsuggestio':
        return process_user_request(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


def lambda_handler(event, context):
    # TODO implement
    return dispatch(event)
