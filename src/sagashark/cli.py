#!/usr/bin/env python3
"""
GitSaga CLI - Development Context Manager
Track the story behind your code
"""

import click
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from .core.saga import Saga
from .core.config import Config
from .core.repository import GitRepository
from .search.text_search import TextSearcher
from .capture.auto_chronicler import AutoChronicler
from .capture.significance import SignificanceScorer, CommitContext

# Create console with proper encoding for Windows
console = Console(force_terminal=True, legacy_windows=False)

# ASCII art banner - ANSI Shadow style
BANNER = """
███████╗ █████╗  ██████╗  █████╗ ███████╗██╗  ██╗ █████╗ ██████╗ ██╗  ██╗
██╔════╝██╔══██╗██╔════╝ ██╔══██╗██╔════╝██║  ██║██╔══██╗██╔══██╗██║ ██╔╝
███████╗███████║██║  ███╗███████║███████╗███████║███████║██████╔╝█████╔╝ 
╚════██║██╔══██║██║   ██║██╔══██║╚════██║██╔══██║██╔══██║██╔══██╗██╔═██╗ 
███████║██║  ██║╚██████╔╝██║  ██║███████║██║  ██║██║  ██║██║  ██║██║  ██╗
╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
"""

def show_banner():
    """Show banner on first run in session"""
    # Use environment variable to track if banner was shown
    if not os.environ.get('SAGASHARK_BANNER_SHOWN'):
        try:
            # Set encoding for Windows
            if sys.platform == 'win32':
                sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
        
        try:
            # Try to print with Rich console
            console.print(BANNER, style="bold cyan")
            console.print("  Track the story behind your code", style="dim")
            console.print("  Version 2.0.0 | Type 'saga --help' for commands\n", style="dim")
        except Exception:
            # Fallback to simple print - should always work with new ASCII banner
            try:
                print(BANNER)
                print("  Track the story behind your code")
                print("  Version 2.0.0 | Type 'saga --help' for commands\n")
            except:
                # If even simple ASCII fails, skip banner entirely
                pass
        
        # Always mark as shown to prevent repeats
        os.environ['SAGASHARK_BANNER_SHOWN'] = '1'


