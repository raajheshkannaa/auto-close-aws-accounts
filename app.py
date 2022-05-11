#!/usr/bin/env python3

import aws_cdk as cdk

from stacks.auto_close_accounts_stack import AutoCloseAccountsStack


app = cdk.App()
AutoCloseAccountsStack(app, "auto-close-accounts")

app.synth()
