
import gzip
import tempfile

import streamlit as st

import py3Dmol
import parmed

from rdkit.Chem import AllChem as Chem


class MetaViewer(py3Dmol.view):

    def __init__(self):
        super().__init__(width=1000, height=800)
        self.removeAllModels()
        self.setBackgroundColor(0x000000)

        # Set simple parameters
        self.n_ligands = 0
        self.rec_model = None
        self.rec_path = None
        self.colors = list(mcolors.CSS4_COLORS.keys())

    def add_receptor(self, path):
        if '.pdb' in path:
            self.rec_path = path
            self.addModel(open(path, 'r').read(), 'pdb')
            self.rec_model = self.getModel()
            self.rec_model.setStyle({}, {'cartoon': {'color': '#44546A'}})

    def add_ligand(self, path, keepHs=False, color=None):
        if color is None:
            color = self.colors[self.n_ligands]
        if ('.sdfgz' in path) or ('.sdf.gz' in path):
            with gzip.open(path) as rf:
                suppl = Chem.ForwardSDMolSupplier(rf, removeHs=False)
                for i, m in enumerate(suppl):
                    if i == 0:
                        self.addModel(Chem.MolToMolBlock(m), 'mol', {'keepH': keepHs})
                        model = self.getModel()
                        model.setStyle({}, {'stick': {"colorscheme": f'{color}Carbon'}})  # #ED7D31 orange
                        self.n_ligands += 1
        elif '.sdf' in path:
            self.addModel(open(path, 'r').read(), 'sdf', {'keepH': keepHs})
            model = self.getModel()
            model.setStyle({}, {'stick': {"colorscheme": f'{color}Carbon'}})
            self.n_ligands += 1
        elif '.pdb' in path:
            self.addModel(path, 'pdb')
            model = self.getModel()
            model.setStyle({}, {'stick': {"colorscheme": f'{color}Carbon'}})
            self.n_ligands += 1
        else:
            st.write('Unknown format, ligand must be sdf or pdb')

    def add_surface(self, surface):
        rec = {'resn': ["AQD", "UNL"], 'invert': 1}
        if surface is not None:
            if surface == 'VDW':
                self.addSurface(py3Dmol.VDW, {'opacity': 0.75, 'color': 'white'}, rec)
            if surface == 'MS':
                self.addSurface(py3Dmol.MS, {'opacity': 0.75, 'color': 'white'}, rec)
            if surface == 'SAS':
                self.addSurface(py3Dmol.SAS, {'opacity': 0.75, 'color': 'white'}, rec)
            if surface == 'SES':
                self.addSurface(py3Dmol.SES, {'opacity': 0.75, 'color': 'white'}, rec)

    def label_receptor(self):
        structure = parmed.read_PDB(self.rec_path)
        self.addResLabels({'resi': [n.number for n in structure.residues]},
                            {'font': 'Arial', 'fontColor': 'white', 'showBackground': 'false',
                            'fontSize': 10})

    def get_residues(self):
        if self.rec_path is not None:
            structure = parmed.read_PDB(self.rec_path)
            return [r.number for r in structure.residues]
        else:
            return []

    def show_residue(self, number):
        self.rec_model.setStyle({'resi': number}, {'stick': {'colorscheme': 'darkslategrayCarbon'}})

    def render2st(self):
        # ----- render -----
        self.zoomTo({'model': -1})  # Zoom to last model
        #self.zoomTo()
        self.render()

        t = self.js()
        with tempfile.NamedTemporaryFile(mode='w+t', suffix='.html') as tfile:
            f = open(tfile.name, 'w')
            f.write(t.startjs)
            f.write(t.endjs)
            f.close()

            st.components.v1.html(open(tfile.name, 'r').read(), width=1200, height=800)    