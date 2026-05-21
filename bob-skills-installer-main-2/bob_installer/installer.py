"""Core installation logic for Bob Skills."""

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Any
import git
from git.exc import GitCommandError
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .config import ConfigManager

console = Console()


class SkillsInstaller:
    """Handles installation and management of Bob skills."""
    
    # Skills catalog with metadata
    SKILLS_CATALOG = {
        'docx': {
            'name': 'docx',
            'category': 'document',
            'description': 'Create, edit, and analyze Word documents (.docx files)',
            'license': 'Proprietary',
            'keywords': ['word', 'document', 'docx', 'doc file']
        },
        'pdf': {
            'name': 'pdf',
            'category': 'document',
            'description': 'PDF manipulation and extraction',
            'license': 'Proprietary',
            'keywords': ['pdf', 'extract text', 'fill form']
        },
        'xlsx': {
            'name': 'xlsx',
            'category': 'document',
            'description': 'Excel spreadsheet operations',
            'license': 'Proprietary',
            'keywords': ['excel', 'spreadsheet', 'xlsx', 'csv']
        },
        'pptx': {
            'name': 'pptx',
            'category': 'document',
            'description': 'PowerPoint presentation creation',
            'license': 'Proprietary',
            'keywords': ['powerpoint', 'presentation', 'slides', 'pptx']
        },
        'mcp-builder': {
            'name': 'mcp-builder',
            'category': 'development',
            'description': 'Build Model Context Protocol servers',
            'license': 'Apache-2.0',
            'keywords': ['mcp server', 'build tool', 'create tool']
        },
        'algorithmic-art': {
            'name': 'algorithmic-art',
            'category': 'creative',
            'description': 'Generate algorithmic art using p5.js',
            'license': 'Apache-2.0',
            'keywords': ['algorithmic art', 'generative art', 'p5.js']
        },
        'canvas-design': {
            'name': 'canvas-design',
            'category': 'creative',
            'description': 'Create visual designs and posters',
            'license': 'Apache-2.0',
            'keywords': ['poster', 'design', 'visual art', 'canvas']
        },
        'doc-coauthoring': {
            'name': 'doc-coauthoring',
            'category': 'document',
            'description': 'Collaborative document editing workflows',
            'license': 'Apache-2.0',
            'keywords': ['collaborate', 'coauthor', 'document editing']
        },
        'frontend-design': {
            'name': 'frontend-design',
            'category': 'development',
            'description': 'Build frontend interfaces and web components',
            'license': 'Apache-2.0',
            'keywords': ['website', 'landing page', 'web app', 'dashboard', 'frontend']
        },
        'internal-comms': {
            'name': 'internal-comms',
            'category': 'enterprise',
            'description': 'Internal communications templates',
            'license': 'Apache-2.0',
            'keywords': ['internal communication', 'announcement', 'memo']
        },
        'skill-creator': {
            'name': 'skill-creator',
            'category': 'utility',
            'description': 'Create new custom skills',
            'license': 'Apache-2.0',
            'keywords': ['create skill', 'new skill', 'build skill']
        },
        'slack-gif-creator': {
            'name': 'slack-gif-creator',
            'category': 'creative',
            'description': 'Create animated GIFs for Slack',
            'license': 'Apache-2.0',
            'keywords': ['slack', 'gif', 'animation']
        },
        'theme-factory': {
            'name': 'theme-factory',
            'category': 'creative',
            'description': 'Generate design themes',
            'license': 'Apache-2.0',
            'keywords': ['theme', 'color scheme', 'design system']
        },
        'web-artifacts-builder': {
            'name': 'web-artifacts-builder',
            'category': 'development',
            'description': 'Create web artifacts and components',
            'license': 'Apache-2.0',
            'keywords': ['web artifact', 'component', 'widget']
        },
        'webapp-testing': {
            'name': 'webapp-testing',
            'category': 'development',
            'description': 'Test web applications with Playwright',
            'license': 'Apache-2.0',
            'keywords': ['test', 'playwright', 'web testing', 'automation']
        },
        'brand-guidelines': {
            'name': 'brand-guidelines',
            'category': 'enterprise',
            'description': 'Brand consistency enforcement',
            'license': 'Apache-2.0',
            'keywords': ['brand', 'guidelines', 'style guide']
        }
    }
    
    REPO_URL = "https://github.com/anthropics/skills.git"
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.config = ConfigManager(base_path)
        
    def install(self, skills: Optional[List[str]] = None, 
                install_all: bool = True) -> Dict:
        """Install skills to the project."""
        
        # Initialize if needed
        if not self.config.is_initialized():
            self.config.initialize()
        
        # Check if any skills are already installed
        existing_skills = self.config.get_installed_skills()
        if existing_skills and not skills:
            # User is trying to install all skills but some already exist
            console.print("\n⚠️  [yellow]Skills are already installed.[/yellow]")
            console.print("\nOptions:")
            console.print("  • Use [cyan]bob-skills update[/cyan] to update existing skills")
            console.print("  • Use [cyan]bob-skills uninstall <skill>[/cyan] then [cyan]bob-skills install -s <skill>[/cyan] to reinstall")
            console.print("  • Use [cyan]bob-skills install -s <skill>[/cyan] to install specific additional skills")
            raise RuntimeError("Skills already installed. Use update or uninstall first.")
        
        # Determine which skills to install
        if install_all:
            skills_to_install = list(self.SKILLS_CATALOG.keys())
        elif skills:
            skills_to_install = skills
        else:
            skills_to_install = list(self.SKILLS_CATALOG.keys())
        
        # Validate skills
        invalid_skills = [s for s in skills_to_install
                         if s not in self.SKILLS_CATALOG]
        if invalid_skills:
            raise ValueError(f"Invalid skills: {', '.join(invalid_skills)}")
        
        # Clone repository to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            console.print(f"📥 Downloading skills from {self.REPO_URL}...")
            
            try:
                repo = git.Repo.clone_from(
                    self.REPO_URL,
                    temp_dir,
                    depth=1,  # Shallow clone for speed
                    branch='main'
                )
            except Exception as e:
                raise RuntimeError(f"Failed to clone repository: {str(e)}")
            
            # Install each skill
            installed = []
            for skill_name in skills_to_install:
                skill_info = self.SKILLS_CATALOG[skill_name]
                
                source_path = Path(temp_dir) / "skills" / skill_name
                dest_path = self.config.skills_dir / skill_name
                
                if not source_path.exists():
                    console.print(f"⚠️  Skill '{skill_name}' not found in repository, skipping...")
                    continue
                
                # Check if this is a custom skill (don't overwrite)
                existing_skill = next((s for s in existing_skills if s['name'] == skill_name), None)
                if existing_skill and existing_skill.get('custom'):
                    console.print(f"⚠️  Skipping '{skill_name}' - it's a custom skill. Uninstall first if you want to replace it.")
                    continue
                
                # Copy skill directory
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                
                shutil.copytree(source_path, dest_path)
                
                # Update config
                self.config.add_installed_skill(skill_name, skill_info)
                
                installed.append(skill_info)
        
        # Generate rules file with ALL installed skills (including custom)
        all_installed = self.config.get_installed_skills()
        self._generate_rules_file(all_installed)
        
        return {
            'installed': installed,
            'count': len(installed)
        }
    
    def interactive_selection(self) -> List[str]:
        """Interactive skill selection interface."""
        
        console.print("\n🎯 [bold]Bob Skills Installer[/bold]")
        console.print("━" * 60)
        
        # Group skills by category
        categories = {}
        for skill_name, skill_info in self.SKILLS_CATALOG.items():
            category = skill_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(skill_info)
        
        # Display skills by category
        selected = []
        
        for category, skills in sorted(categories.items()):
            console.print(f"\n[bold cyan]{category.title()} Skills:[/bold cyan]")
            
            for skill in skills:
                choice = Confirm.ask(
                    f"  Install {skill['name']}? ({skill['description']})",
                    default=True
                )
                if choice:
                    selected.append(skill['name'])
        
        if not selected:
            console.print("\n⚠️  No skills selected. Installing all skills by default.")
            return list(self.SKILLS_CATALOG.keys())
        
        return selected
    
    def _extract_skill_keywords(self, skill_name: str) -> Dict[str, Any]:
        """Extract keywords and metadata from a skill's SKILL.md file.
        
        Supports YAML frontmatter format:
        ---
        keywords: keyword1, keyword2, keyword3
        triggers: "trigger phrase 1", "trigger phrase 2"
        description: Skill description
        ---
        """
        skill_path = self.config.skills_dir / skill_name / "SKILL.md"
        
        keywords = []
        description = ""
        
        if skill_path.exists():
            try:
                with open(skill_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Parse YAML frontmatter if present
                    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                    if frontmatter_match:
                        frontmatter = frontmatter_match.group(1)
                        
                        # Extract keywords from frontmatter (single line, comma-separated)
                        keywords_match = re.search(r'keywords:\s*(.+?)(?:\n\w+:|\Z)', frontmatter, re.DOTALL)
                        if keywords_match:
                            keywords_str = keywords_match.group(1).strip()
                            keywords = [k.strip() for k in keywords_str.split(',')]
                        
                        # Extract description from frontmatter
                        desc_match = re.search(r'description:\s*(.+?)(?:\n\w+:|\Z)', frontmatter, re.DOTALL)
                        if desc_match:
                            description = desc_match.group(1).strip()
                    
                    # If no frontmatter keywords, try inline format
                    if not keywords:
                        keyword_match = re.search(r'(?:Keywords?|Trigger\s+words?):\s*([^\n]+)', content, re.IGNORECASE)
                        if keyword_match:
                            keywords_str = keyword_match.group(1)
                            keywords = [k.strip() for k in keywords_str.split(',')]
                    
                    # If no description from frontmatter, get from first heading
                    if not description:
                        desc_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                        if desc_match:
                            description = desc_match.group(1).strip()
                    
            except Exception as e:
                console.print(f"[yellow]Warning: Could not extract keywords from {skill_name}: {e}[/yellow]")
        
        return {
            'keywords': keywords if keywords else [skill_name],
            'description': description if description else f"{skill_name} skill"
        }
    
    def _generate_rules_file(self, installed_skills: List[Dict]):
        """Generate dynamic rules file for Bob with keyword index."""
        
        rules_file = self.config.rules_dir / "bob_skills.md"
        
        # Group skills by category
        categories = {}
        for skill in installed_skills:
            category = skill['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(skill)
        
        # Generate rules content with enhanced format
        content = """# Bob Skills - Dynamic Loading System

## ⚠️ MANDATORY SKILL DETECTION PROTOCOL

**CRITICAL: You MUST follow this protocol for EVERY user request:**

1. **STOP** - Do not proceed with any task until you complete skill detection
2. **SCAN** - Check the user's prompt against the Skill Keyword Index below
3. **MATCH** - If ANY keyword matches, that skill MUST be loaded
4. **LOAD** - Immediately read `.bob/skills/{skill-name}/SKILL.md` using read_file tool
5. **FOLLOW** - Execute the skill's workflow completely before proceeding
6. **APPLY** - Use the skill's formatting, best practices, and output requirements

**Failure to detect and load matching skills will result in incomplete, low-quality responses.**

## How It Works

All skills in `.bob/skills/` are available for automatic use. You MUST:
1. **ALWAYS** detect which skill is needed based on the user's request
2. **IMMEDIATELY** load the skill's instructions from `.bob/skills/{skill-name}/SKILL.md`
3. **COMPLETELY** apply the skill to complete the task

## Skill Keyword Index

**MANDATORY: Scan EVERY user prompt against these keywords BEFORE starting any work.**

"""
        
        # Add keyword index for each skill
        for skill in sorted(installed_skills, key=lambda x: x['name']):
            skill_meta = self._extract_skill_keywords(skill['name'])
            keywords_str = ', '.join(skill_meta['keywords'])
            
            content += f"""### {skill['name']}
**Keywords:** {keywords_str}
**Description:** {skill['description']}
**Triggers:** "use {skill['name']}"

"""
        
        content += f"""## Installed Skills ({len(installed_skills)} total)

"""
        
        # Add skills by category
        for category, skills in sorted(categories.items()):
            content += f"### {category.title()} Skills\n"
            for skill in sorted(skills, key=lambda x: x['name']):
                content += f"- **{skill['name']}** - {skill['description']}\n"
            content += "\n"
        
        content += """## Usage

Simply make requests - Bob automatically uses the right skill:
- "Create a Word document" → docx skill loads automatically
- "Build a landing page" → frontend-design skill loads automatically
- "Create a poster" → canvas-design skill loads automatically
- "Help me create a new skill" → skill-creator skill loads automatically

## Manual Skill Invocation (Optional)

Explicitly invoke a skill when needed:
- `@skill-name your request`
- Example: `@canvas-design create a poster for our team event`

## Skill Detection Algorithm

When processing a user request:
1. **Scan the prompt** for keywords from the Skill Keyword Index
2. **Match keywords** to find the most relevant skill(s)
3. **Load the skill** by reading `.bob/skills/{skill-name}/SKILL.md`
4. **Follow the skill's workflow** from start to finish
5. **Apply skill-specific formatting** and best practices

**Priority Rules:**
- Exact keyword matches take precedence
- Multiple keyword matches increase confidence
- Context matters - consider the full request
- When in doubt, load the skill and verify

## Managing Skills

```bash
# List installed skills
bob-skills list

# Show skill details
bob-skills info docx

# Update all skills
bob-skills update

# Uninstall specific skills
bob-skills uninstall algorithmic-art
```

## Context Management

Skills are loaded on-demand to optimize context window usage:
- Only relevant skills are loaded per request
- Reduces token usage and improves response speed
- All skills remain available when needed

## License Information

Some skills have different licenses:
- **Proprietary skills** (docx, pdf, xlsx, pptx): See individual LICENSE.txt files
- **Open source skills**: Apache 2.0 license

By using these skills, you agree to their respective license terms.

---

*This configuration was auto-generated by bob-skills-installer*
"""
        
        # Write rules file
        with open(rules_file, 'w') as f:
            f.write(content)
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """Get information about a skill."""
        
        # Check if it's a catalog skill
        if skill_name in self.SKILLS_CATALOG:
            skill_info = self.SKILLS_CATALOG[skill_name].copy()
            skill_info['installed'] = self.config.is_skill_installed(skill_name)
            return skill_info
        
        # Check if it's a custom skill
        skill_path = self.config.skills_dir / skill_name
        if skill_path.exists():
            return self._get_custom_skill_info(skill_name)
        
        return None
    
    def _get_custom_skill_info(self, skill_name: str) -> Dict:
        """Get information about a custom skill."""
        skill_path = self.config.skills_dir / skill_name
        skill_md = skill_path / "SKILL.md"
        
        # Try to extract info from SKILL.md
        description = "Custom skill"
        category = "custom"
        license_type = "Unknown"
        
        if skill_md.exists():
            try:
                with open(skill_md, 'r') as f:
                    content = f.read()
                    # Try to extract description from first line or frontmatter
                    lines = content.split('\n')
                    for line in lines[:10]:
                        if line.startswith('# '):
                            description = line[2:].strip()
                            break
            except:
                pass
        
        # Check for LICENSE.txt
        license_file = skill_path / "LICENSE.txt"
        if license_file.exists():
            license_type = "See LICENSE.txt"
        
        return {
            'name': skill_name,
            'category': category,
            'description': description,
            'license': license_type,
            'installed': True,
            'custom': True
        }
    
    def get_all_installed_skills(self) -> List[Dict]:
        """Get all installed skills including custom ones."""
        # Get skills from config
        config_skills = self.config.get_installed_skills()
        skill_names = {s['name'] for s in config_skills}
        
        # Scan for custom skills not in config
        if self.config.skills_dir.exists():
            for skill_dir in self.config.skills_dir.iterdir():
                # Skip hidden directories (like .git) and non-directories
                if skill_dir.is_dir() and not skill_dir.name.startswith('.') and skill_dir.name not in skill_names:
                    # This is a custom skill
                    custom_info = self._get_custom_skill_info(skill_dir.name)
                    config_skills.append(custom_info)
        
        return config_skills
    
    def update_skills(self, skill_names: List[str]) -> Dict:
        """Update specified skills to latest version."""
        
        # Filter out custom skills - they can't be updated from the catalog
        installed_skills = self.config.get_installed_skills()
        custom_skills = [s['name'] for s in installed_skills if s.get('custom')]
        
        # Separate catalog skills from custom skills
        catalog_skills = [s for s in skill_names if s not in custom_skills]
        skipped_custom = [s for s in skill_names if s in custom_skills]
        
        if skipped_custom:
            console.print(f"\n⚠️  [yellow]Skipping custom skills (cannot update from catalog):[/yellow]")
            for skill in skipped_custom:
                console.print(f"   - {skill}")
            console.print("\n[dim]Custom skills must be updated manually from their source.[/dim]\n")
        
        # Re-install the catalog skills
        if catalog_skills:
            result = self.install(skills=catalog_skills, install_all=False)
            updated = result['installed']
        else:
            updated = []
        
        return {
            'updated': updated,
            'skipped': skipped_custom
        }
    
    def uninstall(self, skill_names: List[str]) -> Dict:
        """Uninstall specified skills."""
        
        removed = []
        
        for skill_name in skill_names:
            skill_path = self.config.skills_dir / skill_name
            
            if skill_path.exists():
                shutil.rmtree(skill_path)
                self.config.remove_installed_skill(skill_name)
                removed.append(skill_name)
        
        # Regenerate rules file
        installed = self.config.get_installed_skills()
        self._generate_rules_file(installed)
        
        return {
            'removed': removed
        }
    
    def detect_skills(self, prompt: str) -> List[str]:
        """Detect which skills would be used for a prompt."""
        
        prompt_lower = prompt.lower()
        detected = []
        
        # Check catalog skills
        for skill_name, skill_info in self.SKILLS_CATALOG.items():
            keywords = skill_info.get('keywords', [])
            
            if any(keyword.lower() in prompt_lower for keyword in keywords):
                detected.append(skill_name)
        
        # Check custom skills by reading their SKILL.md files
        installed_skills = self.config.get_installed_skills()
        for skill in installed_skills:
            if skill.get('custom') and skill['name'] not in detected:
                # Extract keywords from SKILL.md
                skill_meta = self._extract_skill_keywords(skill['name'])
                keywords = skill_meta.get('keywords', [])
                
                if any(keyword.lower() in prompt_lower for keyword in keywords):
                    detected.append(skill['name'])
        
        return detected
    
    def install_custom_skill(self, source: str, branch: Optional[str] = None) -> Dict:
        """Install a custom skill from a local directory or Git repository.
        
        Args:
            source: Path to local directory, Git repository URL, or GitHub subdirectory URL
                   Examples:
                   - /path/to/skill
                   - git@github.com:user/repo.git
                   - git@github.com:user/repo.git//path/to/skill
                   - https://github.com/user/repo/tree/branch-name/path/to/skill
                   - https://github.ibm.com/org/repo/tree/feature/branch/path/to/skill
            branch: Optional explicit branch name. If provided, overrides branch detection from URL.
                   Useful when branch names contain slashes or for disambiguation.
            
        Returns:
            Dict with installation result
        """
        
        # Clean up common URL mistakes
        if source.startswith('httpshttps://'):
            source = source.replace('httpshttps://', 'https://')
            console.print("[yellow]⚠️  Fixed malformed URL (removed duplicate 'https')[/yellow]")
        
        # Determine if source is a Git URL or local path
        is_git = source.startswith('git@') or source.startswith('http://') or source.startswith('https://')
        
        if is_git:
            # Check if it's a subdirectory URL
            subdirectory = None
            detected_branch = None
            repo_url = source
            
            if '/tree/' in source:
                # Parse HTTPS GitHub subdirectory URL
                # Format: https://github.com/user/repo/tree/branch/path/to/dir
                # Note: branch names can contain slashes (e.g., feature/my-branch)
                parts = source.split('/tree/', 1)
                if len(parts) == 2:
                    repo_url = parts[0]
                    # The rest after /tree/ contains branch and optional subdirectory
                    # We need to extract both, but branch names can have slashes
                    # Strategy: Everything after /tree/ is branch+path, we'll let git handle it
                    # and check if subdirectory exists after cloning
                    branch_and_path = parts[1]
                    
                    # If explicit branch provided, use it to split the path
                    if branch:
                        # User explicitly specified the branch, so we can parse the subdirectory
                        if branch_and_path.startswith(branch + '/'):
                            subdirectory = branch_and_path[len(branch) + 1:]
                        elif branch_and_path == branch:
                            subdirectory = None
                        else:
                            # Branch doesn't match the URL path, use the full path for auto-detection
                            detected_branch = branch_and_path
                            subdirectory = None
                    else:
                        # No explicit branch, store full path for auto-detection
                        detected_branch = branch_and_path
                        subdirectory = None
                    
                    # Convert to SSH format if it's github.ibm.com (requires auth)
                    if 'github.ibm.com' in repo_url:
                        # Extract org/repo from URL
                        url_parts = repo_url.replace('https://', '').replace('http://', '').split('/')
                        if len(url_parts) >= 3:
                            org = url_parts[1]
                            repo = url_parts[2]
                            repo_url = f"git@github.ibm.com:{org}/{repo}.git"
                    elif not repo_url.endswith('.git'):
                        repo_url = repo_url + '.git'
            elif '//' in source and source.startswith('git@'):
                # Parse SSH URL with subdirectory
                # Format: git@github.com:user/repo.git//path/to/skill
                parts = source.split('//', 1)
                if len(parts) == 2:
                    repo_url = parts[0]
                    subdirectory = parts[1]
            
            # Clone from Git repository
            with tempfile.TemporaryDirectory() as temp_dir:
                console.print(f"📥 Cloning from {repo_url}...")
                try:
                    # Determine which branch to use
                    branch_to_use = branch if branch else detected_branch
                    
                    # If explicit branch provided, use it directly
                    if branch:
                        console.print(f"🌿 Using explicit branch: {branch}")
                        repo = git.Repo.clone_from(repo_url, temp_dir, depth=1, branch=branch)
                    # For URLs with /tree/, try progressive branch detection
                    elif detected_branch and '/tree/' in source:
                        # Try to clone with progressively shorter branch names until we succeed
                        # This handles branch names with slashes like "feature/my-branch"
                        branch_parts = detected_branch.split('/')
                        cloned = False
                        
                        for i in range(len(branch_parts), 0, -1):
                            try_branch = '/'.join(branch_parts[:i])
                            try_subdir = '/'.join(branch_parts[i:]) if i < len(branch_parts) else None
                            
                            try:
                                console.print(f"🌿 Trying branch: {try_branch}")
                                repo = git.Repo.clone_from(repo_url, temp_dir, depth=1, branch=try_branch)
                                branch = try_branch
                                subdirectory = try_subdir
                                cloned = True
                                break
                            except GitCommandError:
                                # This branch name didn't work, try shorter
                                continue
                        
                        if not cloned:
                            raise ValueError(f"Could not find valid branch in: {detected_branch}")
                    elif detected_branch:
                        console.print(f"🌿 Using branch: {detected_branch}")
                        repo = git.Repo.clone_from(repo_url, temp_dir, depth=1, branch=detected_branch)
                    else:
                        repo = git.Repo.clone_from(repo_url, temp_dir, depth=1)
                    
                    if subdirectory:
                        # Use the subdirectory as the skill source
                        skill_source_path = Path(temp_dir) / subdirectory
                        if not skill_source_path.exists():
                            raise ValueError(f"Subdirectory '{subdirectory}' not found in repository")
                        console.print(f"📂 Using subdirectory: {subdirectory}")
                    else:
                        skill_source_path = Path(temp_dir)
                        
                except Exception as e:
                    raise RuntimeError(f"Failed to clone repository: {str(e)}")
                
                return self._install_custom_skill_from_path(skill_source_path)
        else:
            # Install from local directory
            skill_source_path = Path(source).expanduser().resolve()
            if not skill_source_path.exists():
                raise ValueError(f"Source path does not exist: {source}")
            
            return self._install_custom_skill_from_path(skill_source_path)
    
    def _install_custom_skill_from_path(self, source_path: Path) -> Dict:
        """Install a custom skill from a local path.
        
        Args:
            source_path: Path to the skill directory
            
        Returns:
            Dict with installation result
        """
        # Initialize if needed
        if not self.config.is_initialized():
            self.config.initialize()
        
        # Validate skill structure
        skill_md = source_path / "SKILL.md"
        if not skill_md.exists():
            raise ValueError(f"Invalid skill: SKILL.md not found in {source_path}")
        
        # Extract skill name from directory name
        skill_name = source_path.name
        
        # Validate skill name (alphanumeric and hyphens only)
        if not re.match(r'^[a-z0-9-]+$', skill_name):
            raise ValueError(f"Invalid skill name '{skill_name}'. Must contain only lowercase letters, numbers, and hyphens.")
        
        # Check if skill already exists
        dest_path = self.config.skills_dir / skill_name
        if dest_path.exists():
            console.print(f"\n⚠️  [yellow]Skill '{skill_name}' already exists.[/yellow]")
            console.print("\n[bold]To replace this skill, you have two options:[/bold]")
            console.print("  1. Uninstall and reinstall:")
            console.print(f"     [cyan]bob-skills uninstall {skill_name}[/cyan]")
            console.print(f"     [cyan]bob-skills install --custom {source_path}[/cyan]")
            console.print("  2. Update the skill:")
            console.print(f"     [cyan]bob-skills update {skill_name}[/cyan]")
            raise RuntimeError(f"Skill '{skill_name}' already installed. Use uninstall or update.")
        
        # Copy skill directory
        console.print(f"📦 Installing custom skill '{skill_name}'...")
        shutil.copytree(source_path, dest_path)
        
        # Get skill info
        skill_info = self._get_custom_skill_info(skill_name)
        
        # Add to config
        self.config.add_installed_skill(skill_name, {
            'category': skill_info['category'],
            'description': skill_info['description'],
            'license': skill_info['license'],
            'custom': True
        })
        
        # Regenerate rules file
        installed = self.config.get_installed_skills()
        self._generate_rules_file(installed)
        
        return {
            'skill_name': skill_name,
            'skill_info': skill_info
        }
        return detected