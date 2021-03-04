# Webserver!

from aiohttp import web
import aiohttp_jinja2
import jinja2
import sqlite3

@aiohttp_jinja2.template('Title_page.html.jinja2')
async def title(request):
    conn = sqlite3.connect('table.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY likes DESC")
    results = cursor.fetchall()
    conn.close()
    return {"tweets": results}

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


def main():

    app = web.Application()

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))

    app.add_routes([web.get('/home.html', title),
                    web.get('/',title),
                    web.get('/hobbies.html.jinja2', hobbies),
                    web.get('/2.html.jinja2', two),
                    web.get('/3.html.jinja2', three),
                    web.static('/static','static',show_index=True)])
    print("Welcome to Webserver 1.0")
    web.run_app(app, host="0.0.0.0", port=80)


main()