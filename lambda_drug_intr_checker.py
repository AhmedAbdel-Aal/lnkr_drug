import boto3
import json

print('Loading function')
dynamo = boto3.client('dynamodb')


def respond(err, data=None):
    return {
        'statusCode': 400 if err else 200,
        'body': err if err else json.dumps(data),
        'headers': {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
    }
    

def check_interaction(drug_1, drug_2):
  """
  A method that checks if drug_1 is in the interaction list of drug 2 with the three possible interaction levels
  
  params:
    drug_1 : drug 1 item dict
    drug_2 : drug 2 item dict
    
  return:
    boolean: True if interacts and False otherwise
  """
  for level in ['Unkown','Moderate','Major']:
    if [drug_1['id'], level] in drug_2['drug_interaction']:
      return True
  return False
  
  
def check_interaction_list(drug_list):
  """
  a method that given list of drugs, check for interaction for every possible pair in the list
  
  params:
    drug_list: a list of drug items
  
  returns:
    interactions: a dict that in form of: 
        interaction = {drug_1:{drug_2:True, drug_3, False}, drug_2:{drug_1:True, drug_3:false}, drug_3:{drug_1:False, drug_2:False}}
      where this example mean that drug 1 interacts with drug 2 but not with 3
  """
  interactions = {}
  drug_list_items = [drug['Item'] for drug in drug_list]
  print(drug_list_items)
  for drug_1 in drug_list_items:
    interactions[drug_1['id']] = {}
    for drug_2 in drug_list_items:
      if drug_1['id'] != drug_2['id']:
        interactions[drug_1['id']][drug_2['id']] =  check_interaction(drug_1, drug_2)
  
  return interactions


def lambda_handler(event, context):
    try:
      data = event["body"]
      data = check_interaction_list(data)
      response = {
        'statusCode': 200,
        'body':  json.dumps(data),
        'headers': {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
      }
      return respond(err = None, data = response)
    except Exception  as e:
      return respond(err = e, data = None)
