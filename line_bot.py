# -*- coding: utf-8 -*-
from flask import Flask, request
import json
import requests
from subprocess import call, Popen, PIPE

import sys
import os
import re
app = Flask(__name__)

@app.route('/')
def index():
    return "<p>Hello World!</p>"

CHANNEL_TOKEN_FILE = 'channel_token.dat'
CHANNEL_TOKEN = ''
with open(CHANNEL_TOKEN_FILE, 'r') as f:
    CHANNEL_TOKEN = f.read()

if not CHANNEL_TOKEN:
    print 'cannot get line channel token from file %s, get the line channel token from line developer site, exit'%(CHANNEL_TOKEN_FILE)
    exit(0)
    
CFG_FILE='bot.cfg'

img_upload_queue=[]
robot_state = 0
flickr_auth_url =None
replyToken =''
userId = ''

TEXT_CMD_PREFIX='@bot'


@app.route('/callback', methods=['POST'])
def callback():
    json_line = request.get_json()
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    print 'Received ==>'
    print decoded
    handle_request(decoded)
    return ''
    
def write_cfg():
    if config:
        print 'write config=', config
        
        with open(CFG_FILE, 'w') as outfile:  
            json.dump(config, outfile)

def load_cfg():
    global config
    if os.path.isfile(CFG_FILE):
        with open(CFG_FILE, 'r') as json_file:  
            config = json.load(json_file)
            print 'load config = ',config
    
def handle_request(msg):
    mtype = msg['events'][0]['message']['type']
    replyToken = msg['events'][0]['replyToken']
    userId = get_userid(msg)
    global config
    if userId:
        if userId not in config.keys():
            config[userId]=dict(config_default)
    
    for handler in type_handler.keys():
        if mtype == handler:
            type_handler[handler](msg)
            break
    
    
def send_help(msg):
    all_cmds = ''
    cmd_title = '{-10}:{-10}:{-10}:\n'.format('command', 'usage', 'description')
    cmd_format = '{-11}{-11}{-11}\n'
    all_cmds=cmd_title
    for cmd in text_commands:
        cmd_format.format(cmd['cmd'], cmd['help'], cmd['desc'])
        all_cmds += cmd_format
    send(msg, 'try "@bot command", available commands: \n%s'%(all_cmds))
    
    
def text_handler(msg):
    print 'text_handler=>'
    text = msg['events'][0]['message']['text']
    args = text.split(' ')
    print 'args=', args, 'len=', len(args)
    if args[0] == TEXT_CMD_PREFIX:
        if len(args)>1:
            for command in text_commands:
                if args[1].lower() == command['cmd']:
                    command['handler'](msg, args[2:])
                    break
            else:
                send_help(msg)
                
        else:
            send_help(msg)

        
def config_get(msg, key):
    userId = get_userid(msg)
    if userId and userId in config.keys():
        if key in config[userId].keys():
            return config[userId][key]
                 
def config_set(userId, name, value):
    global config
    if userId not in config.keys():
        config[userId]=dict(config_default)
    config[userId][name]=value
    
def img_handler(msg):
    photo_backup(msg)
    

def handle_help(msg,args):
    send_help(msg)



def handle_set(msg, args):
    userId = get_userid(msg)
   
    if len(args)>=2:
        set_name = args[0]
        set_value = args[1]
        set_config(userId, set_name, set_value)
        send(msg, 'set %s to %s'%(set_name, set_value))
        write_cfg()
            
def handle_show(msg, args):
    userId=get_userid(msg)
    text = ''
    for name in config[userId]:
        text += u'%s = %s\n'%(name, config[userId][name])
    print 'handle_show=',text
    
    if config[userId]['flickr_username']:
        username = config[userId]['flickr_username']
        flickr = flickrapi.FlickrAPI(configuration['api_key'],configuration['api_secret'], token_cache_location='.', username=username)
        if flickr.token_valid(perms='write'):
            status = 'Authorized'
        else:
            status = 'Not Authorized'
        text += '\nflickr user status :{} '.format(status)
    send(msg, text)

