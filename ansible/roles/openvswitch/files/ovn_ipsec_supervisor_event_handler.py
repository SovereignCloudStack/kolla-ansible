#!/usr/bin/env python3
import os
import sys
import xmlrpc.client


def write_stdout(s):
    # Only event listener protocol messages may be sent to stdout
    sys.stdout.write(s)
    sys.stdout.flush()


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()


def get_rpc_interface():
    # Extract required environment variables
    supervisor_server_url = "http://localhost:9001/RPC2"
    username = os.getenv('SUPERVISOR_USERNAME', None)
    password = os.getenv('SUPERVISOR_PASSWORD', None)

    if username and password:
        return xmlrpc.client.ServerProxy(f'http://{username}:{password}@{supervisor_server_url}')
    else:
        return xmlrpc.client.ServerProxy(supervisor_server_url)


def main():
    rpc = get_rpc_interface()

    while True:
        # Transition from ACKNOWLEDGED to READY
        write_stdout('READY\n')

        # Read header line and print it to stderr
        line = sys.stdin.readline()
        write_stderr(line)

        # Read event payload and print it to stderr
        headers = dict([x.split(':') for x in line.split()])
        data = sys.stdin.read(int(headers['len']))
        write_stderr(data)

        event_type = headers.get('eventname')
        if event_type in ("PROCESS_STATE_STOPPED", "PROCESS_STATE_EXITED"):
            process_name = headers.get('processname')
            write_stderr(f"Process {process_name} has stopped or exited. Stopping all processes.\n")

            # Stop all processes managed by Supervisor
            rpc.supervisor.stopAllProcesses()

        # Transition from READY to ACKNOWLEDGED
        write_stdout('RESULT 2\nOK\n')


if __name__ == '__main__':
    main()
