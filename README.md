## User-friendy interface for Boltz-2 (for the Maresso Lab)

### Boltz-2:
[Boltz-2](https://github.com/jwohlwend/boltz) is a fast deep learning model for biomolecular interaction prediction - in this case, protein(s) to __any__ ligand(s). Boltz-1 was the first open source model that approached AlphaFold3 in terms of structural accuracy prediction, and Boltz-2 is an improvement upon Boltz-1. Most importantly, Boltz has no restrictions on what ligand to model. As long as you can find Protein Data Bank identifier or SMILES molecular description, you are good to go!

### Steps:
1. Create and download input file with sequence and ligand information. [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/espickle1/boltz-2/blob/main/src/input_config.ipynb)<br/>(Here are some sample input files: [data](https://github.com/espickle1/boltz-2/tree/main/data))
2. Run Boltz-2 by uploading the input file. [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/espickle1/boltz-2/blob/main/src/boltz_2_prediction.ipynb)

**Note: This code for Boltz-2 requires GPU to run (change to GPU by going to Runtime -> Change runtime type). Boltz-2 needs a lot of memory. Since free version of Google Colab typically only allows GPU with smaller memory, please consider only running the binding subunit if you are interested in modeling bigger complexes.

### References:
[Boltz-2](https://www.biorxiv.org/content/10.1101/2025.06.14.659707v1) ; 
[Boltz-1](https://www.biorxiv.org/content/10.1101/2024.11.19.624167v4) ; 
[ColabFold MSA generation](https://pubmed.ncbi.nlm.nih.gov/35637307/)
