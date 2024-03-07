from CybORG.Emulator.Actions.RedeployHostAction import RedeployHostAction


redeploy_host_action = RedeployHostAction(
    hostname='testmachine',
    auth_url='https://cloud.isislab.vanderbilt.edu:5000/v3',
    project_name='castle',
    username='ninehs',
    password='XXXXXXXXX',
    user_domain_name='ISIS',
    project_domain_name='ISIS'
)

redeploy_host_action.execute(None)