@click.group()
@click.pass_context
def cli(ctx):
    """SagaShark - Track the story behind your code"""
    ctx.ensure_object(dict)
    
    # Check if we're in a GitSaga repository
    saga_dir = Path.cwd() / '.sagashark'
    ctx.obj['saga_dir'] = saga_dir
    ctx.obj['is_initialized'] = saga_dir.exists()
    
    if ctx.obj['is_initialized']:
        ctx.obj['config'] = Config(saga_dir / 'config.json')
        ctx.obj['git'] = GitRepository()
        ctx.obj['searcher'] = TextSearcher(saga_dir / 'sagas')


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize a GitSaga repository"""
    show_banner()
    saga_dir = ctx.obj['saga_dir']
    
    if saga_dir.exists():
        console.print("[yellow]Warning: GitSaga already initialized in this directory[/yellow]")
        if not click.confirm("Reinitialize?"):
            return
    
    # Initialize repository
    config = Config.init_repository(Path.cwd())
    
    console.print("[green][OK] GitSaga repository initialized![/green]")
    console.print(f"• Created .sagashark/ directory")
    console.print(f"• Configuration saved to .sagashark/config.json")
    
    # Check if we're in a git repository
    git_dir = Path.cwd() / '.git'
    if git_dir.exists():
        # Offer to install git hooks
        console.print("\n[bold]Install git hooks for automatic saga capture?[/bold]")
        console.print("This will automatically create sagas for significant commits.")
        
        if click.confirm("Install git hooks?", default=True):
            # Install hooks
            src_hook = Path(__file__).parent / 'hooks' / 'post_commit.py'
            hooks_dir = git_dir / 'hooks'
            hooks_dir.mkdir(exist_ok=True)
            dest_hook = hooks_dir / 'post-commit'
            
            if dest_hook.exists():
                if click.confirm("post-commit hook already exists. Overwrite?", default=False):
                    shutil.copy2(src_hook, dest_hook)
                    console.print("[green]✓ Git hooks installed![/green]")
            else:
                shutil.copy2(src_hook, dest_hook)
                # Make executable on Unix-like systems
                if os.name != 'nt':
                    import stat
                    dest_hook.chmod(dest_hook.stat().st_mode | stat.S_IEXEC)
                console.print("[green]✓ Git hooks installed for automatic capture![/green]")
        else:
            console.print("You can install hooks later with: [cyan]saga install-hooks[/cyan]")
    
    # Offer to set up AI features
    console.print("\n[bold]Optional: Set up AI features?[/bold]")
    console.print("This will install Ollama and download a small AI model (638MB).")
    console.print("AI features enhance automatic saga capture and structure.")
    
    if click.confirm("Set up AI features now?", default=True):
        from gitsaga.setup import OllamaAutoInstaller
        installer = OllamaAutoInstaller()
        installer.full_setup()
    else:
        console.print("You can set up AI later with: [cyan]saga setup-ai[/cyan]")
    
    console.print("\n[green]✨ GitSaga is ready![/green]")
    console.print("\nNext steps:")
    console.print("  • Create your first saga: [cyan]saga commit \"Initial setup\"[/cyan]")
    console.print("  • Search for sagas: [cyan]saga search \"keyword\"[/cyan]")
    console.print("  • View help: [cyan]saga --help[/cyan]")


@cli.command()
@click.argument('message')
@click.option('--type', 'saga_type', default='general', 
              type=click.Choice(['general', 'debugging', 'feature', 'architecture', 'optimization']),
              help='Type of saga')
@click.option('--content', '-c', help='Saga content (will prompt if not provided)')
@click.option('--tags', '-t', help='Comma-separated tags')
@click.pass_context
def commit(ctx, message, saga_type, content, tags):
    """Create a new saga"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    git = ctx.obj['git']
    
    # Get git context
    branch = git.get_current_branch()
    modified_files = git.get_modified_files()
    
    # Parse tags
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
    
    # Auto-generate tags from git context
    last_commit = git.get_last_commit_message()
    if last_commit:
        auto_tags = git.extract_tags_from_commit(last_commit)
        tag_list.extend([t for t in auto_tags if t not in tag_list])
    
    # Get content if not provided
    if not content:
        console.print("[cyan]Enter saga content (Ctrl+D or Ctrl+Z when done):[/cyan]")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        content = '\n'.join(lines)
        
        if not content.strip():
            console.print("[yellow]Warning: No content provided. Creating minimal saga.[/yellow]")
            content = f"## Context\n\nWorking on: {message}\n\n## Changes\n\nModified files:\n"
            for f in modified_files[:5]:
                content += f"- {f}\n"
    
    # Create saga
    saga = Saga(
        title=message,
        content=content,
        saga_type=saga_type,
        branch=branch,
        tags=tag_list,
        files_changed=modified_files
    )
    
    # Determine storage directory
    saga_base_dir = ctx.obj['saga_dir'] / 'sagas'
    
    # Organize by branch
    if branch != 'main':
        saga_dir = saga_base_dir / branch / saga_type
    else:
        saga_dir = saga_base_dir / saga_type
    
    # Save saga
    filepath = saga.save(saga_dir)
    
    console.print(f"[green][OK] Saga created successfully![/green]")
    console.print(f"ID: [cyan]{saga.id}[/cyan]")
    console.print(f"Saved to: {filepath.relative_to(Path.cwd())}")
    console.print(f"Tags: {', '.join(tag_list) if tag_list else 'none'}")
    console.print(f"Branch: {branch}")


