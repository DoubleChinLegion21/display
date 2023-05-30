# importing tkinter for gui
import tkinter as tk
import socket   
from microdot_asyncio import Microdot, Response
import asyncio
import pyiface
import time

# creating window
window = tk.Tk()
 
# setting attribute
window.attributes('-fullscreen', True)
window.title("Timer Board Results")

#Set up variables using tk stringvar
timeText = tk.StringVar()
timeText.set('Connecting')

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

app = Microdot()

#Handle request and sanitize for bad values sent
@app.route('/', methods=['GET'])
def index(request):
    if "time" in request.args:
        timeMs = request.args['time']
        if timeMs != '':
            try:
                sanitizedTimeMs = int(timeMs)
                minutes = seconds = mili = 0
                if sanitizedTimeMs >= 1000*60:
                    minutes = sanitizedTimeMs // 60000
                if sanitizedTimeMs >= 1000:
                    seconds = sanitizedTimeMs % 60000
                    seconds = seconds // 1000
                mili = sanitizedTimeMs % 1000
                timeText.set('%02d:%02d:%03d' % (minutes, seconds, mili))
                return 'success'
            except ValueError:
                # Handle the exception
                return Response(status_code=400, body='\'time\' value is not integer')
        else:
            return Response(status_code=400, body='Missing \'time\' value')
    else:
        return Response(status_code=400, body='Missing \'time\' key')

async def update_loop():
    while True:
        window.update()
        await asyncio.sleep(0.25)

async def main():
    task1 = asyncio.create_task(update_loop())
    task2 = asyncio.create_task(app.start_server(debug=True, port=5000))
    await asyncio.gather(task2, task1)
    
# Get a specific interface by name
wlan0 = pyiface.Interface(name='wlan0')
while wlan0.sockaddrToStr(wlan0.addr) == None:
    # view wlan0 info
    print(wlan0.sockaddrToStr(wlan0.addr))
    time.sleep(2)

# Call the function to get the local IP address
timeText.set('Standby')
ipText.set(wlan0.sockaddrToStr(wlan0.addr))

if __name__ == "__main__":
    asyncio.run(main())
