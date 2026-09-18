"""Core synthetic enterprise network model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import networkx as nx


@dataclass(frozen=True)
class Vulnerability:
    """Synthetic vulnerability used only inside the simulator."""

    vulnerability_id: str
    required_privilege: str = "none"


@dataclass
class Host:
    """A synthetic enterprise host."""

    host_id: str
    role: str
    critical: bool = False
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    privileges: tuple[str, ...] = ("none",)


class EnterpriseNetwork:
    """Deterministic graph-based representation of an AEGIS network."""

    def __init__(self, configuration_id: str, seed: int) -> None:
        if not configuration_id:
            raise ValueError("configuration_id must not be empty")
        self.configuration_id = configuration_id
        self.seed = seed
        self.graph = nx.Graph()

    def add_host(self, host: Host) -> None:
        if host.host_id in self.graph:
            raise ValueError(f"Host already exists: {host.host_id}")
        self.graph.add_node(host.host_id, host=host)

    def connect(self, source: str, target: str) -> None:
        self._require_host(source)
        self._require_host(target)
        if source == target:
            raise ValueError("Self-connections are not allowed")
        self.graph.add_edge(source, target)

    def host(self, host_id: str) -> Host:
        self._require_host(host_id)
        return self.graph.nodes[host_id]["host"]

    def hosts(self) -> Iterable[Host]:
        for host_id in self.graph.nodes:
            yield self.graph.nodes[host_id]["host"]

    def neighbors(self, host_id: str) -> tuple[str, ...]:
        self._require_host(host_id)
        return tuple(self.graph.neighbors(host_id))

    def _require_host(self, host_id: str) -> None:
        if host_id not in self.graph:
            raise KeyError(f"Unknown host: {host_id}")


def build_reference_network(
    configuration_id: str = "NET_00001",
    seed: int = 0,
) -> EnterpriseNetwork:
    """Build the initial six-host AEGIS reference network.

    Topology: internet -- web01 -- app01 -- db01 -- critical01,
    with app01 also connected to work01.
    """
    network = EnterpriseNetwork(configuration_id=configuration_id, seed=seed)
    network.add_host(Host("internet", "external_entry"))
    network.add_host(
        Host(
            "web01",
            "web_server",
            vulnerabilities=[Vulnerability("SYNTH_WEB_01")],
            privileges=("none", "web_service"),
        )
    )
    network.add_host(
        Host(
            "app01",
            "application_server",
            vulnerabilities=[Vulnerability("SYNTH_APP_01")],
            privileges=("none", "app_service"),
        )
    )
    network.add_host(
        Host(
            "work01",
            "workstation",
            vulnerabilities=[Vulnerability("SYNTH_WORK_01")],
            privileges=("none", "user"),
        )
    )
    network.add_host(
        Host(
            "db01",
            "database_server",
            vulnerabilities=[Vulnerability("SYNTH_DB_01")],
            privileges=("none", "database_user"),
        )
    )
    network.add_host(
        Host("critical01", "critical_asset", critical=True, privileges=("restricted",))
    )

    network.connect("internet", "web01")
    network.connect("web01", "app01")
    network.connect("app01", "work01")
    network.connect("app01", "db01")
    network.connect("db01", "critical01")
    return network
