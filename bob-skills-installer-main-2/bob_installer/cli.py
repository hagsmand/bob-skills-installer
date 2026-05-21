"""Main CLI interface for Bob Skills Installer."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
import sys

from .installer import SkillsInstaller
from .config import ConfigManager

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Bob Skills Installer - Manage AI skills for Bob."""
    pass


@cli.command()
@click.option('--all', 'install_all', is_flag=True, default=True,
              help='Install all available skills (default)')
@click.option('--skills', '-s', multiple=True,
              help='Specific skills to install (e.g., -s docx -s pdf)')
@click.option('--interactive', '-i', is_flag=True,
              help='Interactive skill selection')
@click.option('--custom', '-c',
              help='Install custom skill from local path or Git URL')
@click.option('--branch', '-b',
              help='Git branch name (optional, for custom skills from Git repos)')
@click.option('--path', '-p', default='.',
              help='Installation directory (default: current directory)')
def install(install_all, skills, interactive, custom, branch, path):
    """Install Bob skills to your project."""
    
    installer = SkillsInstaller(path)
    
    # Handle custom skill installation
    if custom:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Installing custom skill...", total=None)
                
                result = installer.install_custom_skill(custom, branch=branch)
                
                progress.update(task, completed=True)
            
            console.print(f"\n✅ [bold green]Custom skill installed successfully![/bold green]\n")
            console.print(f"[cyan]Skill:[/cyan] {result['skill_name']}")
            console.print(f"[cyan]Description:[/cyan] {result['skill_info']['description']}")
            console.print(f"[cyan]Category:[/cyan] {result['skill_info']['category']}")
            
            console.print(f"\n🚀 [bold green]Start using:[/bold green] Bob will automatically detect and use this skill!")
            return
            
        except Exception as e:
            console.print(f"\n❌ [bold red]Installation failed:[/bold red] {str(e)}")
            sys.exit(1)
    
    # Handle regular skill installation
    if interactive:
        skills_to_install = installer.interactive_selection()
    elif skills:
        skills_to_install = list(skills)
        install_all = False
    else:
        skills_to_install = None  # Will install all
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing skills...", total=None)
            
            result = installer.install(
                skills=skills_to_install,
                install_all=install_all
            )
            
            progress.update(task, completed=True)
        
        # Display results
        console.print("\n✅ [bold green]Installation complete![/bold green]\n")
        
        table = Table(title="Installed Skills")
        table.add_column("Skill", style="cyan")
        table.add_column("License", style="yellow")
        table.add_column("Status", style="green")
        
        for skill_info in result['installed']:
            table.add_row(
                skill_info['name'],
                skill_info['license'],
                "✓ Installed"
            )
        
        console.print(table)
        
        # Show license info
        proprietary_count = sum(1 for s in result['installed'] 
                               if s['license'] == 'Proprietary')
        opensource_count = len(result['installed']) - proprietary_count
        
        console.print(f"\n📄 [bold]License Information:[/bold]")
        console.print(f"   - {proprietary_count} proprietary skills (see LICENSE.txt)")
        console.print(f"   - {opensource_count} open source skills (Apache 2.0)")
        
        console.print(f"\n🚀 [bold green]Start using:[/bold green] Just make requests, Bob will use the right skill!")
        console.print(f"   Example: 'Create a Word document' → docx skill loads automatically")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Installation failed:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command('list')
@click.option('--path', '-p', default='.',
              help='Project directory (default: current directory)')
