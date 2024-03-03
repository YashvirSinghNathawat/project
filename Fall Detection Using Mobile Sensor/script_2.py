import websocket
import json
import threading 
import numpy as np
import pickle
import sys
import math
import time
import requests
import json
sensor_data = []
list = []
window_size = 20
index = 0
step_size = 20  
flag = True
class_names = ["falling", "jumping", "sitting", "standing","turning","walking"]


    
timer = 0
count = 0
ALERT = 0
state = 0
minV = 10
maxV = -1

def pushbullet_noti(title, body):
 
    TOKEN = 'o.t3LEA7SVuu2dtoYcpoYcs2lCn8bGgxVx'  # Pass your Access Token here
    # Make a dictionary that includes, title and body
    msg = {"type": "note", "title": title, "body": body}
    # Sent a posts request
    resp = requests.post('https://api.pushbullet.com/v2/pushes',
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + TOKEN,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:  # Check if fort message send with the help of status code
        raise Exception('Error', resp.status_code)
    else:
        print('Message sent')

def time_in_millis():
    return int(round(time.time() * 1000))
def fall_detect(Anet,pitch,roll,y_value):
    global state, timer, count, ALERT,flag,minV,maxV
    
    
    if minV > Anet:
        minV = Anet
         # Open the file in append mode
        with open('c.txt', 'w') as file:
            # Write the current value of minV to the file
            file.write(f'MinV: {minV}\n')
    if maxV < Anet:
        maxV = Anet
         # Open the file in append mode
        with open('d.txt', 'w') as file:
            # Write the current value of minV to the file
            file.write(f'MaxV: {maxV}\n')
    
    if Anet > 9 and y_value > 1.5:
        state = 0
        time.sleep(5)


    if Anet < 0.52 and  state!=0 :
        state = 1
        timer = time_in_millis()
    
    
        

    if state == 1:
        if Anet > 1:
            state = 2
            timer = time_in_millis()

        if (time_in_millis() - timer) / 1000 > 2:
            state = 0

    if state == 2:
        if abs(pitch) > 60 or abs(roll) > 60:
            state = 3
            timer = time_in_millis()

        if (time_in_millis() - timer)> 100:
            state = 0

    if state == 3:
        if abs(pitch) < 60 and abs(roll) < 60:
            count += 1
            if count > 20:
                state = 0
                count = 0

        if (time_in_millis() - timer) / 1000 > 5:
            state = 4
            ALERT = 1
            # tone(9, 250)  # Uncomment this if you have an equivalent function for tone


    if state == 4 and ALERT == 1 and flag==True:
        if (time_in_millis() - timer) / 1000 > 10:
            state = 5
            # tone(9, 4000)  # Uncomment this if you have an equivalent function for tone
            pushbullet_noti("Fall Detection", "Shivam Has injured")
            flag = False

    if ALERT==1:
        print('---------------------------------------------------------------------------------------------------------------------------------------------')
        print("---------------------------------------------------FALL DETECTED ! --------------------------------------------------------------------------")
        print('---------------------------------------------------------------------------------------------------------------------------------------------')
        time.sleep(0.5)
    else :
        print("State : \t\t" ,state,"ALERT  :" ,ALERT)
        print()
    



def on_message(ws, message):
    message_dict = json.loads(message)
    values = message_dict['values']
    x_val = values[0]/10.2
    y_val = values[1]/10.2
    z_val = values[2]/10.2
    Anet = math.sqrt(x_val**2 + y_val**2 + z_val**2)

    # Pitch and roll calculation
    pitch = math.atan(x_val / math.sqrt(y_val**2 + z_val**2))
    roll = math.atan(y_val / math.sqrt(x_val**2 + z_val**2))

    # Convert radians into degrees
    pitch = math.degrees(pitch) - 90
    roll = math.degrees(roll)
    print("ANet : ",Anet,"\t Pitch : ",pitch,"\t Roll : ",roll)
    print("X : ",x_val,"\t Y : ",y_val,"\t Z : ",z_val)

    fall_detect(Anet,pitch,roll,y_val)
    # time.sleep(0.05)


    



def on_error(ws, error):
    print("### error ###")
    print(error)

def on_close(ws, close_code, reason):
    print("### closed ###")
    print("close code : ", close_code)
    print("reason : ", reason  )

def on_open(ws):
    print("connection opened")
    

if __name__ == "__main__":
    ws = websocket.WebSocketApp('ws://192.168.112.113:8080/sensor/connect?type=android.sensor.accelerometer',
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever()