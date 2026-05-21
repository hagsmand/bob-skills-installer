# Bob Skills Installer

**A command-line tool that supercharges IBM Bob with specialized AI skills for documents, development, creative work, and enterprise tasks.**

---

## 🚀 Quick Start

### 1. Install the CLI Tool

**For Linux/Unix:**
```bash
# Clone and install
git clone git@github.ibm.com:weicao/bob-skills-installer.git
cd bob-skills-installer
pip3 install -e .

# Add to PATH (required)
export PATH="$HOME/.local/bin:$PATH"
```

**For macOS:**
```bash
# Clone and install
git clone git@github.ibm.com:weicao/bob-skills-installer.git
cd bob-skills-installer

# Install (use regular install, not editable mode)
sudo pip3 install .

# Verify installation
ls -la /usr/local/bin/bob-skills

# The script is installed to /usr/local/bin (already in PATH)
# No need to export PATH - /usr/local/bin is typically in your PATH by default
```

**Important for macOS:**
- Use `sudo pip3 install .` (without `-e` flag) to ensure the `bob-skills` command is created properly
- Editable installs (`-e`) may not create console scripts correctly with sudo on macOS
- The script will be installed to `/usr/local/bin/bob-skills` (system-wide location)
- `/usr/local/bin` is typically already in your PATH, so no PATH configuration needed

### 2. Navigate to Your Project

```bash
cd /path/to/your-project
```

### 3. Install Skills

```bash
# Install all 16 Anthropic skills (recommended)
bob-skills install

# Or install specific skills
bob-skills install -s docx -s pdf -s xlsx

# Or install a custom skill
bob-skills install --custom https://github.ibm.com/org/repo/tree/main/path/to/skill
```

**That's it!** Bob now has specialized skills and will use them automatically.

---

## 📋 Command Reference

### `bob-skills install`

Install Anthropic catalog skills or custom skills to your project.

**Usage:**
```bash
# Install all catalog skills (default)
bob-skills install

# Install specific catalog skills
bob-skills install -s docx -s pdf -s xlsx

# Install custom skill from GitHub subdirectory
bob-skills install --custom https://github.ibm.com/org/repo/tree/main/path/to/skill

# Install custom skill with explicit branch (recommended for branches with slashes)
bob-skills install --custom https://github.ibm.com/org/repo/tree/feature/my-branch/path/to/skill --branch feature/my-branch

# Install custom skill from local directory
bob-skills install --custom /path/to/my-skill

# Install custom skill from Git repository
bob-skills install --custom git@github.com:user/repo.git

# Interactive selection
bob-skills install --interactive

# Install to specific directory
bob-skills install --path /path/to/project
```

**Options:**
- `--all` - Install all available catalog skills (default: true)
- `-s, --skills` - Specific skills to install (e.g., `-s docx -s pdf`)
- `-i, --interactive` - Interactive skill selection
- `-c, --custom` - Install custom skill from local path or Git URL
- `-b, --branch` - Explicit branch name for Git URLs (optional, helps with branch names containing slashes)
- `-p, --path` - Installation directory (default: current directory)

**What This Command Does:**

1. **Downloads/Copies Skill Files** → `.bob/skills/{skill-name}/`
   - For catalog skills: Clones from `https://github.com/anthropics/skills.git`
   - For custom skills: Copies from local path or clones from Git URL
   - Creates skill directory with SKILL.md, README.md, LICENSE.txt, etc.

2. **Updates Config File** → `.bob/config.yaml`
   - Adds skill entry to `installed_skills` list
   - Tracks metadata: name, category, description, license
   - Marks custom skills with `custom: true` flag

3. **Regenerates Rules File** → `.bob/rules/bob_skills.md`
   - Complete rewrite with all installed skills
   - Includes keyword index for skill detection
   - Contains usage instructions and examples

**Protection:**
- ✅ Checks if skill already exists before installing
- ✅ Provides guidance to use `uninstall` or `update` if skill exists
- ✅ Prevents accidental overwrites

**Example Output:**
```
📥 Downloading skills from https://github.com/anthropics/skills.git...
✅ Installation complete!

Installed Skills:
  - docx (Proprietary)
  - pdf (Proprietary)
```

---

### `bob-skills uninstall`

Remove specific skills or all skills from your project.

**Usage:**
```bash
# Uninstall specific skills
bob-skills uninstall docx pdf xlsx

# Uninstall all skills (with confirmation)
bob-skills uninstall --all

# Uninstall from specific directory
bob-skills uninstall docx --path /path/to/project
```