def list_skills(path):
    """List all installed skills."""
    
    installer = SkillsInstaller(path)
    config = ConfigManager(path)
    
    if not config.is_initialized():
        console.print("❌ [red]No skills installed. Run 'bob-skills install' first.[/red]")
        sys.exit(1)
    
    # Get all skills including custom ones
    installed = installer.get_all_installed_skills()
    
    if not installed:
        console.print("No skills installed.")
        return
    
    table = Table(title=f"Installed Skills ({len(installed)} total)")
    table.add_column("Skill", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Description", style="white")
    
    for skill in installed:
        skill_name = skill['name']
        # Add indicator for custom skills
        if skill.get('custom'):
            skill_name = f"{skill_name} [dim](custom)[/dim]"
        
        table.add_row(
            skill_name,
            skill.get('category', 'unknown'),
            skill.get('description', '')[:60] + "..."
        )
    
    console.print(table)


@cli.command()
@click.argument('skill_name')
@click.option('--path', '-p', default='.', 
              help='Project directory (default: current directory)')
def info(skill_name, path):
    """Show detailed information about a skill."""
    
    installer = SkillsInstaller(path)
    skill_info = installer.get_skill_info(skill_name)
    
    if not skill_info:
        console.print(f"❌ [red]Skill '{skill_name}' not found.[/red]")
        sys.exit(1)
    
    panel = Panel(
        f"[bold cyan]{skill_info['name']}[/bold cyan]\n\n"
        f"[bold]Description:[/bold]\n{skill_info['description']}\n\n"
        f"[bold]Category:[/bold] {skill_info.get('category', 'unknown')}\n"
        f"[bold]License:[/bold] {skill_info.get('license', 'unknown')}\n"
        f"[bold]Status:[/bold] {'✓ Installed' if skill_info.get('installed') else '○ Not installed'}",
        title=f"Skill Information",
        border_style="cyan"
    )
    
    console.print(panel)


@cli.command()
@click.option('--path', '-p', default='.',
              help='Project directory (default: current directory)')
def update(path):
    """Update all installed catalog skills to latest version (custom skills are skipped)."""
    
    installer = SkillsInstaller(path)
    config = ConfigManager(path)
    
    if not config.is_initialized():
        console.print("❌ [red]No skills installed. Run 'bob-skills install' first.[/red]")
        sys.exit(1)
    
    installed = config.get_installed_skills()
    skill_names = [s['name'] for s in installed]
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Updating skills...", total=None)
            
            result = installer.update_skills(skill_names)
            
            progress.update(task, completed=True)
        
        console.print(f"\n✅ [bold green]Updated {len(result['updated'])} skills![/bold green]")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Update failed:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('skills', nargs=-1, required=False)
@click.option('--all', '-a', is_flag=True,
              help='Uninstall all skills')
@click.option('--path', '-p', default='.',
              help='Project directory (default: current directory)')
def uninstall(skills, all, path):
    """Uninstall specific skills or all skills with --all flag."""
    
    installer = SkillsInstaller(path)
    config = ConfigManager(path)
    
    # Determine which skills to uninstall
    if all:
        if not config.is_initialized():
            console.print("❌ [red]No skills installed.[/red]")
            sys.exit(1)
        
        installed = config.get_installed_skills()
        skills_to_remove = [s['name'] for s in installed]
        
        if not skills_to_remove:
            console.print("❌ [red]No skills installed.[/red]")
            sys.exit(1)
            
        console.print(f"\n⚠️  [yellow]About to uninstall {len(skills_to_remove)} skills:[/yellow]")
        for skill in skills_to_remove:
            console.print(f"   - {skill}")
        
        if not click.confirm("\nAre you sure you want to uninstall all skills?"):
            console.print("❌ [yellow]Uninstall cancelled.[/yellow]")
            sys.exit(0)
    elif not skills:
        console.print("❌ [red]Error: Specify skill names or use --all flag[/red]")
        console.print("\nExamples:")
        console.print("  bob-skills uninstall docx pdf")
        console.print("  bob-skills uninstall --all")
        sys.exit(1)
    else:
        skills_to_remove = list(skills)
    
    try:
        result = installer.uninstall(skills_to_remove)
        
        console.print(f"\n✅ [bold green]Uninstalled {len(result['removed'])} skills:[/bold green]")
        for skill in result['removed']:
            console.print(f"   - {skill}")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Uninstall failed:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('prompt')
@click.option('--path', '-p', default='.', 
              help='Project directory (default: current directory)')
def detect(prompt, path):
    """Detect which skills would be used for a given prompt."""
    
    installer = SkillsInstaller(path)
    detected = installer.detect_skills(prompt)
    
    if not detected:
        console.print("No skills detected for this prompt.")
        return
    
    console.print(f"\n🔍 [bold]Detected skills for:[/bold] '{prompt}'\n")
    
    for skill in detected:
        console.print(f"   ✓ [cyan]{skill}[/cyan]")


@cli.command()
@click.argument('skill_name')
@click.option('--path', '-p', default='.', 
              help='Project directory (default: current directory)')
def check(skill_name, path):
    """Check if a skill is installed and ready."""
    
    config = ConfigManager(path)
    
    if not config.is_initialized():
        console.print("❌ [red]No skills installed.[/red]")
        sys.exit(1)
    
    installed = config.get_installed_skills()
    skill_names = [s['name'] for s in installed]
    
    if skill_name in skill_names:
        console.print(f"✓ [green]{skill_name} is installed and ready[/green]")
    else:
        console.print(f"○ [yellow]{skill_name} is not installed[/yellow]")
        console.print(f"   Run: bob-skills install -s {skill_name}")


if __name__ == '__main__':
    cli()