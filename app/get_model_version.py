"""
Module to check the model version.
"""

import h5py


def get_keras_model_version(model_path):
    """
    Get in whivh verison was the model created.
    """

    with h5py.File(model_path, 'r') as f:
        # Check for version attribute in the root group
        if 'keras_version' in f.attrs:
            keras_version = f.attrs['keras_version'].encode('utf-8')
        else:
            keras_version = "Unknown (possibly < Keras 2.0)"

        # Check for TensorFlow backend version (if applicable)
        if 'backend' in f.attrs:
            backend = f.attrs['backend'].encode('utf-8')
        else:
            backend = "Unknown"

        print(f"Keras version: {keras_version}")
        print(f"Backend: {backend}")


get_keras_model_version('assets/models/model_unet_light_new_better.h5')
