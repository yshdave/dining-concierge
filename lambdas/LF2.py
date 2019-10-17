import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from boto3.dynamodb.conditions import Key, Attr
import random


def lambda_handler(event, context):
    es_client = Elasticsearch(
        hosts=[{'host': "search-test-7ehhq5kgikifouzfu7lgvl62qy.us-east-1.es.amazonaws.com", 'port': 443}],
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection)

    sqs_client = boto3.resource('sqs')
    max_number_of_message = 10
    wait_time_in_seconds = 5
    dynamodb_client = boto3.resource('dynamodb')
    sms_client = boto3.client('sns')
    yelp_data = dynamodb_client.Table('yelp_data')
    q1 = sqs_client.get_queue_by_name(QueueName='Q1')

    if True:  # response.get("Messages",None) is not None and len(response["Messages"])>0:
        for message in q1.receive_messages(MaxNumberOfMessages=max_number_of_message,
                                           WaitTimeSeconds=wait_time_in_seconds):
            print(message)
            # message_receipt_handle = message["ReceiptHandle"]
            body_dict = json.loads(message.body)
            query = {"query": {"match": {"cuisine": body_dict["cuisine"]}}}
            user_contact = "1" + str(body_dict["user_contact"])
            print(user_contact)
            search_result = es_client.search(index="restaurant", body=query)
            number_of_records_found = int(search_result["hits"]["total"]["value"])
            if number_of_records_found > 0:
                random_index = random.randint(0, len(search_result["hits"]["hits"]) - 1)
                print("***", random_index)
                restaurant_id = search_result["hits"]["hits"][random_index]["_source"]["id"]
                print(restaurant_id)
                query_response = yelp_data.query(KeyConditionExpression=Key('yelp_id').eq(restaurant_id))
                restaurant_details = query_response["Items"][0]
                print(restaurant_details)
                text_message = "Here's your lucky recommendation of the day\nRestaurant Name : {} \nRating : {}({} reviews)\nAddress : {}\n{}\n{}".format(
                    restaurant_details["name"], restaurant_details["rating"], restaurant_details["review_count"],
                    restaurant_details["address"], restaurant_details["contact"], restaurant_details["yelp_url"])
                print(text_message)
                print(body_dict)
                is_sms_sent = sms_client.publish(PhoneNumber=user_contact, Message=text_message)
                # print("****",is_sms_sent)
            else:
                is_sms_sent = sms_client.publish(PhoneNumber=user_contact, Message="No recommendations")

            print(search_result)
            message.delete()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


