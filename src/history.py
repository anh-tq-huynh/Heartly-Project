from src.liveTime import timestamp
from src.mqtt import Connection
import time
import ujson as json

class History():
    id = 1
    def __init__(self):
        """
        self.ppi = data_feed.ppi
        self.meanPPI_value = data_feed.meanPPI_value
        self.SDSD_value = data_feed.SDSD_value
        self.SDNN_value = data_feed.SDNN_value
        self.meanHR_value = data_feed.meanHR_value
        self.RMSSD = data_feed.RMSSD
        self.history = None
        """
        
    def create_history(self,hr,mean_ppi,rmssd,sdnn):
        """self.history = {
            "Mean HR": self.meanHR_value,
            "Mean PPI": self.meanPPI_value,
            "RMSSD": self.RMSSD,
            "SDNN": self.SDNN_value,
            }"""
        self.history = {
            "id": History.id,
            "Time": timestamp(),
            "Mean HR": hr,
            "Mean PPI": mean_ppi,
            "RMSSD": rmssd,
            "SDNN": sdnn,
            }
        History.id += 1
            
    def save_to_history(self):
        filename = "history.json"
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(e)
            existing_data = []

        existing_data.append(self.history)

        with open(filename, 'w') as f:
            json.dump(existing_data, f)

        print(f"Your dictionary has been successfully added to '{filename}'.")
    
    def list_from_history(self):
        filename = "history.json"
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(e)
        history_list = []
        for i in range(len(existing_data)):
            history_list.append(f"Measurement {i +1}")
        return history_list
    
    def get_from_history(self,id):
        filename = "history.json"
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(e)
        
        dataset = existing_data[id-1]
        return dataset
        
"""      
oled.text('Mean HR: 75',0 , line_height * 1 - y)
oled.text('Mean PPI: 750', 0, line_height*2 - y)
oled.text('RMSSD: 23', 0, line_height*3 - y)
oled.text('SDNN: 22', 0, line_height*4 - y)
oled.text('SNS: 1.234', 0, line_height*5 - y)
oled.text('PNS: -1.234', 0, line_height*6 - y)

SSID = "Zyxel_09A1"
PASSWORD = "RQAFDNPMRN"
BROKER_IP = "networkinggroup2.asuscomm.com"
connection = Connection(SSID,PASSWORD,BROKER_IP)
while connection.wlan_status == "off":
    connection.wlan_connection()
    time.sleep(0.5)
history = History()
print(history.list_from_history())
print(history.get_from_history(2))
"""