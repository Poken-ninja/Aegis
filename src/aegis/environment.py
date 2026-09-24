"""Core simulation environment for AEGIS."""

from __future__ import annotations

import random

from aegis.actions import Action, ActionType, Agent
from aegis.network import EnterpriseNetwork, build_reference_network
from aegis.state import CyberState, Outcome, PrivilegeLevel


class AegisEnvironment:
    """Runs one synthetic Red-vs-Blue cyber episode."""

    EXPLOIT_SUCCESS_PROBABILITY = 0.70
    ESCALATE_SUCCESS_PROBABILITY = 0.60

    def __init__(
        self,
        network: EnterpriseNetwork | None = None,
        seed: int = 0,
        max_steps: int = 50,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")

        self.network = network or build_reference_network(seed=seed)
        self.seed = seed
        self.max_steps = max_steps
        self.rng = random.Random(seed)

        self.state: CyberState | None = None
        self.current_agent = Agent.RED

    def reset(self) -> CyberState:
        """Start a fresh episode."""
        self.rng = random.Random(self.seed)
        self.state = CyberState(red_position="internet")
        self.current_agent = Agent.RED
        return self.state

    def step(self, action: Action) -> CyberState:
        """Advance the simulation by one agent action."""
        if self.state is None:
            raise RuntimeError("Environment must be reset before stepping")

        if self.state.outcome is not Outcome.IN_PROGRESS:
            raise RuntimeError("Cannot step a terminated episode")

        if action.agent is not self.current_agent:
            raise ValueError(
                f"It is {self.current_agent.value}'s turn, "
                f"not {action.agent.value}'s"
            )

        if action.agent is Agent.RED:
            self._apply_red_action(action)
        else:
            self._apply_blue_action(action)

        self._check_terminal_conditions()

        if self.state.outcome is Outcome.IN_PROGRESS:
            self._advance_turn()

            if self.current_agent is Agent.RED:
                self.state.step_count += 1

            self._check_terminal_conditions()

        return self.state

    def _apply_red_action(self, action: Action) -> None:
        if action.action_type is ActionType.DISCOVER:
            self._red_discover(action.target)
            return

        if action.action_type is ActionType.MOVE:
            self._red_move(action.target)
            return

        if action.action_type is ActionType.EXPLOIT:
            self._red_exploit(action.target)
            return

        if action.action_type is ActionType.ESCALATE:
            self._red_escalate(action.target)
            return

        raise NotImplementedError(
            f"Red action not implemented yet: {action.action_type.value}"
        )

    def _apply_blue_action(self, action: Action) -> None:
        if action.action_type is ActionType.MONITOR:
            return

        if action.action_type is ActionType.DETECT:
            self._blue_detect(action.target)
            return

        if action.action_type is ActionType.ISOLATE:
            self._blue_isolate(action.target)
            return

        if action.action_type is ActionType.REMEDIATE:
            self._blue_remediate(action.target)
            return

        raise NotImplementedError(
            f"Blue action not implemented yet: {action.action_type.value}"
        )

    def _red_discover(self, target: str | None) -> None:
        if target is None:
            raise ValueError("DISCOVER requires a target")

        self.network.host(target)

        current_position = self.state.red_position

        if target not in self.network.neighbors(current_position):
            raise ValueError(
                f"Host {target} is not directly reachable from "
                f"{current_position}"
            )

        self.state.discovered_hosts.add(target)

    def _red_move(self, target: str | None) -> None:
        if target is None:
            raise ValueError("MOVE requires a target")

        self.network.host(target)

        current_position = self.state.red_position

        if current_position in self.state.isolated_hosts:
            raise ValueError(
                f"Red cannot move from isolated host {current_position}"
            )

        if target not in self.state.discovered_hosts:
            raise ValueError(
                f"Host {target} has not been discovered"
            )

        if target not in self.network.neighbors(current_position):
            raise ValueError(
                f"Host {target} is not directly reachable from "
                f"{current_position}"
            )

        if target in self.state.isolated_hosts:
            raise ValueError(
                f"Host {target} is isolated"
            )

        if not self._movement_allowed(current_position, target):
            raise ValueError(
                f"Red lacks a compromised foothold required to move "
                f"from {current_position} to {target}"
            )

        self.state.red_position = target

    def _movement_allowed(
        self,
        current_position: str,
        target: str,
    ) -> bool:
        """Determine whether Red has a valid foothold for movement."""

        # Initial Internet -> Web entry is an explicit simulation exception.
        if current_position == "internet" and target == "web01":
            return True

        # Internal movement requires the current host to be compromised.
        return current_position in self.state.compromised_hosts

    def _red_exploit(self, target: str | None) -> None:
        if target is None:
            raise ValueError("EXPLOIT requires a target")

        host = self.network.host(target)

        if target != self.state.red_position:
            raise ValueError(
                "EXPLOIT target must be Red's current host"
            )

        if target not in self.state.discovered_hosts:
            raise ValueError(
                f"Host {target} has not been discovered"
            )

        available_vulnerabilities = [
            vulnerability
            for vulnerability in host.vulnerabilities
            if vulnerability.vulnerability_id
            not in self.state.remediated_vulnerabilities
        ]

        if not available_vulnerabilities:
            raise ValueError(
                f"Host {target} has no exploitable vulnerabilities"
            )

        current_privilege = self._current_red_privilege()

        eligible_vulnerabilities = [
            vulnerability
            for vulnerability in available_vulnerabilities
            if self._privilege_satisfies(
                current_privilege,
                vulnerability.required_privilege,
            )
        ]

        if not eligible_vulnerabilities:
            raise ValueError(
                f"Red lacks the required privilege to exploit {target}"
            )

        if self.rng.random() < self.EXPLOIT_SUCCESS_PROBABILITY:
            self.state.compromised_hosts.add(target)

    def _current_red_privilege(self) -> PrivilegeLevel:
        """Return Red's highest acquired synthetic privilege."""

        privilege_levels = {
            PrivilegeLevel.NONE: 0,
            PrivilegeLevel.USER: 1,
            PrivilegeLevel.ADMIN: 2,
        }

        if not self.state.host_privileges:
            return PrivilegeLevel.NONE

        return max(
            self.state.host_privileges.values(),
            key=lambda privilege: privilege_levels[privilege],
        )

    def _red_escalate(self, target: str | None) -> None:
        if target is None:
            raise ValueError("ESCALATE requires a target")

        self.network.host(target)

        if target != self.state.red_position:
            raise ValueError(
                "ESCALATE target must be Red's current host"
            )

        if target not in self.state.compromised_hosts:
            raise ValueError(
                f"Host {target} has not been compromised"
            )

        current_privilege = self.state.host_privileges.get(
            target,
            PrivilegeLevel.NONE,
        )

        if current_privilege is PrivilegeLevel.ADMIN:
            raise ValueError(
                f"Red already has ADMIN privilege on {target}"
            )

        if self.rng.random() >= self.ESCALATE_SUCCESS_PROBABILITY:
            return

        if current_privilege is PrivilegeLevel.NONE:
            self.state.host_privileges[target] = PrivilegeLevel.USER
        elif current_privilege is PrivilegeLevel.USER:
            self.state.host_privileges[target] = PrivilegeLevel.ADMIN

    def _blue_detect(self, target: str | None) -> None:
        """Mark a compromised host as detected by Blue."""

        if target is None:
            raise ValueError("DETECT requires a target")

        self.network.host(target)

        if target not in self.state.compromised_hosts:
            raise ValueError(
                f"DETECT requires a compromised host: {target}"
            )

        self.state.detected_hosts.add(target)

    def _blue_isolate(self, target: str | None) -> None:
        """Isolate a detected compromised host from Red's attack path."""

        if target is None:
            raise ValueError("ISOLATE requires a target")

        self.network.host(target)

        if target not in self.state.compromised_hosts:
            raise ValueError(
                f"ISOLATE requires a compromised host: {target}"
            )

        if target not in self.state.detected_hosts:
            raise ValueError(
                f"ISOLATE requires a detected host: {target}"
            )

        self.state.isolated_hosts.add(target)

    def _blue_remediate(self, target: str | None) -> None:
        """Remediate an unremediated vulnerability on a detected host."""

        if target is None:
            raise ValueError("REMEDIATE requires a target")

        host = self.network.host(target)

        if target not in self.state.compromised_hosts:
            raise ValueError(
                f"REMEDIATE requires a compromised host: {target}"
            )

        if target not in self.state.detected_hosts:
            raise ValueError(
                f"REMEDIATE requires a detected host: {target}"
            )

        available_vulnerabilities = [
            vulnerability.vulnerability_id
            for vulnerability in host.vulnerabilities
            if vulnerability.vulnerability_id
            not in self.state.remediated_vulnerabilities
        ]

        if not available_vulnerabilities:
            raise ValueError(
                f"No unremediated vulnerabilities on host: {target}"
            )

        vulnerability_id = available_vulnerabilities[0]
        self.state.remediated_vulnerabilities.add(vulnerability_id)

    @staticmethod
    def _privilege_satisfies(
        current: PrivilegeLevel,
        required: str,
    ) -> bool:
        levels = {
            PrivilegeLevel.NONE: 0,
            PrivilegeLevel.USER: 1,
            PrivilegeLevel.ADMIN: 2,
        }

        try:
            required_level = PrivilegeLevel(required)
        except ValueError as exc:
            raise ValueError(
                f"Unknown required privilege: {required}"
            ) from exc

        return levels[current] >= levels[required_level]

    def _check_terminal_conditions(self) -> None:
        if self._critical_host_compromised():
            self.state.outcome = Outcome.RED_WIN
            return

        if self._blue_has_contained_red():
            self.state.outcome = Outcome.BLUE_WIN
            return

        if self.state.step_count >= self.max_steps:
            self.state.outcome = Outcome.TIMEOUT

    def _blue_has_contained_red(self) -> bool:
        """Return True when Blue has successfully contained Red."""

        return (
            self.state.red_position in self.state.isolated_hosts
            and self.state.red_position != self._critical_host_id()
        )

    def _critical_host_compromised(self) -> bool:
        critical_host_id = self._critical_host_id()
        return critical_host_id in self.state.compromised_hosts

    def _critical_host_id(self) -> str:
        critical_hosts = [
            host.host_id
            for host in self.network.hosts()
            if host.critical
        ]

        if len(critical_hosts) != 1:
            raise RuntimeError(
                "Network must contain exactly one critical host"
            )

        return critical_hosts[0]

    def _advance_turn(self) -> None:
        if self.current_agent is Agent.RED:
            self.current_agent = Agent.BLUE
        else:
            self.current_agent = Agent.RED