import os

# Define the path to the parent __init__.py
# Based on user's path: /workspaces/agent-hub/projects/langchain/libs/community/langchain_community/tools/__init__.py
init_path = "projects/langchain/libs/community/langchain_community/tools/__init__.py"

if not os.path.exists(init_path):
    print(f"❌ Could not find file at: {init_path}")
    print("Please check if you are in the root of 'agent-hub' and if 'projects/langchain' exists.")
    exit(1)

with open(init_path, "r") as f:
    lines = f.readlines()

# Check if already added
if any("AgentHubTool" in line for line in lines):
    print("✅ AgentHubTool is already registered in parent __init__.py")
    exit(0)

# 1. Add the import
# We'll add it after the imports start
import_added = False
new_lines = []
for line in lines:
    new_lines.append(line)
    if line.startswith("from langchain_community.tools.") and not import_added:
        # Add our import right at the beginning of the imports section
        new_lines.insert(-1, "from langchain_community.tools.agent_hub import AgentHubTool\n")
        import_added = True

if not import_added:
    # If no imports found, append to end (fallback)
    new_lines.append("from langchain_community.tools.agent_hub import AgentHubTool\n")

# 2. Add to __all__
# This is trickier to parse reliably with regex, but usually it's a list.
# We'll look for `__all__ = [` and add it there.
final_lines = []
in_all_block = False
added_to_all = False

for line in new_lines:
    if "__all__ = [" in line:
        final_lines.append(line)
        final_lines.append('    "AgentHubTool",\n')
        added_to_all = True
        continue
    final_lines.append(line)

with open(init_path, "w") as f:
    f.writelines(final_lines)

print(f"✅ Successfully registered AgentHubTool in {init_path}")
