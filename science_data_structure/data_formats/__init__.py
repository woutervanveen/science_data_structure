from data_formats import general_formats
import numpy

available_types = {
    numpy.ndarray: general_formats.LeafNumpy 
}


available_extensions = {
    "npy": general_formats.LeafNumpy,
}


