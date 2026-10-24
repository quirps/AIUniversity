from __future__ import annotations

import random

from aiu.generators.base import register_generator
from aiu.models import Item

IN_TAX_CATEGORIES = ("billing", "login", "shipping", "refund", "bug")
OOT_COUNTS = {"feature_request": 7, "partnership": 7, "press": 6}

TEMPLATES = {
    "billing": (
        "I was charged twice for my subscription this month.",
        "My invoice does not match the plan I signed up for.",
        "The price on my receipt is higher than the quoted price.",
        "I need a copy of last month's invoice for my records.",
        "My card was declined but the payment still shows as pending.",
        "Please explain the extra line item on my latest bill.",
    ),
    "login": (
        "I cannot sign in even after resetting my password.",
        "The login page keeps returning me to the sign-in form.",
        "My account is locked and I did not request a reset.",
        "Two-factor codes are not arriving on my phone.",
        "I changed phones and cannot access my account.",
        "The session expires immediately after I sign in.",
    ),
    "shipping": (
        "My parcel has been stuck at the depot for three days.",
        "The tracking page has not updated since last week.",
        "The delivery address on the order is wrong.",
        "My package arrived damaged and the box was open.",
        "I need to change the delivery date for my order.",
        "The courier left my parcel at the wrong door.",
    ),
    "refund": (
        "I returned the item last week but have no refund yet.",
        "The refund amount is less than I paid for the order.",
        "Please cancel the order and refund the payment.",
        "I was told the refund would take three days and it has been ten.",
        "The returned item was rejected without an explanation.",
        "I need the refund sent to a different card.",
    ),
    "bug": (
        "The export button does nothing when I click it.",
        "The dashboard shows an error after I upload a file.",
        "Saving my settings silently discards the changes.",
        "The search results page is blank on my browser.",
        "The app crashes when I open the reports tab.",
        "Dates are displayed one day off in the activity log.",
    ),
    "feature_request": (
        "Could you add a dark mode to the web app?",
        "It would help to have a bulk import option.",
        "Please add a weekly digest email for my team.",
        "I would like to filter reports by custom tags.",
        "A keyboard shortcut for search would save time.",
        "Can you support exporting charts as images?",
        "An API endpoint for scheduled reports would be useful.",
    ),
    "partnership": (
        "Our agency would like to resell your product.",
        "We are exploring a co-marketing partnership and would like to talk.",
        "Could we discuss an integration partnership for our platform?",
        "Our company wants to become a certified partner.",
        "We would like to sponsor your next developer event.",
        "Our consultancy is interested in a referral agreement.",
        "Please connect us with your partnerships team.",
    ),
    "press": (
        "I am writing an article about your product and have questions.",
        "Our publication would like to interview your founder.",
        "Can you send a press kit and recent product screenshots?",
        "We are covering your launch and need a comment by Friday.",
        "A reporter would like to confirm details about your funding.",
        "Please add our editor to your press mailing list.",
    ),
}


@register_generator("E4")
def generate(rng: random.Random) -> list[Item]:
    records: list[tuple[str, bool, str]] = []

    for category in IN_TAX_CATEGORIES:
        templates = TEMPLATES[category]
        for index in range(12):
            records.append((category, True, templates[index % len(templates)]))

    for category, count in OOT_COUNTS.items():
        templates = TEMPLATES[category]
        for index in range(count):
            records.append((category, False, templates[index % len(templates)]))

    rng.shuffle(records)

    items: list[Item] = []
    for index, (category, in_taxonomy, message) in enumerate(records):
        items.append(
            Item(
                id=f"e4{index:03d}",
                input={"message": message},
                expected={"label": category, "in_taxonomy": in_taxonomy},
                meta={"category": category, "in_taxonomy": in_taxonomy},
            )
        )
    return items