**Options:**
- `-a, --all` - Uninstall all skills (requires confirmation)
- `-p, --path` - Project directory (default: current directory)

**What This Command Does:**

1. **Removes Skill Files** → `.bob/skills/{skill-name}/`
   - Deletes entire skill directory
   - Works for both Anthropic and custom skills

2. **Updates Config File** → `.bob/config.yaml`
   - Removes skill entry from `installed_skills` list
   - Preserves other configuration settings

3. **Regenerates Rules File** → `.bob/rules/bob_skills.md`
   - Complete rewrite with remaining skills
   - Removes uninstalled skill from keyword index

**Safety Features:**
- ✅ `--all` flag requires confirmation before proceeding
- ✅ Shows list of skills to be uninstalled
- ✅ Provides clear error messages

**Example Output:**
```
⚠️  About to uninstall 2 skills:
   - docx
   - pdf

Are you sure? [y/N]: y

✅ Uninstalled 2 skills:
   - docx
   - pdf
```

---

### `bob-skills update`

Update all Anthropic catalog skills to the latest version. Custom skills are automatically skipped.

**Usage:**
```bash
# Update all catalog skills
bob-skills update

# Update in specific directory
bob-skills update --path /path/to/project
```

**Options:**
- `-p, --path` - Project directory (default: current directory)

**What This Command Does:**

1. **Identifies Skills to Update**
   - Gets list of all installed skills from config
   - Filters out custom skills (cannot update from catalog)
   - Shows which custom skills are being skipped

2. **Downloads Latest Versions** → `.bob/skills/{skill-name}/`
   - Clones latest from `https://github.com/anthropics/skills.git`
   - Deletes old skill directories
   - Copies new versions from cloned repo

3. **Updates Config File** → `.bob/config.yaml`
   - Updates metadata for updated skills
   - Preserves custom skill entries unchanged

4. **Regenerates Rules File** → `.bob/rules/bob_skills.md`
   - Complete rewrite with ALL skills (updated + custom)
   - Custom skills remain in rules file

**Important Notes:**
- ✅ Only updates Anthropic catalog skills
- ✅ Automatically skips custom skills with clear messaging
- ✅ Custom skills remain unchanged on disk and in config
- ❌ Cannot update custom skills (must reinstall from source)

**Example Output:**
```
⚠️  Skipping custom skills (cannot update from catalog):
   - db2-trap-analysis

Custom skills must be updated manually from their source.

📥 Downloading skills from https://github.com/anthropics/skills.git...
✅ Updated 16 skills!
```

**To Update Custom Skills:**
```bash
# Uninstall and reinstall from source
bob-skills uninstall my-custom-skill
bob-skills install --custom https://github.com/org/repo/tree/main/path/to/skill
```

---

### `bob-skills list`

Display all installed skills with their categories and descriptions.

**Usage:**
```bash
# List all installed skills
bob-skills list

# List skills in specific directory
bob-skills list --path /path/to/project
```

**Options:**
- `-p, --path` - Project directory (default: current directory)

**What This Command Does:**

1. **Reads Config File** → `.bob/config.yaml`
   - Gets list of installed skills
   - Retrieves metadata for each skill

2. **Scans Skill Directories** → `.bob/skills/`
   - Detects any custom skills not in config
   - Extracts information from SKILL.md files

3. **Displays Table**
   - Shows skill name, category, description
   - Marks custom skills with "(custom)" indicator
   - Groups by category

**Files Accessed (Read-Only):**
- `.bob/config.yaml` - Skill metadata
- `.bob/skills/{skill-name}/SKILL.md` - Skill descriptions

**Example Output:**
```
Installed Skills (17 total)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Skill                      ┃ Category ┃ Description                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ docx                       │ document │ Create, edit, and analyze   │
│                            │          │ Word documents...           │
│ db2-trap-analysis (custom) │ custom   │ Db2 Trap Analysis - SOP...  │
└────────────────────────────┴──────────┴─────────────────────────────┘
```

---

### `bob-skills info`

Get detailed information about a specific skill.

**Usage:**
```bash
# Get info about a skill
bob-skills info docx
bob-skills info my-custom-skill

# Get info from specific directory
bob-skills info docx --path /path/to/project
```

**Options:**
- `-p, --path` - Project directory (default: current directory)

