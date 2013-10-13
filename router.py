from flask import Flask, jsonify, abort, make_response, request
from pulp import *
import re
import uuid


app = Flask(__name__)

# subnet(10.0.x.0/24), throughput, cost
plans = {"small": [1, 1, 0.01],
        "medium": [2, 5, 0.05],
        "large": [3, 10, 0.1],
        "super": [4, 25, 0.25]}     


def optimize(size):
    # define variables as number of requests in each category
    # its value is from 0 to 254, 0 means we won't use that category
    s = LpVariable("small", 0, 254, cat=LpInteger)
    m = LpVariable("medium", 0, 254, cat=LpInteger)
    l = LpVariable("large", 0, 254, cat=LpInteger)
    x = LpVariable("super", 0, 254, cat=LpInteger) 

    # the objective to optimize
    total_requests = lpSum([s, m, l, x])
    problem = LpProblem("routing", LpMinimize)
    problem += total_requests

    # constraints
    total_messages = lpSum([s * plans["small"][1], m * plans["medium"][1], 
                            l * plans["large"][1], x * plans["super"][1]])
    problem += (total_messages == size)

    # run the external LP/MIP solver
    problem.writeLP("routing" + str(uuid.uuid4()) + ".lp")
    problem.solve()

    return map(lambda x: int(value(x)), [problem.objective, s, m, l, x])


def generate_routing_plan(plan, recipients):
    # interpret the result to a routing plan
    routes = []
    s, m, l, x = plan[1:]
    r = recipients[:]

    for i in range(1, s+1):
        routes.append({"ip": "10.0.1." + str(i), 
            "recipients": [str(r[i-1])]})
    
    r[0:s] = [] # remove first s phone numbers

    for i in range(1, m+1):
        routes.append({"ip": "10.0.2." + str(i), 
            "recipients": map(str, r[(i-1)*5 : (i-1)*5+5])})
    r[0:m] = []

    for i in range(1, l+1):
        routes.append({"ip": "10.0.3." + str(i), 
            "recipients": map(str, r[(i-1)*10 : (i-1)*10+10])})
    r[0:l] = []

    for i in range(1, x+1):
        routes.append({"ip": "10.0.4." + str(i), 
            "recipients": map(str, r[(i-1)*25 : (i-1)*25+25])})

    return routes


# 404 in JSON format
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)


@app.route('/router/api/v1.0/message', methods = ['POST'])
def route():
    if not request.json:
        abort(400) # bad request
    if "message" not in request.json and type(request.json["message"]) is not unicode:
        abort(400)
    if "recipients" not in request.json and type(request.json["recipients"]) is not unicode:
        abort(400)

    recipients = request.json['recipients']

    #TODO: more checking on telephone numbers e.g. area code
    phonePattern = r'\+1\d{10}$'
    for phone in recipients:
        # if type(phone) is not unicode:
        #     abort(400)
        if re.search(phonePattern, phone) is None:
            abort(400)

    size = len(recipients)

    #TODO: the maximum size of recipients will be 254 * (1 + 5 + 10 + 25) = 10414
    # although in this case it won't go above 5k
    result = generate_routing_plan(optimize(size), recipients)
    return jsonify({ 'message': request.json['message'], "routes": result}), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0")
