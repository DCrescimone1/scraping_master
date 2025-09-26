#!/bin/bash

# Set the output file name
output_file="scraping_master_dump.txt"

# Set maximum file size to process (in bytes, 1MB = 1048576)
max_file_size=524288  # Reduced to 512KB

# Maximum content to include per file (in bytes)
max_content_size=100000

# Generate the tree structure
echo "Folder structure:" > "$output_file"
tree -L 4 -I 'node_modules|.git|build|.next|venv|__pycache__|*.pyc|.yoyo' >> "$output_file"

# Add a separator
echo -e "\n\n--- File Contents ---\n" >> "$output_file"

# Find and dump file contents, with improved exclusions and size limit
find . -type f \
    ! -path "*/node_modules/*" \
    ! -path "*/.git/*" \
    ! -path "*/build/*" \
    ! -path "*/.next/*" \
    ! -path "*/public/gallery/*" \
    ! -path "*/venv/*" \
    ! -path "*/__pycache__/*" \
    ! -path "*/webpage/*" \
    ! -path "*/dist/*" \
    ! -path "*/cache/*" \
    ! -path "*/tmp/*" \
    ! -path "*/coverage/*" \
    ! -path "*/tests/*" \
    ! -path "*/.yoyo/*" \
    ! -path "./.yoyo/db/snapshot_embeddings.sqlitejs" \
    ! -name "*.pyc" \
    ! -name "*.png" \
    ! -name "*.jpg" \
    ! -name "*.jpeg" \
    ! -name "*.gif" \
    ! -name "*.bmp" \
    ! -name "*.svg" \
    ! -name "*.ico" \
    ! -name "*.txt" \
    ! -name "*.log" \
    ! -name "*.json" \
    ! -name "*.md" \
    ! -name "*.min.js" \
    ! -name "*.lock" \
    ! -name "*.map" \
    ! -name "*.sqlitejs" \
    ! -name "package-lock.json" \
    ! -name ".DS_Store" \
    ! -name ".env.local" \
    ! -name ".gitignore" \
    ! -name ".git*" \
    ! -name "project_dump.sh" \
    ! -name "logs/*" \
    ! -name ".vscode" \
    ! -name ".pytest_cache" \
    ! -name ".env" \
    -size -${max_file_size}c \
    -print0 | while IFS= read -r -d '' file; do
    # Check if the file is not empty
    if [ -s "$file" ]; then
        echo -e "\n------------------------------------------------- $file --------------------------------------------------\n" >> "$output_file"
        head -c $max_content_size "$file" >> "$output_file"
    fi
done

echo "Dump completed. Output saved to $output_file"