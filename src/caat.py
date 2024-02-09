import socket
import select
import os
import json
import subprocess
import sys

socket_var_name = 'CAAT_SOCKET'
cmd_line_var_name = 'CAAT_ARGS'


"""
Commands as Arrow Types for Python.
Or Caat for short.

This is a library and framework that allows for calling commands as if they
were functions built natively within our language. In this case, Python.

A ForeignFunction is a class that allows us to transparently call foreign
code as if it were a native function.
This looks the cleanest in Python since we can override the __call__ method
to make it look like a function call.

The value 'argv' is provided to be similar to sys.argv. The only difference
is that it will only be a list of strings if:
    1.) Only strings are passed in.
    2.) The script wasn't called by another command that uses a Caat compatible
        library.
Otherwise, it will be a collection of different types that can be used as if
your Python script was called as a function.

The function 'return_caat' is provided as a way of 'returning' from the script.
It takes any base Python value (int, list, float, dict, str) and 'returns' it
to the script's caller.
"""


class ForeignFunction:
    def __init__(self, cmd: str):
        self.cmd = cmd

    def __call__(self, *args, **kwargs):
        pid = os.getpid()
        socket_path = f'/tmp/caat_{pid}.sock'
        try:
            os.unlink(socket_path)
        except OSError:
            if os.path.exists(socket_path):
                raise
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
        server.setblocking(0)
        server.bind(socket_path)

        # spawn command
        json_data = json.dumps(args)
        command = [self.cmd] + list(map(lambda x: str(x), args))
        env = os.environ.copy()
        env[socket_var_name] = socket_path
        env[cmd_line_var_name] = json_data
        subproc = subprocess.Popen(command, env=env)

        server.listen(1)
        read_list = [server]
        conn = None
        loop = True
        while loop:
            readable, writable, errored = select.select(read_list, [], [], 1)
            for s in readable:
                if s is server:
                    conn, addr = server.accept()
                    loop = False
                    break
            if subproc.poll() is not None:
                return subproc.returncode

        try:
            buffer = ""
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data.decode('utf-8')
            return json.loads(buffer)
        finally:
            conn.close()
            server.close()
            os.unlink(socket_path)
        return subproc.returncode


def get_arguments() -> list:
    if cmd_line_var_name in os.environ:
        return json.loads(os.environ[cmd_line_var_name])
    else:
        return sys.argv


argv = get_arguments()


def return_caat(arg):
    data = json.dumps(arg)
    env = os.environ.copy()
    socket_path = env[socket_var_name]
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    connected = False
    while not connected:
        try:
            client.connect(socket_path)
            connected = True
        except:
            pass

    client.sendall(bytes(data, 'utf-8'))

    client.close()

    exit(0)
