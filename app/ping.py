import requests
import time
import datetime
from threading import Thread
from requests.exceptions import RequestException


class HerokuPinger:
	"""Class to ping a page of the application on
	heroku every 30 minutes to ensure the dynos
	don't sleep.
	"""
	def ping(self, url):
		"""Send a GET request to the home page of the application
		every 30 minutes between the hours of 8am and 6pm. If there 
		is an error with the request, the method will try
		connecting another two times before quitting.
		"""
		
		#only need to ping servers during hours when someone might
		#visit the site
		retries = 0
		while True:
			lower_bound = datetime.time(8, 0)
			upper_bound = datetime.time(18, 0)
			if lower_bound <= datetime.datetime.now().time() <= upper_bound:
				while retries < 3:
					try:
						response = requests.get(url, timeout=10)
						response.raise_for_status()
						if response.status_code == 200:
							break
					except RequestException:
						time.sleep(3) #sleep before retrying
					except Exception:
						time.sleep(3)
					retries += 1
			if retries == 3: #entire loop will end after 3 retries
				break
			time.sleep(60 * 30) #sleep for 30 minutes

	def ping_homepage(self, url):
		# app = current_app._get_current_object()
		if url is not None:
			thread = Thread(target=self.ping, args=[url])
			thread.start()
			return thread

