text = "Following Lenin’s advice, we recommend a “materialist reading” of the Logic. That is, where Hegel talks of a “spirit” which expresses or “posits” itself in Nature or human affairs."


def character_split(text: str):
    size = 35
    chunks = []

    i = 0
    while i <= len(text):
        chunk = text[i:i + size]
        chunks.append(chunk)
        i += size

    return chunks
















def main():
    res = character_split(text)
    for l in res:
        print(l + ".")


if __name__ == "__main__":
    main()
