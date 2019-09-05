from flask import Flask, render_template, request, redirect
import requests
import json
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.resources import CDN
from bokeh.embed import file_html

app = Flask(__name__)
global input_text

@app.route('/')
def index():
    input_text = ''
    return render_template('index.html',ticker=input_text)

@app.route('/plot', methods=['POST'])
def my_form_post():
    input_text = request.form['ticker']
    try:
        features = request.form.getlist('features')
        if features==[]:
            features=['adj_close']
    except json.decoder.JSONDecodeError:
        features =['adj_close']
        
    print(features)
    #tick_code = 
    display_plot(input_text.upper(),features)
    return render_template('plot.html')

def display_plot(tick_code, features):
    print(tick_code)
    URL = "https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json"
    PARAMS = {'ticker':tick_code,
              'api_key':'-7aCUwxHs3Pxvkz8mF3N'}
    resp = requests.get(url=URL,params=PARAMS)
#    if resp.status_code!=200:
#        return render_template('error.html',err_code= resp.status_code)
    json_data = json.loads(resp.text)
    data = json_data['datatable']['data']
    cols = [x['name'] for x in json_data['datatable']['columns']]
    data_tick = pd.DataFrame(data, columns=cols)
    data_tick['date']=pd.to_datetime(data_tick['date'], format='%Y-%m-%d')
    print('Dataframe shape:' , data_tick.shape)
    print('Datatype: ',data_tick.dtypes)
    
    data = data_tick[data_tick['date']>'2017-03-30']
    print(data.head())
    print(data.shape)
    x = data['date']
    output_file('templates/plot.html')
    p = figure(
            title= 'Plot for {}'.format(tick_code),
            x_axis_label='Date',
            x_axis_type='datetime')
    if len(features)==0:
        y = data['adj_close']
        p.line(x,y,legend='adj_close')
    colors=['red','blue','orange','green']
    for i, feature in enumerate(features):
        y = data[feature]
        p.line(x,y,legend=feature,line_color=colors[i])
    save(p)
#    html = file_html(plot, CDN, "my plot")


if __name__ == '__main__':
  app.run()
