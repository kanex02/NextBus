from flask import render_template, request
from realtime import nextBus
from app import app

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('nextbus.html')

@app.route('/search')
def search():
    query = request.args.get('jsdata')

    data = nextBus(query)

    return render_template('buses.html', stop=data[0], buses=data[1])