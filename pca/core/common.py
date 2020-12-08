__all__ = ["INDICATOR_LOOKUP"]

from pca.util import Enumerator

INDICATOR_LOOKUP = {
    "appearance": {
        "grammar": {0: "Grammar - Poor", 1: "Grammar - Decent", 2: "Grammar - Proper"},
        "link_domain": {0: "Link/Domain - Fake", 1: "Link/Domain - Spoofed/Hidden "},
        "logo_graphics": {0: "Logo/Graphics - None", 1: "Logo/Graphics - Spoofed/HTML"},
    },
    "sender": {
        "external": {
            0: "External - Not Applicable or Unknown",
            1: "External - Spoofed",
        },
        "internal": {
            0: "Internal - Not Applicable",
            1: "Internal - Unknown",
            2: "Internal - Spoofed",
        },
        "authoritative": {
            0: "Authoritative - Not Applicable",
            1: "Authoritative - Corporate/Local",
            2: "Authoritative - State/Federal",
        },
    },
    "relevancy": {
        "organization": {0: "Organization - False", 1: "Organization - True"},
        "public_news": {0: "Public News - False", 1: "Public News - True"},
    },
    "behavior": {
        "fear": {0: "Fear - False", 1: "Fear - True"},
        "duty_obligation": {
            0: "Duty or Obligation - False",
            1: "Duty or Obligation - True",
        },
        "curiosity": {0: "Curiosity - False", 1: "Curiosity - True"},
        "greed": {0: "Greed - False", 1: "Greed - True"},
    },
}
