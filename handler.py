import json
import view_spot_finder.finder

def find_spot(event, context):
    # at the moment the `event` is just the input data
    body = event
    # the input data should be either a json string or dict obj
    if isinstance(event, str):
        body = json.loads(event)
    # extract parameters
    mesh = body.get('mesh')
    N = body.get('N')
    # call actual bacend
    return view_spot_finder.finder.find_spot(mesh, N)
