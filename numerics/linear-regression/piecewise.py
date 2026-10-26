# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.11.2",
#     "numpy>=2.5.3",
# ]
# ///

import marimo

__generated_with = "0.23.9"
app = marimo.App()


@app.cell
def _():
    import numpy as np
    import marimo as mo
    import matplotlib.pyplot as plt

    return mo, np


@app.cell
def _(np):
    import marimo

    __generated_with = "0.10.0"
    app = marimo.App(width="medium")


    @app.cell
    def __():
        import marimo as mo
        import numpy as np
        import matplotlib.pyplot as plt

        return mo, np, plt


    @app.cell
    def __(mo):
        mo.md(
            r"""
            # 📈 Piecewise Function Builder
            Configure the number of segments, set break-point boundaries, and customize the value or expression for each segment.
            """
        )
        return


    @app.cell
    def __(mo):
        # Step 1: Control global range and number of segments
        n_segments_slider = mo.ui.slider(
            start=2, stop=6, step=1, value=3, label="Number of segments (N)"
        )
        domain_slider = mo.ui.range_slider(
            start=-20.0, stop=20.0, step=0.5, value=[-10.0, 10.0], label="Overall Domain [X_min, X_max]"
        )

        mo.vstack([
            mo.md("### 1. Global Setup"),
            mo.hstack([n_segments_slider, domain_slider], justify="start", gap=2)
        ])
        return domain_slider, n_segments_slider


    @app.cell
    def __(domain_slider, mo, n_segments_slider):
        n_seg = n_segments_slider.value
        x_min, x_max = domain_slider.value

        # Default equidistant split points
        default_cuts = list(np.linspace(x_min, x_max, n_seg + 1))[1:-1]

        # Dynamically create control point inputs
        cut_inputs = [
            mo.ui.number(
                start=x_min,
                stop=x_max,
                step=0.1,
                value=round(val, 2),
                label=f"Cut-point $x_{i+1}$",
            )
            for i, val in enumerate(default_cuts)
        ]

        # Mode selector: Constant value vs. Linear expression (m*x + c)
        mode_dropdown = mo.ui.dropdown(
            options={"Constant Value": "constant", "Linear (m*x + c)": "linear"},
            value="Constant Value",
            label="Segment parameterization mode",
        )

        mo.vstack([
            mo.md("### 2. Segment Boundaries (Control Points)"),
            mo.hstack(cut_inputs, wrap=True),
            mo.md("---"),
            mo.md("### 3. Segment Parameters"),
            mode_dropdown,
        ])
        return cut_inputs, mode_dropdown, n_seg, x_max, x_min


    @app.cell
    def __(mo, mode_dropdown, n_seg):
        # Step 3: Create parameter controls for each segment based on the selected mode
        segment_controls = []
        mode = mode_dropdown.value

        for i in range(n_seg):
            if mode == "constant":
                ctrl = mo.ui.number(
                    start=-100.0,
                    stop=100.0,
                    step=0.5,
                    value=float((i + 1) * 2),
                    label=f"Segment {i+1} value (y)",
                )
                segment_controls.append(ctrl)
            else:
                slope = mo.ui.number(start=-10.0, stop=10.0, step=0.5, value=1.0 if i % 2 == 0 else -1.0, label="Slope (m)")
                intercept = mo.ui.number(start=-20.0, stop=20.0, step=0.5, value=0.0, label="Intercept (c)")
                segment_controls.append(mo.ui.dictionary({"m": slope, "c": intercept}))

        mo.hstack(
            [
                mo.callout(
                    ctrl if mode == "constant" else mo.vstack([mo.md(f"**Segment {i+1}**"), ctrl["m"], ctrl["c"]]),
                    kind="neutral",
                )
                for i, ctrl in enumerate(segment_controls)
            ],
            wrap=True,
        )
        return mode, segment_controls


    @app.cell
    def __(cut_inputs, mode, np, plt, segment_controls, x_max, x_min):
        # Extract & sort partition boundaries
        raw_cuts = sorted([inp.value for inp in cut_inputs])
        # Enforce clamping strictly within [x_min, x_max]
        cuts = [x_min] + [min(max(c, x_min), x_max) for c in raw_cuts] + [x_max]
        # Re-sort in case numbers crossed
        cuts = sorted(cuts)

        # Evaluate piecewise function over a dense grid
        xs = np.linspace(x_min, x_max, 1000)
        ys = np.zeros_like(xs)

        # Compute piece by piece
        for i in range(len(cuts) - 1):
            left, right = cuts[i], cuts[i + 1]
        
            # Include right edge on the final segment
            if i == len(cuts) - 2:
                mask = (xs >= left) & (xs <= right)
            else:
                mask = (xs >= left) & (xs < right)

            if mode == "constant":
                val = segment_controls[i].value
                ys[mask] = val
            else:
                m = segment_controls[i]["m"].value
                c = segment_controls[i]["c"].value
                ys[mask] = m * xs[mask] + c

        # Plotting
        fig, ax = plt.subplots(figsize=(9, 4.5), dpi=150)
    
        # Plot segments separately to avoid connecting vertical jump discontinuities
        for i in range(len(cuts) - 1):
            left, right = cuts[i], cuts[i + 1]
            seg_x = np.linspace(left, right, 200)
            if mode == "constant":
                seg_y = np.full_like(seg_x, segment_controls[i].value)
            else:
                seg_y = segment_controls[i]["m"].value * seg_x + segment_controls[i]["c"].value

            ax.plot(seg_x, seg_y, color="#2563eb", lw=2.5)

        # Mark partition boundaries (control points)
        for boundary in cuts[1:-1]:
            ax.axvline(boundary, color="#ef4444", linestyle="--", alpha=0.7, label="Boundary" if boundary == cuts[1] else "")

        ax.set_title("Piecewise Function Plot", fontsize=13, fontweight="bold")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.grid(True, linestyle=":", alpha=0.6)
        fig.tight_layout()

        return ax, boundary, cuts, fig, left, mask, raw_cuts, right, xs, ys


    @app.cell
    def __(cuts, fig, mo, mode, segment_controls):
        # Output latex description of the piecewise function
        conditions = []
        for i in range(len(cuts) - 1):
            x_l, x_r = round(cuts[i], 2), round(cuts[i + 1], 2)
            comp = f"{x_l} \\le x \\le {x_r}" if i == len(cuts) - 2 else f"{x_l} \\le x < {x_r}"
        
            if mode == "constant":
                val_str = f"{segment_controls[i].value:.2f}"
            else:
                m = segment_controls[i]["m"].value
                c = segment_controls[i]["c"].value
                val_str = f"{m:.2f}x + {c:.2f}"
            
            conditions.append(f"{val_str} & \\text{{if }} {comp}")

        latex_code = r"f(x) = \begin{cases} " + r" \\ ".join(conditions) + r" \end{cases}"

        mo.vstack([
            mo.as_html(fig),
            mo.md("### Mathematical Representation:"),
            mo.md(f"$${latex_code}$$")
        ])
        return comp, conditions, latex_code, val_str, x_l, x_r


    if __name__ == "__main__":
        app.run()
    return


@app.cell
def _(mo, np):
    L = 10

    # make a slider to control a piecewise function of n segments
    n = mo.slider(1, 10, value=3, label="Number of segments")

    # make the control points for the piecewise function
    x = mo.linspace(0, L, n + 1)

    # make the widget to control the y values of the piecewise function
    y = mo.slider(-5, 5, value=np.zeros(n + 1), label="Control points")
    return


if __name__ == "__main__":
    app.run()
