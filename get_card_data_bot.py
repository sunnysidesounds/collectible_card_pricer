import json
import time
import subprocess
import requests
from websocket import create_connection
import settings
import logging
from termcolor import colored, cprint

def start_browser(browser_path, debugging_port):
    options = ['--headless',
               '--crash-dumps-dir=' + settings.CHROME_CRASH_DUMP_PATH,
               '--remote-debugging-port={}'.format(debugging_port)]
    browser_proc = subprocess.Popen([browser_path] + options)
    wait_seconds = 10.0
    sleep_step = 0.25
    while wait_seconds > 0:
        try:
            url = 'http://127.0.0.1:{}/json'.format(debugging_port)
            resp = requests.get(url).json()
            ws_url = resp[0]['webSocketDebuggerUrl']
            return browser_proc, create_connection(ws_url)
        except requests.exceptions.ConnectionError:
            time.sleep(sleep_step)
            wait_seconds -= sleep_step
    raise Exception('Unable to connect to chrome')
request_id = 0


def run_command(conn, method, **kwargs):
    global request_id
    request_id += 1
    command = {'method': method,
               'id': request_id,
               'params': kwargs}

    print(" - command: " + str(command))
    conn.send(json.dumps(command))
    while True:
        msg = json.loads(conn.recv())
        if msg.get('id') == request_id:
            return msg


def wait_for(seconds):
    for i in range(seconds, 0, -1):
        print(colored("   - debug: waiting for :" + str(i), 'yellow'), end='\r')
        time.sleep(1)


if __name__ == '__main__':
    print("-----------------------------------------------")
    browser = None
    try:
        target_url = settings.BASE_URL
        chrome_path = settings.CHROME_APP
        browser, conn = start_browser(chrome_path, 9222)

        run_command(conn, 'DOM.enable', url=target_url)
        run_command(conn, 'Network.enable', url=target_url)
        run_command(conn, 'Page.enable', url=target_url)


        page = run_command(conn, 'Page.navigate', url=target_url)

        print(page)

        wait_for(5) # let it load
       # js = """
       # var sel = '[role="heading"][aria-level="2"]';
       # var headings = document.querySelectorAll(sel);
       # headings = [].slice.call(headings).map((link)=>{return link.innerText});
       # JSON.stringify(headings);
        # var x = document.getElementsByClassName("user-profile-bio");
       # """

       # print("network_obj :")
        #print(network_obj['id'])

       # document = run_command(conn, 'Network.requestWillBeSent', requestId=str(network_obj['id']))

        #print(document)


        #result = run_command(conn, 'DOM.getOuterHTML', nodeId=1)

       # js = """
        
        # var x = document.querySelector('#js-pjax-container > div > div.h-card.col-3.float-left.pr-3 > div.js-profile-editable-area > div > div')
        #JSON.stringify({"value": x});
        
        
        #"""

        #print(js)

        #result = run_command(conn, 'Runtime.evaluate', expression=js)


        #print("result : ")
        #print(result)

        #headings = json.loads(result['result']['result'])



        #for heading in headings:
         #   print(heading)
        #browser.terminate()

    except Exception as e:
        logging.log(logging.ERROR, e)
        browser.terminate()