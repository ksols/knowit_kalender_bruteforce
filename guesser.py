from stmpy import Machine, Driver
from datetime import datetime, timedelta
import time
import json
import requests
time_left = 0
c = open("controller.json")
controller = json.load(c)
c.close()
class Tick:
    def __init__(self):
        global controller
        self.lower_limit = controller["machine_1_lower_limit"]
        self.upper_limit = self.lower_limit + 62
        self.cookies = {
        '_kodekalender_session': controller["hackerGoblin_cookie"],
    }
        self.headers = {
        'Host': 'julekalender-backend.knowit.no',
        # 'Content-Length': '28',
        'Sec-Ch-Ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'X-Csrf-Token': controller["hackerGoblin_token"],
        'Sec-Ch-Ua-Mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.72 Safari/537.36',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Origin': 'https://julekalender.knowit.no',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://julekalender.knowit.no/',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'close',
        # 'Cookie': '_kodekalender_session=mMmzN1vkTPTQe9ZGgnRAbtN6nhl6vWwUZGzT4BfgkM4geBxp9TQgxZ2FIxAikZqEH%2F1tqRZQVNIZvVa4EA%2BS0Wkb%2F9p4eMjqhTIDFVeqdc9Q5JUk5y0CuSrm26viq%2BQzPCTJl8tVu027Elg0ixsq%2B41XLLxEBaghXWO6iop%2F7uvmf2miG2MGaQALM5Ll4dQxS1UdQhwXD%2FTUIbmbP62yy35cAEO0F0IzFVEKWEPVk1JPw82O%2FWfndfDRsfpI%2FDoCuG7ue9hufOOIOvvWKzujM%2FR1z%2FyYD6gF%2Bdnv3pHNEMzBSVd7Ek%2F3s3rZ3I6BX0ibOuzbEW8Pe%2Fn8RJafYp2BsNUij2%2F%2BDZP1cpMGMmdLPEvy6P2UjxPebC8ouYCNVEUYtfIDFY69xqxpzSXtXCBAB3ETZerFKOq67SRpA1dnlc%2FkwMznf1D0HMYxUuNv9lkth9ZyImKUUFhEt7ekbjCH%2FMijYal3Dl40hOP7--CO8svRZ6gyUCfAR1--3nPkSZ56%2F7tBTz39f%2F0xOg%3D%3D',
    }
    def on_init(self):
        global time_left
        if (int(time_left) > 0):
            now = datetime.now()
            result = now + timedelta(seconds=int(time_left))
            current_time1 = result.strftime("%H:%M:%S")
            print("Ready at:", current_time1)
            time.sleep(int(time_left))

    def guess(self):
        for x in range(self.lower_limit,self.upper_limit, 2):
            self.json_data = {
            'solution': {
            'answer': f'{x}',
                },
            }
            response = requests.post(
            "https://julekalender-backend.knowit.no/challenges/" + controller["machine_1_task"] +"/solutions.json",
            cookies=self.cookies,
            headers=self.headers,
            json=self.json_data,
        )    
            r = response
            global time_left
            time_left = 0
            print()
            json_response = json.loads(r.text)
            print(json_response, "with number: ", self.json_data)
            print()
            if('Retry-After' in r.headers.keys()):
                time_left = r.headers['Retry-After']
                self.lower_limit = x #Setter lower her så den alltid blir det siste som ikke ble testet
                print("Lower_limit sat to", x)
                break
            elif(json_response == {'solved': True}):
                print("--------------")
                print(f"Solution is {x}")
                f = open("fasiter.txt", "a")
                f.write("Fasit paa oppg "+ controller["machine_1_task"] +" fra machine_1" +" "+ str(x) + "\n")
                f.close() 
                print("--------------")
                exit("Program stopping...")
        with open("controller.json", "r") as f:
            co = json.load(f)
        co["machine_1_lower_limit"] = self.lower_limit
        print(self.lower_limit, " written to controller...")
        json_object = json.dumps(co, indent=4)
        with open("controller.json", "w") as outfile:
            outfile.write(json_object)
        self.upper_limit = self.lower_limit + 60
    def enter_cooldown(self):
        global time_left
        print(f'Entered cooldown, ready in {time_left} sec')

driver = Driver()
tick = Tick()
init = {'source':'initial', 'target':'idle', 'effect':'; start_timer("letsgo", 1000)'}
t0 = {"trigger": "letsgo",'source':'idle', 'target':'guessing', 'effect':f'on_init; start_timer("t", 1000)'}
t1 = {'trigger':'t', 'source':'guessing', 'target':'cooldown', 'effect':'guess; start_timer("done", 1000)'}
t2 = {'trigger':'done', 'source':'cooldown', 'target':'idle', 'effect':'enter_cooldown; start_timer("letsgo", 1000)'}

stm_tick = Machine(transitions=[t0, t1, t2, init], obj=tick, name='stm_tick')
tick.stm = stm_tick

driver.add_machine(stm_tick)
driver.start()