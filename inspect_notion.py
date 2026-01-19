"""
Utility script to inspect and analyze your Notion Job Tracker database.
Run this to see your current database structure and get optimization recommendations.
"""

import asyncio
from notion_client import create_notion_tracker
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
import sys

console = Console()


def main():
    """Inspect Notion database and provide recommendations."""
    console.print(Panel.fit(
        "[bold cyan]Notion Job Tracker Inspector[/bold cyan]",
        subtitle="Analyzing your database structure"
    ))

    try:
        # Initialize Notion client
        tracker = create_notion_tracker()
        console.print("[green]✓[/green] Connected to Notion API")

        # Analyze current schema
        console.print("\n[bold]Current Database Schema:[/bold]")
        schema = tracker.analyze_schema()

        # Create table for current schema
        schema_table = Table(title="Database Properties")
        schema_table.add_column("Property Name", style="cyan")
        schema_table.add_column("Type", style="yellow")

        for prop_name, prop_type in schema.items():
            schema_table.add_row(prop_name, prop_type)

        console.print(schema_table)

        # Get statistics
        console.print("\n[bold]Database Statistics:[/bold]")
        stats = tracker.get_statistics()

        stats_table = Table(title="Application Stats")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Count", style="green")

        stats_table.add_row("Total Applications", str(stats["total"]))
        stats_table.add_row("This Week", str(stats["this_week"]))
        stats_table.add_row("This Month", str(stats["this_month"]))

        console.print(stats_table)

        # Status breakdown
        if stats["by_status"]:
            console.print("\n[bold]Applications by Status:[/bold]")
            status_table = Table(title="Status Breakdown")
            status_table.add_column("Status", style="cyan")
            status_table.add_column("Count", style="yellow")

            for status, count in stats["by_status"].items():
                status_table.add_row(status, str(count))

            console.print(status_table)

        # Get recommended schema
        console.print("\n[bold]Recommended Schema (for optimal automation):[/bold]")
        recommended = tracker.get_recommended_schema()

        rec_table = Table(title="Recommended Properties")
        rec_table.add_column("Property Name", style="cyan")
        rec_table.add_column("Type", style="yellow")
        rec_table.add_column("Status", style="green")

        for prop_name, prop_config in recommended.items():
            prop_type = prop_config["type"]
            # Check if property exists in current schema
            if prop_name in schema:
                current_type = schema[prop_name]
                if current_type == prop_type:
                    status = "✓ Exists"
                else:
                    status = f"⚠ Type mismatch ({current_type})"
            else:
                status = "✗ Missing"

            rec_table.add_row(prop_name, prop_type, status)

        console.print(rec_table)

        # Recommendations
        missing_props = [
            prop for prop in recommended.keys()
            if prop not in schema
        ]

        if missing_props:
            console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            console.print("Consider adding these properties to your Notion database for full functionality:")
            for prop in missing_props:
                prop_type = recommended[prop]["type"]
                console.print(f"  • [cyan]{prop}[/cyan] ([yellow]{prop_type}[/yellow])")

            console.print("\n[dim]The agent will work with your current schema, but these properties")
            console.print("will enhance automation capabilities.[/dim]")
        else:
            console.print("\n[bold green]✓ Your database has all recommended properties![/bold green]")

        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Update your .env file with API keys")
        console.print("2. Run the LinkedIn scraper to discover jobs")
        console.print("3. Jobs will be automatically added to this Notion database")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("1. Ensure NOTION_API_KEY is set in .env")
        console.print("2. Ensure NOTION_DATABASE_ID is set in .env")
        console.print("3. Verify the integration has access to your database")
        console.print("4. Check that the database ID is correct")
        sys.exit(1)


if __name__ == "__main__":
    main()
