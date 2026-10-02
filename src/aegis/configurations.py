"""Reproducible synthetic enterprise network configuration generation."""

from __future__ import annotations

import random
from dataclasses import dataclass

from aegis.network import EnterpriseNetwork, Host, Vulnerability


@dataclass(frozen=True)
class ConfigurationRecord:
    """A generated configuration and the seed that defines it."""

    configuration_id: str
    seed: int


@dataclass(frozen=True)
class ConfigurationSplit:
    """Deterministic train/familiar/unseen configuration IDs."""

    train: tuple[ConfigurationRecord, ...]
    familiar: tuple[ConfigurationRecord, ...]
    unseen: tuple[ConfigurationRecord, ...]


def generate_network(
    *,
    configuration_id: str,
    seed: int,
) -> EnterpriseNetwork:
    """Generate one connected six-host enterprise configuration.

    V1 varies internal topology/connectivity while keeping host roles and
    synthetic vulnerability semantics fixed. This isolates topology exposure
    as the first controlled form of network-configuration diversity.
    """

    rng = random.Random(seed)
    network = EnterpriseNetwork(configuration_id, seed)

    hosts = (
        Host("internet", "external_entry"),
        Host(
            "web01",
            "web_server",
            vulnerabilities=[Vulnerability("SYNTH_WEB_01", "none")],
        ),
        Host(
            "app01",
            "application_server",
            vulnerabilities=[Vulnerability("SYNTH_APP_01", "user")],
        ),
        Host(
            "work01",
            "workstation",
            vulnerabilities=[Vulnerability("SYNTH_WORK_01", "none")],
        ),
        Host(
            "db01",
            "database_server",
            vulnerabilities=[Vulnerability("SYNTH_DB_01", "admin")],
        ),
        Host(
            "critical01",
            "critical_asset",
            critical=True,
            vulnerabilities=[Vulnerability("SYNTH_CRITICAL_01", "admin")],
        ),
    )

    for host in hosts:
        network.add_host(host)

    network.connect("internet", "web01")

    internal_hosts = [
        "web01",
        "app01",
        "work01",
        "db01",
        "critical01",
    ]
    rng.shuffle(internal_hosts)

    # Random spanning tree guarantees that every host remains reachable.
    for index in range(1, len(internal_hosts)):
        source = internal_hosts[index]
        target = rng.choice(internal_hosts[:index])
        network.connect(source, target)

    # Optional additional internal links create controlled topology diversity.
    existing = {
        frozenset(edge)
        for edge in network.graph.edges
    }
    candidates = [
        ("web01", "work01"),
        ("web01", "db01"),
        ("web01", "critical01"),
        ("app01", "db01"),
        ("app01", "critical01"),
        ("work01", "db01"),
        ("work01", "critical01"),
        ("db01", "critical01"),
    ]

    for source, target in candidates:
        if frozenset((source, target)) in existing:
            continue
        if rng.random() < 0.25:
            network.connect(source, target)

    return network


def build_configuration_pool(
    *,
    count: int,
    seed_start: int = 0,
    id_prefix: str = "NET",
) -> tuple[ConfigurationRecord, ...]:
    """Return deterministic configuration records for a seed sequence."""

    if count <= 0:
        raise ValueError("count must be positive")
    if not id_prefix:
        raise ValueError("id_prefix must not be empty")

    return tuple(
        ConfigurationRecord(
            configuration_id=f"{id_prefix}_{seed:05d}",
            seed=seed,
        )
        for seed in range(seed_start, seed_start + count)
    )


def build_configuration_split(
    *,
    train_count: int,
    familiar_count: int,
    unseen_count: int,
    seed_start: int = 0,
) -> ConfigurationSplit:
    """Create non-overlapping deterministic configuration splits."""

    counts = (train_count, familiar_count, unseen_count)
    if any(count <= 0 for count in counts):
        raise ValueError("all split counts must be positive")

    records = build_configuration_pool(
        count=sum(counts),
        seed_start=seed_start,
    )

    train_end = train_count
    familiar_end = train_count + familiar_count

    return ConfigurationSplit(
        train=records[:train_end],
        familiar=records[train_end:familiar_end],
        unseen=records[familiar_end:],
    )
