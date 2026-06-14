import io

from matplotlib.figure import Figure


class ChartService:
    """Renders finance charts as PNG bytes. Uses the object-oriented Figure API
    (no pyplot global state) so it is safe to call from a worker thread."""

    INCOME_COLOR = "#2ecc71"
    EXPENSE_COLOR = "#e74c3c"
    NET_COLOR = "#3498db"

    def render_monthly_overview(self, month_label, income, expense, net, breakdown):
        """month_label: str; income/expense/net: Decimal|float;
        breakdown: list[{'name', 'total'}] of this month's expenses by category.
        Returns PNG bytes."""
        income, expense, net = float(income), float(expense), float(net)

        fig = Figure(figsize=(10, 4.5), dpi=130)
        ax_bar, ax_pie = fig.subplots(1, 2)

        labels = ["Income", "Expense", "Net"]
        values = [income, expense, net]
        colors = [self.INCOME_COLOR, self.EXPENSE_COLOR, self.NET_COLOR]
        bars = ax_bar.bar(labels, values, color=colors)
        ax_bar.set_title(f"{month_label} — Overview")
        ax_bar.axhline(0, color="#999999", linewidth=0.8)
        ax_bar.grid(axis="y", linestyle="--", alpha=0.3)
        for bar, value in zip(bars, values):
            ax_bar.annotate(
                f"{value:,.0f}",
                (bar.get_x() + bar.get_width() / 2, value),
                ha="center",
                va="bottom" if value >= 0 else "top",
                fontsize=9,
            )

        if breakdown:
            names = [row["name"] for row in breakdown]
            totals = [float(row["total"]) for row in breakdown]
            ax_pie.pie(
                totals,
                labels=names,
                autopct="%1.0f%%",
                startangle=90,
                textprops={"fontsize": 8},
            )
            ax_pie.set_title("Expenses by category")
        else:
            ax_pie.text(0.5, 0.5, "No expenses yet", ha="center", va="center", fontsize=11)
            ax_pie.axis("off")

        fig.tight_layout()
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        buffer.seek(0)
        return buffer.getvalue()
