import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import os
from os import path
import pickle

from autoconf import conf

import autofit as af
import autocti as ac
import warnings

warnings.filterwarnings("ignore")

"""
__Database + Paths__
"""
workspace_path = os.getcwd()

config_path = path.join(workspace_path, "config")
conf.instance.push(new_path=config_path)

output_path = path.join(workspace_path, "output")

plot_path = path.join(workspace_path, "paper", "images", "estimates")
pickle_path = path.join(workspace_path, "paper", "pickles", "estimates")

resolution_list = ["low", "mid", "high", "x2", "x4"]

sigma = 2.0

total_images = 1

name_list = ["parallel[x2]", "parallel[x3]", "serial[x2]", "serial[x3]"]

for name in name_list:

    median_pdf_image_list = []
    upper_error_image_list = []
    lower_error_image_list = []
    error_size_image_list = []

    if name == "parallel[x2]":
        search_name = f"search_{name}"
    else:
        search_name = f"search[1]_{name}"

    if "parallel" in name:

        database_name_list = [
            "uniform",
            "poisson",
            "non_uniform",
            "cosmic_rays",
        ]

    else:

        database_name_list = [
            "uniform",
            "non_uniform",
            "cosmic_rays",
        ]

    for database_name in database_name_list:

        median_pdf_resolution_list = []
        upper_error_resolution_list = []
        lower_error_resolution_list = []
        error_size_resolution_list = []

        from sqlalchemy import exc

        try:
            agg = af.Aggregator.from_database(
                filename=f"{database_name}.sqlite", completed_only=False
            )
        except exc.OperationalError:
            pass

        agg_query = agg.query(agg.search.name == search_name)

        for resolution in resolution_list:

            agg_res = agg_query.query(agg_query.search.unique_tag == resolution)

            samples = list(agg_res.values("samples"))[0]

            median_pdf_resolution_list.append(samples.median_pdf_vector)
            upper_error_resolution_list.append(
                samples.error_vector_at_upper_sigma(sigma=sigma)
            )
            lower_error_resolution_list.append(
                samples.error_vector_at_lower_sigma(sigma=sigma)
            )
            error_size_resolution_list.append(
                samples.error_vector_at_sigma(sigma=sigma)
            )

        median_pdf_image_list.append(median_pdf_resolution_list)
        upper_error_image_list.append(upper_error_resolution_list)
        lower_error_image_list.append(lower_error_resolution_list)
        error_size_image_list.append(error_size_resolution_list)

        out_path = path.join(pickle_path, name)

        os.makedirs(out_path, exist_ok=True)

        with open(path.join(out_path, "median_pdf_image_list.pickle"), "wb") as f:
            pickle.dump(median_pdf_image_list, f)

        with open(path.join(out_path, "upper_error_image_list.pickle"), "wb") as f:
            pickle.dump(upper_error_image_list, f)

        with open(path.join(out_path, "lower_error_image_list.pickle"), "wb") as f:
            pickle.dump(lower_error_image_list, f)

        with open(path.join(out_path, "error_size_image_list.pickle"), "wb") as f:
            pickle.dump(error_size_image_list, f)
