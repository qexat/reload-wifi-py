# reload-wifi-py

`reload-wifi-py` is a Python implementation of `reload-wifi`, an automation script to periodically restart the `NetworkManager` service until a connection is established again.

> [!IMPORTANT]
> This is NOT a cron job: this script must be run manually.

## Assumptions

- `iwgetid` is available on your system (provided by `wireless-tools`).
- The `NetworkManager` service is run under `systemd`, thus `systemctl` is available.

> [!NOTE]
> By default, it uses `sudo`, but you can configure it to use a similar tool
> as long as its use is identical to the former.

## Installation

The use of a virtual environment is recommended.

- Clone the repository and `cd` into the directory
- Run `pip install .`

A command `reload-wifi` should be available to run.

> Personally, I have this repository in `~/.local/share/reload-wifi-py/`, with a
> symlink `~/.local/bin/reload-wifi` that points to the script file and
> `~/.local/bin` on `PATH`. It does the job 👍
