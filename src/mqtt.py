import network, asyncio
from time import sleep
from umqtt.simple import MQTTClient
import ujson as json
import micropython, gc, time



#--------------class Connection--------------#
class Connection:
    def __init__(self, ssid, password, broker_ip):
        self.ssid = ssid
        self.password = password
        self.mqtt_client = MQTTClient("", broker_ip, port=1883)
        self.mqtt_client.set_callback(self.callback)
        self.mqtt_status = "off"
        self.wlan_status = "off"
        self.response_received = False
        self.data_received = None
        #print(self.mqtt_client)
        
        self.hr = 0
        self.ppi = 0
        self.rmssd = 0
        self.sdnn = 0
        
    def wlan_connection(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        try:   
            wlan.connect(self.ssid, self.password)
            if wlan.isconnected():
                self.wlan_status = "on"
                print("WLAN connection successful")
            
        except Exception as e:
            print("Failed to connect WiFi",e)
        
        
    
    def mqtt_connection(self):
        print("Connecting MQTT...")
        try:
            self.mqtt_client.connect(clean_session = True)
            self.mqtt_status = "on"
            print("MQTT connection successful", self.mqtt_status)
              
        except Exception as error:
            print("Failed to connect MQTT:", error)
        gc.collect()
        time.sleep(1)

    def connect(self, oled):
        # Connect to WLAN
        self.wlan_connection(oled)
        sleep(1)
        # Connect to MQTT
        self.mqtt_connection(oled)


    def publish_mqtt(self, topic, message):
        self.response_received = False
        try:
            #message_bytes = json.dumps(message).encode('utf-8')
            self.mqtt_client.publish(topic, message)
            print("Finished publishing", topic)   
            return 0
        except Exception as e:
            print("Error publishing",e)
    
    def callback(self, topic, msg):
        print("Received message on topic:", topic.decode("utf-8"))
        #print("Message: ", msg.decode("utf-8"))
        
        try:
            response = json.loads(msg)
            self.hr = int(response['data']['analysis']['mean_hr_bpm'])
            self.ppi = int(response['data']['analysis']['mean_rr_ms'])
            self.rmssd = int(response['data']['analysis']['rmssd_ms'])
            self.sdnn = int(response['data']['analysis']['sdnn_ms'])
            self.pns = round(response['data']['analysis']['pns_index'],3)
            self.sns = round(response['data']['analysis']['sns_index'],3)
            self.data_received = {
                "id": response.get("id"),
                "mean_hr": f"{response['data']['analysis']['mean_hr_bpm']:.2f}"
            }
            self.response_received = True
            
        except ValueError as ve:
            print("Invalid response", ve)
        except KeyError as ke:
            print("Missing key in JSON", ke)
    
        
    async def subscribe_mqtt(self,pub_topic,message):
        print("Start subscribing...")

        await self.mqtt_client.subscribe("kubios-response")
        print(f"[mqtt] message: {message}")
        self.publish_mqtt(pub_topic,message)
        
        while self.response_received != True:
            self.mqtt_client.check_msg()
            await asyncio.sleep(1)
            
    def return_result(self):
        hr = self.hr
        ppi = self.ppi
        rmssd = self.rmssd
        sdnn = self.sdnn
        return hr,ppi,rmssd, sdnn
    
    async def main(self,topic, message):
        """
        retry_count = 2
        while self.mqtt_status == "off":
            try:
                mqtt_client.connect(clean_session=True)
                print("Connected MQTT")
                mqtt_connection = "on"
            except Exception as error:
                print("Failed to connect MQTT:", error)
                gc.collect()
                print(f"Retrying in {retry_count} seconds")
                await asyncio.sleep(retry_count)
        """
        
        
        if self.mqtt_status == "on":
            self.response_received = False
            listener = await asyncio.create_task(self.subscribe_mqtt(topic,message))
            await asyncio.sleep(2)
            print("Received data:", self.data_received)
            
