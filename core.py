from flask import Flask, request, jsonify
import os
import requests
import shelve

DATABASE = os.path.abspath("fileshare.db")
DEFAULT_DOWNLOAD_FOLDER = os.path.abspath("downloads")

with shelve.open(DATABASE) as db:
    if "download_folder" not in db.keys():
        db["download_folder"] = DEFAULT_DOWNLOAD_FOLDER

    DOWNLOAD_FOLDER = db["download_folder"]

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.mkdir(DOWNLOAD_FOLDER)

# maintain a list of file transferred in current session
transfers_file_list = []

app = Flask(__name__)


@app.route("/")
@app.route("/is_up")
def is_up():
    return "UP", 200


@app.route("/upload", methods=["POST"])
def receive_file():
    # Receive file from remote peer
    # print(request.files)
    # print(request.data)
    data = request.files["files"]
    filename = data.filename
    with shelve.open(DATABASE) as db:
        print(data, filename,type(filename),type(db["download_folder"]))
        file_path = os.path.join(db["download_folder"], filename)
        new_name = filename
        num = 0
        while os.path.exists(file_path):
            num += 1
            fn, ext = filename.split(".", maxsplit=1)
            new_name = fn + f"({num})" + f".{ext}"
            file_path = os.path.join(db["download_folder"], new_name)

        with open(file_path, "wb") as f:
            f.write(data.read())
        transfers_file_list.append((request.remote_addr, new_name, "Received"))
    return "File upload success", 200


@app.route("/send_to_remote", methods=["POST"])
def send_to_remote():
    """
    Accepts JSON
    {
        "filepath" : "<filepath>",
        "remote_ip": "<ip>",
        "remote_port": <port>
    }
    """
    # Blocking api, start in thread when making request to this
    data = request.get_json()
    file_path = data["filepath"]
    remote_ip = data["remote_ip"]
    remote_port = data["remote_port"]

    upload_url = f"http://{remote_ip}:{remote_port}/upload"
    file_name = os.path.basename(file_path)

    print(file_path, file_name, upload_url)
    if not os.path.exists(file_path):
        return "File doesn't exist", 400
    with open(file_path, "rb") as f:
        # files = {'files': f}
        # resp = requests.post(upload_url,files=files)
        try:
            r = requests.post(upload_url, files={"files": (file_name, f)})
        except requests.exceptions.ConnectionError:
            return "Failed to connect to remote peer", 400
        else:
            if r.status_code == 200:
                transfers_file_list.append((remote_ip, file_path, "Sent"))
                return "Request received successfully", 200
            else:
                return "Some Error occurred on remote side", 502


# peer CRUD


@app.route("/peers", methods=["GET"])
def read_peer():
    with shelve.open(DATABASE) as db:
        response = db.get("peers") or []
    return jsonify(response)


@app.route("/peers", methods=["POST"])
def create_peer():
    """
    Accepts JSON
    {
        "peer_name": "<peer name>",
        "peer_ip": "<ip>",
        "peer_port": <port>
    }
    """
    data = request.get_json()
    peer = (
        data["peer_ip"],
        data["peer_port"],
        data["peer_name"],
    )

    with shelve.open(DATABASE) as db:
        peers = db.get("peers") or []
        if peer in peers:
            return "Peer already exists", 400
        peers.append(peer)
        db["peers"] = peers

        return "Peer added succesfully", 200


@app.route("/transfers", methods=["GET"])
def get_transfers():
    return jsonify(transfers_file_list)


@app.route("/config/download_folder", methods=["GET", "PUT"])
def download_folder():
    if request.method == "GET":
        with shelve.open(DATABASE) as db:
            return db["download_folder"], 200
    elif request.method == "PUT":
        new_path = request.get_data().decode(encoding='utf8')
        print(type(new_path))
        new_path = os.path.abspath(new_path)
        if not os.path.exists(new_path):
            return "Path doesn't exist", 406
        with shelve.open(DATABASE) as db:
            db["download_folder"] = new_path
            return "Success", 200


if __name__ == "__main__":
    DEBUG = False
    HOST = "0.0.0.0"  # use 0.0.0.0 to allow external connections
    PORT = 5000
    app.run(debug=DEBUG, host=HOST, port=PORT)
