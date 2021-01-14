from flask import session, render_template
from functools import wraps


def check_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> str:
        if 'logged_in' in session:
            return func(*args, **kwargs)
        title = 'Oops! Something went wrong...'
        message = 'You are NOT logged in'
        return render_template('auth.html',
                               the_title=title,
                               the_message=message)
    return wrapper
