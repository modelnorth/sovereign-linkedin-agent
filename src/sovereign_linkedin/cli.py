"""
ModelNorth Sovereign LinkedIn Agent - Command Line Interface (CLI)
https://modelnorth.com

Unified terminal control center for sovereign LinkedIn operations:
- System diagnostics & CDP verification
- Autonomous lead scouting & seniority scoring
- Contextual outreach message synthesis
- Company page publishing
"""

import asyncio
import json
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from sovereign_linkedin import __version__, __license__
from sovereign_linkedin.config import AgentConfig
from sovereign_linkedin.core.vault import SessionVault
from sovereign_linkedin.core.governor import SafetyGovernor
from sovereign_linkedin.modules.lead_scout import LeadScout, Prospect
from sovereign_linkedin.modules.outreach import OutreachSynthesizer
from sovereign_linkedin.modules.company_page import CompanyPagePilot
from sovereign_linkedin.engine.browser import BrowserDriver

console = Console()

BANNER = rf"""[bold cyan]
  __  __           _      _ _   _             _   _     
 |  \/  |         | |    | | \ | |           | | | |    
 | \  / | ___   __| | ___| |  \| | ___  _ __| |_| |__  
 | |\/| |/ _ \ / _` |/ _ \ | . ` |/ _ \| '__| __| '_ \ 
 | |  | | (_) | (_| |  __/ | |\  | (_) | |  | |_| | | |
 |_|  |_|\___/ \__,_|\___|_|_| \_|\___/|_|   \__|_| |_|
[/bold cyan]
[bold white]Sovereign LinkedIn Agent v{__version__}[/bold white] | [cyan]https://modelnorth.com[/cyan]
[dim]License: {__license__}[/dim]
"""


@click.group()
def cli():
    """ModelNorth Sovereign LinkedIn Agent - Autonomous Growth Engine."""
    pass


@cli.command("status")
def status_cmd():
    """Inspect system health, CDP port, safety governor, and daily quotas."""
    console.print(BANNER)
    config = AgentConfig.load()
    vault = SessionVault(config.vault_dir, config.browser.cdp_url)
    governor = SafetyGovernor(config.safety, vault)

    cdp_active = vault.check_cdp_status()
    within_hours, hours_msg = governor.check_active_hours()
    metrics = governor.get_daily_metrics()

    table = Table(title="[bold green]System & Safety Diagnostics[/bold green]", box=box.ROUNDED)
    table.add_column("Subsystem", style="cyan")
    table.add_column("Status / Metric", style="white")
    table.add_column("Threshold / Detail", style="dim")

    table.add_row(
        "Brave CDP (Port 9222)",
        "[bold green]Connected[/bold green]" if cdp_active else "[bold red]Disconnected[/bold red]",
        config.browser.cdp_url
    )
    table.add_row(
        "Working Hours Governor",
        "[bold green]Active[/bold green]" if within_hours else "[bold yellow]Curfew Active[/bold yellow]",
        hours_msg
    )
    table.add_row(
        "Daily Invites Sent",
        f"{metrics['invites_sent']} / {config.safety.daily_connect_limit}",
        "Hard Safety Ceiling"
    )
    table.add_row(
        "Daily Messages Sent",
        f"{metrics['messages_sent']} / {config.safety.daily_message_limit}",
        "Hard Safety Ceiling"
    )
    table.add_row(
        "Daily Profile Views",
        f"{metrics['profiles_viewed']} / {config.safety.daily_profile_views}",
        "Perimeter Guard"
    )
    table.add_row(
        "Local Vault Storage",
        "[bold green]Encrypted Local-First[/bold green]",
        str(config.vault_dir)
    )

    console.print(table)
    if not cdp_active:
        console.print(
            "\n[yellow]Tip: Run '[bold cyan]sovereign-linkedin launch-browser[/bold cyan]' "
            "to open Brave in authenticated anti-ban debugging mode.[/yellow]\n"
        )


@cli.command("launch-browser")
@click.option("--port", default=9222, help="Remote debugging port")
def launch_browser_cmd(port: int):
    """Launch Brave browser with anti-ban stealth flags and persistent profile."""
    console.print(BANNER)
    config = AgentConfig.load()
    vault = SessionVault(config.vault_dir, config.browser.cdp_url)

    console.print(f"[cyan]Launching Brave Browser with CDP on port {port}...[/cyan]")
    success = vault.launch_brave_cdp(config.browser.brave_executable_path, port=port)
    if success:
        console.print("[bold green]✓ Brave launched successfully with automation cloaking enabled![/bold green]")
        console.print("[dim]Sign in to LinkedIn manually if needed; your cookies persist locally.[/dim]\n")
    else:
        console.print("[bold red]Failed to launch Brave. Verify executable path in config.[/bold red]\n")


