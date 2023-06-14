import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import LabelEncoder, StandardScaler
app = Flask(__name__)

scheduler = BackgroundScheduler()
label_encoder = LabelEncoder()
std_scaler = StandardScaler()

df = pd.read_csv('/Users/jangminseong/Downloads/data (2).csv')

bssid_list = []
rssi_list = []
df_POST = pd.DataFrame(columns=['bssid', 'rssi'])

@app.route('/')
def home():
    return 'HI'

@app.route('/flask', methods = ['GET', 'POST'])
def estimate_location():
    if request.method == 'POST':        
        data = request.get_json()
        print("Data get successfully ! ")
        
        for i in data:
            bssid_list.append(i["bssid"])
            rssi_list.append(i["rssi"])
        df_POST = pd.DataFrame({
                                'bssid' : list(bssid_list),
                                'rssi' : list(rssi_list)})
        return 'Data Frame has done'
    
    else:
        df_wifi = df[df['bssid'].isin(df_POST['bssid'])]
    
        print("mySQL Data read successfully")
        print(df_wifi)

        df_POST['bssid'] = [int(x.replace(":", "")[-12:], 16) for x in df_POST['bssid']]
        df_wifi['bssid'] = [int(x.replace(":", "")[-12:], 16) for x in df_wifi['bssid']]

        distances = euclidean_distances(df_POST[['rssi', 'bssid']], df_wifi[['rssi', 'bssid']])

        closest_index = np.argmin(distances)
        closest_data = df_wifi.iloc[closest_index]

        if closest_data is not None:
            location = closest_data['place']
            print("Successfully get location")
            return jsonify({location})
        else:
            return jsonify({'NaN'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)