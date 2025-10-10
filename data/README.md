## Input file primer

Sequences: Any valid sequence in fasta format works

Ligand: One can use either Chemical Component Dictionary identifier (ccd) or SMILES string.<br/>
Examples: ccd: FE for iron(III), HEM for heme, CC(=O)NC1=CC=C(C=C1)O for acetaminophen (tylenol)<br/>
These can be searched by
  1. For Chemical Component Dictionary (ccd): [PDBeChem: Ligand Dictionary](https://www.ebi.ac.uk/pdbe-srv/pdbechem/).
  2. For SMILES: Both Ligand Dictionary and [PubChem](https://pubchem.ncbi.nlm.nih.gov/).

Binding: This is expressed in terms of "constraints" where "binder" is the ligand chain id and "contacts" is the protein chain id and amino acid residue number.

An example input file (.yaml) would look something like the following:
```
sequences:
  - protein:
      id: [a, b, c]
      sequence: LNGRGATGSMRGVVKLTTQAG...
  - protein:
      id: [d]
      sequence: MAIETNAVVVTDLNPLYPRDR...
  - ligand:
      id: FE
      ccd: FE
  - ligand:
      id: kdo3
      smiles: 'C1[C@H]([C@H]([C@H](O[C@]1(C(=O)O)O[C@@H]2C[C@@](O[C@@H]([C@@H]2O)[C@@H](CO)O)(C(=O)O)O)[C@@H](CO)O)O)O'
constraints:
  - pocket:
      binder: kdo3
      contacts: [[a, ...], [b, ...]]
properties:
  - affinity:
      binder: kdo3
```
