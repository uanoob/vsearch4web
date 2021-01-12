from flask import Flask, render_template, request
from vsearch import search4letters
from dbcontextmanager import UseDatabase

app = Flask(__name__)

app.config['dbconfig'] = {
    'host': '127.0.0.1',
    'user': 'vsearch',
    'password': 'vsearchpass',
    'database': 'vsearchlogDB',
}


def log_write(request: 'flask_request', result: str) -> None:
    with UseDatabase(app.config['dbconfig']) as cursor:
        add_row = (
            "INSERT INTO log (phrase, letters, ip, browser_string, results) VALUES (%s, %s, %s, %s, %s)")
        cursor.execute(
            add_row,
            (request.form['phrase'],
             request.form['letters'],
             request.remote_addr,
             request.user_agent.browser,
             result)
        )
        print('db_write')


def log_read() -> list:
    with UseDatabase(app.config['dbconfig']) as cursor:
        fetch_all = (
            "SELECT phrase, letters, results, browser_string, ip, ts FROM log")
        cursor.execute(fetch_all)
        print('db_read')
        return cursor.fetchall()


@ app.route('/search', methods=['POST'])
def do_search() -> 'html':
    title = 'Here are you results'
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))
    log_write(request, results)
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results)


@ app.route('/viewlog')
def view_log() -> 'html':
    title = 'View Log'
    row_titles = ('Phrase', 'Letters',
                  'Result', 'User Agent', 'IP', 'Timestamp')
    content = log_read()
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
