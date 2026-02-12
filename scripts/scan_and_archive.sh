#!/bin/bash

# Configuration
CENTRAL_DIR="$HOME/Documents/Academic_Work_Central"
BACKUP_DIR="$CENTRAL_DIR/Legacy_Unsynced_Assets"
DIFFS_DIR="$BACKUP_DIR/Diffs"
LOOSE_FILES_DIR="$BACKUP_DIR/Loose_Files"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ensure directories exist
mkdir -p "$DIFFS_DIR"
mkdir -p "$LOOSE_FILES_DIR"

# Function to calculate file hash
calculate_hash() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        shasum -a 256 "$1" | awk '{print $1}'
    else
        sha256sum "$1" | awk '{print $1}'
    fi
}

# Function to scan and process files
scan_and_process() {
    local source_dir="$1"
    local dir_name=$(basename "$source_dir")
    
    echo "Scanning $source_dir..."
    
    find "$source_dir" -type f -not -path "*/.*" -print0 | while IFS= read -r -d '' file; do
        relative_path="${file#$source_dir/}"
        filename=$(basename "$file")
        
        # Check if file exists in Central Directory (by name match primarily)
        # We search in the Central Dir for a file with the same name
        found_in_central=$(find "$CENTRAL_DIR" -name "$filename" -type f -head 1)
        
        if [ -z "$found_in_central" ]; then
            echo "New file found: $relative_path"
            # Maintain directory structure in Loose_Files
            target_dir="$LOOSE_FILES_DIR/$dir_name/$(dirname "$relative_path")"
            mkdir -p "$target_dir"
            cp "$file" "$target_dir/"
        else
            # File exists, compare content
            hash_src=$(calculate_hash "$file")
            hash_dest=$(calculate_hash "$found_in_central")
            
            if [ "$hash_src" != "$hash_dest" ]; then
                echo "Difference found: $relative_path"
                # Save the different version in Diffs
                target_dir="$DIFFS_DIR/$dir_name/$(dirname "$relative_path")"
                mkdir -p "$target_dir"
                cp "$file" "$target_dir/${filename}_${TIMESTAMP}_conflict"
            else
                echo "Identical file: $relative_path (Skipping)"
            fi
        fi
    done
}

# 1. Scan Desktop for loose academic files (heuristic: pdf, docx, md, tex, json)
echo "--- Scanning Desktop ---"
find "$HOME/Desktop" -maxdepth 1 \( -name "*.pdf" -o -name "*.docx" -o -name "*.md" -o -name "*.tex" -o -name "*.json" \) -print0 | while IFS= read -r -d '' file; do
    scan_and_process "$(dirname "$file")" # Hacky way to process single file loop effectively reusing function logic or just simplify
    # Let's simplify for single files on Desktop
    filename=$(basename "$file")
    found_in_central=$(find "$CENTRAL_DIR" -name "$filename" -type f | head -n 1)
    
    if [ -z "$found_in_central" ]; then
         echo "Archiving loose Desktop file: $filename"
         cp "$file" "$LOOSE_FILES_DIR/"
    else
        hash_src=$(calculate_hash "$file")
        hash_dest=$(calculate_hash "$found_in_central")
        if [ "$hash_src" != "$hash_dest" ]; then
             echo "Diff found for Desktop file: $filename"
             cp "$file" "$DIFFS_DIR/${filename}_${TIMESTAMP}_desktop_diff"
        fi
    fi
done

# 2. Scan specific known legacy paths
# Adjust these paths based on what we found earlier or standard locations
LEGACY_PATHS=(
    "$HOME/Documents/DOIP-Segments-Specification" 
    "$HOME/github"
)

for path in "${LEGACY_PATHS[@]}"; do
    if [ -d "$path" ]; then
        scan_and_process "$path"
    fi
done

echo "Scan and archive complete. Results in $BACKUP_DIR"
