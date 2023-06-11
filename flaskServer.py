import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from apscheduler.schedulers.background import BackgroundScheduler
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import LabelEncoder, StandardScaler

app = Flask(__name__)

app.config['MYSQL_HOST'] = '3.34.148.235'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Iot1234!'
app.config['MYSQL_DB'] = 'Iot'
app.config['MYSQL_DATABASE_CONNECT'] = True

mysql = MySQL(app)
scheduler = BackgroundScheduler()
label_encoder = LabelEncoder()
std_scaler = StandardScaler()

@app.route('/')
def estimate_location():
    
    # data = request.get_json()
    # df_query = pd.DataFrame(data)
    df_dic = {
        'bssid' : ['94:64:24:a1:07:90', '94:64:24:9e:c0:a2', '32:cd:a7:bf:19:1a'],
        'rssi' : [-58, -50, -62]
    }
    df_query = pd.DataFrame(df_dic)
    
    conn = mysql.connection
    cursor = conn.cursor()
    query = "SELECT rssi, bssid, place FROM wifi WHERE bssid IN ('{}')".format("', '".join(df_query['bssid']))
    cursor.execute(query)
    result = cursor.fetchall()
    
    df_wifi = pd.DataFrame(result, columns=['rssi', 'bssid', 'place'])
    
    # print(df_query)
    # print(df_wifi)
    
    df_query['bssid'] = [int(x.replace(":", "")[-12:], 16) for x in df_query['bssid']]
    df_wifi['bssid'] = [int(x.replace(":", "")[-12:], 16) for x in df_wifi['bssid']]
    
    distances = euclidean_distances(df_query[['rssi', 'bssid']], df_wifi[['rssi', 'bssid']])
    
    closest_index = np.argmin(distances)
    closest_data = df_wifi.iloc[closest_index]
    
    if closest_data is not None:
        location = closest_data['place']
        return jsonify({'location': location})
    else:
        return jsonify({'message': 'Location not found'})

if __name__ == '__main__':
    app.run()
