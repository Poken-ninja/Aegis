"""Tests for reproducible network configuration generation."""

from aegis.configurations import (
    build_configuration_pool,
    build_configuration_split,
    generate_network,
)


def _edges(network):
    return {frozenset(edge) for edge in network.graph.edges}


def test_generated_configuration_is_reproducible() -> None:
    first = generate_network(configuration_id="NET_A", seed=7)
    second = generate_network(configuration_id="NET_B", seed=7)

    assert _edges(first) == _edges(second)
    assert [
        (
            host.host_id,
            host.role,
            host.critical,
            tuple(
                (vulnerability.vulnerability_id, vulnerability.required_privilege)
                for vulnerability in host.vulnerabilities
            ),
        )
        for host in first.hosts()
    ] == [
        (
            host.host_id,
            host.role,
            host.critical,
            tuple(
                (vulnerability.vulnerability_id, vulnerability.required_privilege)
                for vulnerability in host.vulnerabilities
            ),
        )
        for host in second.hosts()
    ]


def test_configuration_seed_changes_topology_for_some_seed() -> None:
    reference = generate_network(configuration_id="NET_A", seed=0)
    different = generate_network(configuration_id="NET_B", seed=1)

    assert _edges(reference) != _edges(different)


def test_generated_configuration_remains_connected() -> None:
    network = generate_network(configuration_id="NET_A", seed=19)

    assert len(network.graph.nodes) == 6
    assert len(network.graph.edges) >= 5


def test_configuration_pool_is_deterministic_and_non_overlapping() -> None:
    first = build_configuration_pool(count=4, seed_start=10)
    second = build_configuration_pool(count=4, seed_start=10)

    assert first == second
    assert len({record.configuration_id for record in first}) == 4
    assert len({record.seed for record in first}) == 4


def test_configuration_split_is_reproducible_and_disjoint() -> None:
    split = build_configuration_split(
        train_count=4,
        familiar_count=2,
        unseen_count=3,
        seed_start=100,
    )

    groups = [split.train, split.familiar, split.unseen]
    ids = [record.configuration_id for group in groups for record in group]

    assert [len(group) for group in groups] == [4, 2, 3]
    assert len(ids) == len(set(ids))
    assert split == build_configuration_split(
        train_count=4,
        familiar_count=2,
        unseen_count=3,
        seed_start=100,
    )
