from flask import Flask, render_template, request
import requests
import json
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.util.string import encode_utf8
from bokeh.embed import components

app = Flask(__name__)
global input_text

@app.route('/')
def index():
    input_text = ''
    months = ['04-2017', '05-2017','06-2017', '07-2017', '08-2017', '09-2017',
              '10-2017','11-2017','12-2017','01-2018','02-2018','03-2018','04-2018']
    return render_template('index.html',ticker=input_text, months=months)

@app.route('/plot', methods=['POST'])
def form_post_plot():
    input_text = request.form['ticker']
    month = request.form['months']
    try:
        features = request.form.getlist('features')
        if features==[]:
            features=['adj_close']
    except json.decoder.JSONDecodeError:
        features =['adj_close']         
    script, div = display_plot(input_text.upper(),features,month)
    return encode_utf8(render_template('plot.html', script=script, div=div))

def display_plot(tick_code, features, month_yr):
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
    #data = data_tick[data_tick['date']>'2017-03-30']
    data = data_tick[data_tick['date'].dt.strftime('%m-%Y') == month_yr]
    x = data['date']
    print (x.head())
    #output_file('templates/plot.html')
    p = figure(
            title= 'Stock chart for {} for the month of {}'.format(tick_code,month_yr),
            x_axis_label='Date',
            x_axis_type='datetime')
    
    colors=['red','blue','orange','green']
    feat_legend = {'open':'Opening', 
                   'close':'Closing',
                   'adj_open':'Adjusted Opening',
                   'adj_close':'Adjusted Closing'}
    for i, feature in enumerate(features):
        y = data[feature]
        print("y:  ", y)
        p.line(x,y,legend=feat_legend[feature],line_color=colors[i])
        print('Plotted feature: ', feature)
    # save(p)
    script, div = components(p)
    return script,div

if __name__ == '__main__':
    app.run(port=33507)
