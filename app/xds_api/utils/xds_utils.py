import json
import requests

from core.models import CourseSpotlight, XDSConfiguration


def get_request(request_url):
    """This method handles a simple HTTP get request to the passe in 
        request_url"""
    headers = {'Content-Type': 'application/json'}

    response = requests.get(request_url)

    return response

def get_spotlight_courses_api_url():
    """This method gets the list of configured course spotlight IDs, the 
        configured XIS api url and generates the query to request records"""
    # get XIS API url
    course_spotlights = CourseSpotlight.objects.filter(active=True)
    # get search string
    composite_api_url = XDSConfiguration.objects.first()\
        .target_xis_composite_ledger_api
    queryString = '?id='

    for num, spotlight in enumerate(course_spotlights):
        if num >= (len(course_spotlights) - 1):
            queryString += spotlight.course_id
        else:
            queryString += spotlight.course_id + ','

    full_api_string = composite_api_url + queryString

    return full_api_string

def metadata_to_target(metadata_JSON):
    """This method takes in a JSON representation of a record and transforms it
        into the search engine format"""
    metadata_dict = json.loads(metadata_JSON)
    result_list = []

    for record in metadata_dict:
        if 'metadata' in record:
            currObj = record['metadata']
            meta = {}

            meta["id"] = record["unique_record_identifier"]
            currObj["meta"] = meta
            result_list.append(currObj)

    return json.dumps(result_list)
