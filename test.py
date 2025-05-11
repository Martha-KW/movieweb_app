"""simple test file for debugging purposes to check if the port is working or not."""

from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World!"

if __name__ == "__main__":
    app.run(port=5000)
