import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time
from multiprocessing.pool import ThreadPool
API_KEY ="tWhsw1U-5hQT"
PROJECT_TOKEN ="tTr2OXto73LB"
# RUN_TOKEN="t1n3qoCcuTBk"
RUN_TOKEN="t1FEwCeT2udn"

response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={"api_key":API_KEY})
data = json.loads(response.text)
# print(data)

class Data:
    def __init__(self,api_key,project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params ={
            "api_key" : self.api_key
        }
        self.data=self.get_data()
    
    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={"api_key":API_KEY})
        data = json.loads(response.text)
        return data

    def get_total_cases(self):
        data =self.data['total']
        for content in data:
            if content['name'] == "Active Cases":
                return content['value']

    def get_total_cured(self):
            data =self.data['total']
            for content in data:
                if content['name'] == "Cured / Discharged":
                    return content['value']
            return"0"

    def get_total_deaths(self):
            data =self.data['total']
            for content in data:
                if content['name'] == "Deaths":
                    return content['value']
            return "0"

    def get_state_data(self,state):
        data =self.data["state"]
        for content in data:
            if content['name'].lower() == state.lower():
                return content
        return "0"


    def get_state_list(self):
        states=[]
        for state in self.data['state']:
            states.append(state['name'].lower())
        
        return states
    
    def update(self):
       	    response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)
            def poll():
                time.sleep(0.2)
                old_data = self.data  
                while True:
                    new_data=self.get_data()
                    if new_data != old_data:
                        self.data=new_data
                        print("Data is updated")
                        break
                    time.sleep(5)          
                
            t=threading.Thread(target=poll)
            t.start()
#print(Data.get_state_list())
#print(Data.get_state_data("Maharashtra")['total_cases'])
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# speak("hello geeta")
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said=""
        try:
            said=r.recognize_google(audio)
        except Exception as e:
            print("Exception:",str(e))
    
    return said.lower()


def main():
    print("The program is started")
    data = Data(API_KEY,PROJECT_TOKEN)
    state_list = data.get_state_list()
    END_PHRASE ="stop"

    PATTERNS= {
            re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
            re.compile("[\w\s]+ total cases"):data.get_total_cases,
            re.compile("[\w\s]+ total [\w\s]+ deaths"):data.get_total_deaths,
            re.compile("[\w\s]+ total deaths"):data.get_total_deaths,
            re.compile("[\w\s]+ total [\w\s]+ cured"):data.get_total_cured,
            re.compile("[\w\s]+ total cured"):data.get_total_cured
                }

    STATE_PATTERNS = {
                    re.compile("[\w\s]+ cases [\w\s]+"):lambda state: data.get_state_data(state)['total_cases'],
                    re.compile("[\w\s]+ deaths [\w\s]+"):lambda state: data.get_state_data(state)['total_deaths'],
                    re.compile("[\w\s]+ cured [\w\s]+"):lambda state: data.get_state_data(state)['total_cured']
                    }
    while True:
        print("I am Listening...")
        text=input()
        print(text)
        result=None
        for pattern, func in STATE_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for state in state_list:
                    if state in words:
                        result=func(state)
                        break
        
        for pattern, func in PATTERNS.items():
            if pattern.match(text):
                result=func()
                break
        
        if text == "update":
            speak("Data is being updated..")
            data.update()

        if result:
            speak(result)
            # print(result)
        if text.find(END_PHRASE) != -1:
            print("Exit")
            break

main()