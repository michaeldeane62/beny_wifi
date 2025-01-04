import json

def bump_version():
    with open("manifest.json", "r") as file:
        manifest = json.load(file)

    current_version = manifest.get("version")
    if not current_version:
        raise ValueError("Version not found in manifest.json")

    # Increment the patch version
    major, minor, patch = map(int, current_version.split("."))
    new_version = f"{major}.{minor}.{patch + 1}"
    manifest["version"] = new_version

    # Write the updated manifest back
    with open("manifest.json", "w") as file:
        json.dump(manifest, file, indent=4)

    return new_version

if __name__ == "__main__":
    print(bump_version())
