import logging
from flask import Flask
from router import opt

app = Flask(__name__)
app.register_blueprint(opt)

logging.basicConfig(
    filename="logs.txt",
    filemode="w",
    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
    datefmt="%d-%M-%Y %H:%M:%S",
    level=logging.DEBUG
)


if __name__ == '__main__':
    app.run()
