from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def main():
    if False:  # TODO logged in<=>has session
        return render_template('main.html')
    else:
        return render_template('login_page.html')


@app.route('/hello')
def hello():
    return render_template('main.html')


if __name__ == '__main__':
    app.run()
