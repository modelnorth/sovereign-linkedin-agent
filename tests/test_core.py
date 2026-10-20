"""
Tests for ModelNorth Sovereign LinkedIn Agent
https://modelnorth.com
"""

import tempfile
from pathlib import Path
import pytest
from sovereign_linkedin.config import AgentConfig, SafetyLimits
from sovereign_linkedin.core.vault import SessionVault
from sovereign_linkedin.core.governor import SafetyGovernor
from sovereign_linkedin.core.stealth import StealthEngine
from sovereign_linkedin.modules.lead_scout import LeadScout, Prospect
from sovereign_linkedin.modules.outreach import OutreachSynthesizer


def test_config_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AgentConfig()
        config.vault_dir = Path(tmpdir)
        assert config.brand.brand_name == "ModelNorth"
        assert config.brand.website == "https://modelnorth.com"
        assert config.safety.daily_connect_limit == 25


def test_safety_governor():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = SessionVault(Path(tmpdir))
        limits = SafetyLimits(daily_connect_limit=2, daily_message_limit=2)
        governor = SafetyGovernor(limits, vault)

        assert governor.can_send_invite() is True
        governor.record_action("invite")
        assert governor.can_send_invite() is True
        governor.record_action("invite")
        assert governor.can_send_invite() is False


def test_lead_scout_seniority_scoring():
    # High title match with GCC location
    score, notes = LeadScout.calculate_seniority_score(
        "Chief Technology Officer at Sovereign Cloud",
        location="Dubai, UAE"
    )
    assert score >= 95
    assert any("Title seniority match" in n for n in notes)
    assert any("GCC" in n for n in notes)

    # General title without boost
    score2, _ = LeadScout.calculate_seniority_score("Junior Associate", location="London, UK")
    assert score2 <= 50


def test_outreach_synthesizer_constraints():
    prospect = Prospect(
        name="Tariq Al-Hashimi",
        headline="Chief Information Security Officer | Air-Gapped Infrastructure",
        profile_url="https://linkedin.com/in/sample",
        current_company="Gulf Defense Matrix",
        location="Abu Dhabi, UAE"
    )

    # Assert connection note is STRICTLY <= 300 chars
    note = OutreachSynthesizer.synthesize_invite_note(prospect, angle="sovereign")
    assert len(note) <= 300
    assert "Tariq" in note
    assert "ModelNorth" in note
    assert "modelnorth.com" in note

    # Assert direct message contains ModelNorth positioning
    dm = OutreachSynthesizer.synthesize_direct_message(prospect)
    assert "Tariq" in dm
    assert "ModelNorth (modelnorth.com)" in dm
    assert "Air-gapped on-premise foundation model" in dm


def test_stealth_bezier_trajectory():
    start = (100.0, 100.0)
    end = (500.0, 500.0)
    points = 20
    trajectory = StealthEngine.calculate_bezier_trajectory(start, end, points=points)
    assert len(trajectory) == points + 1
    # Check bounds
    assert abs(trajectory[0][0] - start[0]) < 2.0
    assert abs(trajectory[-1][0] - end[0]) < 2.0


def test_lead_scout_clean_helpers():
    raw_name = "Tariq Al-Mansoor • 2nd\nView Tariq's profile"
    cleaned = LeadScout.clean_name(raw_name)
    assert cleaned == "Tariq Al-Mansoor"

    raw_url = "https://www.linkedin.com/in/tariq-al-mansoor?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3A12345"
    cleaned_url = LeadScout.clean_url(raw_url)
    assert cleaned_url == "https://www.linkedin.com/in/tariq-al-mansoor"
