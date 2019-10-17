import requests
import boto3
from decimal import Decimal
from elasticsearch import Elasticsearch, RequestsHttpConnection


esClient = Elasticsearch(
   hosts=[{'host': "search-test-7ehhq5kgikifouzfu7lgvl62qy.us-east-1.es.amazonaws.com",'port':443}],
   use_ssl=True,
   verify_certs=True,
   connection_class=RequestsHttpConnection)

YELP_SEARCH_API = "https://api.yelp.com/v3/businesses/search"
YELP_API_KEY = "PmIpbnmm5u6TrbI5Q-b-IA7Zri89io0ptFEgMitnaDoh0nFM5CfdzKaK1cm-wn1qEnG3SKpjIhF2PNlL255hYZFgzmxFIY6LQwO_h_1UCGSLdEzLJ1p_431-KwihXXYx"

def get_required_yelp_data(location,cuisine,cuisine_display_name):
    query_string = "?"
    query_string = query_string+"location={}".format(location)

    #https://www.yelp.com/developers/documentation/v3/all_category_list
    query_string = query_string+"&categories={}".format(cuisine)
    limit = "&limit=50"
    complete_yelp_api = YELP_SEARCH_API + query_string + limit

    headers = {"Authorization": "Bearer " + YELP_API_KEY}
    yelp_response_json = requests.get(complete_yelp_api, headers=headers).json()
    list_of_businesses = []
    total_records = yelp_response_json["total"]
    offset = 0
    offset_query_string = "&offset="
    while total_records!=0:
        if yelp_response_json.get("businesses",None) is not None:
            number_of_business_in_current_page = len(yelp_response_json["businesses"])
            for business in yelp_response_json["businesses"]:
                required_attributes_of_business = get_required_attributes_of_business(business,location,cuisine_display_name)
                list_of_businesses.append(required_attributes_of_business)
            total_records = total_records - number_of_business_in_current_page
            offset = offset + number_of_business_in_current_page
            yelp_response_json = requests.get(complete_yelp_api+offset_query_string+str(offset), headers=headers).\
                json()
        else:
            break

    return list_of_businesses

def get_required_attributes_of_business(business,location,cuisine):
    required_attributes_of_business = {"location" : location, "cuisine" : cuisine}
    required_attributes_of_business["yelp_id"] = business["id"]
    if not is_none_or_empty(business.get("rating",None)):
        required_attributes_of_business["rating"] = Decimal(business["rating"])
    if not is_none_or_empty(business.get("review_count",None)):
        required_attributes_of_business["review_count"] = business["review_count"]
    required_attributes_of_business["name"] = business["name"]
    required_attributes_of_business["yelp_url"] = business["url"]
    if not is_none_or_empty(business.get("price",None)) :
        required_attributes_of_business["price_range"] = business["price"]
    if not is_none_or_empty(business.get("phone",None)):
        required_attributes_of_business["contact"] = business["phone"]
    if business.get("location",None) is not None:
        restaurant_address = ""
        for address_line in business["location"]["display_address"]:
            restaurant_address = restaurant_address + address_line+" "
        required_attributes_of_business["address"] = restaurant_address

    return required_attributes_of_business

def is_none_or_empty(value):
    try:
        if value is None:
            return True
        value = str(value)
        if len(value) == 0:
            return True
        return False
    except:
        return True
def push_data_in_dynamo_and_elasticsearch(restaurants_list):
    print("Inserting ",len(restaurants_list)," records in dynamodb")
    dynamodb = boto3.resource('dynamodb')
    yelp_data = dynamodb.Table('yelp_data')
    restaurants_list_size = len(restaurants_list)
    batch_size = restaurants_list_size//20
    remaining_batches = batch_size
    start_index = -batch_size
    while remaining_batches!=0 :
        start_index = start_index+batch_size
        #writing in dynamo
        with yelp_data.batch_writer() as batch:
            for restaurant in restaurants_list[start_index:start_index+batch_size]:
                print(restaurant)
                batch.put_item(Item=restaurant)
        #uploading indexes
        for restaurant in restaurants_list[start_index:start_index + batch_size]:
            esClient.index(index='restaurant', doc_type='doc', body={
                "id" : restaurant["yelp_id"],
                "cuisine" : restaurant["cuisine"],
                #"location": restaurant["location"],
            })
        remaining_batches = remaining_batches-1


if __name__ == '__main__':
    boto3.setup_default_session(profile_name='cc')
    restaurants_list = get_required_yelp_data("manhattan","indpak","indian")
    restaurants_list= restaurants_list + get_required_yelp_data("manhattan", "mexican","mexican")
    restaurants_list = restaurants_list + get_required_yelp_data("manhattan", "italian","italian")
    restaurants_list = restaurants_list + get_required_yelp_data("manhattan", "chinese","chinese")
    restaurants_list = restaurants_list + get_required_yelp_data("manhattan", "mideastern","mideastern")
    push_data_in_dynamo_and_elasticsearch(restaurants_list)