**What This Command Does:**

1. **Reads Skill Files** → `.bob/skills/{skill-name}/`
   - Reads SKILL.md for description and instructions
   - Reads LICENSE.txt for license information
   - Checks for README.md and other files

2. **Reads Config File** → `.bob/config.yaml`
   - Gets skill metadata (category, description, custom flag)

3. **Displays Details**
   - Skill name and description
   - Category and license
   - Installation status
   - Custom skill indicator

**Files Accessed (Read-Only):**
- `.bob/config.yaml` - Skill metadata
- `.bob/skills/{skill-name}/SKILL.md` - Skill details
- `.bob/skills/{skill-name}/LICENSE.txt` - License info

**Example Output:**
```
Skill: docx
Category: document
Description: Create, edit, and analyze Word documents (.docx files)
License: Proprietary
Status: Installed
Custom: No
```

---

### `bob-skills check`

Check if a specific skill is installed.

**Usage:**
```bash
# Check if skill is installed
bob-skills check docx
bob-skills check my-custom-skill

# Check in specific directory
bob-skills check docx --path /path/to/project
```

**Options:**
- `-p, --path` - Project directory (default: current directory)

**What This Command Does:**

1. **Checks Skill Directory** → `.bob/skills/{skill-name}/`
   - Verifies directory exists
   - Checks for SKILL.md file

2. **Checks Config File** → `.bob/config.yaml`
   - Verifies skill is registered in config

3. **Returns Status**
   - Installed: Skill exists and is registered
   - Not installed: Skill not found

**Files Accessed (Read-Only):**
- `.bob/config.yaml` - Skill registration
- `.bob/skills/{skill-name}/` - Skill directory

**Example Output:**
```
✅ Skill 'docx' is installed
```

---

### `bob-skills detect`

Detect which skills would be used for a given prompt.

**Usage:**
```bash
# Detect skills for a prompt
bob-skills detect "Create a Word document with charts"

# Detect in specific directory
bob-skills detect "Build a landing page" --path /path/to/project
```

**Options:**
- `-p, --path` - Project directory (default: current directory)

**What This Command Does:**

1. **Reads Rules File** → `.bob/rules/bob_skills.md`
   - Gets keyword index for all skills
   - Extracts trigger phrases

2. **Analyzes Prompt**
   - Matches keywords against prompt
   - Identifies relevant skills

3. **Displays Results**
   - Lists detected skills
   - Shows matching keywords

**Files Accessed (Read-Only):**
- `.bob/rules/bob_skills.md` - Keyword index

**Example Output:**
```
Detected skills for "Create a Word document with charts":
  - docx (matched: "Word document")
```

---

## 📁 File Structure

After installation, your project will have:

```
your-project/
├── .bob/
│   ├── skills/              # Skill files
│   │   ├── docx/
│   │   │   ├── SKILL.md     # Skill instructions
│   │   │   ├── README.md    # Documentation
│   │   │   ├── LICENSE.txt  # License
│   │   │   └── scripts/     # Helper scripts
│   │   ├── pdf/
│   │   ├── my-custom-skill/ # Custom skills
│   │   └── ...
│   ├── rules/
│   │   └── bob_skills.md    # Auto-generated rules
│   └── config.yaml          # Installation metadata
```

### File Descriptions

#### `.bob/config.yaml`
**Purpose:** Tracks installed skills and their metadata

**Structure:**
```yaml
version: '1.0.0'
skill_source: 'https://github.com/anthropics/skills'
installed_skills:
  - name: docx
    category: document
    description: Create, edit, and analyze Word documents
    license: Proprietary
    custom: false
  - name: db2-trap-analysis
    category: custom
    description: Db2 Trap Analysis - SOP
    license: Unknown
    custom: true
auto_update: false
```

**Modified By:**
- `install` - Adds skill entries
- `uninstall` - Removes skill entries
- `update` - Updates skill metadata

#### `.bob/rules/bob_skills.md`
**Purpose:** Dynamic rules file for Bob with skill detection

**Structure:**
```markdown
# Bob Skills - Dynamic Loading System

## Skill Keyword Index
### docx
**Keywords:** docx
**Description:** Create, edit, and analyze Word documents
**Triggers:** "use docx"

## Installed Skills (17 total)
...
```

**Modified By:**
- `install` - Regenerated with new skills
- `uninstall` - Regenerated without removed skills
- `update` - Regenerated with updated skills

