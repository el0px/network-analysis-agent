GENE_KB = {
    "MAPK1": "A key kinase in the MAPK/ERK signaling pathway. Activated by growth factors and promotes cell proliferation and survival. Frequently overactivated in cancer.",
    "MAPK3": "Works alongside MAPK1 in the ERK cascade. Phosphorylates transcription factors that drive cell growth. Co-activation with MAPK1 amplifies proliferation signals.",
    "RAF1": "Upstream activator of the MAPK cascade. Receives signals from RAS proteins and passes them down to MEK and ERK. Mutations cause constitutive pathway activation in cancer.",
    "BRAF": "A RAF family kinase. The BRAF V600E mutation is one of the most common cancer mutations, found in melanoma, thyroid, and colon cancers. Directly activates MEK.",
    "MAP2K1": "Also called MEK1. Acts as a relay between RAF and ERK (MAPK1/3). Inhibiting MEK is a major cancer drug strategy.",
    "KRAS": "A RAS GTPase that acts as an on/off switch for the MAPK pathway. KRAS mutations lock it permanently 'on', driving uncontrolled growth. Mutated in ~25% of all cancers.",
    "EGFR": "A cell surface receptor that activates both MAPK and PI3K pathways when bound by growth factors. Targeted by drugs like erlotinib in lung cancer.",
    "PIK3CA": "The catalytic subunit of PI3K. When activated, generates signals that promote cell survival and growth via AKT. Frequently mutated in breast and ovarian cancer.",
    "AKT1": "A central survival kinase downstream of PI3K. Promotes cell survival by inhibiting apoptosis and activating mTOR. Often overactivated in cancer.",
    "AKT2": "An AKT isoform particularly important in metabolic regulation and insulin signaling. Also promotes cell survival downstream of PI3K.",
    "MTOR": "A master regulator of cell growth and metabolism. Integrates signals from PI3K-AKT and nutrients to control protein synthesis. Target of rapamycin drugs.",
    "PTEN": "A tumor suppressor that opposes PI3K by breaking down its lipid products. Loss of PTEN leads to constitutive AKT activation. One of the most commonly lost tumor suppressors.",
    "PDK1": "Activates AKT by phosphorylation downstream of PI3K. A key relay node in the PI3K-AKT survival pathway.",
    "TP53": "Called the 'guardian of the genome.' Activated by DNA damage and stress signals from both MAPK and PI3K pathways. Triggers cell cycle arrest or apoptosis. Mutated in over 50% of all human cancers. Its connections across multiple pathways make it a network hub.",
    "MDM2": "The primary negative regulator of p53. Binds p53 and marks it for degradation. Forms a feedback loop — p53 activates MDM2, which then destroys p53.",
    "CDKN1A": "Also called p21. A p53 target gene that inhibits CDK proteins to halt the cell cycle, giving the cell time to repair DNA damage.",
    "BAX": "A pro-apoptotic protein activated by p53. When DNA damage is too severe to repair, p53 activates BAX to trigger programmed cell death.",
    "BCL2": "An anti-apoptotic protein that opposes BAX. High BCL2 expression helps cancer cells survive. The negative correlation with p53 pathway genes reflects this antagonism.",
    "CCND1": "Cyclin D1. Drives cells through the G1 phase of the cell cycle by activating CDK4 and CDK6. Overexpressed in many cancers.",
    "CDK4": "Pairs with Cyclin D1 to phosphorylate and inactivate RB1, pushing cells into division. A major drug target — CDK4/6 inhibitors are used in breast cancer.",
    "CDK6": "Works alongside CDK4 to overcome the RB1 brake on cell division. CDK4/6 inhibitors block both.",
    "RB1": "The retinoblastoma protein. Acts as a brake on cell division. When phosphorylated by CDK4/6 it releases E2F transcription factors. Loss of RB1 is a hallmark of many cancers.",
    "E2F1": "A transcription factor released when RB1 is inactivated. Drives expression of genes needed for DNA replication and cell division.",
    "CCNB1": "Cyclin B1. Partners with CDK1 to drive cells through the G2/M transition — the final checkpoint before cell division.",
    "NFKB1": "The master transcription factor of the NF-kB inflammatory pathway. When activated, it drives expression of dozens of inflammatory genes and promotes cancer cell survival.",
    "RELA": "The p65 subunit of NF-kB. Forms the active transcription complex and directly binds DNA to activate inflammatory gene expression.",
    "TNF": "Tumor necrosis factor. A key inflammatory cytokine that can both activate NF-kB and trigger apoptosis depending on context. Central to inflammatory signaling.",
    "IL6": "Interleukin-6. A cytokine produced downstream of NF-kB that promotes inflammation, immune cell recruitment, and cancer cell survival. Elevated in many cancers.",
    "IL1B": "Interleukin-1 beta. An upstream activator of NF-kB and a potent inflammatory mediator. Part of the inflammasome complex.",
    "IKBKB": "The kinase that activates NF-kB by phosphorylating its inhibitor IkB, freeing NF-kB to enter the nucleus.",
    "CXCL8": "Also called IL-8. A chemokine produced by NF-kB that recruits immune cells and promotes tumor angiogenesis.",
    "CTNNB1": "Beta-catenin. The central mediator of Wnt signaling. When Wnt is active, beta-catenin enters the nucleus and activates MYC and other growth genes.",
    "APC": "Adenomatous polyposis coli. Part of the destruction complex that degrades beta-catenin when Wnt is off. APC mutations cause familial colon cancer.",
    "GSK3B": "Part of the beta-catenin destruction complex alongside APC. Phosphorylates beta-catenin to mark it for degradation.",
    "AXIN1": "A scaffold protein in the destruction complex. Coordinates APC and GSK3B to efficiently degrade beta-catenin.",
    "MYC": "A transcription factor activated by Wnt/beta-catenin. One of the most potent drivers of cell proliferation. Overexpressed in the majority of human cancers.",
    "LRP6": "A Wnt co-receptor on the cell surface. When bound by Wnt ligands, it inactivates the destruction complex, allowing beta-catenin to accumulate.",
    "GAPDH": "A glycolytic enzyme used as a housekeeping gene in expression studies. Expression is relatively constant across conditions — should appear as a singleton with no strong pathway correlations.",
    "ACTB": "Beta-actin. A structural cytoskeletal protein used as a housekeeping reference gene. Like GAPDH, its stable expression means it should not correlate strongly with pathway genes.",
    "B2M": "Beta-2-microglobulin. A component of MHC class I molecules. Used as a housekeeping reference. Should appear as a singleton.",
}

def get_gene_context(gene_names: list) -> str:
    entries = []
    for gene in gene_names:
        gene_upper = gene.upper()
        if gene_upper in GENE_KB:
            entries.append(f"{gene_upper}: {GENE_KB[gene_upper]}")
    if not entries:
        return ""
    return "Gene biological context:\n" + "\n".join(entries)