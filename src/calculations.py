import math
import time

class HRVAnalysis:
    def __init__(self):
        self.samples = None
        self.peaks = []
        self.PPIs = []
        self.meanPPI_value = 0
        self.meanHR_value = 0
        self.SDSD_value = 0
        self.SDNN_value = 0
        self.RMSSD_value = 0
        
    def add_sample(self, data):
        self.samples = data #acumulate new samples

    def find_peaks(self):
        self.peaks.clear()
        
        if len(self.samples) < 2:
            print("Warning: No samples to process.")
            return self.peaks
        
        # Finds the midpoint between the global max and min of the data.
        threshold = (max(self.samples) + min(self.samples))/2
        
        # Start with the first sample.
        previous = self.samples[0]
        
        # Tracks whether the signal has been rising (i.e. the last step was an “up”).
        upward = False
        # Prevents you from marking multiple peaks in one excursion above threshold. It only goes True again once you’ve dipped below the threshold.
        passed = False
        
        for i in range(1, len(self.samples)):
            current = self.samples[i]
            if current - previous > 0:
                # Going upwards.
                upward = True
            else:
                # Going downwards.
                if upward and passed and current > threshold:
                    #record index of the peak
                    self.peaks.append(i)
                    passed = False
                upward = False
                
            if current < threshold:
                passed = True
            previous = current
            
        return self.peaks

    # Peak-to-peak interval (in ms)    
    def calculate_ppi(self, sampling_interval_ms=4):
        self.PPIs.clear()
        for i in range(len(self.peaks) - 1):
            ppi = (self.peaks[i + 1] - self.peaks[i]) * sampling_interval_ms  # Adjust based on sampling rate
            if 300 < ppi < 2000:  # Valid PPI range
                self.PPIs.append(ppi)
        return self.PPIs

    def meanPPI(self):
        if not self.PPIs:
            print("Warning: PPI data is empty, returning 0 for meanPPI.")
            return 0
        self.meanPPI_value = sum(self.PPIs) / len(self.PPIs)
        return self.meanPPI_value

    def meanHR(self):
        if self.meanPPI_value == 0:
            print("Warning: Cannot calculate HR, meanPPI is zero.")
            return 0
        self.meanHR_value = 60000 / self.meanPPI_value  # Convert PPI to HR
        return self.meanHR_value

    # def SDNN(self):
    #     if len(self.PPIs) < 2:
    #         print("Warning: PPI data is empty, cannot calculate SDNN.")
    #         return 0
    #     mean_ppi = self.meanPPI()
    #     variance = sum((x - mean_ppi) ** 2 for x in self.PPIs) / (len(self.PPIs) - 1)
    #     self.SDNN_value = math.sqrt(variance)
    #     return self.SDNN_value
    
    # def RMSSD(self):
    #     if len(self.PPIs) < 2:
    #         print("Warning: Insufficient PPI data to calculate RMSSD.")
    #         return 0
    #     diffs = [(self.PPIs[i + 1] - self.PPIs[i]) for i in range(len(self.PPIs) - 1)]
    #     self.RMSSD_value = math.sqrt(sum(diffs)/len(diffs))
    #     return self.RMSSD_value
                 
    # def SDSD(self):
    #     if len(self.PPIs) < 2:
    #         print("Warning: Insufficient PPI data to calculate SDSD.")
    #         return 0
    #     diffs = [self.PPIs[i + 1] - self.PPIs[i] for i in range(len(self.PPIs) - 1)]
    #     mean_diffs = sum(diffs) / len(diffs)
    #     variance_diffs = sum((d - mean_diffs)**2 for d in diffs)/(len(diffs)-1)
    #     self.SDSD_value = math.sqrt(variance_diffs)
    #     return self.SDSD_value

    # def SD1(self):
    #     sd1 = math.sqrt(self.SDSD_value ** 2 / 2)
    #     return sd1
        
    # def SD2(self):
    #     sd2 = math.sqrt((2 * (self.SDNN_value ** 2)) - (self.SDSD_value ** 2 / 2))
    #     return sd2
        
    def calculate_all(self):
        self.find_peaks()
        self.calculate_ppi()
        self.meanPPI()
        self.meanHR()
        #self.SDNN()
        #self.SDSD()
        #self.RMSSD()