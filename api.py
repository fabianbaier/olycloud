from flask import Flask, jsonify, make_response, request, abort
import requests

import sys
import os

conf_dir_default = os.path.expanduser('/Users/fabianbaier/Documents/Stuff/Python/CCM/config')
crtfilename = 'client.crt'
keyfilename = 'client.key'
crt = os.path.join(conf_dir_default, crtfilename)
key = os.path.join(conf_dir_default, keyfilename)

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Alex you are cool!',
        'done': False
    }
]


@app.route('/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/v1.0/containers', methods=['GET'])
def get_containers():
    lxdapi = requests.get('https://10.0.49.207:8443/1.0/containers', verify=False, cert=(crt, key))
    lxdapi = lxdapi.json()
    container_list = []
    containers = [{'container-list': container_list}]
    for i in range(len(lxdapi['metadata'])):
        container_list.append(lxdapi['metadata'][i].replace('/1.0/containers/',''))
    return jsonify(containers)

@app.route('/v1.0/containers/raw', methods=['GET'])
def get_containers_rawdata():
    lxdapi = requests.get('https://10.0.49.207:8443/1.0/containers', verify=False, cert=(crt, key))
    lxdapi = lxdapi.json()
    containers_rawdata = [{'container-rawdata': lxdapi}]
    return jsonify(containers_rawdata)

@app.route('/v1.0/containers/raw/<string:task_id>', methods=['GET'])
def get_rawdata_container(task_id):
    lxdapi = requests.get('https://10.0.49.207:8443/1.0/containers/'+task_id+'/state', verify=False, cert=(crt, key))
    lxdapi = lxdapi.json()
    containers_rawdata = [{'container-rawdata': lxdapi}]
    return jsonify(containers_rawdata)

@app.route('/v1.0/<string:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

@app.route('/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 500)

if __name__ == '__main__':
    app.run(debug=True)
    #app.run()
