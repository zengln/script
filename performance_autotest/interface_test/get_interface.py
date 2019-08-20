# -*- coding:utf-8 -*-


import flask, json


server = flask.Flask(__name__)


@server.route('/index', methods=['get'])
def index():
    res = {"msg": '这是一个示例接口', 'msg_code': 0}
    return json.dumps(res, ensure_ascii=False)


server.run(port=6892, debug=True, host='0.0.0.0')