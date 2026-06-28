"""
Embodied-carbon benefit of reusing reclaimed lumber (addresses the problem
statement's "embodied-carbon goals").

Two sourced, separable climate effects per unit reused:

1. Avoided manufacturing emissions, not producing new softwood lumber.
   Canadian softwood, cradle-to-gate (A1-A3): about 62 kg CO2e per m3.
   Source: "A Review of Cradle-to-Gate GHG Emission Factors for Canada's
   Harvested Wood Products" (2024); Athena Institute, Cradle-to-Gate LCA of
   Canadian Surfaced Dry Softwood Lumber (2018).

2. Biogenic carbon kept in use, the carbon locked in the wood that stays out of
   the atmosphere while the wood remains in service rather than being landfilled
   or burned. About 785 kg CO2e per m3 of surfaced dry softwood lumber.
   Source: Athena Institute, Cradle-to-Gate LCA of Canadian Surfaced Dry
   Softwood Lumber (2018).

Displacement sanity check: reusing a tonne of timber emits about 30 kg CO2e
versus about 310 kg for virgin supply, roughly 280 kg CO2e/tonne avoided
(UK Forest Research, 2025; Community Wood Recycling, 2026).

Policy hook: Toronto Green Standard v4 lets reused or salvaged components count
as zero upfront embodied carbon against its 350 (Tier 2) and 250 (Tier 3)
kg CO2e/m2 caps, so reclaimed lumber directly helps developers meet the cap.
"""

BF_TO_M3 = 0.0023597  # one board foot = 1/12 cubic foot
AVOIDED_PRODUCTION_KG_PER_M3 = 62.0
BIOGENIC_STORED_KG_PER_M3 = 785.0

# Toronto Green Standard v4 embodied-carbon caps (kg CO2e/m2), for context.
TGS_TIER2_CAP = 350
TGS_TIER3_CAP = 250


def avoided_production_t(board_feet):
    """Tonnes CO2e of new-lumber manufacturing avoided by reusing this volume."""
    return board_feet * BF_TO_M3 * AVOIDED_PRODUCTION_KG_PER_M3 / 1000.0


def biogenic_stored_t(board_feet):
    """Tonnes CO2e of biogenic carbon kept in use by reusing this volume."""
    return board_feet * BF_TO_M3 * BIOGENIC_STORED_KG_PER_M3 / 1000.0


def total_benefit_t(board_feet):
    """Avoided manufacturing plus biogenic carbon kept in use (tonnes CO2e)."""
    return avoided_production_t(board_feet) + biogenic_stored_t(board_feet)
