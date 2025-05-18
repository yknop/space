from enum import Enum


class Disruptions(Enum):
    SATURATION = "saturation"
    SMEAR = "smear"
    BLUR = "blur"
    CUT_IMAGE = "cut_image"
