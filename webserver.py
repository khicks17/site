from aiohttp import web
import aiohttp_jinja2
from random import randint
import jinja2
import sqlite3
import secrets
import hashlib
import requests
import socket

#@aiohttp_jinja2.template('Title_page.html.jinja2')
async def title(request):
    response = aiohttp_jinja2.render_template('Title_page.html.jinja2', request, {})
    response.set_cookie('logged_in', 'yes')

    return response

@aiohttp_jinja2.template('hobbies.html.jinja2')
async def hobbies(request):
    return {
        "hobbies": ["waterskiing", "traveling", "hiking"]
        }

@aiohttp_jinja2.template('2.html.jinja2')
async def two(request):
    return {
        'show': 'westworld'
    }

@aiohttp_jinja2.template('3.html.jinja2')
async def three(request):
    return {}

@aiohttp_jinja2.template('login.html.jinja2')
async def show_login(request):

    raise web.HTTPFound('/')

async def logout(request):
    global logged_in_secret
    response = aiohttp_jinja2.render_template('login.html.jinja2', request, {})
    response.cookies['logged_in'] = ''
    logged_in_secret = "--invalid--"
    return response

async def login(request):
    data = await request.post()
    # check if username and password match an entry in the user table
    conn = sqlite3.connect('tweet_db.db')
    cursor = conn.cursor()

    cursor.execute("SELECT salt FROM users WHERE username=?", (data['username'],))
    result = cursor.fetchone()
    if result is None:
        raise web.HTTPFound('/login')
    salt = result[0]
    salted_password = data['password'] + salt
    hashed_password = hashlib.md5(salted_password.encode('ascii')).hexdigest()
    print("using salt: ", salt)
    print("Using hashed password: ", hashed_password)
    cursor.execute("SELECT COUNT(*) FROM users WHERE username=? AND password=?",
                   (data['username'], hashed_password))
    query_result = cursor.fetchone()

    user_exists = query_result[0]
    if user_exists == 0:  # no good, try again!
        raise web.HTTPFound('/login')

    # everything checks out, give them a cookie :)
    response = web.Response(text="congrats!",
                            status=302,
                            headers={'Location': "/"})
    # generate a new cookie value!
    logged_in_secret = secrets.token_hex(8)
    response.cookies['logged_in'] = logged_in_secret
    cursor.execute("UPDATE users SET cookie=? WHERE username=?", (logged_in_secret, data['username']))
    conn.commit()
    # store the cookie in our own database

    conn.close()

    return response

@aiohttp_jinja2.template('login.html.jinja2')
async def show_login(request):
    return {}


@aiohttp_jinja2.template('tweets.html.jinja2')
async def tweets(request):
    conn = sqlite3.connect('table.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    print(results)
    return {"tweets": results}

async def add_tweet(request):
    ip = request.remote
    print(ip)
    api = 'b098163670077c784be931441c9a96d8'
    resp = requests.get("http://api.ipstack.com/%s?access_key=%s" % (ip, api))
    result = resp.json()
    city = result["city"]
    data = await request.post()
    content = data['content']
    conn = sqlite3.connect("table.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tweets (content, likes, location) VALUES (?,0,?)", (content,city))
    conn.commit()
    print("The user tweeted %s" % content)
    raise web.HTTPFound('/tweets.html')

async def like(request):
    conn = sqlite3.connect('table.db')
    cursor = conn.cursor()
    tweet_id = request.query['id']
    cursor.execute("SELECT likes FROM tweets WHERE id=?", tweet_id)
    like_count = cursor.fetchone()[0]
    cursor.execute("UPDATE tweets SET likes=%d WHERE id=?", (like_count +1, tweet_id))
    conn.commit()
    print(request.query['id'])
    raise web.HTTPFound('/tweets.html')

async def like_json(request):
    conn = sqlite3.connect('table.db')
    cursor = conn.cursor()
    tweet_id = request.query['id']
    # get the current like count
    cursor.execute("SELECT likes FROM tweets WHERE id=?", (tweet_id,))
    like_count = cursor.fetchone()[0]
    # add 1 to the like count and save it
    cursor.execute("UPDATE tweets SET likes=? WHERE id=?", (like_count + 1, tweet_id))
    conn.commit()
    conn.close()
    return web.json_response(data={"like_count": like_count+1})

async def location(request):
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    api = 'b098163670077c784be931441c9a96d8'
    resp = requests.get("http://api.ipstack.com/%s?access_key=%s" % (ip,api))
    result = resp.json()
    location = result["city"]
    conn = sqlite3.connect('table.db')
    cursor = conn.cursor()
    tweet_id = request.query['id']
    cursor.execute("SELECT location FROM tweets WHERE id=?", tweet_id)
    cursor.execute("UPDATE tweets SET location=%s WHERE id=?", (location, tweet_id))
    conn.commit()
    print(request.query['location'])
    raise web.HTTPFound('/tweets.html')

def main():
    app = web.Application()

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))

    app.add_routes([web.get('/',title),
                    web.get('/login', show_login),
                    web.get('/logout', logout),
                    web.post('/login', login),
                    web.get('/hobbies.html', hobbies),
                    web.get('/2.html', two),
                    web.get('/3.html', three),
                    web.get('/tweets.html', tweets),
                    web.get('/like',like),
                    web.get('/like.json', like_json),
                    web.get('/location', location),
                    web.post('/tweets', add_tweet),
                    web.static('/static','static',show_index=True)])
    print("Welcome to Webserver 2.1")

    web.run_app(app, host="127.0.0.1", port=3000)

main()

