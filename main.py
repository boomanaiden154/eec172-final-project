from flask import Flask
from flask import request, Response
from PIL import Image
import requests
import numpy

app = Flask(__name__)

order = [4,3,2,1,0]
weather = "sun"

def getWeather():
 r = requests.get("https://api.open-meteo.com/v1/forecast?latitude=38.54&longitude=121.74&current=temperature_2m,wind_speed_10m,precipitation")
 weather = r.json()["current"]
 if weather["wind_speed_10m"] > 15:
   return "wind"
 elif weather["precipitation"] > 0:
   return "rain"
 else:
   return "sun"

@app.route("/getimage")
def getImage():
  global weather
  image_name = request.args.get("name")
  if image_name == "9":
    image_name = weather
  print(image_name)
  image = numpy.array(Image.open(f"{image_name}.png").resize((128,128)).convert("RGB"))
  output_buffer = b""
  for x in range(0,128):
    for y in range(0,128):
      R = int(image[x][y][0] >> 3)
      G = int(image[x][y][1] >> 2)
      B = int(image[x][y][2] >> 3)

      rgb = (R << 11) | (G << 5) | B
      msb_rgb = int(rgb/256)
      lsb_rgb = rgb%256
      output_buffer += msb_rgb.to_bytes(1) + lsb_rgb.to_bytes(1)
  output = output_buffer + b"endofmessage"
  return Response(output, mimetype='application/octet-stream')

@app.route("/getorder")
def getOrder():
  print(order)
  return ",".join([str(index) for index in order]) + "endofmessage"

@app.route("/setorder")
def setOrder():
  global order
  order = [int(index_str) for index_str in request.args.get("order").split(",")]
  return "done"

if __name__ == "__main__":
  weather = getWeather()
  app.run(host="0.0.0.0", port=5000)

