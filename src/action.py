###ACTIONS TO PERFORM###
from src.hardware import Display, Encoder, Sensor
from src.DisplayControl import DisplayControl
from src.mqtt import Connection
from src.history import History
from src.kubiosDataPrep import Kubios
from src.SensorDataSosFilter import finger_sensor
from src.calculations import HRVAnalysis
from src.graphing import draw_data
from src.buffer import RoundRobin
import time,gc, asyncio
import ujson as json

#--------------initiate variables--------------#
#SSID = "KME759_Group_2_2.4GHz"
#PASSWORD = "V@cineVoy@ge"
SSID = "abinader"
PASSWORD = "senhadobrunoetaysa1985"
#SSID = "Zyxel_09A1"
#ASSWORD = "RQAFDNPMRN"
BROKER_IP = "networkinggroup2.asuscomm.com"


class Action():
    def __init__(self):
        self.display = DisplayControl()
        self.data = None
        self.state = 1
        self.connection = Connection(SSID, PASSWORD, BROKER_IP)
        self.history = History()
        self.kubios = Kubios()
        self.selection = None
        self.hrv = HRVAnalysis()
        """
            self.state list:
            1 - Welcome screen
            2 - Establish WiFi connection
            3 - Main menu
            4 - HR
            5 - HRV
            6 - Kubios
            7 - History
        """
    def update_state(self):
        self.state = self.display.state
    
        
    
    def reset_state(self):
        self.state = None
        
    def attempt_connection(self):
        #Connect WiFi
        self.display.print_text("Connect WiFi")
        time.sleep(0.5)
        while self.connection.wlan_status == "off":
            gc.collect()
            self.display.connecting()
            self.connection.wlan_connection()
            time.sleep(0.5)
        self.display.print_text("Successful ^.^ ")
        time.sleep(0.5)
    def attempt_mqtt(self):
        #Connect MQTT
        self.display.print_text("Connect MQTT")
        self.display.connecting()
        self.connection.mqtt_connection()
        while self.connection.mqtt_status == "off":
            time.sleep(0.05)
        self.display.print_text("Successful ^.^ ")
        time.sleep(0.5)

    def history_run(self):
        history_list = self.history.list_from_history()
        self.display.execute_history(history_list)
        self.selection = self.display.selection
        dataset = self.history.get_from_history(self.selection)
        self.display.print_selected_history(dataset)
        self.update_state()
        
    def hrv_run(self):
        hrv = finger_sensor(40000,self.display.oled, self.display.rotary)
        self.history.create_history(int(hrv.meanHR_value), int(hrv.meanPPI_value),int(hrv.RMSSD_value), int(hrv.SDNN_value), round(hrv.PNS_value,3), round(hrv.SNS_value,3))
        self.history.save_to_history()
        try:
            filename = "history.json"
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(e)
        self.display.print_selected_history(existing_data[-1])
        self.update_state()
        
        
    async def kubios_main_flow(self,topic,data):
        self.kubios.add_ppi(data)
        dataset = self.kubios.create_data()
        print(f"dataset: {dataset}")
        #subscribe and publish to kubios
        self.connection.main(topic, dataset)
        hr, ppi, rmssd, sdnn = self.connection.return_result()
        self.history.create_history(hr,ppi,rmssd,sdnn)
        self.history.save_to_history()
    

    def execute_on_state(self):
        if self.state == 1: #Welcome
            self.display.welcome()
            self.state = 2
            time.sleep(0.5)

        elif self.state == 2: #Connect to WiFi
            self.attempt_connection()
            self.state = 3
            time.sleep(0.5)

        elif self.state == 3: #Main menu
            menu = ["HR", "HRV", "Kubios","History"]
            self.display.execute_menu(menu)
            self.update_state()
            time.sleep(0.5)
         
        elif self.state == 4: #HR
            hrv = finger_sensor(5000,self.display.oled, self.display.rotary)
            self.state = 3
            
        elif self.state == 5: #HRV
            self.hrv_run()
            
        elif self.state == 6: #Kubios
            self.attempt_mqtt()
            hrv = finger_sensor(40000,self.display.oled, self.display.rotary)
            sample = hrv.PPIs
            print(f"sample: {sample}")
            topic = "kubios-request"
            self.kubios_main_flow(topic,sample)
            self.state = 3
        elif self.state == 7:
            self.history_run()
