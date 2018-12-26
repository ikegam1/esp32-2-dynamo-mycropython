import sys
import dht
import machine
import time
import ambient
from umqtt.simple import MQTTClient
import json
import usocket
import ntptime

# this is the mbedtls test RSA key; you must change it to your own for production!
key = """-----BEGIN RSA PRIVATE KEY-----
ABCDEF..........
-----END RSA PRIVATE KEY-----
"""

# this is the mbedtls test certificate; you must change it to your own for production!
cert = """-----BEGIN CERTIFICATE-----
ABCDEF..........
-----END CERTIFICATE-----
"""

ssid = 'xxxx'
password = 'xxxx'
channel_id = '8500'
write_key = 'xxxx'

certificate_key_file = 'cert/private.pem.key'
certificate_cert_file = 'cert/certificate.pem.crt'
certificate_ca_file = 'cert/ca1.pem'
mqtt_endpoint = 'xxxx-ats.iot.ap-northeast-1.amazonaws.com'
mqtt_topic = 'kamekusa/DHT22'

def do_connect(ssid, password):
  import network
  sta_if = network.WLAN(network.STA_IF)
  if not sta_if.isconnected():
    print ('connecting ...')
    sta_if.active(True)
    sta_if.connect(ssid, password)
    timeout = 10
    while not sta_if.isconnected() and timeout > 0:
      print('.')
      time.sleep(3)
      timeout -= 1
  print(sta_if.ifconfig())
  
def mqttpub(tem,hum):
  a=usocket.getaddrinfo(mqtt_endpoint,8883)
  addr = a[0][-1][0]
  time = ntptime.time() + 946684800 # + (datetime.date(2000,1,1) - datetime.date(1970, 1, 1)).days * 24 * 60 * 60
  msg = {
          "id": "id{}".format(time),
          "expire": time + 48 * 60 * 60,
          "d1": "{}".format(tem),
          "d2": "{}".format(hum)
        }
  msg = json.dumps(msg)
  client = MQTTClient(client_id="ESP2866DHT22", server=addr, port=8883, keepalive=5000, ssl=True, ssl_params={ "key":key, "cert":cert, "server_side":False })
  client.connect()
  print(str(client))
 
  loop = 10
  while loop > 1:
    print (".")
    try:
      res = client.publish(topic=mqtt_topic, msg=msg, qos=0)
      print('Sending: ' + msg)
      print(str(res))
      loop = 0
    except Exception as e:
      print('Could not establish MQTT connection')
      print (str(e))
      time.sleep(1)
      loop -= 1
    
    
def send_am(tem,hum):
    am = ambient.Ambient(channel_id, write_key)
    res = am.send({
      "d1": tem,
      "d2": hum
    })
  
    print(res.status_code)
    res.close()
    
def main(d):
  loop = 10
  while loop > 1:
    print(".")
    try:
      time.sleep(1)
      d.measure()
      loop = 0
    except:
      loop -= 1
  
  print("Temperature: %3.1f ℃" % d.temperature())
  print("   Humidity: %3.1f %%" % d.humidity())
  tem = d.temperature()
  hum = d.humidity()
  mqttpub(tem,hum)
  send_am(tem,hum)
  
  print ("start sleep")
  #machine.deepsleep(1000 * 1000 * 600)
  #esp.deepsleep(1000 * 1000 * 600)

do_connect(ssid, password)
d = dht.DHT22(machine.Pin(4))
main(d)













