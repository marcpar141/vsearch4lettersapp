from flask import Flask, render_template, request, escape, session
from vsearch import search4letters
import mysql.connector
from checker import check_loggen_in

app = Flask(__name__)

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'vsearchpasswd',
                          'database': 'vsearchlogDB'}


def log_request(req: 'flask_request', res: str) -> None:
    conn = mysql.connector.connect(**app.config['dbconfig'])
    cursor = conn.cursor()

    _SQL = """insert into log
                (phrase, letters, ip, browser_string, results)
                values
                (%s, %s, %s, %s, %s)"""

    cursor.execute(_SQL, (req.form['phrase'],
                          req.form['letters'],
                          req.remote_addr,
                          req.user_agent.browser,
                          res,))

    conn.commit()
    cursor.close()
    conn.close()


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title='Witamy na stronie internetowej search4letters!')


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Oto Twoje wyniki:'
    results = str(search4letters(phrase, letters))
    log_request(request, results)
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results, )


# @app.route('/login')
# def do_login() -> 'html':
#     return render_template('login.html',
#                            the_title='Zaloguj się!')
#
#
# @app.route('/verification', methods=['POST'])
# def do_verification() -> 'html':
#     administrator = {'user': ' Marceli',
#                      'password': '1234'}
#     verification = {'user': request.form['login'],
#                     'password': request.form['password']}
#     if administrator.__eq__(verification):
#         session['logged_in'] = True
#         return 'Teraz jesteś zalogowany'
#     return 'Nie jesteś zalogowany'


@app.route('/viewlog')
def view_the_log() -> 'html':
    conn = mysql.connector.connect(**app.config['dbconfig'])
    cursor = conn.cursor()

    _SQL = """select phrase, letters, ip, browser_string, results
        from log"""

    cursor.execute(_SQL)
    contents = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    titles = ('Fraza', 'litery', 'Adres klienta', 'Agent użytkownika', 'Wyniki')
    return render_template('viewlog.html',
                           the_title='Widok logu',
                           the_row_titles=titles,
                           the_data=contents)


if __name__ == '__main__':
    app.run(debug=True)
