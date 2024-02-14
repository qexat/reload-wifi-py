#!/usr/bin/env python
# pyright: reportUnusedCallResult = false

from __future__ import annotations

import argparse
import dataclasses
import os
import subprocess
import time
import typing

from reload_wifi_py import default
from reload_wifi_py.config import SUPERUSER
from reload_wifi_py.logging import LogKind, flag_note, log
from reload_wifi_py.messages import MESSAGES
from reload_wifi_py.utils import number


@dataclasses.dataclass(slots=True)
class Script:
    waiting_time: float = dataclasses.field(default=default.WAITING_TIME)
    force: bool = dataclasses.field(kw_only=True, default=default.FORCE)
    skip_failures: bool = dataclasses.field(kw_only=True, default=default.SKIP_FAILURES)
    dry_run: bool = dataclasses.field(kw_only=True, default=default.DRY_RUN)

    attempts: int = dataclasses.field(init=False, default=0)
    should_exit: bool = dataclasses.field(init=False, default=False)
    exit_code: int = dataclasses.field(init=False, default=os.EX_OK)

    @staticmethod
    def parse_args() -> argparse.Namespace:
        """
        Parse the command line arguments.
        """

        parser = argparse.ArgumentParser()

        parser.add_argument("--waiting-time", type=number, default=default.WAITING_TIME)
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--skip-failures", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

        return parser.parse_args()

    @classmethod
    def from_command_line_args(cls) -> typing.Self:
        """
        Create an App with the configuration set from the command line.
        """

        namespace = cls.parse_args()

        return cls(
            namespace.waiting_time,
            force=namespace.force,
            skip_failures=namespace.skip_failures,
            dry_run=namespace.dry_run,
        )

    def check_wifi_already_established(self) -> None:
        """
        Check if the Wi-Fi connection is already established and set up the
        exit flag if it is.
        """

        if (ssid := self.get_wifi_ssid()) is not None:
            log(
                LogKind.INFO, MESSAGES["wifi_already_established_template"].format(ssid)
            )

            if not self.force:
                self.should_exit = True

    def restart_if_forced(self) -> None:
        """
        Force a restart if the `force` flag is set to `True` and notice the user about it.
        """

        if self.force:
            flag_note(MESSAGES["reset_anyway"], "force")
            self.make_attempt()

    def restart_until_established_connection(self) -> None:
        """
        Restart the NetworkManager service until a connection is established.
        """

        while not self.is_connection_established():
            try:
                self.make_attempt()
            except (KeyboardInterrupt, EOFError):
                log(LogKind.INFO, MESSAGES["user_exit_requested"])

                if not self.is_connection_established():
                    log(LogKind.NOTE, MESSAGES["no_wifi_established"])
                    self.exit_code = 1

                break

            if self.should_exit:
                break

        if self.is_connection_established():
            log(
                LogKind.SUCCESS,
                MESSAGES["wifi_established_template"].format(
                    self.get_wifi_ssid(),
                    self.attempts,
                ),
            )
            self.exit_code = 0
        else:
            log(
                LogKind.ERROR, MESSAGES["cant_establish_template"].format(self.attempts)
            )
            log(LogKind.NOTE, MESSAGES["note_instant_disconnection"])

            self.exit_code = 1

        self.should_exit = True

    def get_wifi_ssid(self) -> str | None:
        """
        Return the current Wi-Fi SSID. If no connection is established, return None.
        """

        if self.dry_run:
            return None

        result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True)
        ssid = result.stdout.strip()

        return ssid if ssid else None

    def is_connection_established(self) -> bool:
        """
        Return whether a connection is established, i.e. if there is a Wi-FI SSID available.
        """

        return self.get_wifi_ssid() is not None

    def restart_nm(self) -> bool:
        """
        Restart the NetworkManager service and return whether it's a success or not.
        """

        if self.dry_run:
            return True

        try:
            proc = subprocess.run([SUPERUSER, "systemctl", "restart", "NetworkManager"])
        except KeyboardInterrupt:
            self.should_exit = True
            return False
        else:
            return proc.returncode == 0

    def make_attempt(self) -> None:
        """
        Restart NetworkManager and sleep for a certain time.

        It sometimes reports the number of attempts which is useful if there
        is a lot of them, to tell apart from the program simply hanging.
        """

        self.attempts += 1
        restart_success = self.restart_nm()

        if not restart_success:
            log(LogKind.ERROR, MESSAGES["restart_failure"])

            if not self.skip_failures:
                self.exit_code = 1
                self.should_exit = True
                return

            flag_note(MESSAGES["ignored_failure"], "skip_failures")

        if self.attempts % 10 == 0:
            log(
                LogKind.INFO, MESSAGES["attempts_report_template"].format(self.attempts)
            )

        if self.is_connection_established():
            self.exit_code = os.EX_OK
            self.should_exit = True
        else:
            time.sleep(self.waiting_time)

    def run(self) -> int:
        """
        Run the different steps of the script.

        Steps:
            - Checks if a Wi-Fi connection is already established
            - If restarting is forced anyway, it does that
            - Restarts `NetworkManager` until a connection is established or the
              user interrupted the program (e.g. via `^C`)
        """

        if self.dry_run:
            log(LogKind.INFO, MESSAGES["dry_run_mode"])

        steps = [
            self.check_wifi_already_established,
            self.restart_if_forced,
            self.restart_until_established_connection,
        ]

        for step in steps:
            step()

            if self.should_exit:
                break

        # Should never be reached but static checkers do not know that
        return self.exit_code


def main() -> int:
    """
    Main function of the script.
    """

    return Script.from_command_line_args().run()


if __name__ == "__main__":
    raise SystemExit(main())
