import json
import sys

def update_version(new_version):
    # Load the manifest.json file
    with open("manifest.json", "r") as file:
        manifest = json.load(file)

    # Update the version field
    manifest["version"] = new_version

    # Write the updated manifest back to the file
    with open("manifest.json", "w") as file:
        json.dump(manifest, file, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_manifest_version.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]
    update_version(new_version)
