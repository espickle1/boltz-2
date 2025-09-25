## User-friendlier site to use Boltz-2 (for the Maresso Group and friends)

### Boltz-2:
[Boltz-2](https://github.com/jwohlwend/boltz) is a fast deep learning model for biomolecular interaction prediction - in this case, protein(s) to __any__ ligand(s). Boltz-1 was the first open source model that approached AlphaFold3 in terms of structural accuracy prediction, and Boltz-2 is an improvement upon Boltz-1. Most importantly, Boltz has no restrictions on what ligand to model. As long as you can find Protein Data Bank identifier or SMILES molecular description, you are good to go!

### Steps:
1. Create and download input file with sequence and ligand information. [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/espickle1/boltz-2/blob/main/src/input_config.ipynb)<br/>(Here are some sample input files: [data](https://github.com/espickle1/boltz-2/tree/main/data))
3. Run Boltz-2 by uploading the input file. [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/espickle1/boltz-2/blob/main/src/boltz_2_prediction.ipynb)

### References:
[Boltz-2](https://www.biorxiv.org/content/10.1101/2025.06.14.659707v1) ; 
[Boltz-1](https://www.biorxiv.org/content/10.1101/2024.11.19.624167v4) ; 
[ColabFold MSA generation](https://pubmed.ncbi.nlm.nih.gov/35637307/)

---

Note: Special thanks to ChatGPT for helping me create this repository in a single day. 😇
