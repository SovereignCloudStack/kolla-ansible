#!/bin/env python3
import os
import sys
from supervisor import childutils

def main():
    # Set up an XML-RPC interface to Supervisor
    rpc = childutils.getRPCInterface(os.environ)

    # Listen for events indefinitely
    while True:
        headers, payload = childutils.listener.wait(sys.stdin, sys.stdout)
        event_type = headers['eventname']

        # Check if the event is a process state change related to exiting or stopping
        if "PROCESS_STATE_STOPPED" in event_type or "PROCESS_STATE_EXITED" in event_type:
            process_name = headers['processname']

            print(f"Process {process_name} has stopped or exited. Stopping all processes.")

            # Stop all processes managed by Supervisor
            rpc.supervisor.stopAllProcesses()

        # Acknowledge the event to Supervisor
        childutils.listener.ok(sys.stdout)


if __name__ == '__main__':
    main()