@cli.command()
@click.argument('query')
@click.option('--limit', '-l', default=5, help='Maximum results to show')
@click.pass_context
def search(ctx, query, limit):
    """Search for sagas"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    # Try hybrid search first
    try:
        from gitsaga.search.vector_search import HybridSearcher
        searcher = HybridSearcher(ctx.obj['saga_dir'])
        results = searcher.search(query, limit=limit, mode='hybrid')
        console.print("[dim]Using hybrid search (text + semantic)[/dim]")
    except ImportError:
        # Fallback to text search
        searcher = ctx.obj['searcher']
        results = searcher.search(query, limit=limit)
        console.print("[dim]Using text search (install faiss-cpu for semantic search)[/dim]")
    
    if not results:
        console.print(f"[yellow]No sagas found matching '{query}'[/yellow]")
        return
    
    # Display results
    table = Table(title=f"Search Results for '{query}'")
    table.add_column("Score", style="cyan", width=8)
    table.add_column("Title", style="green")
    table.add_column("Type", style="yellow", width=12)
    table.add_column("Date", style="blue", width=10)
    table.add_column("Preview", style="dim")
    
    for saga, score in results:
        date_str = saga.timestamp.strftime("%Y-%m-%d")
        preview = saga.get_preview(max_lines=1)[:50] + "..."
        
        table.add_row(
            f"{score:.1f}",
            saga.title[:40] + ("..." if len(saga.title) > 40 else ""),
            saga.saga_type,
            date_str,
            preview
        )
    
    console.print(table)
    console.print(f"\nTip: Use 'saga show <id>' to view full saga content")


@cli.command()
@click.option('--limit', '-l', default=10, help='Number of sagas to show')
@click.option('--since', '-s', help='Show sagas since date (YYYY-MM-DD or "yesterday", "week")')
@click.pass_context
def log(ctx, limit, since):
    """Show recent sagas chronologically"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    searcher = ctx.obj['searcher']
    
    # Parse since date
    min_date = None
    if since:
        if since == "yesterday":
            min_date = datetime.now() - timedelta(days=1)
        elif since == "week":
            min_date = datetime.now() - timedelta(days=7)
        elif since == "month":
            min_date = datetime.now() - timedelta(days=30)
        else:
            try:
                min_date = datetime.strptime(since, "%Y-%m-%d")
            except ValueError:
                console.print(f"[red]Invalid date format: {since}[/red]")
                return
    
    # Get recent sagas
    sagas = searcher.get_recent(limit=limit * 2 if min_date else limit)
    
    # Filter by date if needed
    if min_date:
        sagas = [s for s in sagas if s.timestamp >= min_date][:limit]
    
    if not sagas:
        console.print("[yellow]No sagas found[/yellow]")
        return
    
    # Display sagas
    console.print("[bold]Recent Sagas[/bold]\n")
    
    for saga in sagas:
        # Create a panel for each saga
        header = f"[cyan]{saga.id}[/cyan] | [green]{saga.title}[/green]"
        metadata = f"[dim]{saga.timestamp.strftime('%Y-%m-%d %H:%M')} | {saga.saga_type} | {saga.branch}[/dim]"
        
        if saga.tags:
            tags_str = f"Tags: {', '.join(saga.tags)}"
        else:
            tags_str = ""
        
        preview = saga.get_preview(max_lines=2)
        
        content = f"{metadata}\n{tags_str}\n\n{preview}"
        
        panel = Panel(content, title=header, title_align="left")
        console.print(panel)


@cli.command()
@click.argument('saga_id')
@click.pass_context
def show(ctx, saga_id):
    """Display a specific saga"""
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    # Find saga by ID
    saga_dir = ctx.obj['saga_dir'] / 'sagas'
    found_saga = None
    saga_file = None
    
    for file_path in saga_dir.glob('**/*.md'):
        try:
            saga = Saga.from_file(file_path)
            if saga.id == saga_id or saga.id.startswith(saga_id):
                found_saga = saga
                saga_file = file_path
                break
        except Exception:
            continue
    
    if not found_saga:
        console.print(f"[red]Saga not found: {saga_id}[/red]")
        return
    
    # Display saga
    console.print(f"\n[bold cyan]Saga: {found_saga.id}[/bold cyan]")
    console.print(f"[bold green]{found_saga.title}[/bold green]\n")
    
    # Metadata
    console.print(f"Created: {found_saga.timestamp.strftime('%Y-%m-%d %H:%M')}")
    console.print(f"Branch: {found_saga.branch}")
    console.print(f"Type: {found_saga.saga_type}")
    
    if found_saga.tags:
        console.print(f"Tags: {', '.join(found_saga.tags)}")
    
    if found_saga.files_changed:
        console.print(f"Files: {', '.join(found_saga.files_changed[:5])}")
    
    console.print("")
    
    # Content
    console.print(Panel(Markdown(found_saga.content), title="Content", title_align="left"))
    
    console.print(f"\n[dim]File: {saga_file.relative_to(Path.cwd())}[/dim]")


