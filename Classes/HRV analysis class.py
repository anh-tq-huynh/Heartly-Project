class HRV_analysis:
	self.meanPPI=meanPPI
	self.data=data
	self.PPI=PPI
	self.SDSD_value=SDSD_value
	self.SDNN_value=SDNN_value
	self.peaks=peaks
	self.samples=samples
	self.peaks=[]
	
		
	def reading(self):
		list=[]
		for i in range(750):
			list.append(fifo.get())
			time.sleep(0.001)
		return list
	
	
	def peaks(self.samples):
		average=round(sum(self.samples)/len(self.samples))
		threshold= average + ((max(self.samples)-min(self.samples))/2)
		for i in samples:
			if self.samples[i] < threshold and self.samples[i+1] >= threshold:
				self.peaks.append(i+1)
		return self.peaks		
		
	
	def ppi(self.peaks):
        ppi_list = []
        for i in range(len(self.peaks)-1):
            ppi = (self.peaks[i+1]-self.peaks[i])*4
            if ppi > 300 and ppi < 2000:
                ppi_list.append(ppi)
    return ppi_list


    def meanPPI(self.data):
        sumPPI = 0 
        for i in self.data:
            sumPPI += i
        mean_ppi= sumPPI/len(self.data)
        return round(mean_ppi)


	def meanHR(self.meanPPI):
		mean_hr= 60000/self.meanPPI
		return round(hr_mean)


	def SDNN(self.data, self.mean_ppi):
		ppi_difference_sum = 0
		for i in self.data:
			ppi_difference_sum += (i-self.mean_ppi)**2
		sdnn = math.sqrt(ppi_difference_sum/(len(self.data)-1))
		return round(sdnn)


	def RMSSD(self.data):
		i = 0
		ppi_difference = 0
		while i < len(self.data)-1:
			ppi_difference += (self.data[i+1]-self.data[i])**2
			i +=1
		rmssd = math.sqrt((ppi_difference/(len(self.data)-1)))
		return round(rmssd)


	def SDSD(self.data):
		PP_array = array.array('l')
		i = 0
		first_value = 0
		second_value = 0
		while i < len(self.data)-1:
			PP_array.append(int(self.data[i+1])-int(self.data[i]))
			i += 1
		i = 0
		while i < len(PP_array)-1:
			first_value += float(PP_array[i]**2)
			second_value += float(PP_array[i])
			i += 1
		first = first_value/(len(PP_array)-1)
		second = (second_value/(len(PP_array)))**2
		sdsd= math.sqrt(first - second)
		return round(sdsd)


	def SD1(self.SDSD_value):
		sd1 = math.sqrt((self.SDSD_value**2)/2)
		return round(sd1)


	def SD2(self.SDNN_value, self.SDSD_value):
		sd2=math.sqrt((2*(self.SDNN_value**2))-((self.SDSD_value**2)/2))
		return round(sd2)

