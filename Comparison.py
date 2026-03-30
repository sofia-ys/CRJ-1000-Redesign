from __future__ import annotations

from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import loading_diagram as part1
import loading_diagram_Part2 as part2


PART1_EXCEL = "data_(4).xlsx"
PART2_EXCEL = "data_(4).xlsx"

def plot_family(
    ax,
    paths_group,
    color: str,
    marker: str,
    label: str | None,
    mode: str,
    n_rows: int,
    linestyle: str,
    filled: bool,
) -> None:
    label_added = False

    for _, path in paths_group:
        if mode == "cargo":
            pts = path
        elif mode == "window":
            pts = path[2:]
        elif mode == "aisle":
            pts = path[-(n_rows + 1):]
        elif mode == "fuel":
            pts = path[-2:]
        else:
            raise ValueError(f"Unknown plot mode: {mode}")

        x = [p.x_percent_mac for p in pts]
        y = [p.weight_kg for p in pts]

        ax.plot(
            x,
            y,
            color=color,
            marker=marker,
            linewidth=1.6,
            markersize=4,
            alpha=0.8,
            linestyle=linestyle,
            markerfacecolor=color if filled else "none",
            markeredgecolor=color,
            label=label if (label is not None and not label_added) else None,
        )
        label_added = True


def plot_single_diagram(ax, data: dict, paths: dict, prefix: str, style: str) -> None:
    """
    style:
        - "part1": solid lines, filled markers
        - "part2": dashed lines, hollow markers
    """
    if style == "part1":
        linestyle = "-"
        filled = True
        add_legend_labels = True
    elif style == "part2":
        linestyle = "--"
        filled = False
        add_legend_labels = False
    else:
        raise ValueError("style must be 'part1' or 'part2'")

    plot_family(
        ax, paths["cargo_paths"],
        color="tab:blue", marker="o",
        label="Cargo" if add_legend_labels else None,
        mode="cargo", n_rows=data["n_rows"],
        linestyle=linestyle, filled=filled
    )
    plot_family(
        ax, paths["window_paths"],
        color="tab:orange", marker="x",
        label="Window seats" if add_legend_labels else None,
        mode="window", n_rows=data["n_rows"],
        linestyle=linestyle, filled=filled
    )
    plot_family(
        ax, paths["aisle_paths"],
        color="tab:green", marker="s",
        label="Aisle seats" if add_legend_labels else None,
        mode="aisle", n_rows=data["n_rows"],
        linestyle=linestyle, filled=filled
    )
    plot_family(
        ax, paths["fuel_paths"],
        color="tab:red", marker="D",
        label="Fuel" if add_legend_labels else None,
        mode="fuel", n_rows=data["n_rows"],
        linestyle=linestyle, filled=filled
    )

    # OEW point
    oew = part1.make_point("OEW", data["oew"], paths["oew_x"], data)
    ax.scatter(
        [oew.x_percent_mac], [oew.weight_kg],
        color="black", s=70, zorder=6,
        marker="o" if style == "part1" else "s"
    )
    ax.annotate(f"{prefix} OEW", (oew.x_percent_mac, oew.weight_kg), xytext=(8, 8), textcoords="offset points")

    # Extreme points
    extremes = part1.get_extremes(paths)
    _, p_fwd = extremes["most_forward"]
    _, p_aft = extremes["most_aft"]

    ax.scatter(
        [p_fwd.x_percent_mac], [p_fwd.weight_kg],
        color="crimson", s=60, zorder=6,
        marker="o" if style == "part1" else "s"
    )
    ax.annotate(f"{prefix} most forward", (p_fwd.x_percent_mac, p_fwd.weight_kg), xytext=(8, -14), textcoords="offset points")

    ax.scatter(
        [p_aft.x_percent_mac], [p_aft.weight_kg],
        color="crimson", s=60, zorder=6,
        marker="o" if style == "part1" else "s"
    )
    ax.annotate(f"{prefix} most aft", (p_aft.x_percent_mac, p_aft.weight_kg), xytext=(8, 8), textcoords="offset points")

def main() -> None:
    script_dir = Path(__file__).resolve().parent

    part1_excel = script_dir / PART1_EXCEL
    part2_excel = script_dir / PART2_EXCEL

    if not part1_excel.exists():
        raise FileNotFoundError(f"Could not find '{PART1_EXCEL}' next to this script.")
    if not part2_excel.exists():
        raise FileNotFoundError(f"Could not find '{PART2_EXCEL}' next to this script.")

    # -----------------------------
    # Read Part 1 data
    # -----------------------------
    data1 = part1.read_inputs(str(part1_excel))
    paths1 = part1.build_all_paths(data1)

    # -----------------------------
    # Read Part 2 data
    # -----------------------------
    data2 = part2.read_inputs_rik(str(part2_excel))
    paths2 = part1.build_all_paths(data2)

    # -----------------------------
    # Create comparison figure
    # -----------------------------
    fig, ax = plt.subplots(figsize=(14, 9))

    plot_single_diagram(ax, data1, paths1, prefix="Part 1", style="part1")
    plot_single_diagram(ax, data2, paths2, prefix="Part 2", style="part2")

    # Optional explicit CG markers from table values
    part1_oew_table_x = part1.x_front_to_percent_mac(data1["oew_x_table"], data1["nose_to_lemac"], data1["mac"])
    part2_oew_table_x = part1.x_front_to_percent_mac(data2["oew_x_table"], data2["nose_to_lemac"], data2["mac"])

    ax.scatter([part1_oew_table_x], [data1["oew"]], color="purple", s=80, zorder=7)
    ax.annotate("Part 1 CG@OEW (table)", (part1_oew_table_x, data1["oew"]), xytext=(8, -18), textcoords="offset points")

    ax.scatter([part2_oew_table_x], [data2["oew"]], color="purple", s=80, zorder=7)
    ax.annotate("Part 2 CG@OEW (table)", (part2_oew_table_x, data2["oew"]), xytext=(8, -18), textcoords="offset points")

    ax.set_xlabel("x_cg [%MAC]")
    ax.set_ylabel("Mass [kg]")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ax.set_title(f"Comparison of Loading Diagrams - Part 1 vs Part 2\n{timestamp}")

    ax.grid(True, alpha=0.3)
    # First legend: load types
    handles, labels = ax.get_legend_handles_labels()
    legend1 = ax.legend(handles, labels, fontsize=9, ncol=2, loc="upper left")
    ax.add_artist(legend1)

    # Second legend: line style meaning
    style_handles = [
        Line2D(
            [0], [0],
            color="black",
            linestyle="-",
            linewidth=1.8,
            label="Part 1 style"
        ),
        Line2D(
            [0], [0],
            color="black",
            linestyle="--",
            linewidth=1.8,
            label="Part 2 style"
        ),
    ]

    ax.legend(
        handles=style_handles,
        fontsize=9,
        ncol=1,
        loc="upper right",
        title="Diagram style"
    )
    fig.tight_layout()

    output_folder = script_dir / "Loading Diagram Comparisons"
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / f"comparison_loading_diagrams_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    fig.savefig(output_file, dpi=300)
    plt.show()

    print(f"Saved comparison plot to: {output_file}")


if __name__ == "__main__":
    main()