import math
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import os
from os import path


from autoconf import conf
from autofit.non_linear.samples.pdf import quantile
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

agg = af.Aggregator.from_database(filename="uniform.sqlite", completed_only=True)

plot_path = path.join(workspace_path, "paper", "images_old", "require")

if not os.path.exists(plot_path):
    os.makedirs(plot_path)

agg_query = agg
agg_query = agg_query.query(agg_query.search.name == "search[2]_parallel[x2]")
# agg_query = agg_query.query(agg_query.model.cti.serial_trap_list.density > 0.0)

parallel_trap_0 = ac.TrapInstantCapture(density=0.214, release_timescale=1.25)
parallel_trap_1 = ac.TrapInstantCapture(density=0.412, release_timescale=4.4)
parallel_trap_list = [parallel_trap_0, parallel_trap_1]

input_delta_ellipticity = sum(trap.delta_ellipticity for trap in parallel_trap_list)

median_list = []
error_list = []

resolution_list = ["low", "mid", "high", "x2", "x4"]

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

        sigma = 2.0
        low_limit = (1 - math.erf(sigma / math.sqrt(2))) / 2

        median = quantile(x=delta_ellipticity_list, q=0.5, weights=weight_list)[0]
        lower_error = quantile(
            x=delta_ellipticity_list, q=low_limit, weights=weight_list
        )[0]
        upper_error = quantile(
            x=delta_ellipticity_list, q=1 - low_limit, weights=weight_list
        )[0]

        error = (upper_error - lower_error) / 2.0

        median_list.append(median)
        error_list.append(error)

        print(median)
        print(error)

parallel_epers = [517 * 6, 1034 * 6, 2068 * 6, 4136 * 6]  # , 8272 * 6]

jitters = [-30.0, -10.0, 10.0, 30.0]

plt.figure(figsize=(13.0, 13.0))

parallel_epers_plot = list(
    map(lambda parallel_eper: parallel_eper + jitters[0], parallel_epers)
)

eb0 = plt.errorbar(
    x=parallel_epers_plot,
    y=median_list,
    yerr=[error_list, error_list],
    capsize=10,
    elinewidth=2,
    markeredgewidth=5,
    linestyle="-",
)
eb0[-1][0].set_linestyle("-")

eper_limits = [517 - 30, 1034 * 6, 2068 * 6, 4136 * 6, 8272 * 6 + 30]

lin1 = plt.plot(eper_limits, len(eper_limits) * [1.1e-4], linestyle="--", color="b")
plt.plot(eper_limits, len(eper_limits) * [-1.1e-4], linestyle="--", color="b")

plt.legend(
    handles=[
        eb0,
        #  eb1, eb2, eb3,
        lin1,
    ],
    labels=["Parallel x2", "Parallel x3", "Serial x2", "Serial x3"],
    loc="best",
    fontsize=22,
    frameon=False,
)
plt.tick_params(labelsize=16)
plt.xscale("log")
plt.xlim([517 - 100, 8272 * 6 + 100])
eper_ticks = [517, 1034, 2068, 517 * 6, 1034 * 6, 2068 * 6, 4136 * 6, 8272 * 6]
plt.yticks(fontsize=20)
plt.xticks(ticks=eper_ticks, labels=eper_ticks, fontsize=20)
plt.gca().yaxis.set_major_formatter(StrMethodFormatter("{x:,.4f}"))
plt.xlabel("$N_{\mathrm{EPER}}$", fontsize=24)
plt.ylabel(r"$\Delta e_{\rm 1}$", fontsize=24)
plt.savefig(path.join(plot_path, "requirement_accuracy_backup.png"))
plt.show()