@cli.command()
@click.pass_context
def status(ctx):
    """Show GitSaga repository status"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    saga_dir = ctx.obj['saga_dir'] / 'sagas'
    
    # Count sagas
    total_sagas = len(list(saga_dir.glob('**/*.md')))
    
    # Count by type
    type_counts = {}
    for file_path in saga_dir.glob('**/*.md'):
        try:
            saga = Saga.from_file(file_path)
            type_counts[saga.saga_type] = type_counts.get(saga.saga_type, 0) + 1
        except Exception:
            continue
    
    # Get git info
    git = ctx.obj['git']
    git_info = git.get_repo_info()
    
    # Display status
    console.print("[bold]GitSaga Repository Status[/bold]\n")
    
    console.print(f"Total sagas: [cyan]{total_sagas}[/cyan]")
    
    if type_counts:
        console.print("\n[bold]Sagas by type:[/bold]")
        for saga_type, count in sorted(type_counts.items()):
            console.print(f"  • {saga_type}: {count}")
    
    console.print(f"\n[bold]Git Status:[/bold]")
    console.print(f"  Current branch: [green]{git_info['branch']}[/green]")
    
    if git_info['modified_files']:
        console.print(f"  Modified files: {len(git_info['modified_files'])}")
        for f in git_info['modified_files'][:5]:
            console.print(f"     - {f}")
        if len(git_info['modified_files']) > 5:
            console.print(f"     ... and {len(git_info['modified_files']) - 5} more")
    
    # Recent activity
    searcher = ctx.obj['searcher']
    recent = searcher.get_recent(limit=3)
    
    if recent:
        console.print("\n[bold]Recent sagas:[/bold]")
        for saga in recent:
            date_str = saga.timestamp.strftime("%Y-%m-%d %H:%M")
            console.print(f"  • [{date_str}] {saga.title[:50]}")


@cli.command()
@click.option('--commit', '-c', default='HEAD', help='Commit to capture (default: HEAD)')
@click.option('--force', '-f', is_flag=True, help='Force capture even if not significant')
@click.pass_context
def capture(ctx, commit, force):
    """Capture a saga from a git commit"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    # Auto-setup AI if not configured
    from gitsaga.setup import check_and_setup_ollama
    check_and_setup_ollama(silent=True)
    
    chronicler = AutoChronicler()
    
    if force:
        # Temporarily lower the threshold to capture
        chronicler.scorer.min_threshold = 0.0
    
    saga = chronicler.capture_from_commit(commit)
    
    if saga:
        console.print(f"[green]✓ Captured saga: {saga.title}[/green]")
    else:
        console.print("[yellow]Commit not significant enough for saga capture.[/yellow]")
        console.print("Use --force to capture anyway.")


@cli.command()
@click.option('--since', '-s', default='HEAD~10', help='Analyze commits since (default: HEAD~10)')
@click.option('--dry-run', is_flag=True, help='Show what would be captured without saving')
@click.pass_context
def monitor(ctx, since, dry_run):
    """Monitor recent commits and capture significant sagas"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    chronicler = AutoChronicler()
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No sagas will be saved[/yellow]\n")
    
    chronicler.monitor_commits(since)


@cli.command()
@click.argument('commit', default='HEAD')
@click.pass_context
def score(ctx, commit):
    """Score a commit's significance for saga capture"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    chronicler = AutoChronicler()
    context = chronicler._get_commit_context(commit)
    
    if not context:
        console.print(f"[red]Could not get context for commit {commit}[/red]")
        return
    
    scorer = SignificanceScorer()
    result = scorer.calculate_score(context)
    
    # Display results
    console.print(f"\n[bold]Commit Significance Analysis[/bold]")
    console.print(f"Commit: {commit[:8]}")
    console.print(f"Message: {context.message.split(chr(10))[0][:60]}...")
    console.print(f"\n[bold]Score: {result['score']:.2f}[/bold]")
    
    if result['is_significant']:
        console.print("[green]✓ This commit is saga-worthy![/green]")
    else:
        console.print("[yellow]✗ Not significant enough for automatic capture[/yellow]")
    
    console.print(f"\nSuggested type: [cyan]{result['suggested_type']}[/cyan]")
    
    if result['factors']:
        console.print("\n[bold]Scoring factors:[/bold]")
        for factor in result['factors']:
            console.print(f"  • {factor}")


