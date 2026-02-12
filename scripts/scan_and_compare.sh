#!/bin/bash

# 定义核心目录（新家）
CENTRAL_HOME="$HOME/Documents/Academic_Work_Central"
LEGACY_BACKUP="$CENTRAL_HOME/Legacy_Unsynced_Assets"
DIFF_BACKUP="$LEGACY_BACKUP/Diffs"
LOOSE_FILES_BACKUP="$LEGACY_BACKUP/Loose_Files"

# 创建备份目录
mkdir -p "$DIFF_BACKUP"
mkdir -p "$LOOSE_FILES_BACKUP"

# 定义需要扫描的目录列表
# 注意：这里我们主要扫描用户提到的几个关键位置
SCAN_DIRS=(
    "$HOME/Desktop/mcp-legal-chia"
    "$HOME/github" # 假设这是用户提到的 github 文件夹
    "$HOME/Desktop" # 扫描桌面以防有散落文件
)

# 定义核心文件名，用于识别是否为相关项目目录
CORE_FILES=("Policy_Dictionary.json" "Paper_Section3_Methodology.tex")

echo "开始扫描旧目录..."

for dir in "${SCAN_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "正在扫描目录: $dir"
        
        # 查找包含核心文件的子目录（递归深度限制为3，避免搜索太深）
        find "$dir" -maxdepth 3 -type f \( -name "Policy_Dictionary.json" -o -name "Paper_Section3_Methodology.tex" \) -print0 | while IFS= read -r -d '' file; do
            parent_dir=$(dirname "$file")
            echo "发现潜在旧项目目录: $parent_dir"
            
            # 比对逻辑
            # 遍历该旧目录下的所有文件
            find "$parent_dir" -type f | while read -r old_file; do
                # 计算相对路径
                rel_path="${old_file#$parent_dir/}"
                target_file="$CENTRAL_HOME/$rel_path"
                
                if [ ! -e "$target_file" ]; then
                    # 如果新家没有这个文件，提取出来
                    echo "  [差异-新增] 发现新家没有的文件: $rel_path"
                    # 保持目录结构复制到 Loose_Files
                    mkdir -p "$(dirname "$LOOSE_FILES_BACKUP/$rel_path")"
                    cp "$old_file" "$LOOSE_FILES_BACKUP/$rel_path"
                else
                    # 如果新家有这个文件，比较时间戳或内容
                    # 这里简单比较修改时间，如果旧文件比新文件新，或者内容不同，则备份
                    if [ "$old_file" -nt "$target_file" ]; then
                         echo "  [差异-更新] 旧文件比新文件新: $rel_path"
                         mkdir -p "$(dirname "$DIFF_BACKUP/$rel_path")"
                         cp "$old_file" "$DIFF_BACKUP/$rel_path"
                    elif ! cmp -s "$old_file" "$target_file"; then
                         echo "  [差异-冲突] 内容不同（虽然旧文件不比新文件新）: $rel_path"
                         mkdir -p "$(dirname "$DIFF_BACKUP/$rel_path")"
                         cp "$old_file" "$DIFF_BACKUP/$rel_path"
                    fi
                fi
            done
            
            # 标记该目录以便后续（手动或再次确认后）删除
            # 这里我们不直接删除，而是输出建议
            echo "  [建议删除] $parent_dir 已完成扫描比对。" >> "$LEGACY_BACKUP/folders_to_delete.txt"
        done
    else
        echo "跳过不存在的目录: $dir"
    fi
done

echo "扫描与比对完成。"
echo "差异文件已备份至: $DIFF_BACKUP"
echo "独有文件已备份至: $LOOSE_FILES_BACKUP"
echo "建议删除的目录列表已保存至: $LEGACY_BACKUP/folders_to_delete.txt"
