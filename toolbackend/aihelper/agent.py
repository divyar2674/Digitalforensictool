# ai/agent.py

from .correlator import correlate_events
from .chain_builder import build_chains


def run_correlation_engine(events):
    grouped = correlate_events(events)

    chains, alerts = build_chains(grouped)

    return {
        "chains": chains,
        "alerts": alerts,
        "total_chains": len(chains)
    }