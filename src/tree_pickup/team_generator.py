"""Team name generation using NATO phonetic alphabet."""

NATO_ALPHABET = [
    "Alpha",
    "Bravo",
    "Charlie",
    "Delta",
    "Echo",
    "Foxtrot",
    "Golf",
    "Hotel",
    "India",
    "Juliet",
    "Kilo",
    "Lima",
    "Mike",
    "November",
    "Oscar",
    "Papa",
    "Quebec",
    "Romeo",
    "Sierra",
    "Tango",
    "Uniform",
    "Victor",
    "Whiskey",
    "X-ray",
    "Yankee",
    "Zulu",
]


def generate_team_names(count: int) -> list[str]:
    """
    Generate team names using NATO phonetic alphabet.

    For counts > 26, cycles through alphabet with numbers appended.

    Args:
        count: Number of team names to generate

    Returns:
        List of team names like "Team Alpha", "Team Bravo", etc.
    """
    names = []

    for i in range(count):
        cycle = i // len(NATO_ALPHABET)
        idx = i % len(NATO_ALPHABET)

        if cycle == 0:
            names.append(f"Team {NATO_ALPHABET[idx]}")
        else:
            names.append(f"Team {NATO_ALPHABET[idx]} {cycle + 1}")

    return names
