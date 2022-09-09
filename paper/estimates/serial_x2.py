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

name = "serial[x2]"

out_path = path.join(pickle_path, name)

with open(path.join(out_path, "median_pdf_image_list.pickle"), "rb") as f:
    median_pdf_image_list = pickle.load(f)

with open(path.join(out_path, "upper_error_image_list.pickle"), "rb") as f:
    upper_error_image_list = pickle.load(f)

with open(path.join(out_path, "lower_error_image_list.pickle"), "rb") as f:
    lower_error_image_list = pickle.load(f)

with open(path.join(out_path, "error_size_image_list.pickle"), "rb") as f:
    error_size_image_list = pickle.load(f)

resolution_list = ["low", "mid", "high", "x2", "x4"]

sigma = 2.0
epers = [517, 1034, 2068, 4136, 8272]
input_model_parameters = [0.214, 1.25, 0.412, 4.4, 0.58]
ylabels = [r"$\rho_{1}$", r"$\rho_{2}$", r"$\tau_{1}$", r"$\tau_{2}$", r"$\beta$"]

total_params = len(input_model_parameters)

total_images = len(median_pdf_image_list)

plt.figure(figsize=(19.0, 12.0), dpi=100)
# plt.suptitle("Accuracy of Parallel CTI Model", fontsize=20)

ebs = []

jitters = [-40.0 * 6, -20.0 * 6, 0.0, 20.0 * 6, 40.0 * 6]

color_list = ["b", "r", "y", "cy", "m"]

for param_index in range(total_params):

    subplot_index = [1, 3, 5, 7, 9]

    plt.subplot(5, 2, subplot_index[param_index])

    epers_plot = [min(epers) + min(jitters), 1034, 2068, 4136, 8272]
    jitter_factors = [1.0, 2.0, 4.0, 9.0, 15.0]

    plt.plot(
        epers_plot,
        [input_model_parameters[param_index] for j in range(len(epers))],
        linestyle="--",
        linewidth=2,
        color="k",
    )

    for image_index in range(total_images):

        epers_plot = list(
            map(
                lambda eper, jitter_factor: eper + jitter_factor * jitters[image_index],
                epers,
                jitter_factors,
            )
        )

        eb = plt.errorbar(
            x=epers_plot,
            y=[
                median_pdfs[param_index]
                for median_pdfs in median_pdf_image_list[image_index]
            ],
            yerr=[
                [
                    lower_errors[param_index]
                    for lower_errors in lower_error_image_list[image_index]
                ],
                [
                    upper_errors[param_index]
                    for upper_errors in upper_error_image_list[image_index]
                ],
            ],
            capsize=5,
            elinewidth=1,
            markeredgewidth=3,
            linestyle="--",
        )
        eb[-1][0].set_linestyle("-")
        eb[-1][0].set_linewidth(1)

    plt.xscale("log")
    plt.tick_params(
        axis="x",  # changes apply to the x-axis
        which="minor",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off
    plt.xticks(ticks=epers, labels=epers, fontsize=8)
    plt.yticks(fontsize=8)
    plt.ylabel(ylabels[param_index], fontsize=12)
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter("{x:,.4f}"))

ylabels = [
    r"$\delta \rho_{1}$",
    r"$\delta \rho_{2}$",
    r"$\delta \tau_{1}$",
    r"$\delta \tau_{2}$",
    r"$\delta \beta$",
]

for param_index in range(total_params):

    subplot_index = [2, 4, 6, 8, 10]

    plt.subplot(5, 2, subplot_index[param_index])

    plt.xscale("log")

    for image_index in range(total_images):

        plt.plot(
            epers,
            [
                model_errors[param_index]
                for model_errors in error_size_image_list[image_index]
            ],
        )

    plt.tick_params(
        axis="x",  # changes apply to the x-axis
        which="minor",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off
    plt.xticks(ticks=epers, labels=epers, fontsize=8)
    plt.yticks(fontsize=8)
    plt.ylabel(ylabels[param_index], fontsize=12)
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter("{x:,.4f}"))
    if subplot_index[param_index] >= 10:
        plt.xlabel("$EPER_{\mathrm{8}}$", usetex=True, fontsize=12)

plt.figlegend(
    labels=["Input Value", "All", "Uniform", "Non-uniform", "Cosmic Rays"],
    bbox_to_anchor=(0.84, 0.935),
    ncol=6,
    fontsize=17,
    frameon=False,
)

plt.subplots_adjust(top=0.87, bottom=0.06, left=0.05, right=0.95)
plt.savefig(path.join(plot_path, "serial_x2_estimates.png"))
plt.show()
