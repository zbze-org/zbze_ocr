from diff_match_patch import diff_match_patch
import json


def generate_text_diff(text1, text2):
    dmp = diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diffs)

    changes = []
    line_num = 0

    for op, data in diffs:
        line_num += data.count('\n') + 1

        if op == -1:  # Deleted
            changes.append({"type": "deleted", "line_number": line_num, "content": data})
        elif op == 1:  # Inserted
            changes.append({"type": "added", "line_number": line_num, "content": data})

    return changes