def photo_backup(msg):
    messageId = msg['events'][0]['message']['id']
    print 'photo_backup ', messageId
    curl_cmd="curl -X GET -H 'Authorization: Bearer %s' https://api.line.me/v2/bot/message/%s/content > %s.jpg"%(CHANNEL_TOKEN, messageId, messageId)
    print 'curl_cmd:', curl_cmd
    p = call(curl_cmd, shell=True)
    
    tags = u'line_photo'
    
    upload_cmd = "python flickr-upload.py -v -g %s %s.jpg"%(tags, messageId)
    print 'upload_cmd:', upload_cmd
    p = call(upload_cmd, shell=True)
    print 'upload %s.jpg done'%(messageId)
    delete_cmd = "rm %s.jpg"%(messageId)
    p = call(delete_cmd, shell=True)
    print 'delete %s.jpg done'%(messageId)

def get_userid(msg):
    if 'userId' in msg['events'][0]['source'].keys():
        userId = msg['events'][0]['source']['userId']
    elif 'roomId' in msg['events'][0]['source'].keys():
        userId = msg['events'][0]['source']['roomId']
    elif 'groupId' in msg['events'][0]['source'].keys():
        userId = msg['events'][0]['source']['groupId']
    
    return userId
    
def send(msg, text):
    replyToken = msg['events'][0]['replyToken']
    
    
    reply=sendReply(replyToken, text)
    if reply and 'Invalid' in reply['message']:
        userId = get_userid(msg)
        if userId:
            sendText(userId, text)
        
def get_userinfo(msg):
    userId = get_userid(msg)
    LINE_API = 'https://api.line.me/v2/bot/profile/{}'.format(userId)
    print 'get_userinfo request=',LINE_API
    headers = {
        'Content-Type': 'application/json',
        'Authorization':'Bearer %s'%(CHANNEL_TOKEN)
    }
    r = requests.get(LINE_API, headers=headers)
    print 'response = ', r.text
    userInfo=json.loads(r.text)
    return userInfo
    
def sendReply(token, text):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'
                     
    #print 'Channel Token=', CHANNEL_TOKEN
    headers = {
        'Content-Type': 'application/json',
        #'X-Line-ChannelID': CHANNEL_ID,
        #'X-Line-ChannelSecret': CHANNEL_SERECT,
        'Authorization':'Bearer %s'%(CHANNEL_TOKEN)
        #'X-Line-Trusted-User-With-ACL': MID
    }

    data = json.dumps({
        "replyToken":token,
        "messages":[{
            "type":'text',
            "text":text
        }]
    })
    #print 'headers=', headers
    #print 'data=', data
    print 'SendReply:', data
    #print("送出資料：",data)
    r = requests.post(LINE_API, headers=headers, data=data)
    print 'response = ', r.text
    return json.loads(r.text)

def sendText(user, text):
    LINE_API = 'https://api.line.me/v2/bot/message/push'

                   
    print 'Channel Token=', CHANNEL_TOKEN
    headers = {
        'Content-Type': 'application/json',
        #'X-Line-ChannelID': CHANNEL_ID,
        #'X-Line-ChannelSecret': CHANNEL_SERECT,
        'Authorization':'Bearer {%s}'%(CHANNEL_TOKEN)
        #'X-Line-Trusted-User-With-ACL': MID
    }

    data = json.dumps({
        "to": user,
        "messages":[{
            "type":'text',
            "text":text
        }]
    })
    print 'headers=', headers
    print 'data=', data

    #print("送出資料：",data)
    r = requests.post(LINE_API, headers=headers, data=data)
    print(r.text)

type_handler = {
    'text': text_handler,
    'image': img_handler
}


text_commands = [
    {'cmd':'set', 'help':'set [variable] [value]', 'desc':'set variable', 'handler': handle_set},
    {'cmd':'show', 'help':'show', 'desc':'show variables and status', 'handler': handle_show},
    {'cmd':'?', 'help':'?', 'desc':'show help', 'handler': handle_help},
]
config = {}


config_default = {
    'flickr_username': '',
    'auto_upload':'',
    'tags':''
}



if __name__ == '__main__':
    load_cfg()
    app.run(debug=True)
