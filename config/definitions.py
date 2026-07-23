"""
Plain-language definitions of the variables shown across the app, rendered as
collapsible tables so a reader can look up any term without leaving the page.
Each entry is (Variable, Definition).
"""

# Supply cascade terms (Overview, Municipal baseline, Chain of evidence).
CASCADE_TERMS = [
    ("Gross wood content", "All the wood in a building: framing plus panels, sheathing, subfloor and finish."),
    ("Framing lumber", "The dimensional structural lumber (studs, joists, rafters), the reusable "
     "structural fraction the model tracks."),
    ("Recoverable", "Framing that survives the teardown method, the building's age condition, and "
     "contamination or engineered-wood losses."),
    ("Salvageable dimensional", "Recoverable lumber that then survives denailing, sorting and trimming "
     "to clean stock."),
    ("Spec-ready reusable", "Clean, dried dimensional lumber that passes a No.2-or-better structural "
     "regrade. The narrowest, highest-confidence category."),
    ("Reclaimed value", "The market value of the spec-ready lumber, priced per board foot by grade."),
]

# Cascade-strategy dimensions (Cascade strategy page).
CASCADE_DIMENSIONS = [
    ("Functionality", "How high up the material cascade a use sits; structural reuse is the highest use."),
    ("Value premium", "Reclaimed price as a multiple of commodity value; architectural runs 3 to 10 times."),
    ("Ease to unlock", "How few regulatory and technical barriers stand between the wood and this market."),
    ("Market today", "Roughly how much of this market already exists, rather than being future demand."),
    ("Speed", "How soon the market can realistically be served, from now to about a decade out."),
    ("Tier", "Legal today (Tier A, non-structural) versus code-gated (Tier B, structural reuse)."),
]

# Carbon terms (Embodied carbon page).
CARBON_TERMS = [
    ("Avoided manufacturing", "Emissions saved by not producing new softwood lumber (about 62 kg CO2e/m3)."),
    ("Avoided landfill methane", "Methane emissions avoided by keeping the wood out of landfill "
     "(about 217 kg CO2e per tonne of wood)."),
    ("Biogenic carbon kept in use", "Carbon stored in the wood that stays out of the air while the "
     "wood remains in service rather than being landfilled or burned."),
    ("Total climate benefit", "The sum of avoided manufacturing, avoided landfill methane, and "
     "biogenic carbon kept in use."),
]

# Data-quality tiers (the map colour and confidence bands).
DATA_QUALITY = [
    ("High", "A live municipal permit feed backs the demolition count; band about plus or minus 10 percent."),
    ("Medium", "A real StatCan demolition figure with the era split modelled; band about 25 percent."),
    ("Low", "No permit feed; the count is inferred from dwellings times a sourced rate; band about 45 percent."),
]