**Important:** This file is auto-generated. Do not edit manually.

#### `.bob/skills/{skill-name}/`
**Purpose:** Contains skill files and instructions

**Contents:**
- `SKILL.md` - Skill instructions for Bob (required)
- `README.md` - Documentation (optional)
- `LICENSE.txt` - License information (optional)
- `scripts/` - Helper scripts (optional)
- `examples/` - Example files (optional)

**Modified By:**
- `install` - Creates directory and copies files
- `uninstall` - Deletes entire directory
- `update` - Replaces directory with new version (catalog skills only)

---

## 🎨 Custom Skills

Create and install your own skills to extend Bob's capabilities.

### Quick Example

```bash
# Install from GitHub subdirectory
bob-skills install --custom https://github.ibm.com/DB2/db2-agent-skills/tree/main/skills/shared/db2-trap-analysis

# Install with explicit branch (recommended for branches with slashes)
bob-skills install --custom https://github.ibm.com/DB2/db2-agent-skills/tree/feature/my-branch/skills/shared/db2-trap-analysis --branch feature/my-branch

# Verify installation
bob-skills list
# Output: db2-trap-analysis (custom) │ custom │ Db2 Trap Analysis...

# Use it
"Analyze this Db2 trap file"
→ Bob automatically uses db2-trap-analysis skill
```

### Supported Sources

| Source Type | Format | Example |
|-------------|--------|---------|
| **Local Directory** | `/path/to/skill` | `bob-skills install --custom ~/my-skills/api-tester` |
| **Git Repository** | `git@host:org/repo.git` | `bob-skills install --custom git@github.com:user/skill.git` |
| **GitHub Subdirectory** | `https://host/org/repo/tree/branch/path` | `bob-skills install --custom https://github.ibm.com/org/repo/tree/main/skills/my-skill` |
| **GitHub with Branch** | `https://host/org/repo/tree/branch/path --branch name` | `bob-skills install --custom https://github.ibm.com/org/repo/tree/feature/branch/skills/my-skill --branch feature/branch` |
| **Git Subdirectory** | `git@host:org/repo.git//path` | `bob-skills install --custom git@github.com:user/repo.git//skills/my-skill` |

**Note:** Use `--branch` parameter when branch names contain slashes (e.g., `feature/my-branch`) for faster, unambiguous installation.

### Creating a Custom Skill

**Minimum Structure:**
```
my-custom-skill/
├── SKILL.md          # Required: Skill instructions for Bob
├── README.md         # Optional: Documentation
├── LICENSE.txt       # Optional: License information
└── examples/         # Optional: Example files
```

**SKILL.md Template:**
```markdown
---
name: my-custom-skill
description: Brief description of what this skill does
keywords: keyword1, keyword2, keyword3
---

# My Custom Skill

## Purpose
Brief description of what this skill does.

## When to Use
- Trigger phrase 1
- Trigger phrase 2

## Instructions
Step-by-step instructions for Bob to follow...
```

### Custom Skill Features

✅ **Full Integration**: Custom skills work exactly like Anthropic skills
✅ **Auto-Detection**: Bob automatically detects and uses them
✅ **Lifecycle Management**: Install, list, info, and uninstall
✅ **Version Control**: Install directly from Git repositories
✅ **Subdirectory Support**: Install from monorepos or skill collections

---

## 💡 How It Works

### Dynamic Loading

1. **Install** = Download skill files to `.bob/skills/` (all 16 by default)
2. **Enable** = Bob knows about the skill and can use it (automatic via rules file)
3. **Load** = Bob reads skill instructions only when needed (on-demand)

### The Process

```
You: "Create a Word document"
  ↓
Bob: Scans for keywords → "Word document" matches docx skill
  ↓
Bob: Loads .bob/skills/docx/SKILL.md on-demand
  ↓
Bob: Applies docx skill instructions
  ↓
Result: Only docx skill loaded, not all 16 skills
```

### Benefits

- ✅ **Context-efficient**: Only loads skills when needed
- ✅ **All skills available**: Any skill can be used anytime
- ✅ **No configuration**: Works automatically after installation
- ✅ **Flexible**: Manual override available with `@skill-name`

---

## 📚 Available Skills (16 Total)

### 📄 Document Skills (4)
| Skill | Use For | Example |
|-------|---------|---------|
| **docx** | Word documents | "Create a Word doc with Q4 meeting notes" |
| **pdf** | PDF manipulation | "Extract text from this PDF report" |
| **xlsx** | Excel spreadsheets | "Create a spreadsheet with sales data" |
| **pptx** | PowerPoint presentations | "Build a presentation about our project" |

