from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/vector/move_forward', methods=["GET"])
def move_forward():

    return jsonify({"message": "Moving forward..."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)