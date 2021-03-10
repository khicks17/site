
from aiohttp import web
import aiohttp_jinja2
import jinja2
import sqlite3

@aiohttp_jinja2.template('Title_page.html.jinja2')
async def title(request):
    print("actually running")
    return {}

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
    conn.close()
    return {"tweets": results}

async def add_tweet(request):
    data = await request.post()
    content = data['content']
    query = "INSERT INTO tweets (content,likes) VALUES (\"%s\",0)" % content
    print("QUERY: %s" % query)
    conn = sqlite3.connect("table.db")
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("The user tweeted %s" % content)
    raise web.HTTPFound('/')

async def like(request):
    conn = sqlite3.connect('table.db')
    cursor = conn.cursor()
    tweet_id = request.query[id]
    cursor.execute("SELECT likes FROM tweets WHERE id=%s" % tweet_id)
    like_count = cursor.fetchone()[0]
    cursor.execute("UPDATE tweets SET likes=%d WHERE id=%s" % (like_count +1, tweet_id))
    print(request.query['id'])
    raise web.HTTPFound('/')


def main():

    app = web.Application()

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))

    app.add_routes([web.get('/home.html', title),
                    web.get('/',title),
                    web.get('/hobbies.html.jinja2', hobbies),
                    web.get('/2.html.jinja2', two),
                    web.get('/3.html.jinja2', three),
                    web.get('/tweets.html.jinja2', tweets),
                    web.get('/like',like),
                    web.post('/tweet', add_tweet),
                    web.static('/static','static',show_index=True)])
    print("Welcome to Webserver 2.1")

    web.run_app(app, host="127.0.0.1", port=3001)

main()