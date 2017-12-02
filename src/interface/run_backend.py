from backend import app
import logging

if __name__ == '__main__':
    format = '%(levelname)s:%(name)s:%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=format)
    app.run(host='0.0.0.0', debug=True)
