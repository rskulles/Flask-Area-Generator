# Created By Roy Skullestad On 4 May 2018

import argparse
import os
import json

parser = argparse.ArgumentParser(description = 'Generate an area and add it to a wscgi flask application.')
parser.add_argument('name', metavar='<name>', type = str, help = 'Name of the area')
parser.add_argument('--application','-a', required = False, type = str, default='app.py', help = 'The main script of the application. Usually app.py for wscgi applications.')
parser.add_argument('--flaskname','-fn', required = False, type = str, default='app', help = 'The variable Flask(__name__) is set to.')
parser.add_argument('--database','-d', required = False, type = str, default = 'app', help = 'Name of the database for mongo client.')
parser.add_argument('--collection','-c', required = False, type = str, default = None, help = 'Name of the collection for mongo client.')
parser.add_argument('--path', '-p', required = False, type = str, default='./', help = 'Root path to application.')

args = parser.parse_args()

area_name = args.name
main_file_path = args.application
flask_name = args.flaskname
root_path = args.path
db = args.database
collection = args.collection
if collection is None:
    collection = area_name

print 'Creating {}!\n'.format(area_name)
print '...Registering blueprint area file {}\n...Flask(__name__) set to variable {}'.format(main_file_path, flask_name)

if not os.path.isfile(root_path + main_file_path):
    print '!!! The file {} does not exist. Exiting !!!'.format(main_file_path)
    quit()

# Register the blueprint with the application
with open(root_path + main_file_path, "r") as in_file:
    buf = in_file.readlines()

with open(root_path + main_file_path, "w") as out_file:
    for line in buf:
        if line.startswith('#>>bpdump'):
            line ="app.register_blueprint(api.{}_area, url_prefix='/{}')\n".format(area_name, area_name) + line
            
        out_file.write(line)

print '...Blueprint registered!\n'

#include new area in module
print '...Adding area to __init__.py in module api.'

if not os.path.exists('{}api'.format(root_path)):
    print '...Directory not found. Creating it.'
    os.mkdir('./api', 2775)

init_import_statement = 'from {} import  {}_area\n'.format(area_name, area_name)

if not os.path.exists('{}api/__init__.py'.format(root_path)):
    print '...Creating init file'
    with open('./api/__init__.py', "w") as init_file:
        init_file.write(init_import_statement)
else:
    with open('{}api/__init__.py'.format(root_path), "r") as in_file:
        buf = in_file.readlines()

    with open('{}api/__init__.py'.format(root_path), 'w') as init_file:
        init_file.write(init_import_statement)
        
        for line in buf:
            init_file.write(line)



# Write new area
print '...Writing new area'

area_string = """
import pymongo
from flask import Blueprint, jsonify, request, Flask

client = pymongo.MongoClient('localhost')
db = client['{}']
collection = db['{}']

{}_area = Blueprint('{}_area', __name__)


@{}_area.route('/', methods=['POST'])
def area_func():
    json = request.json
    action = json['action']
    if action == 'create':
        return create(json)
    elif action == 'update':
        return update(json)
    elif action == 'read':
        return read(json)
    elif action == 'delete':
        return delete(json)


def create(json):
    pass


def update(json):
    pass


def read(json):
    pass


def delete(json):
    pass

""".format(db, collection, area_name, area_name, area_name)

with open('{}api/{}.py'.format(root_path, area_name), "w") as area_file:
    area_file.write(area_string);

print 'Good to go!'