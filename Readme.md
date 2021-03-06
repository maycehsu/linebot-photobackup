#Line Bot (flickr photo backup for line group)


[reference](https://becoder.org/python-flask-requests-line-bot-api/) 

###install

####1. create virtual environment
```
cd my-project-folder
virtualenv --no-site-packages venv
source venv/bin/activate
```

####2. install python packages
```

pip install -r requirements.txt
```

#### 3. run ngrok
use ngrok to forward https requests/response to/from local port

```
./ngrok http 5000
```

display screen after ngrok lauched

```
ngrok by @inconshreveable                                                                                                                (Ctrl+C to quit)
                                                                                                                                                         
Session Status                online                                                                                                                     
Version                       2.2.4                                                                                                                      
Region                        United States (us)                                                                                                         
Web Interface                 http://127.0.0.1:4040                                                                                                      
Forwarding                    http://b363d123.ngrok.io -> localhost:5000                                                                                 
Forwarding                    https://b363d123.ngrok.io -> localhost:5000                                                                                
                                                                                                                                                         
Connections                   ttl     opn     rt1     rt5     p50     p90                                                                                
                              2       0       0.00    0.00    3.47    6.92                                                                               
                                                                                                                                                         
HTTP Requests                                                                                                                                            
-------------                                                                                                                                            
                                                                                                                                                         
POST /callback                 200 OK                                                                                                                    
POST /callback                 200 OK   
```

#### 4. line bot setting

Set the Webhook URL to url generated by ngrok "https://b363d123.ngrok.io/callback"

#### 5. flickr api preparation

5.1 prepare .flickr-api
put your api_key and api_secret in .flickr-api

for example:

```
api_key=f4ac3a179fbadedededeefefefe
api_secret=55c335e23434243f
```

5.2 authorize flickr user by below command

`python flickr-upload.py -a`

Follow the authorize url to permit access and input the access code to authorize.

#### 6. run line bot daemon

`python line-bot.py`


[github linebot-photobackup](https://github.com/maycehsu/linebot-photobackup)
