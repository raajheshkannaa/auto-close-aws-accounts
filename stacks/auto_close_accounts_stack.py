from constructs import Construct
from aws_cdk import (
	Duration,
	Stack,
	aws_iam as iam,
	aws_lambda as _lambda,
	aws_events as events,
	aws_events_targets as targets
)


class AutoCloseAccountsStack(Stack):

	def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
		super().__init__(scope, construct_id, **kwargs)

		# Create a new IAM Role Policy which will be used by the Lambda to gather list of accounts from Organization and
		# assume a role in the new account either using OrganizationAccountAccessRole or AWSControlTowerExecution
		closeaccount_role_policy = iam.ManagedPolicy(self, 'closeaccount-policy',
			managed_policy_name='autocloseaccount-policy',
			description='Policy for Auto Closing Accounts',
			statements = [
			iam.PolicyStatement(
			sid="CDKBootstrapPermissions",
			actions=[
				"sts:GetCallerIdentity",
				"iam:GetUser",
				"iam:ListRoles",
				"iam:ListAccountAliases",
				"organizations:ListAccounts",
				"organizations:ListAccountsForParent",
				"organizations:CloseAccount"],
			effect=iam.Effect.ALLOW,
			resources=['*'],
			)
			]			
		)

		# Create the IAM Role
		autocloseaccount_role = iam.Role(
			self, 'autocloseaccount-role',
			role_name='autocloseaccount-role',
			assumed_by=iam.CompositePrincipal(
				iam.ServicePrincipal('lambda.amazonaws.com'),
				iam.ServicePrincipal('ec2.amazonaws.com')
				)
		)
		# Attach the policy to the role
		closeaccount_role_policy.attach_to_role(autocloseaccount_role)
		# Attach necessary managed policies for Lambda execution
		autocloseaccount_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaVPCAccessExecutionRole'))
		autocloseaccount_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaRole'))

		auto_close_accounts_lambda = _lambda.Function(
			self, 'AutoCloseAccounts',
			code=_lambda.Code.from_asset('src/'),
			runtime=_lambda.Runtime.PYTHON_3_9,
			handler='close_accounts.main',
			timeout=Duration.seconds(900),
			memory_size=128,
			role=autocloseaccount_role,
			function_name='AutoCloseAccounts',
		)

		# AWS CloudTrail API call as the EventPattern to trigger the lambda 
		rule1 = events.Rule(
			self, 'TriggerAutoClosing',
			rule_name='TriggerAutoAccountClosing',
			event_pattern=events.EventPattern(
				# source=['aws.organizations'],
				# detail_type=['AWS Service Event via CloudTrail'],
				detail={
					"eventSource": ["organizations.amazonaws.com"],
					"eventName": ["MoveAccount"]
				}
			)
		)

		rule2 = events.Rule(
			self, 'TriggerAccountClosureEvery30Days',
			rule_name='TriggerAccountClosureEvery30Days',
			schedule=events.Schedule.rate(Duration.days(30))
		)
		
		# Point the Event Rule to the our Lambda
		rule1.add_target(targets.LambdaFunction(auto_close_accounts_lambda))
		rule2.add_target(targets.LambdaFunction(auto_close_accounts_lambda))
