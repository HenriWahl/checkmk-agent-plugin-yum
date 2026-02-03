# Dockerfile_fedora-43

This Dockerfile creates a Fedora 43 container with Check_MK agent running via supervisord on port 6556 for testing purposes.

## Features

- **Base Image**: Fedora 43
- **No xinetd**: Uses supervisord instead of xinetd for process management
- **Check_MK Agent**: Official Check_MK agent (version 2.3.0) listening on port 6556
- **Supervisord**: Manages the check_mk_agent process with automatic restart capability

## Files

- `Dockerfile_fedora-43`: The main Dockerfile
- `supervisord-checkmk.conf`: Supervisord configuration file
- `check_mk_agent.linux`: Official Check_MK agent script from CheckMK repository

## Building the Image

```bash
docker build -f Dockerfile_fedora-43 -t fedora43-checkmk:latest .
```

## Running the Container

```bash
docker run -d --name checkmk-agent -p 6556:6556 fedora43-checkmk:latest
```

## Testing the Agent

You can test the agent by connecting to port 6556:

```bash
echo | nc localhost 6556
```

Or using telnet:

```bash
telnet localhost 6556
```

## Managing the Agent

Check the status of the agent:

```bash
docker exec checkmk-agent supervisorctl status
```

Restart the agent:

```bash
docker exec checkmk-agent supervisorctl restart check_mk_agent
```

View logs:

```bash
docker logs checkmk-agent
```

## Architecture

The container uses the following architecture:

1. **supervisord** runs as PID 1 and manages all processes
2. **check_mk_agent_tcp** wrapper script listens on port 6556 using netcat
3. When a connection is made, netcat executes `/usr/bin/check_mk_agent`
4. The agent returns system information in Check_MK format

## Notes

- The agent runs as root to access system information
- Supervisord automatically restarts the agent if it crashes
- The netcat loop ensures the agent continues listening even if a connection fails
- No xinetd is installed, making the container more lightweight
