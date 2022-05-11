# Automatically Close AWS Accounts

With a sigh of relief 😮‍💨 at last, AWS has recently announced a straight forward easy way to `close` an AWS Account using an Organizations API call. 

## Objectives Accomplished
1. Automatically intiate Account Closure when moved to a specific Organizational Unit(OU). For example we could have a dumpyard OU named such as OldOU or BlackHole or something similar, you get the point. 

2. We make use of a Lambda function which will be triggered when the `MoveAccount` event occurs, which means an account is being moved in the `AWS Organizations` realm. 

3. We also have another EventBridge Rule trigger which will invoke the Lambda function every 30 days to workaround the 10% Account Closure Quota Restriction. More info here - https://docs.aws.amazon.com/organizations/latest/APIReference/API_CloseAccount.html

4. We make use of the latest boto3 library, as the one which is used by Lambda is always couple minor versions behind and doesn't work with the recently announced API features.

5. All of this built and deployed as a CDK App 🔥

## Usage
> git clone https://github.com/raajheshkannaa/auto-close-aws-accounts
* Update the `parent_id` variable in the `src/close_accounts.py` file with the Organizational Unit which will be the dumpyard for accounts to be closed.
* Move the accounts you want to close that Organizational Unit you updated in the first step.
* Watch the accounts being closed automatically 😎 _(however would stop when it reaches the 10% quota)_ 😛

## Considerations
* Because there is an account closure quota restriction of 10% of the total AWS Accounts in an Organizations, we have the second trigger invoking the lambda every 30 days, however if there was an account moved to the OU in the meantime, the next trigger of the lambda would still be unable to close the remaining accounts in the OU, as the 30 days period from the last closure is not completed.
* However this should be okay in the long run, as the initial number of accounts will be high and would decrease as accounts are closed along the way.