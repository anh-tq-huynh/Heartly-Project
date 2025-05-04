import math, array, time
from filefifo import Filefifo
filename='xyz.txt'
fifo = Filefifo(10, name=filename)
class HRVAnalysis:
    def __init__(self):
        self.fifo=fifo
        self.samples = []
        self.peaks = []
        self.PPI = []
        self.data = []
        self.meanPPI_value = 0
        self.SDSD_value = 0
        self.SDNN_value = 0
        #self.samples=samples
        #self.meanPPI_value = 0
        #self.SDSD_value = 0
        #self.SDNN_value = 0

    def reading(self):
        self.samples = []
        for _ in range(20):
            self.samples.append(fifo.get())
            time.sleep(0.001)
        return self.samples

    def find_peaks(self):
        average = round(sum(self.samples) / len(self.samples))
        threshold = average + ((max(self.samples) - min(self.samples)) / 2)
        for i in range(len(self.samples) - 1):
            if self.samples[i] < threshold and self.samples[i + 1] >= threshold:
                self.peaks.append(i + 1)
        return self.peaks

    def calculate_ppi(self):
        self.PPI = []
        for i in range(len(self.peaks) - 1):
            ppi = (self.peaks[i + 1] - self.peaks[i]) * 4
            if 300 < ppi < 2000:
                self.PPI.append(ppi)
        self.data = self.PPI  # use PPI as data for other calculations
        return self.PPI

    def meanPPI(self):
        if not self.PPI:
            print("warning: PPI data is empty.")
            return 0
        self.meanPPI_value = sum(self.PPI) / len(self.PPI)
        return round(self.meanPPI_value)

    def meanHR(self):
        if self.meanPPI_value == 0:
            self.meanPPI()
        mean_hr = 60000 / self.meanPPI_value
        return round(mean_hr)

    def SDNN(self):
        mean_ppi = self.meanPPI()
        variance = sum((x - mean_ppi) ** 2 for x in self.data) / (len(self.data) - 1)
        self.SDNN_value = math.sqrt(variance)
        return round(self.SDNN_value)

    def RMSSD(self):
        diffs = [(self.data[i + 1] - self.data[i]) ** 2 for i in range(len(self.data) - 1)]
        rmssd = math.sqrt(sum(diffs) / (len(self.data) - 1))
        return round(rmssd)

    def SDSD(self):
        pp_diff = [self.data[i + 1] - self.data[i] for i in range(len(self.data) - 1)]
        first = sum([x ** 2 for x in pp_diff]) / (len(pp_diff) - 1)
        second = (sum(pp_diff) / len(pp_diff)) ** 2
        self.SDSD_value = math.sqrt(first - second)
        return round(self.SDSD_value)

    def SD1(self):
        if self.SDSD_value == 0:
            self.SDSD()
        sd1 = math.sqrt((self.SDSD_value ** 2) / 2)
        return round(sd1)

    def SD2(self):
        if self.SDNN_value == 0:
            self.SDNN()
        if self.SDSD_value == 0:
            self.SDSD()
        sd2 = math.sqrt((2 * (self.SDNN_value ** 2)) - ((self.SDSD_value ** 2) / 2))
        return round(sd2)

#samples = [
 #   828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816,
#    800, 812, 812, 812, 756, 820, 812, 800
#]

hrv = HRVAnalysis()
samples = hrv.reading()
peaks = hrv.find_peaks()
ppi = hrv.calculate_ppi()
mean_ppi = hrv.meanPPI()
mean_hr = hrv.meanHR()
sdnn = hrv.SDNN()
rmssd = hrv.RMSSD()
sdsd = hrv.SDSD()
sd1 = hrv.SD1()
sd2 = hrv.SD2()

print('ppi=',mean_ppi)
print('hr=',mean_hr)
print('sdnn=',sdnn)
print('rmssd',rmssd)
print('sdsd=',sdsd)
print('sd1=',sd1)

