import pytest

from forge_cli.utils.key_manager import RoundRobinKeyManager


def test_round_robin_key_manager_single_key() -> None:
    manager = RoundRobinKeyManager(["key1"])
    assert manager.get_key() == "key1"
    assert manager.next_key() == "key1"


def test_round_robin_key_manager_multiple_keys() -> None:
    manager = RoundRobinKeyManager(["key1", "key2"])
    assert manager.get_key() == "key1"
    assert manager.next_key() == "key2"
    assert manager.get_key() == "key2"
    assert manager.next_key() == "key1"


def test_round_robin_key_manager_empty() -> None:
    with pytest.raises(ValueError):
        RoundRobinKeyManager([])
