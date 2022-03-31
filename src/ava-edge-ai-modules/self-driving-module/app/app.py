import json
import torch
import logging
from yolov5 import YoloV5Model
from flask import Flask, Response, Request, abort, request


def init_logging():
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger != None:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)


app = Flask(__name__)

init_logging()

model = YoloV5Model()
app.logger.info('Model initialized')


@app.route("/score", methods=['POST'])
def score():
    with torch.no_grad():
        detected_objects = model.main(request)

    if len(detected_objects) > 0:
        respBody = {"inferences": detected_objects}
        return Response(json.dumps(respBody), status=200, mimetype='application/json')
    else:
        return Response(status=204)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
