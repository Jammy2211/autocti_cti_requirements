import os
from os import path
import pickle

from autoconf import conf

import autofit as af
import autocti as ac

import warnings


def input_delta_ellipticity_from(name):

    if (name == "parallel[x2]") or (name == "serial[x2]"):

        trap_0 = ac.TrapInstantCapture(density=0.214, release_timescale=1.25)
        trap_1 = ac.TrapInstantCapture(density=0.412, release_timescale=4.4)
        trap_list = [trap_0, trap_1]

    else:

        trap_0 = ac.TrapInstantCapture(density=0.07275, release_timescale=0.8)
        trap_1 = ac.TrapInstantCapture(density=0.21825, release_timescale=4.0)
        trap_2 = ac.TrapInstantCapture(density=6.54804, release_timescale=20.0)

        trap_list = [trap_0, trap_1, trap_2]

    return sum([trap.delta_ellipticity for trap in trap_list])


def median_error_from(delta_ellipticity_list, weight_list):

    import math
    from autofit.non_linear.samples.pdf import quantile

    sigma = 2.0
    low_limit = (1 - math.erf(sigma / math.sqrt(2))) / 2

    median = quantile(x=delta_ellipticity_list, q=0.5, weights=weight_list)[0]
    lower_error = quantile(x=delta_ellipticity_list, q=low_limit, weights=weight_list)[
        0
    ]
    upper_error = quantile(
        x=delta_ellipticity_list, q=1 - low_limit, weights=weight_list
    )[0]

    error = (upper_error - lower_error) / 2.0

    return median, error


warnings.filterwarnings("ignore")

# database_name = "uniform"
# database_name = "poisson"
# database_name = "non_uniform"
database_name = "cosmic_rays"

"""
__Database + Paths__
"""
workspace_path = os.getcwd()

config_path = path.join(workspace_path, "config")
conf.instance.push(new_path=config_path)

output_path = path.join(workspace_path, "output")

agg = af.Aggregator.from_database(
    filename=f"{database_name}.sqlite", completed_only=True
)

pickle_path = path.join(workspace_path, "paper", "pickles", "require")

agg_query = agg

if database_name == "poisson":

    name_list = ["parallel[x2]", "parallel[x3]"]

else:

    name_list = ["parallel[x2]", "parallel[x3]", "serial[x2]", "serial[x3]"]


resolution_list = ["low", "mid", "high", "x2", "x4"]

for name in name_list:

    if name == "parallel[x2]":
        search_name = "search"
    else:
        search_name = "search[1]"

    input_delta_ellipticity = input_delta_ellipticity_from(name=name)

    parallel_trap_0 = ac.TrapInstantCapture(density=0.214, release_timescale=1.25)
    parallel_trap_1 = ac.TrapInstantCapture(density=0.412, release_timescale=4.4)
    parallel_trap_list = [parallel_trap_0, parallel_trap_1]

    median_list = []
    error_list = []

    agg_query = agg.query(agg.search.name == f"{search_name}_{name}")

    for resolution in resolution_list:

        agg_res = agg_query.query(agg.search.unique_tag == resolution)

        for samples in agg_res.values("samples"):

            delta_ellipticity_list = []
            weight_list = []

            for i in range(samples.total_accepted_samples):

                instance = samples.instance_from_sample_index(sample_index=i)
                weight = samples.weight_list[i]

                if weight > 1.0e-4:

                    delta_ellipticity = (
                        instance.cti.delta_ellipticity - input_delta_ellipticity
                    )

                    delta_ellipticity_list.append(delta_ellipticity)
                    weight_list.append(weight)

            median, error = median_error_from(
                delta_ellipticity_list=delta_ellipticity_list, weight_list=weight_list
            )

            print(median, error)

            median_list.append(median)
            error_list.append(error)

    out_path = path.join(pickle_path, database_name, name)

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    with open(path.join(out_path, "median_list.pickle"), "wb") as f:
        pickle.dump(median_list, f)

    with open(path.join(out_path, "error_list.pickle"), "wb") as f:
        pickle.dump(error_list, f)
