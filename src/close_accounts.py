import boto3
from botocore.exceptions import ClientError

client = boto3.client('organizations')


def main(event, handler):
	
	parent_id = '<Organizational Unit ID>' # Modify this to the Organizational Unit in the format 'ou-g11a-r7abcdef' which will be used for closing accounts
	
	if event['detail']['requestParameters']['destinationParentId'] == parent_id:
		accounts = client.list_accounts_for_parent(
			ParentId=parent_id
			)['Accounts']

		for account in accounts:
			if account['Status'] == 'ACTIVE':
				try:
					close_account_resp = client.close_account(
						AccountId=account['Id'])
					
					print("Account closure initiated for account: {}".format(account['Id']))

				except ClientError as e:
					print(e)

