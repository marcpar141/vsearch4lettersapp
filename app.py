from flask import Flask, render_template, request, escape, session, copy_current_request_context
from vsearch import search4letters

from DBcm import UseDatabase, ConnectionError, CredentialError, SQLError
from checker import check_loggen_in

from threading import Thread

app = Flask(__name__)

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'vsearchpasswd',
                          'database': 'vsearchlogDB'}

app.secret_key = 'YouWillNeverGuess'


@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'Teraz jesteś zalogowany'


@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'Teraz jesteś wylogowany'


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title='Witamy na stronie internetowej search4letters!')


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        try:
            with UseDatabase(app.config['dbconfig']) as cursor:

                _SQL = """insert into log
                        (phrase, letters, ip, browser_string, results)
                        values
                        (%s, %s, %s, %s, %s)"""

                cursor.execute(_SQL, (req.form['phrase'],
                                      req.form['letters'],
                                      req.remote_addr,
                                      req.user_agent.browser,
                                      res,))
        except ConnectionError as err:
            print('Is your database turn on? Error: ', str(err))
        except CredentialError as err:
            print('Wrong login or password. Error: ', str(err))
        except SQLError as err:
            print('Is your request correct? Error: ', str(err))

    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Oto Twoje wyniki:'
    results = str(search4letters(phrase, letters))
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print('Logowanie nie powiodło się; wystąpił błąd: ', str(err))
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results, )


@app.route('/viewlog')
@check_loggen_in
def view_the_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:

            _SQL = """select phrase, letters, ip, browser_string, results
                from log"""

            cursor.execute(_SQL)
            contents = cursor.fetchall()

            titles = ('Fraza', 'litery', 'Adres klienta', 'Agent użytkownika', 'Wyniki')
            return render_template('viewlog.html',
                                   the_title='Widok logu',
                                   the_row_titles=titles,
                                   the_data=contents)
    except ConnectionError as err:
        print('Is your database turn on? Error: ', str(err))
    except CredentialError as err:
        print('Wrong login or password. Error: ', str(err))
    except SQLError as err:
        print('Is your request correct? Error: ', str(err))


app.secret_key = 'NigdyNieZgadnieszMojegoHasła'

if __name__ == '__main__':
    app.run(debug=True)
