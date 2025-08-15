#!/usr/bin/env python3
"""
GitSaga Uninstaller - Clean removal of GitSaga
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
import click


@click.command()
@click.option('--keep-sagas/--remove-sagas', default=True, help='Keep existing saga files')
@click.option('--remove-ollama', is_flag=True, help='Also uninstall Ollama')
def uninstall(keep_sagas, remove_ollama):
    """Uninstall GitSaga and optionally clean up data"""
    
    print("🗑️  GitSaga Uninstaller")
    print("-" * 40)
    
    # 1. Uninstall Python package
    print("\n1. Uninstalling GitSaga package...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'gitsaga', '-y'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ Package uninstalled")
        else:
            print("   ⚠ Package not found or already uninstalled")
    except Exception as e:
        print(f"   ⚠ Could not uninstall: {e}")
    
    # 2. Remove git hooks
    print("\n2. Removing git hooks...")
    git_dir = Path.cwd() / '.git'
    if git_dir.exists():
        hook_file = git_dir / 'hooks' / 'post-commit'
        if hook_file.exists():
            # Check if it's our hook
            try:
                content = hook_file.read_text()
                if 'gitsaga' in content.lower():
                    hook_file.unlink()
                    print("   ✓ Git hook removed")
                else:
                    print("   ⚠ post-commit hook exists but doesn't appear to be GitSaga's")
            except:
                print("   ⚠ Could not check hook file")
    else:
        print("   ℹ Not in a git repository")
    
    # 3. Handle saga data
    print("\n3. Handling saga data...")
    sagadex = Path.cwd() / '.sagadex'
    if sagadex.exists():
        if keep_sagas:
            # Just remove config and index, keep sagas
            config_file = sagadex / 'config.json'
            index_dir = sagadex / '.vector_index'
            
            if config_file.exists():
                config_file.unlink()
                print("   ✓ Removed config file")
            
            if index_dir.exists():
                shutil.rmtree(index_dir)
                print("   ✓ Removed search index")
                
            print("   ℹ Kept saga files in .sagadex/sagas/")
        else:
            if click.confirm(f"   Remove {len(list(sagadex.glob('**/*.md')))} saga files?"):
                shutil.rmtree(sagadex)
                print("   ✓ Removed all saga data")
            else:
                print("   ℹ Kept saga files")
    else:
        print("   ℹ No saga data found in current directory")
    
    # 4. Remove Ollama (optional)
    if remove_ollama:
        print("\n4. Removing Ollama...")
        if sys.platform == 'win32':
            print("   Please uninstall Ollama via Windows Add/Remove Programs")
            print("   Or run: winget uninstall Ollama.Ollama")
        elif sys.platform == 'darwin':
            subprocess.run(['brew', 'uninstall', 'ollama'], capture_output=True)
            print("   ✓ Ollama uninstalled (if it was installed via brew)")
        else:  # Linux
            ollama_bin = Path('/usr/local/bin/ollama')
            if ollama_bin.exists():
                subprocess.run(['sudo', 'rm', '-rf', '/usr/local/bin/ollama'], capture_output=True)
                subprocess.run(['sudo', 'rm', '-rf', str(Path.home() / '.ollama')], capture_output=True)
                print("   ✓ Ollama removed")
            else:
                print("   ℹ Ollama not found")
    
    # 5. Clean up any remaining GitSaga directories
    print("\n5. Final cleanup...")
    
    # Check for GitSaga in site-packages (in case of regular install)
    try:
        import site
        site_packages = Path(site.getsitepackages()[0])
        gitsaga_dir = site_packages / 'gitsaga'
        if gitsaga_dir.exists():
            print(f"   Found GitSaga in {gitsaga_dir}")
            if click.confirm("   Remove?"):
                shutil.rmtree(gitsaga_dir)
                print("   ✓ Removed")
    except:
        pass
    
    print("\n" + "=" * 40)
    print("✅ GitSaga uninstallation complete!")
    
    if keep_sagas and sagadex.exists():
        print(f"\n📁 Your sagas are preserved in: {sagadex / 'sagas'}")
        print("   You can manually delete them anytime with:")
        print(f"   rm -rf {sagadex}")
    
    print("\nTo reinstall GitSaga later:")
    print("   pip install gitsaga")
    print("\nThank you for trying GitSaga! 🙏")


if __name__ == '__main__':
    uninstall()