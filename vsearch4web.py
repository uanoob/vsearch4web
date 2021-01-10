from flask import Flask, render_template, request
from vsearch import search4letters
from mysql import connector

app = Flask(__name__)

db_config = {
    'host': '127.0.0.1',
    'user': 'vsearch',
    'password': 'vsearchpass',
    'database': 'vsearchlogDB',
}


def db_connect() -> list:
    cnx = connector.connect(**db_config)
    cursor = cnx.cursor(buffered=True)
    print('db connected')
    return [cnx, cursor]


def db_disconnect(cnx, cursor) -> None:
    cursor.close()
    cnx.close()
    print('db disconnected')


def db_write(cursor, query, request, result) -> None:
    print('db_write')
    cursor.execute(
        query,
        (request.form['phrase'],
         request.form['letters'],
         request.remote_addr,
         request.user_agent.browser,
         result)
    )


def db_read(cursor, query) -> list:
    print('db_read')
    cursor.execute(query)
    return cursor.fetchall()


def log_request(request: 'flask_request', result: str) -> None:
    [cnx, cursor] = db_connect()

    add_row = (
        "INSERT INTO log (phrase, letters, ip, browser_string, results) VALUES (%s, %s, %s, %s, %s)")
    db_write(cursor, add_row, request, result)
    cnx.commit()
    db_disconnect(cnx, cursor)


@app.route('/search', methods=['POST'])
def do_search() -> 'html':
    title = 'Here are you results'
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))
    log_request(request, results)
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results)


@app.route('/viewlog')
def view_log() -> 'html':
    title = 'View Log'
    row_titles = ('ID', 'Timestamp', 'Phrase', 'Letters',
                  'IP', 'User Agent', 'Result')
    [cnx, cursor] = db_connect()
    fetch_all = ("SELECT * FROM log")
    content = db_read(cursor, fetch_all)
    db_disconnect(cnx, cursor)
    return render_template('viewlog.html',
                           the_title=title,
                           the_row_titles=row_titles,
                           the_data=content)


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html', the_title='Welcome to search4letters on the web!')


if __name__ == '__main__':
    app.run(debug=True)
