from flask import Flask, render_template, request, session, copy_current_request_context
from vsearch import search4letters
from dbcontextmanager import UseDatabase, ConnectionError, CredentialsError, SQLError
from checker_decorator import check_logged_in
from threading import Thread

app = Flask(__name__)

app.secret_key = 'YouWillNeverGuess'

app.config['dbconfig'] = {
    'host': '127.0.0.1',
    'user': 'vsearch',
    'password': 'vsearchpass',
    'database': 'vsearchlogDB',
}


def log_read() -> list:
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            fetch_all = (
                "SELECT phrase, letters, results, browser_string, ip, ts FROM log")
            cursor.execute(fetch_all)
            print('db_read')
            return cursor.fetchall()
    except ConnectionError as err:
        print('Is your database switched on? Error: ', str(err))
    except CredentialsError as err:
        print('User-id/Password issues. Error: ', str(err))
    except SQLError as err:
        print('Is your query correct? Error:', str(err))
    except Exception as err:
        print('Something went wrong: ', str(err))
    return 'Error'


@ app.route('/search', methods=['POST'])
def do_search() -> 'html':
    @copy_current_request_context
    def log_write(request: 'flask_request', result: str) -> None:
        try:
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
        except ConnectionError as err:
            print('Is your database switched on? Error: ', str(err))
        except CredentialsError as err:
            print('User-id/Password issues. Error: ', str(err))
        except SQLError as err:
            print('Is your query correct? Error:', str(err))
        except Exception as err:
            print('Logging failed with this error: ', str(err))
        return 'Error'

    title = 'Here are you results'
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))

    concurrency_log_write = Thread(target=log_write, args=(request, results))
    concurrency_log_write.start()

    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results)


@ app.route('/viewlog')
@check_logged_in
def view_log() -> 'html':
    title = 'View Log'
    row_titles = ('Phrase', 'Letters',
                  'Result', 'User Agent', 'IP', 'Timestamp')
    content = log_read()
    return render_template('viewlog.html',
                           the_title=title,
                           the_row_titles=row_titles,
                           the_data=content)


@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    title = 'Login page'
    message = 'You are now logged in'
    return render_template('auth.html',
                           the_title=title,
                           the_message=message)


@app.route('/logout')
@check_logged_in
def do_logout() -> str:
    session.pop('logged_in')
    title = 'Logout page'
    message = 'You are loggout'
    return render_template('auth.html',
                           the_title=title,
                           the_message=message)


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html', the_title='Welcome to search4letters on the web!')


if __name__ == '__main__':
    app.run(debug=True)