@cli.command()
@click.argument('saga_type', type=click.Choice(['debugging', 'feature', 'incident']))
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def template(ctx, saga_type, output):
    """Generate a saga template for manual documentation"""
    show_banner()
    
    try:
        from gitsaga.butler.dspy_integration import SagaEnhancer
        enhancer = SagaEnhancer(use_local=False)  # Don't need AI for templates
        template_content = enhancer.generate_saga_template(saga_type)
        
        if output:
            output_path = Path(output)
            output_path.write_text(template_content)
            console.print(f"[green]✓ Template saved to {output}[/green]")
        else:
            console.print(template_content)
            
    except ImportError:
        console.print("[yellow]DSPy not installed. Install with: pip install dspy-ai[/yellow]")
        # Provide basic template
        basic_template = f"""# [{saga_type.title()} Title]

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Type**: {saga_type.title()}

## Summary
[Add summary here]

## Details
[Add details here]

## Lessons Learned
[Add lessons here]
"""
        if output:
            Path(output).write_text(basic_template)
            console.print(f"[green]✓ Basic template saved to {output}[/green]")
        else:
            console.print(basic_template)


@cli.command()
@click.argument('saga_file')
@click.pass_context
def validate(ctx, saga_file):
    """Validate saga completeness and quality"""
    show_banner()
    
    if not Path(saga_file).exists():
        console.print(f"[red]File not found: {saga_file}[/red]")
        return
    
    try:
        from gitsaga.butler.dspy_integration import SagaEnhancer
        from gitsaga.core.saga import Saga
        
        # Load saga
        saga = Saga.from_file(Path(saga_file))
        
        # Validate with DSPy
        enhancer = SagaEnhancer(use_local=False)
        validation = enhancer.validate_saga_completeness(saga.content, saga.saga_type)
        
        # Display results
        console.print(f"\n[bold]Saga Validation Report[/bold]")
        console.print(f"File: {saga_file}")
        console.print(f"Type: {saga.saga_type}")
        console.print(f"\nCompleteness Score: [{'green' if validation['completeness_score'] >= 0.8 else 'yellow'}]{validation['completeness_score']:.0%}[/]")
        
        if validation['present_sections']:
            console.print("\n[green]✓ Present Sections:[/green]")
            for section in validation['present_sections']:
                console.print(f"  • {section}")
        
        if validation['missing_sections']:
            console.print("\n[yellow]⚠ Missing Sections:[/yellow]")
            for section in validation['missing_sections']:
                console.print(f"  • {section}")
        
        if validation['recommendations']:
            console.print("\n[bold]Recommendations:[/bold]")
            for rec in validation['recommendations']:
                console.print(f"  • {rec}")
                
    except ImportError:
        console.print("[yellow]DSPy not installed. Cannot validate saga structure.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error validating saga: {e}[/red]")


@cli.command()
@click.pass_context
def reindex(ctx):
    """Rebuild the vector search index"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    try:
        from gitsaga.search.vector_search import VectorSearcher
        
        console.print("Building vector search index...")
        searcher = VectorSearcher(ctx.obj['saga_dir'])
        searcher.reindex_all()
        
        stats = searcher.get_index_stats()
        console.print(f"[green]✓ Indexed {stats['total_sagas']} sagas[/green]")
        console.print(f"Model: {stats['model']}")
        console.print(f"Vector dimension: {stats['dimension']}")
        
    except ImportError:
        console.print("[yellow]Vector search not available.[/yellow]")
        console.print("Install with: pip install faiss-cpu sentence-transformers")
    except Exception as e:
        console.print(f"[red]Error building index: {e}[/red]")


@cli.command('find-similar')
@click.argument('saga_id')
@click.option('--limit', '-l', default=5, help='Number of similar sagas to find')
@click.pass_context
def find_similar(ctx, saga_id, limit):
    """Find sagas similar to a given saga"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    try:
        from gitsaga.search.vector_search import VectorSearcher
        
        searcher = VectorSearcher(ctx.obj['saga_dir'])
        results = searcher.find_similar(saga_id, limit=limit)
        
        if not results:
            console.print(f"[yellow]No similar sagas found for '{saga_id}'[/yellow]")
            return
        
        console.print(f"\n[bold]Sagas similar to {saga_id}:[/bold]\n")
        
        for i, result in enumerate(results, 1):
            console.print(f"{i}. [cyan]{result.title}[/cyan]")
            console.print(f"   ID: {result.saga_id}")
            console.print(f"   Similarity: {result.score:.2f}")
            console.print(f"   {result.preview[:100]}...")
            console.print()
            
    except ImportError:
        console.print("[yellow]Vector search not available.[/yellow]")
        console.print("Install with: pip install faiss-cpu sentence-transformers")
    except Exception as e:
        console.print(f"[red]Error finding similar sagas: {e}[/red]")


