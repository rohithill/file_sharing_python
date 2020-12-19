import requests

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"


def set_download_folder(folder_path):
    pass


def get_download_folder():
    pass


def add_new_peer(name, ip, port):
    URL = f"{SERVER_URL}/peers"
    data = {"peer_name": name, "peer_ip": ip, "peer_port": port}
    resp = requests.post(URL, json=data)
    print(resp.status_code, resp.text)


def get_peers_list():
    URL = f"{SERVER_URL}/peers"
    resp = requests.get(URL)

    return resp.json()


def send_to_remote(filepath, ip, port):
    URL = f"{SERVER_URL}/send_to_remote"
    data = {"filepath": filepath, "remote_ip": ip, "remote_port": port}
    resp = requests.post(URL, json=data)
    print(resp.status_code, resp.text)


def get_transfers_list():
    URL = f"{SERVER_URL}/transfers"
    resp = requests.get(URL)
    return resp.json()