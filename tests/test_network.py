from aegis.network import build_reference_network


def test_reference_network_has_expected_hosts() -> None:
    network = build_reference_network()

    assert set(network.graph.nodes) == {
        "internet",
        "web01",
        "app01",
        "work01",
        "db01",
        "critical01",
    }


def test_reference_network_has_expected_connections() -> None:
    network = build_reference_network()

    expected_edges = {
        frozenset(("internet", "web01")),
        frozenset(("web01", "app01")),
        frozenset(("app01", "work01")),
        frozenset(("app01", "db01")),
        frozenset(("db01", "critical01")),
    }

    actual_edges = {frozenset(edge) for edge in network.graph.edges}
    assert actual_edges == expected_edges


def test_critical_asset_is_unique() -> None:
    network = build_reference_network()

    critical_hosts = [
        host for host in network.hosts()
        if host.critical
    ]

    assert [host.host_id for host in critical_hosts] == ["critical01"]


def test_reference_network_has_intended_privilege_requirements() -> None:
    network = build_reference_network()

    assert network.host("web01").vulnerabilities[0].required_privilege == "none"
    assert network.host("app01").vulnerabilities[0].required_privilege == "user"
    assert network.host("work01").vulnerabilities[0].required_privilege == "none"
    assert network.host("db01").vulnerabilities[0].required_privilege == "admin"
    assert (
        network.host("critical01").vulnerabilities[0].required_privilege
        == "admin"
    )


def test_reference_network_is_reproducibly_identified() -> None:
    first = build_reference_network(
        configuration_id="NET_00001",
        seed=123,
    )
    second = build_reference_network(
        configuration_id="NET_00001",
        seed=123,
    )

    assert first.configuration_id == second.configuration_id
    assert first.seed == second.seed
    assert set(first.graph.edges) == set(second.graph.edges)


def test_unknown_host_is_rejected() -> None:
    network = build_reference_network()

    try:
        network.host("does_not_exist")
    except KeyError as exc:
        assert "Unknown host" in str(exc)
    else:
        raise AssertionError("Unknown host should raise KeyError")


def test_self_connection_is_rejected() -> None:
    network = build_reference_network()

    try:
        network.connect("web01", "web01")
    except ValueError as exc:
        assert "Self-connections" in str(exc)
    else:
        raise AssertionError(
            "Self-connection should raise ValueError"
        )