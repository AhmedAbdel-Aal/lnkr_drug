import boto3
import json

print('Loading function')
dynamo = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')


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
  drug_1_name = drug_1['id']
  drug_1_name_lower = drug_1['id'].lower()
  for level in ['Unkown','Moderate','Major']:
    if [ drug_1_name, level] in drug_2['drug_interaction']:
      return True
    if [drug_1_name_lower,level] in drug_2['drug_interaction']:
      return True
  return False
  
  
def check_interaction_list(drug_list):
  """
  a method that given list of drugs, check for interaction for every possible pair in the list
  
  params:
    drug_list: a list of drug items
  
  returns:
    interactions: a list of list interactions that in form of: 
        interaction = [drug_1:[drug_2], drug_2:[drug_1:True], drug_3:[]}
      where this example mean that drug 1 interacts with drug 2 but not with 3
  """
  interactions = {}
  print(drug_list)
  for drug_1 in drug_list:
    interactions[drug_1['id']] = []
    for drug_2 in drug_list:
      if drug_1['id'] != drug_2['id']:
        if check_interaction(drug_1, drug_2):
          interactions[drug_1['id']].append([drug_2['id']])
  
  return interactions


def get_items(drugs_ids):
  """
  a method that given ids of the drugs, it queries the dynamo database and get the corresponing drugs docs
  
  params:
    drugs_ids: a list of drugs ids
    
  return:
    drug_list: a list of drugs documents
  """
  drug_list = []
  drugs_table = dynamodb.Table('drugs')
  for drug_id in drugs_ids: 
    drug = drugs_table.get_item(Key = {'id':drug_id})
    drug_list.append(drug['Item'])
  return drug_list


def lambda_handler(event, context):
    try:   
      data = json.loads(event["body"])
      drug_list = get_items(data)
      data = check_interaction_list(drug_list)
      response = {
        'statusCode': 200,
        'headers': {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
        'body':  json.dumps(data),
      }
      return response
    except Exception as e:
      return {
        'statusCode': 400,
        'headers': {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
        'body':  e,
      }
