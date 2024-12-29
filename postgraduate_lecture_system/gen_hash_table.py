hash_table_content = []
with open("labels.txt", "r") as f:
    for line in f:
        file_name, label = line.strip().split("\t")
        hash_val = file_name.split(".")[0][5:]
        hash_table_content.append(f"{hash_val},{label}")

with open("hash_table.csv", "w") as f:
    f.write("\n".join(hash_table_content))