### 💻 Development Skills (4)
| Skill | Use For | Example |
|-------|---------|---------|
| **mcp-builder** | Build MCP servers | "Create an MCP server for database queries" |
| **webapp-testing** | Test web apps | "Test this application for bugs" |
| **frontend-design** | Build web interfaces | "Build a landing page for our product" |
| **web-artifacts-builder** | Create web components | "Create a reusable button component" |

### 🎨 Creative Skills (4)
| Skill | Use For | Example |
|-------|---------|---------|
| **algorithmic-art** | Generative art (p5.js) | "Generate algorithmic art for our website" |
| **canvas-design** | Visual designs & posters | "Create a poster for our team event" |
| **slack-gif-creator** | Animated GIFs | "Create an animated GIF for Slack" |
| **theme-factory** | Design themes | "Generate a dark theme for our app" |

### 🏢 Enterprise Skills (2)
| Skill | Use For | Example |
|-------|---------|---------|
| **brand-guidelines** | Brand consistency | "Check if this design follows brand guidelines" |
| **internal-comms** | Communications | "Create an internal announcement template" |

### 🛠️ Utility Skills (2)
| Skill | Use For | Example |
|-------|---------|---------|
| **skill-creator** | Create custom skills | "Help me create a skill for database testing" |
| **doc-coauthoring** | Collaborative editing | "Help me co-author this document" |

---

## 🐛 Troubleshooting

### Skills Not Working

```bash
# Check if skills are installed
bob-skills list

# Verify specific skill
bob-skills check docx

# Reinstall skill
bob-skills install -s docx
```

### Custom Skill Issues

```bash
# Verify SKILL.md exists
ls -la .bob/skills/my-custom-skill/SKILL.md

# Check skill info
bob-skills info my-custom-skill

# Reinstall from source
bob-skills uninstall my-custom-skill
bob-skills install --custom https://github.com/org/repo/tree/main/path/to/skill

# If branch has slashes, use --branch for faster installation
bob-skills install --custom https://github.com/org/repo/tree/feature/branch/path/to/skill --branch feature/branch
```

### Update Issues

```bash
# Update all catalog skills
bob-skills update

# Or reinstall specific skills
bob-skills uninstall docx
bob-skills install -s docx

# Custom skills must be reinstalled from source
bob-skills uninstall my-custom-skill
bob-skills install --custom /path/to/skill
```

### Command Not Found

```bash
# Ensure PATH is set
export PATH="$HOME/.local/bin:$PATH"

# Add to shell profile for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🗑️ Uninstallation

### Remove Specific Skills

```bash
# Uninstall one or more skills
bob-skills uninstall docx pdf xlsx

# Uninstall all skills
bob-skills uninstall --all
```

### Remove CLI Tool

```bash
pip3 uninstall bob-skills-installer
```

### Complete Cleanup

```bash
# Uninstall CLI tool
pip3 uninstall bob-skills-installer

# Remove all skills and configuration
rm -rf .bob/
```

---

## 📄 License Information

This installer downloads skills from [Anthropic's skills repository](https://github.com/anthropics/skills).

### Skill Licenses

#### Proprietary Skills (Source-Available)
- **docx, pdf, xlsx, pptx** - Document creation skills
- License: Proprietary (see individual LICENSE.txt files)
- © Anthropic PBC

#### Open Source Skills (Apache 2.0)
- **All other skills** (12 skills)
- License: Apache 2.0
- © Anthropic PBC

### What You Can Do

✅ **Allowed:**
- Install and use skills in your projects
- Share installer with your team
- Use skills in company's internal tools
- Modify open source skills (Apache 2.0)

❌ **Not Allowed:**
- Modify proprietary skills (docx, pdf, xlsx, pptx)
- Remove license files
- Claim skills as your own
- Redistribute proprietary skills commercially

---

## 🙏 Acknowledgments

- Skills provided by [Anthropic](https://github.com/anthropics/skills)
- Built for IBM Bob AI coding assistant
- Inspired by the Agent Skills standard

---

## 📞 Support

For questions or issues:
- Check this README for detailed information
- Contact: weicao@ca.ibm.com (tool author)
- IBM Bob support channels

---

**Made with ❤️ for better AI-assisted development**
