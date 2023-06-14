import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import LabelEncoder, StandardScaler
from collections import Counter

app = Flask(__name__)

scheduler = BackgroundScheduler()
label_encoder = LabelEncoder()
std_scaler = StandardScaler()

df = pd.read_csv('/Users/jangminseong/Downloads/data (2).csv')

bssid_list = []
rssi_list = []
place_records = []
df_POST = pd.DataFrame(columns=['bssid', 'rssi'])

@app.route('/')
def home():
    return 'HI'

@app.route('/flask', methods = ['GET', 'POST'])
def estimate_location():
    print("민성아힘내")
    global df_POST
    
    if request.method == 'POST':
        data = request.get_json()
        print("Data get successfully ! ")
        
        
        bssid_list = []
        rssi_list = []
        
        for i in data:
            bssid_list.append(i["bssid"])
            rssi_list.append(i["rssi"])
        df_POST = pd.DataFrame({
                                'bssid' : list(bssid_list),
                                'rssi' : list(rssi_list)})
        
        # 안드로이드 rssi 읽은값 데이터프레임으로 출력
        print('Input from android')
        print(df_POST)
        
        location = "Data Frame"

        return jsonify({"location" : location})
    
    else:
        if df_POST.empty:
            return jsonify({'error' : 'No Data'})
        
        place_records = []
        for bssid in df_POST['bssid']:
            df_matched = df[df['bssid'] == bssid]
            rssi = df_POST[df_POST['bssid'] == bssid]['rssi'].values[0]
            distances = euclidean_distances([[rssi]], df_matched[['rssi']])
            closest_index = distances.argmin()
            closest_data = df_matched.iloc[closest_index]
            place = closest_data['place']
            place_records.append(place)
        
        counter = Counter(place_records)
        most_common = counter.most_common(1)
        location = most_common[0][0]
        
        # if df_POST.empty:
        #     return jsonify({'error' : 'No Data'})
        # df_wifi = df[df['bssid'].isin(df_POST['bssid'])]
    
        # print("mySQL Data read successfully")
        # print(df_wifi)

        # df_POST['bssid'] = [int(x.replace(":", "")[-12:], 16) for x in df_POST['bssid']]
        # df_wifi['bssid'] = [int(x.replace(":", "")[-12:], 16) for x in df_wifi['bssid']]

        # distances = euclidean_distances(df_POST[['rssi', 'bssid']], df_wifi[['rssi', 'bssid']])

        # closest_index = np.argmin(distances)
        # closest_data = df_wifi.iloc[closest_index]
        
        print("LOCATION")
        print(location)

        if closest_data is not None:
            print("Successfully get location")
            return jsonify({"location" : location})
        else:
            return jsonify({"location" :'NaN'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)