import pandas as pd
import numpy as np
import os


def prepare_symptoms_array(symptoms):
    '''
    Convert a list of symptoms to a ndim(X) (in this case 131) that matches the
    dataframe used to train the machine learning model

    Output:
    - X (np.array) = X values ready as input to ML model to get prediction
    '''
    symptoms_array = np.zeros((1,133))
    # Get the directory of the Frontend folder
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(script_dir, "data")
    df = pd.read_csv(os.path.join(data_dir, 'clean_dataset.tsv'), sep='\t')
    
    for symptom in symptoms:
        symptom_idx = df.columns.get_loc(symptom)
        symptoms_array[0, symptom_idx] = 1

    return symptoms_array