import boto3
import json

print('Loading function')
dynamo = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def check_interaction_helper(disease, drug):
  """
  A method that checks if disease is in the interaction list of drug with the three possible interaction levels
  
  params:
    disease : string
    drug : drug item dict
    
  return:
    boolean: True if interacts and False otherwise
  """
  disease_lower = disease.lower()
  for level in ['Unkown','Moderate','Major']:
    print(level)
    if [disease, level] in drug['disease_interaction']:
      return True
    if [disease_lower,level] in drug['disease_interaction']:
      return True
  return False


  
def check_interaction_list(disease, drugs_ids):
  """
  a method that given disease and ids of the drugs, it queries the dynamo database and get the corresponing drugs docs
  and return a list of those drugs that interact with the requested disease
  
  params:
    data: disease and a list of drugs ids
    
  return:
    disease: a string for a disease sent with the body of the request
    drug_list: a list of drugs documents
  """
  interaction_list = {}
  drugs_table = dynamodb.Table('drugs')
  
  for drug_id in drugs_ids: 
    drug = drugs_table.get_item(Key = {'id':drug_id})
    drug_item = drug['Item']
    interaction_list[drug_id] =  check_interaction_helper(disease, drug_item)
  return interaction_list
    

def get_items(data):
  """
  a method that given request body, it extracts the disease and drug list
  
  params:
    data: disease and a list of drugs ids
    
  return:
    disease: a string for a disease sent with the body of the request
    drug_list: a list of drugs documents
  """
  disease, drugs_ids = data['disease'], data['drugs']
  return disease, drugs_ids
  
  
  
  
def lambda_handler(event, context):
    try:   
      data = json.loads(event["body"]) 
      disease, drug_list = get_items(data)
      data = check_interaction_list(disease, drug_list)
      response = {
        'statusCode': 200,
        'headers': {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
        'body':  json.dumps(data),
      }
      print(response)
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