@cli.command()
@click.pass_context
def uninstall_help(ctx):
    """Show uninstall instructions"""
    show_banner()
    
    console.print("\n[bold]🗑️  How to Uninstall GitSaga[/bold]\n")
    
    console.print("[bold]Quick Uninstall:[/bold]")
    console.print("  pip uninstall gitsaga\n")
    
    console.print("[bold]Complete Cleanup:[/bold]")
    console.print("  1. Uninstall package:     [cyan]pip uninstall gitsaga[/cyan]")
    console.print("  2. Remove git hooks:      [cyan]rm .git/hooks/post-commit[/cyan]")
    console.print("  3. Remove saga data:      [cyan]rm -rf .sagadex/[/cyan]")
    console.print("  4. Or keep sagas:         [cyan]rm .sagadex/config.json[/cyan]\n")
    
    console.print("[bold]Using Uninstall Script:[/bold]")
    console.print("  [cyan]python path/to/gitsaga/uninstall.py[/cyan]")
    console.print("  Options:")
    console.print("    --keep-sagas     Keep your saga documentation (default)")
    console.print("    --remove-sagas   Remove everything")
    console.print("    --remove-ollama  Also uninstall Ollama\n")
    
    console.print("[bold]What Gets Removed:[/bold]")
    console.print("  • Python package and CLI commands")
    console.print("  • Git hooks (per repository)")
    console.print("  • Configuration files")
    console.print("  • Search indexes")
    console.print("  • Optionally: saga files and Ollama\n")
    
    console.print("[bold]💡 Tip:[/bold] Keep your sagas! They're valuable documentation.")
    console.print("")
    console.print("[bold]To Reinstall:[/bold]")
    console.print("  [cyan]pip install gitsaga[/cyan]")
    console.print("  [cyan]saga init[/cyan]")


@cli.command()
@click.pass_context  
def setup_ai(ctx):
    """Set up AI features (installs Ollama and downloads model)"""
    show_banner()
    
    # Show critical warning about small models
    console.print("\n[bold red]⚠️ CRITICAL WARNING: Small LLM Risk[/bold red]")
    console.print("[yellow]Small models (under 7B parameters) like TinyLlama will:[/yellow]")
    console.print("  • Hallucinate and create false information")
    console.print("  • Corrupt your debugging documentation")
    console.print("  • Generate incorrect root causes and solutions")
    console.print("\n[bold]Only use models with 7B+ parameters:[/bold]")
    console.print("  • Llama 2 7B or larger (recommended)")
    console.print("  • CodeLlama 7B+")
    console.print("  • Mistral 7B")
    console.print("  • Mixtral 8x7B")
    console.print("\n[red]NEVER use: TinyLlama, Phi, StableLM, or any model under 7B[/red]")
    console.print("\nSee HALLUCINATION_WARNING.md for details.")
    
    if not click.confirm("\nDo you understand the risks and want to proceed?"):
        console.print("[green]Good choice! GitSaga works perfectly without AI.[/green]")
        return
    
    from gitsaga.setup import OllamaAutoInstaller
    
    installer = OllamaAutoInstaller()
    if installer.full_setup():
        console.print("\n[green]✨ AI features are configured and ready![/green]")
        console.print("[bold yellow]Remember: Only use 7B+ parameter models![/bold yellow]")
        console.print("Try: saga capture --force")
    else:
        console.print("\n[yellow]AI setup incomplete. GitSaga will work with basic features.[/yellow]")


