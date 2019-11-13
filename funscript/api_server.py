# -*- coding:utf-8 -*-

# @Time    : 2019/11/12 23:20
# @Author  : zengln
# @Filename: api_server.py

import json
from flask import Flask, request, make_response

app = Flask(__name__)

user_dict = {}


@app.route('/api/users/<int:uid>', methods=['POST'])
def create_user(uid):
    user = request.get_json()
    if uid not in user_dict:
        result = {
            'success': True,
            'msg': 'create user success'
        }
        status_code = 200
        user_dict[uid] = user
    else:
        result = {
            'success': False,
            'msg': 'user already exist'
        }
        status_code = 500

    response = make_response(json.dumps(result), status_code)
    response.headers['Content-type'] = 'application/json'
    return response


@app.route('/api/users/<int:uid>', methods=['PUT'])
def update_user(uid):
    user = user_dict.get(uid, {})
    if user:
        user = request.get_json()
        success = True
        status_code = 200
    else:
        success = False
        status_code = 404

    result = {
        'success': success,
        'data': user
    }

    response = make_response(json.dumps(result), status_code)
    response.headers['Content-type'] = 'application/json'
    return response


@app.route('/api/users')
def get_users():
    user_list = [user for uid, user in user_dict.items()]
    if user_dict:

        result = {
            'success': True,
            'count': len(user_dict),
            'items': user_list
        }
        status_code = 201
    else:
        result = {

            'success': False,
            'count': 0
        }
        status_code = 500
    response = make_response(json.dumps(result), status_code)
    response.headers['Content-type'] = 'application/json'
    return response


@app.route('/api/reset-all')
def clear_users():
    user_dict.clear()
    result = {
        'success': True,
    }

    response = make_response(json.dumps(result))
    response.headers['Content-type'] = 'application/json'
    return response
