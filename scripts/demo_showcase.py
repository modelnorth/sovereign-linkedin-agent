"""
ModelNorth Sovereign LinkedIn Agent - Interactive Live Demo Showcase
https://modelnorth.com

Executes an end-to-end recorded demonstration:
1. System Status & Safety Governor Verification
2. Content Calendar Queue Inspection
3. High-Ticket Deal Radar & Hiring Signal Sourcing
4. 14-Day Hiring Gap Architecture Pitch Synthesis
5. Distributed OpenTelemetry Flight Ledger Tracing
"""

import io
import sys
import time
from pathlib import Path

# Force utf-8 console output for Windows terminals
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Add src to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from click.testing import CliRunner
from rich.console import Console
from sovereign_linkedin.cli import cli

console = Console()


def print_step_header(step_num: int, title: str):
    console.print("\n" + "=" * 70, style="dim cyan")
    console.print(f" [STEP {step_num}/5] [bold cyan]{title}[/bold cyan]", style="bold white")
    console.print("=" * 70 + "\n", style="dim cyan")
    time.sleep(1.2)


def main():
    runner = CliRunner()

    # Step 1: Status
    print_step_header(1, "Verifying System Health, CDP Status & Safety Curfew")
    res1 = runner.invoke(cli, ["status"])
    console.print(res1.output)
    time.sleep(2.0)

    # Step 2: Content Queue
    print_step_header(2, "Inspecting Sovereign Content Calendar Queue")
    res2 = runner.invoke(cli, ["queue"])
    console.print(res2.output)
    time.sleep(2.0)

    # Step 3: Deal Radar
    print_step_header(3, "Hunting High-Ticket Deals via Active Hiring Signals ($10k-$35k)")
    res3 = runner.invoke(cli, ["hunt-deals", "--role", "AI Engineer", "--location", "Dubai, UAE"])
    console.print(res3.output)
    time.sleep(2.5)

    # Step 4: Hiring Pitch Synthesis
    print_step_header(4, "Synthesizing Event-Triggered 14-Day Hiring Gap Sprint Pitch")
    res4 = runner.invoke(cli, [
        "hiring-pitch",
        "--company", "Emirates Sovereign Tech",
        "--executive", "Dr. Tariq Al-Mansoor",
        "--role", "Lead AI Architect",
        "--location", "Dubai"
    ])
    console.print(res4.output)
    time.sleep(2.5)

    # Step 5: Distributed Traces
    print_step_header(5, "Auditing Distributed OpenTelemetry Flight Ledger")
    res5 = runner.invoke(cli, ["traces", "--limit", "6"])
    console.print(res5.output)
    time.sleep(1.5)

    console.print("\n[bold green]✓ ModelNorth Sovereign LinkedIn Agent Showcase Completed Successfully![/bold green]\n")


if __name__ == "__main__":
    main()