@cli.command()
@click.argument('commit', default='HEAD')
@click.pass_context
def enhance(ctx, commit):
    """Add high-value debugging details to a saga"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    from .capture.interactive_capture import InteractiveCapturer
    from .capture.auto_chronicler import AutoChronicler
    
    console.print(f"[cyan]Enhancing saga for commit {commit}...[/cyan]")
    
    # Get the basic saga from the commit
    chronicler = AutoChronicler()
    context = chronicler._get_commit_context(commit)
    
    if not context:
        console.print(f"[red]Could not find commit {commit}[/red]")
        return
    
    # Create a basic saga if needed
    saga = chronicler.capture_from_commit(commit)
    if not saga:
        console.print("[yellow]Creating saga from commit...[/yellow]")
        saga = Saga(
            title=context.message.split('\n')[0][:80],
            content=f"Commit: {context.hash[:8]}\n{context.message}",
            saga_type='debugging'
        )
    
    # Prompt for high-value information
    capturer = InteractiveCapturer()
    enhanced_saga = capturer.capture_high_value_info(context.message, saga)
    
    # Save the enhanced saga
    saga_path = enhanced_saga.save(Path.cwd() / '.sagashark' / 'sagas')
    console.print(f"[green]✓ Enhanced saga saved: {saga_path.name}[/green]")


@cli.command()
@click.option('--dry-run', is_flag=True, help='Preview changes without moving files')
@click.option('--cleanup', is_flag=True, help='Remove empty directories after organizing')
@click.pass_context
def organize(ctx, dry_run, cleanup):
    """Organize sagas into year/month/week folder structure"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    from .core.organizer import SagaOrganizer
    
    organizer = SagaOrganizer(ctx.obj['saga_dir'] / 'sagas')
    
    # Get current statistics
    stats = organizer.get_statistics()
    
    if stats['unorganized_sagas'] == 0:
        console.print("[green]✓ All sagas are already organized![/green]")
        console.print(f"Total sagas: {stats['total_sagas']}")
        if stats['by_year']:
            console.print("\n[bold]By Year:[/bold]")
            for year, count in sorted(stats['by_year'].items()):
                console.print(f"  {year}: {count} sagas")
        return
    
    console.print(f"[yellow]Found {stats['unorganized_sagas']} unorganized sagas[/yellow]")
    
    if dry_run:
        console.print("\n[bold]DRY RUN - No files will be moved[/bold]")
    
    # Organize all sagas
    moves = organizer.organize_all(dry_run=dry_run)
    
    if moves:
        console.print(f"\n[bold]{'Would move' if dry_run else 'Moving'} {len(moves)} sagas:[/bold]")
        
        # Group by year/month for display
        by_period = {}
        for old_path, new_path in moves[:10]:  # Show first 10
            period = '/'.join(new_path.relative_to(organizer.saga_dir).parts[:2])
            if period not in by_period:
                by_period[period] = 0
            by_period[period] += 1
            
            console.print(f"  {old_path.name} → {period}/...")
        
        if len(moves) > 10:
            console.print(f"  ... and {len(moves) - 10} more")
        
        if not dry_run:
            console.print(f"\n[green]✓ Organized {len(moves)} sagas[/green]")
            
            if cleanup:
                organizer.cleanup_empty_dirs()
                console.print("[green]✓ Cleaned up empty directories[/green]")
    
    # Show new statistics
    if not dry_run:
        new_stats = organizer.get_statistics()
        console.print("\n[bold]New Structure:[/bold]")
        for year, count in sorted(new_stats['by_year'].items()):
            console.print(f"  {year}: {count} sagas")
    
    if dry_run:
        console.print("\n[dim]Run without --dry-run to apply changes[/dim]")


@cli.command('install-hooks')
@click.pass_context
def install_hooks(ctx):
    """Install git hooks for automatic saga capture"""
    show_banner()
    if not ctx.obj['is_initialized']:
        console.print("[red]X GitSaga not initialized. Run 'saga init' first.[/red]")
        sys.exit(1)
    
    import shutil
    
    # Source hook file
    src_hook = Path(__file__).parent / 'hooks' / 'post_commit.py'
    
    # Destination in .git/hooks
    git_dir = Path.cwd() / '.git'
    if not git_dir.exists():
        console.print("[red]Not in a git repository![/red]")
        return
    
    hooks_dir = git_dir / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    dest_hook = hooks_dir / 'post-commit'
    
    # Check if hook already exists
    if dest_hook.exists():
        if not click.confirm("post-commit hook already exists. Overwrite?"):
            console.print("[yellow]Hook installation cancelled[/yellow]")
            return
    
    # Copy hook file
    shutil.copy2(src_hook, dest_hook)
    
    # Make executable on Unix-like systems
    if os.name != 'nt':
        import stat
        dest_hook.chmod(dest_hook.stat().st_mode | stat.S_IEXEC)
    
    console.print("[green]✓ Git hooks installed successfully![/green]")
    console.print("Sagas will now be automatically captured for significant commits.")
    console.print("\nTo test: make a commit with 'fix' or 'feature' in the message.")


if __name__ == '__main__':
    cli()