from flask import Flask
from threading import Thread
# This is depreciated, we only used this to allow the replit server that hosts our bot to persist
# by pingin it every so often to prevent it from shutting down
# Now we have an actual server to host the bot so we no longer need this
app = Flask('')

@app.route('/')
def home():
  return "Hello. I am alive!"

def run():
  app.run(host = '0.0.0.0', port = 8080)

def keepAlive():
  t = Thread(target = run)
  t.start()