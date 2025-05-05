###CONVERT DATA INTO THE CORRECT FORMAT FOR KUBIOS###
import ujson as json

#----------class kubios-----------------------------#
class Kubios:
    def __init__(self):
        self.ppi_list = None
        self.id = 1
        
    def add_ppi(self, ppi):
        self.ppi_list = ppi
        
        return self.ppi_list
    
    def create_data(self):
        if self.ppi_list != None:
            dataset = {
                "id": self.id,
                "type": "RRI",
                "data": self.ppi_list,
                "analysis": { "type": "readiness" }}
            self.id += 1
            json_dataset = json.dumps(dataset)
        return json_dataset