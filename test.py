import requests
import json
import unittest


class TestRestService(unittest.TestCase):
	def setUp(self):
		self.url = "http://localhost:5000/router/api/v1.0/message"


	def test_input_in_good_format(self):
		data = {"message":"SendHub Rocks",
		 		"recipients":["+15555555556", "+15555555555", "+15555555554", "+15555555553", 
		 				"+15555555552", "+15555555551", "+15555555551", "+12345678901"]}

		r = requests.post(self.url, data=json.dumps(data), headers={'content-type': 'application/json'})

		self.assertEquals(r.status_code, 201)


	def test_wrong_phone_number(self):
		data = {"message":"SendHub Rocks",
		 		"recipients":["+15555555556", "+15555555555", "+15555555554", "+15555555553", 
		 				"+15555555552", "+15555555551", "+15555555551", "+1234567890"]}

		r = requests.post(self.url, data=json.dumps(data), headers={'content-type': 'application/json'})

		self.assertEquals(r.status_code, 400)


	def test_correctness_of_routing(self):
		data = {"message":"SendHub Rocks",
		 		"recipients":["+15555555556", "+15555555555", "+15555555554", "+15555555553", 
		 				"+15555555552", "+15555555551", "+15555555551", "+12345678901"]}

		r = requests.post(self.url, data=json.dumps(data), headers={'content-type': 'application/json'})

		self.assertEquals(r.status_code, 201)
		
		# 3 -> 3 of 1m/r, 5 -> 1 of 5m/r
		self.assertEquals(len(r.json()["routes"][0]["recipients"]), 1)
		self.assertEquals(len(r.json()["routes"][1]["recipients"]), 1)
		self.assertEquals(len(r.json()["routes"][2]["recipients"]), 1)
		self.assertEquals(len(r.json()["routes"][3]["recipients"]), 5)


if __name__ == '__main__':
    unittest.main()