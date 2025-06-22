import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from cortex.completion import process_fragments


def main():
    print("Cortex: AI Memory Logger\n")
    print("Enter memory fragments (comma-separated):")
    fragments = input("> ").strip().split(",")
    fragments = [f.strip() for f in fragments if f.strip()]
    if not fragments:
        print("No fragments entered. Exiting.")
        return
    print("\nOptionally, enter metadata as key=value pairs (comma-separated), or leave blank:")
    meta_input = input("> ").strip()
    metadata = {}
    if meta_input:
        for pair in meta_input.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                metadata[k.strip()] = v.strip()
    memory = process_fragments(fragments, metadata=metadata)
    print("\nStructured memory:")
    print(memory["text"])
    print("\nMemory stored with ID:", memory["id"])

if __name__ == "__main__":
    main() 