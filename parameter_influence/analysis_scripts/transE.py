from log_class import log_recorder
import traveler as tv
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt


Base_dir = "../io_option_advance"
log_file_container = tv.traveler_class(Base_dir)

total_file_count = len(log_file_container.LOG_dirs)
log_vector_container = []

limit = 1
i = 0

for log_file in log_file_container.file_dict:

    filename = log_file_container.file_dict[log_file]["LOG"]
    if "NVMeSSD" in filename:
        print("loaded file %s" % filename)
        log_vector_container.append(log_recorder(filename).to_vector())

        if i > limit:
            break
        i += 1

import torch

tensor1 = torch.from_numpy(log_vector_container[0].values).float() 
tensor2 = torch.from_numpy(log_vector_container[1].values).float() 
print(torch.cosine_similarity(tensor1,tensor2))