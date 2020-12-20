import socket
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path

import server_actions as server


def add_peers_tab(parent):
    peers_tab = ttk.Frame(parent)
    parent.add(peers_tab, text="Peers")
    my_ip = socket.gethostbyname(socket.gethostname())
    tk.Label(peers_tab, text=f"IP: {my_ip}\tPort: {server.SERVER_PORT}", height=2).pack(
        fill="x"
    )

    input_frame = tk.Frame(peers_tab)
    input_frame.pack()

    ttk.Separator(peers_tab, orient="horizontal").pack(fill="x", pady=5)

    peer_list_frame = tk.Frame(peers_tab)
    peer_list_frame.pack()

    tk.Label(master=input_frame, text="Name", width=5).pack(side=tk.LEFT)
    peer_name = tk.Entry(master=input_frame, width=16)
    peer_name.pack(side=tk.LEFT)

    tk.Label(master=input_frame, text="IP", width=3).pack(side=tk.LEFT)
    peer_ip = tk.Entry(master=input_frame, width=16)
    peer_ip.pack(side=tk.LEFT)

    tk.Label(master=input_frame, text="PORT", width=7).pack(side=tk.LEFT)
    peer_port = tk.Entry(master=input_frame, width=10)
    peer_port.pack(side=tk.LEFT)

    def add_peer():
        name = peer_name.get()
        ip = peer_ip.get()
        port = peer_port.get()
        try:
            server.add_new_peer(name, ip, port)
        except:
            pass
        else:
            add_peer_to_ui(name, ip, port)

    tk.Button(master=input_frame, text="Add Peer", command=add_peer).pack(
        side=tk.LEFT, padx=10
    )

    def send_file(name, ip, port):
        filepath = filedialog.askopenfilename(initialdir="/", title="Select a File")
        server.send_to_remote(filepath, ip, port)

    def add_peer_to_ui(name, ip, port):
        new_peer = tk.Frame(master=peer_list_frame)
        new_peer.pack(fill="x")
        tk.Label(master=new_peer, text=f"Name: {name}\tIP: {ip}\tPort: {port}\t").pack(
            side=tk.LEFT
        )
        tk.Button(
            master=new_peer, text="Send", command=lambda: send_file(name, ip, port)
        ).pack()

    peer_list = server.get_peers_list()
    for p in peer_list:
        ip, port, name = p
        add_peer_to_ui(name=name, ip=ip, port=port)


def add_transfers_tab(parent):
    transfers_tab = ttk.Frame(parent)
    parent.add(transfers_tab, text="Transfers")

    def get_and_update_ui():
        nonlocal transfers_list_frame
        tlist = server.get_transfers_list()
        transfers_list_frame.destroy()
        transfers_list_frame = ttk.Frame(transfers_list_frame_sentinel)
        transfers_list_frame.pack(fill="x")
        for i in tlist[2:]:

            remote_ip, filename, status = i
            entry_frame = ttk.Frame(transfers_list_frame)
            entry_frame.pack(fill="x")
            lbl = tk.Label(
                master=entry_frame, anchor="w", font="TkFixedFont", text=f"{status:8}"
            )
            lbl.pack(side=tk.LEFT, anchor="w")
            lbl = tk.Label(
                master=entry_frame,
                anchor="w",
                font="TkFixedFont",
                text=f"{remote_ip:15}",
            )
            lbl.pack(side=tk.LEFT, anchor="w")
            lbl = tk.Label(
                master=entry_frame, anchor="w", font="TkFixedFont", text=f"{filename}"
            )
            lbl.pack(fill="x")

    tk.Button(transfers_tab, text="Refresh Status", command=get_and_update_ui).pack(
        anchor="e"
    )

    transfers_list_frame_sentinel = ttk.Frame(transfers_tab)
    transfers_list_frame_sentinel.pack(fill="x")

    transfers_list_frame = ttk.Frame(transfers_list_frame_sentinel)
    transfers_list_frame.pack(fill="x")


def add_settings_tab(parent):
    settings_tab = ttk.Frame(parent)
    parent.add(settings_tab, text="Settings")
    download_folder = tk.StringVar()

    download_folder_frame = tk.Frame(settings_tab)
    download_folder_frame.pack(fill="x")
    tk.Label(
        master=download_folder_frame, textvariable=download_folder, anchor="w"
    ).pack(side=tk.LEFT, padx=20, pady=10)

    def set_download_folder():

        path = Path(download_folder.get()).parent

        # print(new_svar)
        tempdir = filedialog.askdirectory(
            initialdir=path, title="Please select a directory"
        )
        if not tempdir:
            return
        print("tempdir", tempdir)
        download_folder.set(tempdir)
        server.set_download_folder(tempdir)
        sf = server.get_download_folder()
        get_and_set_download_folder()
        print("Download folder updated to ", sf)

    def get_and_set_download_folder():
        folder = server.get_download_folder()
        download_folder.set(folder)

    get_and_set_download_folder()

    tk.Button(
        master=download_folder_frame,
        text="Change Download Folder",
        command=set_download_folder,
    ).pack(side=tk.RIGHT, padx=20, pady=10)


def add_about_tab(parent):
    credits = (
        "This File Sharing App is created by Komal Negi, Piyush Dangayach "
        "and Rohit Hill as the Major Project during B.Tech. from NIT Hamirpur."
        "\n\nThis App can be used to transfer files on a local network."
        "\nBuilt using Python3.7, Flask, and Tkinter."
        "\n\nProject source is available at: https://github.com/rohithill/file_sharing_python"
    )

    about_tab = ttk.Frame(parent)
    parent.add(about_tab, text="About")

    outer_frame = ttk.Frame(about_tab)
    outer_frame.pack(fill="both", expand=True)

    txt = tk.Text(outer_frame,wrap='word')
    txt.insert(tk.INSERT, credits)
    txt.configure(state="disabled")
    txt.pack(fill="both", expand=True)


def add_tabs(parent):
    tabControl = ttk.Notebook(parent)
    tabControl.pack(expand=1, fill="both")

    add_peers_tab(tabControl)
    add_transfers_tab(tabControl)
    add_settings_tab(tabControl)
    add_about_tab(tabControl)


def main():
    import time

    et = time.perf_counter()
    root = tk.Tk()
    root.title("File Sharing App")
    root.geometry("600x400")
    root.minsize(width=600, height=400)

    add_tabs(root)
    print(time.perf_counter() - et)
    root.mainloop()


if __name__ == "__main__":
    main()