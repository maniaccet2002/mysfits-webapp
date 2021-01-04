import json
import boto3
import logging
import re
import urllib3

from botocore.exceptions import ClientError
s3=boto3.resource('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event,context):
    logger.info("Received event: %s" % json.dumps(event))
    logger.info("context: %s" % context)
    sourcebucket = event['ResourceProperties']['SourceBucket']
    destinationbucket = event['ResourceProperties']['DestinationBucket']
    artifactbucket = event['ResourceProperties']['ArtifactBucket']
    mysfitsapiendpoint=event['ResourceProperties']['MysfitsApiEndpoint']
    cognitouserpoolid=event['ResourceProperties']['CognitoUserPoolId']
    cognitouserpoolclientid=event['ResourceProperties']['CognitoUserPoolClientId']
    awsregion=event['ResourceProperties']['AWSRegion']
    response_url = event['ResponseURL']
    functionname = event['ResourceProperties']['FunctionName']
    
    response_data = {}
    response_data['Status'] = 'SUCCESS'
    response_data['StackId'] = event['StackId']
    response_data['RequestId'] = event['RequestId']
    response_data['LogicalResourceId'] = event['LogicalResourceId']
    response_data['PhysicalResourceId'] = functionname
   
    try:
        if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
            upload_jsfiles(sourcebucket,destinationbucket)
            update_indexhtml(sourcebucket,destinationbucket,mysfitsapiendpoint,cognitouserpoolid,cognitouserpoolclientid,awsregion)
            update_confirmhtml(sourcebucket,destinationbucket,cognitouserpoolid,cognitouserpoolclientid)
            update_registerhtml(sourcebucket,destinationbucket,cognitouserpoolid,cognitouserpoolclientid)
        elif event['RequestType'] == 'Delete':
            delete_html(destinationbucket)
            #delete_html(artifactbucket)
        
    except ClientError as e:
        logger.error('Error: %s', e)
        response_data['Status'] = 'FAILED'
        response_data['Reason'] = e
        
    logger.info(response_data) 
    json_response = json.dumps(response_data)
    headers = {
        'content-type' : ''
    }
    
    http = urllib3.PoolManager()
    response = http.request('PUT',response_url,body=json_response)

def upload_jsfiles(sourcebucket,destinationbucket):
    object=s3.Object(sourcebucket,'web/js/amazon-cognito-identity.min.js').download_file('/tmp/amazon-cognito-identity.min.js')
    object=s3.Object(sourcebucket,'web/js/aws-cognito-sdk.min.js').download_file('/tmp/aws-cognito-sdk.min.js')
    object=s3.Object(sourcebucket,'web/js/aws-sdk-2.246.1.min.js').download_file('/tmp/aws-sdk-2.246.1.min.js')
    
    s3.Object(destinationbucket,'js/amazon-cognito-identity.min.js').upload_file('/tmp/amazon-cognito-identity.min.js')
    s3.Object(destinationbucket,'js/aws-cognito-sdk.min.js').upload_file('/tmp/aws-cognito-sdk.min.js')
    s3.Object(destinationbucket,'js/aws-sdk-2.246.1.min.js').upload_file('/tmp/aws-sdk-2.246.1.min.js')
    
   
def update_confirmhtml(sourcebucket,destinationbucket,cognitouserpoolid,cognitouserpoolclientid):
    object=s3.Object(sourcebucket,'web/confirm.html').download_file('/tmp/confirm_source.html')
    with open('/tmp/confirm_source.html', 'r') as source:
        lines = source.readlines()
    with open('/tmp/confirm_updated.html', 'w') as updatedfile:
        for line in lines:
            if "var cognitoUserPoolId = 'REPLACE_ME'" in line:
                line=re.sub(r'REPLACE_ME',cognitouserpoolid,line)
            if "var cognitoUserPoolClientId = 'REPLACE_ME'" in line:
                line=re.sub(r'REPLACE_ME',cognitouserpoolclientid,line)
            
            updatedfile.write(line)
        
    s3.Object(destinationbucket,'confirm.html').upload_file('/tmp/confirm_updated.html',ExtraArgs={'ContentType':'text/html'})
    
def update_registerhtml(sourcebucket,destinationbucket,cognitouserpoolid,cognitouserpoolclientid):
    object=s3.Object(sourcebucket,'web/register.html').download_file('/tmp/register_source.html')
    with open('/tmp/register_source.html', 'r') as source:
        lines = source.readlines()
    with open('/tmp/register_updated.html', 'w') as updatedfile:
        for line in lines:
            if "var cognitoUserPoolId = 'REPLACE_ME'" in line:
                line=re.sub(r'REPLACE_ME',cognitouserpoolid,line)
            if "var cognitoUserPoolClientId = 'REPLACE_ME'" in line:
                line=re.sub(r'REPLACE_ME',cognitouserpoolclientid,line)
            
            updatedfile.write(line)
        
    s3.Object(destinationbucket,'register.html').upload_file('/tmp/register_updated.html',ExtraArgs={'ContentType':'text/html'})
        
        
def update_indexhtml(sourcebucket,destinationbucket,mysfitsapiendpoint,cognitouserpoolid,cognitouserpoolclientid,awsregion):
    object=s3.Object(sourcebucket,'web/index.html').download_file('/tmp/index_source.html')
    with open('/tmp/index_source.html', 'r') as source:
        lines = source.readlines()
    with open('/tmp/index_updated.html', 'w') as updatedfile:
        for line in lines:
            if "var mysfitsApiEndpoint = 'REPLACE_ME'" in line:
                line=re.sub(r'REPLACE_ME',mysfitsapiendpoint,line)
            if "var cognitoUserPoolId = 'REPLACE_ME'" in line:
                line=re.sub(r'REPLACE_ME',cognitouserpoolid,line)
            if "var cognitoUserPoolClientId = 'REPLACE_ME'" in line:
                line=re.sub(r'REPLACE_ME',cognitouserpoolclientid,line)
            if "var awsRegion = 'REPLACE_ME'" in line:
                line=re.sub(r'REPLACE_ME',awsregion,line)
            
            updatedfile.write(line)
        
    s3.Object(destinationbucket,'index.html').upload_file('/tmp/index_updated.html',ExtraArgs={'ContentType':'text/html'})
def delete_html(bucketname):
    bucket = s3.Bucket(bucketname)
    bucket.object_versions.delete()
        
    
        
    

        
