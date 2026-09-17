import pytest
from app.taxonomy.taxonomy import (
    get_domains,
    get_subcategories,
    is_valid_domain,
    is_valid_subcategory,
    TAXONOMY,
)


def test_get_domains():
    domains = get_domains()
    assert isinstance(domains, list)
    assert len(domains) == 12
    assert "Environment" in domains
    assert "Water Resources" in domains
    assert "Agriculture" in domains


def test_get_subcategories():
    env_subs = get_subcategories("Environment")
    assert "Pollution" in env_subs
    assert "Biodiversity" in env_subs

    invalid_subs = get_subcategories("NonExistentDomain")
    assert invalid_subs == []


def test_is_valid_domain():
    assert is_valid_domain("Education") is True
    assert is_valid_domain("Healthcare") is True
    assert is_valid_domain("InvalidDomain") is False


def test_is_valid_subcategory():
    assert is_valid_subcategory("Environment", "Pollution") is True
    assert is_valid_subcategory("Water Resources", "Leakage") is True
    assert is_valid_subcategory("Education", "Pollution") is False
    assert is_valid_subcategory("InvalidDomain", "Pollution") is False
