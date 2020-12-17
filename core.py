from flask import Flask, request, jsonify
import os
import requests
import shelve

DATABASE = os.path.abspath("fileshare23.db")
DEFAULT_DOWNLOAD_FOLDER = os.path.abspath("downloads")

with shelve.open(DATABASE) as db:
    if "download_folder" not in db.keys():
        db["download_folder"] = DEFAULT_DOWNLOAD_FOLDER

    DOWNLOAD_FOLDER = db["download_folder"]

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.mkdir(DOWNLOAD_FOLDER)

app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def receive_file():
    # Receive file from remote peer
    data = request.files["files"]
    filename = data.filename
    with open(os.path.join(DOWNLOAD_FOLDER, filename), "wb") as f:
        f.write(data.read())
    return "File upload success", 200


@app.route("/send_to_remote", methods=["POST"])
def send_to_remote():
    data = request.get_json()
    file_path = data["filepath"]
    remote_ip = data["remote_ip"]
    remote_port = data["remote_port"]

    upload_url = f"http://{remote_ip}:{remote_port}/upload"
    file_name = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        r = requests.post(upload_url, files={"files": (file_name, f.read())})
    if r.status_code == 200:
        return "Request received successfully", 200
    else:
        return "Some Error occurred on remote side", 502


# peer CRUD


@app.route("/peers", methods=["GET"])
def read_peer():
    response = []
    with shelve.open(DATABASE) as db:
        response = db.get("peers")
    print(response)
    return jsonify(response)


@app.route("/peers", methods=["POST"])
def create_peer():
    # accept peer name, ip address and port
    data = request.get_json()
    peer_name, peer_ip, peer_port = (
        data["peer_name"],
        data["peer_ip"],
        data["peer_port"],
    )

    with shelve.open(DATABASE) as db:
        peer = (peer_ip, peer_port, peer_name)
        peers = db.get("peers") or []
        if peer in peers:
            return "Peer already exists", 400
        peers.append(peer)
        db["peers"] = peers
        print(db["peers"])

        return "Peer added succesfully", 200


@app.route("/config/download_folder", methods=["GET", "PUT"])
def download_folder():
    if request.method == "GET":
        with shelve.open(DATABASE) as db:
            return db["download_folder"], 200
    elif request.method == "PUT":
        new_path = request.data
        new_path = os.path.abspath(new_path)
        if not os.path.exists(new_path):
            return "Path doesn't exist", 406
        with shelve.open(DATABASE) as db:
            db["download_folder"] = new_path
            return "Success", 200


if __name__ == "__main__":
    app.run(debug=True)