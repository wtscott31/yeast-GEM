"""
Functions for importing and exporting the yeast model using COBRA from anywhere in the repo.
"""

from cobra.io import read_sbml_model, write_sbml_model
from dotenv import find_dotenv
from os.path import dirname

# find .env + define paths:
dotenv_path = find_dotenv()
repo_path = dirname(dotenv_path)
MODEL_PATH = f"{repo_path}/ModelFiles/xml/yeastGEM.xml"

def read_yeast_model(make_bigg_compliant=False):
    """Reads the SBML file of the yeast model using COBRA.

    Parameters
    ----------
    make_bigg_compliant : bool, optional
        Whether the model should be initialized with BiGG compliance or not.
        If false, the original ids/names/compartments will be used instead.

    Returns
    -------
    cobra.core.Model
    """

    # Load model:
    model = read_sbml_model(MODEL_PATH)

    # Check if already BiGG compliant:
    is_bigg_compliant = "x" in model.compartments

    # Convert to BiGG compliant if not already:
    if not is_bigg_compliant and make_bigg_compliant:
        # Metabolite changes:
        comp_dic = {"er":"r", "erm":"rm", "p":"x"}
        for met in model.metabolites:
            # Save original id in notes:
            met.notes["Original ID"] = met.id
            # Change name to not include compartment at the end:
            met.name = met.name.replace(f" [{model.compartments[met.compartment]}]", "")
            # Change compartment info:
            if met.compartment in comp_dic:
                met.compartment = comp_dic[met.compartment]
            # Update id with BiGG information:
            if "bigg.metabolite" in met.annotation:
                met.id = f"{met.annotation['bigg.metabolite']}_{met.compartment}"
            else:
                met.id = met.id.replace(f"[{met.compartment}]", f"_{met.compartment}")

        # Compartment changes:
        comps = model.compartments
        comps["r"] = "endoplasmic reticulum"
        comps["rm"] = "endoplasmic reticulum membrane"
        comps["x"] = "peroxisome"
        model.compartments = comps

        # Reaction changes:
        for rxn in model.reactions:
            # Update id with BiGG information:
            if "bigg.reaction" in rxn.annotation:
                rxn.notes["Original ID"] = rxn.id
                rxn.id = rxn.annotation['bigg.reaction']

    return model

def write_yeast_model(model):
    """Writes the SBML file of the yeast model using COBRA.

    Parameters
    ----------
    model : cobra.core.Model
        Yeast model to be written
    """
    write_sbml_model(model, MODEL_PATH)
