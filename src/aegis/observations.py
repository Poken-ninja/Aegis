"""Agent observations for the AEGIS synthetic cyber-range."""

from __future__ import annotations

from dataclasses import dataclass, field

from aegis.network import EnterpriseNetwork
from aegis.state import CyberState
from aegis.telemetry import TelemetryEvent


@dataclass(frozen=True)
class RedObservation:
    """Information intentionally exposed to the simulated Red agent."""

    current_position: str
    discovered_hosts: frozenset[str] = frozenset()
    known_connections: frozenset[tuple[str, str]] = frozenset()
    known_host_roles: dict[str, str] = field(default_factory=dict)
    known_vulnerabilities: frozenset[tuple[str, str]] = frozenset()
    known_remediated_vulnerabilities: frozenset[str] = frozenset()
    known_isolated_hosts: frozenset[str] = frozenset()
    current_host_compromised: bool = False
    acquired_privilege: str = "none"


@dataclass(frozen=True)
class BlueObservation:
    """Information intentionally exposed to the simulated Blue agent."""

    known_hosts: frozenset[str] = frozenset()
    known_connections: frozenset[tuple[str, str]] = frozenset()
    known_host_roles: dict[str, str] = field(default_factory=dict)
    telemetry: tuple[TelemetryEvent, ...] = ()
    detected_hosts: frozenset[str] = frozenset()
    isolated_hosts: frozenset[str] = frozenset()
    remediated_vulnerabilities: frozenset[str] = frozenset()


def build_red_observation(
    network: EnterpriseNetwork,
    state: CyberState,
) -> RedObservation:
    """Build Red's limited view of the hidden simulator state."""

    discovered_hosts = frozenset(state.discovered_hosts)

    # Red can observe the immediate network neighborhood of its current
    # position. This permits the policy to construct discovery/movement
    # candidates without exposing the rest of the hidden topology.
    known_connections = frozenset(
        tuple(sorted((source, target)))
        for source, target in network.graph.edges
        if (
            source == state.red_position
            or target == state.red_position
            or (source in discovered_hosts and target in discovered_hosts)
        )
    )

    known_host_roles = {
        host_id: network.host(host_id).role
        for host_id in discovered_hosts
    }

    known_vulnerabilities: set[tuple[str, str]] = set()
    known_remediated_vulnerabilities: set[str] = set()

    for host_id in discovered_hosts:
        host = network.host(host_id)

        for vulnerability in host.vulnerabilities:
            known_vulnerabilities.add((host_id, vulnerability.vulnerability_id))

            if vulnerability.vulnerability_id in state.remediated_vulnerabilities:
                known_remediated_vulnerabilities.add(
                    vulnerability.vulnerability_id
                )

    known_isolated_hosts = frozenset(
        host_id
        for host_id in state.isolated_hosts
        if host_id in discovered_hosts
    )

    acquired_privilege = state.host_privileges.get(state.red_position)

    return RedObservation(
        current_position=state.red_position,
        discovered_hosts=discovered_hosts,
        known_connections=known_connections,
        known_host_roles=known_host_roles,
        known_vulnerabilities=frozenset(known_vulnerabilities),
        known_remediated_vulnerabilities=frozenset(
            known_remediated_vulnerabilities
        ),
        known_isolated_hosts=known_isolated_hosts,
        current_host_compromised=state.red_position in state.compromised_hosts,
        acquired_privilege=(
            acquired_privilege.value
            if acquired_privilege is not None
            else "none"
        ),
    )


def build_blue_observation(
    network: EnterpriseNetwork,
    state: CyberState,
) -> BlueObservation:
    """Build Blue's observation without exposing Red's hidden state."""

    known_hosts = frozenset(network.graph.nodes)

    known_connections = frozenset(
        tuple(sorted((source, target)))
        for source, target in network.graph.edges
    )

    known_host_roles = {
        host_id: network.host(host_id).role
        for host_id in known_hosts
    }

    telemetry = tuple(state.telemetry)

    return BlueObservation(
        known_hosts=known_hosts,
        known_connections=known_connections,
        known_host_roles=known_host_roles,
        telemetry=telemetry,
        detected_hosts=frozenset(state.detected_hosts),
        isolated_hosts=frozenset(state.isolated_hosts),
        remediated_vulnerabilities=frozenset(
            state.remediated_vulnerabilities
        ),
    )
