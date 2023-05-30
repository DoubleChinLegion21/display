# importing tkinter for gui
import tkinter as tk
from microdot_asyncio import Microdot, Response
import asyncio
import pyautogui
import platform
hostOS = platform.system()
if (hostOS != 'Windows'):
    import pyiface
import json

# creating window
window = tk.Tk()
 
# setting attribute
window.attributes('-fullscreen', True)
window.title("Timer Board Results")

#Set up variables using tk stringvar
timeText = tk.StringVar()
timeText.set('Connecting')
nameText = tk.StringVar()
nameText.set('')

# creating text label to display on window screen
ipText = tk.StringVar()
ipText.set('...')
ipLabel = tk.Label(window, textvariable=ipText)
ipLabel.pack()

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
#print(screen_height, screen_width)

primaryTime = tk.Label(window, textvariable=timeText, font=("Arial", (min(screen_width, screen_height) // 4)))
primaryTime.place(relx=0.5, rely=0.5, anchor="center")

primaryName = tk.Label(window, textvariable=nameText, font=("Arial", (min(screen_width, screen_height) // 15)))
primaryName.place(relx=0.5, rely=0.25, anchor="center")

historyTimeText = tk.StringVar()
historyTimeText.set('')
historyTime = tk.Label(window, textvariable=historyTimeText, font=("Arial", (min(screen_width, screen_height) // 9)))
historyTime.pack(side=tk.BOTTOM)

app = Microdot()

historyObject = {}
updateHistoryFlag = False

async def updateHistoryDisplay():
    while True:
        global historyObject
        global updateHistoryFlag
        counter = 0
        for i in historyObject:
            if counter == 0:
                historyTime.config(bg="purple", fg="white")
            else:
                historyTime.config(bg="white", fg="black")
            try:
                historyTimeText.set('%s: %s' % (i, formatTime(historyObject[i])))
            except ValueError:
                print("ValueError in setHistoryTimes")
            if updateHistoryFlag:
                updateHistoryFlag = False
                break
            await asyncio.sleep(3)
            counter += 1

        #check if historyObject is empty, if yes, wait, otherwise, we already waited at least once
        if len(historyObject) == 0:
            await asyncio.sleep(4)

def setHistoryTimes(request):
    if 'history' in request:
        if request['history'] != '':
            global historyObject, updateHistoryFlag
            historyObject = dict(sorted(request['history'].items(), key=lambda item: item[1]))
            updateHistoryFlag = True

def setName(request):
    if 'name' in request:
        nameText.set(request['name'])
    else:
        nameText.set('')

def formatTime(timeIn):
    sanitizedTimeMs = int(timeIn)
    minutes = seconds = mili = 0
    if sanitizedTimeMs >= 1000*60:
        minutes = sanitizedTimeMs // 60000
    if sanitizedTimeMs >= 1000:
        seconds = sanitizedTimeMs % 60000
        seconds = seconds // 1000
    mili = sanitizedTimeMs % 1000
    outputString = '%02d:%03d' %  (seconds, mili)
    if minutes > 0:
        outputString = '%d:%s' % (minutes, outputString) 
    return outputString

#Handle request and sanitize for bad values sent
@app.route('/', methods=['POST'])
def index(request):
    print(request.body.decode('utf-8'))
    parsedRequest = json.loads(request.body.decode('utf-8'))
    print(parsedRequest)
    if "time" in parsedRequest:
        timeMs = parsedRequest['time']
        if timeMs != '':
            try:
                timeText.set('%s' % (formatTime(timeMs)))
            except ValueError:
                # Handle the exception
                return Response(status_code=400, body='\'time\' value is not integer')
            else:
                #if regular main time is valid and set, check for historyTimes
                setHistoryTimes(parsedRequest)
                setName(parsedRequest)
                return 'success'
        else:
            return Response(status_code=400, body='Missing \'time\' value')
    else:
        return Response(status_code=400, body='Missing \'time\' key')

async def update_loop():
    while True:
        window.update()
        await asyncio.sleep(0.25)

async def waitForWifi():
    # Get a specific interface by name
    if (hostOS != 'Windows'):
        wlan0 = pyiface.Interface(name='wlan0')
        while wlan0.sockaddrToStr(wlan0.addr) == 'None':
            # view wlan0 info
            print(wlan0.sockaddrToStr(wlan0.addr))
            await asyncio.sleep(2)
            
        ipText.set(wlan0.sockaddrToStr(wlan0.addr))
    else:
        ipText.set("onWindows")

    timeText.set('Standby')
    await app.start_server(debug=True, port=5000)

async def clickWake():
    while True:
        pyautogui.press('space')
        await asyncio.sleep(60)

async def main():
    waitForWifiTask = asyncio.create_task(waitForWifi())
    task1 = asyncio.create_task(update_loop())
    clickWakeTask = asyncio.create_task(clickWake())
    updateHistoryTask = asyncio.create_task(updateHistoryDisplay())
    await asyncio.gather(task1, waitForWifiTask, clickWakeTask, updateHistoryTask)

# Call the function to get the local IP address
if __name__ == "__main__":
    asyncio.run(main())
