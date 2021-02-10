import pandas as pd
import utilities
import pickle
import numpy as np


def load_evmodel_data():
    """ Load different models from xlsx file and return a DataFrame with all the data. """
    model_df_path = utilities.get_param_dir() / "ev_models.xlsx"
    return pd.read_excel(model_df_path, index_col='Modell', engine='openpyxl')


def load_segments_and_probs():
    """ Load the different car segments and their relative frequency. """
    seg_path = utilities.get_param_dir() / "seg_prob_dict.pickle"
    seg_prob_dict = pickle.load(open(seg_path, "rb"))
    return zip(*seg_prob_dict.items())


class ElectricVehicleModel(object):
    MODEL_DF = load_evmodel_data()
    SEGMENTS, PROB_SEGMENT = load_segments_and_probs()

    def __init__(self):
        self.segment = self.choose_segment()
        self.model = self.choose_model(self.segment)
        self.capacity = self.MODEL_DF.at[self.model, "Batterie"]
        self.consumption = self.MODEL_DF.at[self.model, "Verbrauch"]

    @classmethod
    def choose_segment(cls):
        """ Choose the segment of the EV based on their respective probabilities. """
        choice = np.random.choice(cls.SEGMENTS, p=cls.PROB_SEGMENT)
        # Vorerst Wahl des häufigsten Segments bei keiner Angabe -> später überarbeiten
        if choice == 95:
            choice = 3
        return choice

    @classmethod
    def choose_model(cls, segment):
        """ Choose model randomly accross models from the particular segment """
        models = cls.MODEL_DF
        filt = models["Segment"] == segment
        choices = models[filt]
        pick = np.random.randint(0, len(choices))
        model = choices.index[pick]
        return model

