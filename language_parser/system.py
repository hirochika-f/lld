
def exact_match(tag: str, supported: list[str]):
    return [locale for locale in supported if tag == locale]

def prefix_match(tag: str, supported: list[str]):
    if "-" not in tag:
        return [locale for locale in supported if locale.startswith(tag + "-")]
    else:
        return exact_match(tag, supported)

def weight_selection(weight: str, supported: list[str]):
    preferences: list[tuple[float, str]] = _parse_weight(weight)
    ret = []
    for _, tag in preferences:
        matched = prefix_match(tag, supported)
        if matched:
            for match in matched:
                ret.append(match)
    return ret

def _parse_weight(weight: str):
    locales_weights: list[str] = weight.split(",")
    preferences = []
    for locale_weight in locales_weights:
        locale_weight = locale_weight.lstrip(" ")
        if "q=" not in locale_weight:
            preferences.append((1.0, locale_weight))
        else:
            locale, weight = locale_weight.split(";")
            preferences.append((float(weight[2:]), locale))
    return sorted(preferences, key=lambda x: x[0], reverse=True)


if __name__ == "__main__":
    supported = ["en-US", "en-CA", "fr-FR"]
    print(exact_match("fr-FR", supported))
    print(prefix_match("en", supported))
    print(prefix_match("en-US", supported))

    weight = "ja-JP, en-SP;q=0.9, fr;q=0.8, en;q=0.8"
    print(weight_selection(weight, supported))
