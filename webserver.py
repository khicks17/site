from aiohttp import web
import aiohttp_jinja2
import jinja2
import sqlite3
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

    app.add_routes([web.get('/home.html', title),
                    web.get('/',title),
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

    web.run_app(app, host="0.0.0.0", port=80)

main()

