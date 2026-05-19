import pandas as pd

def load_probe_annotations(filepath='data/GPL570-55999.txt') -> dict:
    """Load GPL570 annotation file and return probe_id -> description mapping"""
    df = pd.read_csv(filepath, sep='\t', comment='#', low_memory=False)
    
    probe_map = {}
    for _, row in df.iterrows():
        probe_id = str(row.get('ID', '')).strip()
        gene_symbol = str(row.get('Gene Symbol', '')).strip()
        gene_title = str(row.get('Gene Title', '')).strip()
        bio_process = str(row.get('Gene Ontology Biological Process', '')).strip()
        
        if not probe_id or probe_id == 'nan':
            continue
            
        description = ""
        if gene_symbol and gene_symbol != 'nan':
            description += f"Gene: {gene_symbol}"
        if gene_title and gene_title != 'nan':
            description += f" ({gene_title})"
        if bio_process and bio_process != 'nan':
            # Just grab the first process, they can be very long
            first_process = bio_process.split('//')[1].strip() if '//' in bio_process else bio_process
            description += f". Biological process: {first_process}"
            
        probe_map[probe_id] = description
    
    return probe_map

def annotate_genes(gene_list: list, probe_map: dict) -> str:
    """Take a list of probe IDs and return biological context string"""
    annotations = []
    for gene in gene_list:
        desc = probe_map.get(str(gene).strip())
        if desc and desc.strip():
            annotations.append(f"{gene}: {desc}")
    
    if not annotations:
        return ""
    return "Gene annotations:\n" + "\n".join(annotations)