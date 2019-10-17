import json
import boto3
def lambda_handler(event, context):
    print(event)
    lex_client = boto3.client('lex-runtime')
    lex_response = lex_client.post_text(botName = 'Restaurantbot',
                                        botAlias = 'test_restaurant',
                                        userId = 'frontend',
                                        inputText = event["queryStringParameters"]["user_message"])
    if lex_response.get("dialogState",None) == "ReadyForFulfillment":
        user_response = "I will message you the details soon!"
    else:
        user_response = lex_response["message"]
    return {
        'statusCode': 200,
        'body': json.dumps(user_response),
        "headers": { "Access-Control-Allow-Origin" : "*"}
    }