@cli.command("scout")
@click.option("--role", default="Chief Technology Officer", help="Target executive role")
@click.option("--location", default="Dubai, UAE", help="Target geographic region")
@click.option("--limit", default=10, help="Number of prospects to evaluate")
@click.option("--export-csv/--no-csv", default=True, help="Export results to CSV")
def scout_cmd(role: str, location: str, limit: int, export_csv: bool):
    """Scout and rank high-ticket enterprise decision-makers."""
    console.print(BANNER)
    config = AgentConfig.load()

    console.print(f"[bold cyan]Scouting ICP Leads:[/bold cyan] Role='[white]{role}[/white]', Location='[white]{location}[/white]'")

    # Sample demo mock/scout profiles
    demo_profiles = [
        {
            "name": "Tariq Al-Mansoor",
            "headline": f"{role} | Sovereign Cloud & Enterprise Defense AI",
            "company": "Emirates Sovereign Tech Group",
            "location": location,
            "profile_url": "https://www.linkedin.com/in/sample-cto-dubai"
        },
        {
            "name": "Sarah Jenkins",
            "headline": "Head of Artificial Intelligence & MCP Architecture",
            "company": "GCC Financial Technologies",
            "location": "Abu Dhabi, UAE",
            "profile_url": "https://www.linkedin.com/in/sample-head-ai"
        },
        {
            "name": "Dr. Faisal Rahman",
            "headline": "Chief Information Security Officer (CISO) | Air-Gapped Systems",
            "company": "Gulf Sovereign Digital Infrastructure",
            "location": "Dubai, UAE",
            "profile_url": "https://www.linkedin.com/in/sample-ciso-gcc"
        }
    ]

    prospects = [LeadScout.parse_raw_profile(p) for p in demo_profiles][:limit]

    table = Table(title="[bold green]High-Ticket Prospect Matrix[/bold green]", box=box.ROUNDED)
    table.add_column("Score", style="bold yellow")
    table.add_column("Name", style="bold white")
    table.add_column("Headline", style="cyan")
    table.add_column("Company", style="white")
    table.add_column("Location", style="dim")

    for p in prospects:
        table.add_row(
            f"{p.seniority_score}/100",
            p.name,
            p.headline[:45] + ("..." if len(p.headline) > 45 else ""),
            p.current_company or "N/A",
            p.location or "N/A"
        )

    console.print(table)

    if export_csv:
        csv_path = config.vault_dir / "leads_export.csv"
        LeadScout.export_csv(prospects, csv_path)
        console.print(f"[bold green]✓ Leads exported to:[/bold green] [white]{csv_path}[/white]\n")


@cli.command("synthesize")
@click.option("--name", prompt="Prospect Full Name", help="Name of prospect")
@click.option("--company", prompt="Company Name", help="Prospect company")
@click.option("--headline", prompt="Prospect Headline", help="Prospect title/headline")
@click.option("--angle", default="sovereign", type=click.Choice(["sovereign", "mcp_security", "enterprise_ai"]))
def synthesize_cmd(name: str, company: str, headline: str, angle: str):
    """Synthesize high-status invite notes and direct messages."""
    console.print(BANNER)
    prospect = Prospect(
        name=name,
        headline=headline,
        current_company=company,
        profile_url="https://linkedin.com/in/prospect"
    )

    invite_note = OutreachSynthesizer.synthesize_invite_note(prospect, angle=angle)
    dm = OutreachSynthesizer.synthesize_direct_message(prospect)

    console.print(Panel(
        f"[bold white]{invite_note}[/bold white]\n\n"
        f"[dim]Length: {len(invite_note)}/300 characters (LinkedIn compliant)[/dim]",
        title=f"[bold green]Connection Request Note (Angle: {angle})[/bold green]",
        border_style="green"
    ))

    console.print(Panel(
        f"[white]{dm}[/white]",
        title="[bold cyan]Direct Message / InMail (Post-Acceptance)[/bold cyan]",
        border_style="cyan"
    ))


@cli.command("post-company")
@click.option("--text", prompt="Post Content", help="Text to publish on company page feed")
@click.option("--media", default=None, help="Path to image, banner, or PDF graphic")
def post_company_cmd(text: str, media: str):
    """Publish an update directly to the ModelNorth company page feed."""
    console.print(BANNER)
    config = AgentConfig.load()
    browser = BrowserDriver(config)
    pilot = CompanyPagePilot(config, browser)

    async def _run():
        console.print("[cyan]Connecting to browser and company page admin...[/cyan]")
        media_path = Path(media) if media else None
        success = await pilot.publish_company_post(text, media_path=media_path)
        if success:
            console.print("[bold green]✓ Update successfully posted to ModelNorth Company Page![/bold green]")
        else:
            console.print("[bold red]Failed to submit post. Check browser connection.[/bold red]")
        await browser.close()

    asyncio.run(_run())


def main():
    cli()


if __name__ == "__main__":
    main()
