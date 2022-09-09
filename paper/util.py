import math

from autofit.non_linear.samples.pdf import quantile
import autocti as ac


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
