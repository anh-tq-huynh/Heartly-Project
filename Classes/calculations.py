import math
import time
from filefifo import Filefifo

class HRVAnalysis:
    def __init__(self, samples):
        self.samples = samples
        self.peaks = []
        self.PPI = []
        self.data = []
        self.meanPPI_value = 0
        self.SDSD_value = 0
        self.SDNN_value = 0
        
    def find_threshold(self, data):
        maximum = max(data)
        minimum = min(data)
        

    def find_peaks(self):
        self.peaks = []
        if len(self.samples) == 0:
            print("Warning: No samples to process.")
            return self.peaks
        
        else:
            
            #Find threshold
            find_threshold = []
            maximum = 0
            minimum = 0
            for value in self.samples[:-500]:
                find_threshold.append(value)
            maximum = max(find_threshold)
            minimum = min(find_threshold)
            print(maximum)
            print(minimum)
            threshold = (maximum + minimum)/2
            print("threshold",threshold)
            
            #initiate needed variables
            prev_value = 0
            pass_threshold = True #to filter out the small peaks in between
            
            #Go through the sample
            for i, value in enumerate(self.samples):
                current_value = value
                current_dif = current_value - prev_value
                #Check direction: upward or downward
                if current_dif > 0:
                    upward = True
                    #print("upwards")
                if current_dif< 0:
                    if upward:
                        #print("downwards")
                        if pass_threshold:
                            upward = False
                            pass_threshold = False
                            #print("passed threshold")
                            if current_value > threshold:
                                peak_no = i+1
                                self.peaks.append(i)
                if current_value < threshold:
                    pass_threshold = True
                prev_value = current_value
            
        
        

    def calculate_ppi(self):
        self.PPI = []
        for i in range(len(self.peaks) - 1):
            ppi = (self.peaks[i + 1] - self.peaks[i]) * 4  # Adjust based on sampling rate
            if 300 < ppi < 2000:  # Valid PPI range
                self.PPI.append(ppi)
        self.data = self.PPI
        return self.data

    def meanPPI(self):
        if not self.PPI:
            print("Warning: PPI data is empty, returning 0 for meanPPI.")
            return 0
        self.meanPPI_value = sum(self.PPI) / len(self.PPI)
        return self.meanPPI_value

    def meanHR(self):
        mean_ppi = self.meanPPI()
        if mean_ppi == 0:
            print("Warning: Cannot calculate HR, meanPPI is zero.")
            return 0
        mean_hr = 60000 / mean_ppi  # Convert PPI to HR
        return mean_hr

    def SDNN(self):
        if not self.PPI:
            print("Warning: PPI data is empty, cannot calculate SDNN.")
            return 0
        mean_ppi = self.meanPPI()
        variance = sum((x - mean_ppi) ** 2 for x in self.PPI) / (len(self.PPI) - 1)
        self.SDNN_value = math.sqrt(variance)
        return self.SDNN_value

    def RMSSD(self):
        if len(self.PPI) <= 1:
            print("Warning: Insufficient PPI data to calculate RMSSD.")
            return 0
        diffs = [(self.PPI[i + 1] - self.PPI[i]) ** 2 for i in range(len(self.PPI) - 1)]
        rmssd = math.sqrt(sum(diffs) / len(diffs)-1)
        return rmssd

    def SDSD(self):
        if len(self.PPI) <= 1:
            print("Warning: Insufficient PPI data to calculate SDSD.")
            return 0
        pp_diff = [self.PPI[i + 1] - self.PPI[i] for i in range(len(self.PPI) - 1)]
        first = sum([x ** 2 for x in pp_diff]) / (len(pp_diff) - 1)
        second = (sum(pp_diff) / len(pp_diff)) ** 2
        self.SDSD_value = math.sqrt(first - second)
        return self.SDSD_value

    def SD1(self):
        sd1 = 0
        if self.SDSD_value > 0:
            sd1 = math.sqrt(self.SDSD_value ** 2 / 2)
        return round(sd1)

    def SD2(self):
        sd2 = 0
        if self.SDNN_value > 0 and self.SDSD_value > 0:
            sd2 = math.sqrt(2 * self.SDNN_value**2 - self.SDSD_value**2)
        return round(sd2)