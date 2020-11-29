from flask import Flask, request, jsonify
import os
import requests

PEER_LIST = "peer_list.txt"
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(PEER_LIST):
    with open(PEER_LIST, "w"):
        pass

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

@app.route("/peer", methods=["GET"])
def read_peer():
    response = []
    with open(PEER_LIST, "r") as f:
        for line in f:
            response += [line.split()]
    print(response)
    return jsonify(response)


@app.route("/peer", methods=["POST"])
def create_peer():
    # accept peer name, ip address and port
    data = request.get_json()
    peer_name, ip_address, port = data["peer_name"], data["peer_ip"], data["peer_port"]
    string_to_write = f"{peer_name} {ip_address} {port}\n"

    with open(PEER_LIST, "r") as f:
        if string_to_write in f.readlines():
            return "Peer already exists", 400

    with open(PEER_LIST, "a") as f:
        f.write(string_to_write)

    return "Peer added succesfully", 200


if __name__ == "__main__":
    app.run(debug=True)