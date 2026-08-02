#!/usr/bin/env python3
"""
生成未来几集的内容日历 CSV。

列名与 `run_week.py` 期望的保持一致（week/day/series/episode/title/
hook_line_spoken/outro_line_spoken/fact_topics），额外多出来的列
`csv.DictReader` 会直接忽略，所以可以安全地把调研信息（素材搜索词、
素材验证状态、事实出处）放在同一个文件里，不用再维护第二份文档。

`fact_topics` 用 `|` 分隔——run_week.py 按这个符号切成 facts 文件的每一行。

用法::

    uv run python docs/skill/plans/build_calendar.py
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "content_calendar_ep12_18.csv"

FIELDS = [
    "week", "day", "episode", "series", "title", "format", "topic",
    "status", "hook_line_spoken", "outro_line_spoken", "cta_type",
    "fact_topics", "segment_terms", "footage_status", "sources", "notes",
]

ROWS = [
    # ---------------------------------------------------------------- ep 12
    {
        "week": "1", "day": "Mon", "episode": "12",
        "series": "Random But True",
        "title": "Random But True Facts 12 \U0001f440",
        "format": "facts", "topic": "animals / strength",
        "status": "ready to build",
        "hook_line_spoken": "Did you know one beetle can pull 1,100 times its own weight?",
        "outro_line_spoken": "Comment which of these six you'd least want to arm-wrestle.",
        "cta_type": "COMMENT",
        "fact_topics": "|".join([
            "A dung beetle can pull over 1,100 times its own body weight. Scaled up, that is like one person dragging six double-decker buses. Measured in a 2010 study of the horned dung beetle Onthophagus taurus, the strongest animal on Earth relative to its own size.",
            "The saltwater crocodile has the strongest bite force ever measured in a living animal: about 3,700 pounds of force, recorded by Gregory Erickson's team in a 2012 study that tested every living crocodilian species.",
            "Ants can carry many times their own body weight in their jaws, with leafcutter ants commonly cited at up to roughly 50 times. Say 'up to' -- the exact multiple varies by species and by how it is measured, so do not state one hard number as if it were settled.",
            "A harpy eagle is powerful enough to snatch full-grown monkeys and sloths straight out of the treetops and fly off with them. Its rear talons are around the size of a grizzly bear's claws.",
            "A blue whale's tongue alone weighs about as much as an elephant. The whale itself can reach roughly 200 tons, making it the largest animal that has ever lived, bigger than any known dinosaur.",
            "Gorillas are estimated to be several times stronger than an adult human and can tear apart thick bamboo and branches with their hands. Phrase this as an estimate -- the widely repeated 'ten times stronger' figure is not from a controlled measurement, so do not state a hard multiple.",
        ]),
        "segment_terms": (
            '{"0": "dung beetle", "1": "dung beetle", "2": "crocodile jaws open", '
            '"3": "leafcutter ants carrying leaves", "4": "eagle flying close up", '
            '"5": "whale underwater", "6": "gorilla", "7": "gorilla"}'
        ),
        "footage_status": (
            "PROBED 2026-08-02. crocodile=excellent (croc face in water). "
            "gorilla=excellent (silverback eating). ants=good (weaver ants on leaves, "
            "not literally leafcutters -- acceptable, do not claim 'leafcutter' on screen). "
            "dung beetle=WEAK, returns a generic black beetle, no dung-rolling; "
            "consider Veo for a real dung-rolling shot or reword fact 1 to just 'a beetle'. "
            "eagle + whale = NOT yet eyeballed, probe before render."
        ),
        "sources": (
            "Knell & Simmons 2010 (Proc. R. Soc. B) dung beetle 1141x; "
            "Erickson et al. 2012 PLoS ONE croc bite 3700 lbf; "
            "harpy eagle prey: Smithsonian/Peregrine Fund; blue whale tongue: NOAA/WDC"
        ),
        "notes": "Safest opener of the batch: still animals, no format change. Facts 3 and 6 are deliberately hedged in the source text -- keep the hedge.",
    },
    # ---------------------------------------------------------------- ep 13
    {
        "week": "1", "day": "Wed", "episode": "13",
        "series": "Random But True",
        "title": "Random But True Facts 13 \U0001f440",
        "format": "facts", "topic": "ocean / deep sea (FIRST topic shift)",
        "status": "ready to build",
        "hook_line_spoken": "Did you know we've explored less of the ocean than the Moon?",
        "outro_line_spoken": "Comment if the eighty percent we've never seen keeps you up at night.",
        "cta_type": "COMMENT",
        "fact_topics": "|".join([
            "More than eighty percent of the ocean has never been mapped, explored, or even seen by humans. We have better maps of the surface of Mars than of our own seafloor.",
            "The deepest point in the ocean, Challenger Deep in the Mariana Trench, is about 10,900 metres down. Drop Mount Everest into it and the peak would still be roughly two kilometres underwater.",
            "Around three quarters of all ocean animals make their own light. A 2017 survey off the California coast found roughly seventy-six percent of the animals observed were bioluminescent, making glowing the norm in the ocean, not the exception.",
            "The longest mountain range on Earth is underwater. The mid-ocean ridge winds about 65,000 kilometres around the planet, and almost nobody has ever laid eyes on it.",
            "There are lakes and rivers at the bottom of the sea. Brine pools are so dense with salt that they do not mix with the seawater above them, so they form shorelines and waves down in the deep.",
            "Sound travels roughly four times faster underwater than through air, which is how whales can call to each other across enormous distances of open ocean.",
        ]),
        "segment_terms": (
            '{"0": "deep ocean underwater dark", "1": "deep ocean underwater dark", '
            '"2": "deep ocean underwater dark", "3": "bioluminescent glowing jellyfish", '
            '"4": "underwater volcano vent", "5": "underwater cave diving", '
            '"6": "whale underwater", "7": "ocean waves aerial"}'
        ),
        "footage_status": (
            "PROBED 2026-08-02. deep ocean dark=excellent (divers in dark blue crevasse). "
            "bioluminescent jellyfish=excellent (glowing pink jelly on black). "
            "underwater volcano vent=good (rocky underwater ridge + rising bubbles, "
            "reads well as the mid-ocean ridge). "
            "underwater cave diving + whale + ocean waves aerial = NOT yet eyeballed, probe before render. "
            "Ocean is rated 'excellent' coverage in playbook section 5, lowest-risk topic in this batch."
        ),
        "sources": (
            "NOAA Ocean Exploration (>80% unmapped/unexplored); "
            "Challenger Deep ~10,935m (2010 USNS Sumner survey); "
            "Martini & Haddock 2017 Scientific Reports (76% bioluminescent); "
            "NOAA mid-ocean ridge ~65,000km; NOAA brine pools"
        ),
        "notes": "The gentle bridge: still sea ANIMALS in frame, but the topic is now the ocean itself. This is the first real data point on whether non-animal topics retain on this channel.",
    },
    # ---------------------------------------------------------------- ep 14
    {
        "week": "1", "day": "Fri", "episode": "14",
        "series": "Random But True",
        "title": "Random But True: The Octopus That Escaped",
        "format": "STORY (story_episode.py)", "topic": "ocean / true story",
        "status": "needs story file + dry-run lock",
        "hook_line_spoken": "(story format: hook is generated then locked via --from-dry-run)",
        "outro_line_spoken": "Comment if you think Inky made it home.",
        "cta_type": "COMMENT",
        "fact_topics": "|".join([
            "STORY LEAD (not fact lines -- feed this to story_episode.py --story-file):",
            "Inky was a common New Zealand octopus living at the National Aquarium in Napier. He had arrived scarred, after being caught in a crayfish pot.",
            "One night in 2016 the lid of his tank was left slightly ajar. Inky climbed out, crossed the floor of the aquarium, and found a drainpipe about 15 centimetres wide.",
            "He squeezed his whole body down that pipe -- an octopus has no bones, so it can pour itself through any gap bigger than its beak -- and the pipe ran roughly 50 metres straight out to Hawke's Bay.",
            "Staff found only a wet trail across the floor the next morning. Inky was never seen again.",
            "Narrative shape: an animal held in a tank quietly works out the one weakness in the room, and takes it. The reveal should land on the trail of water on the floor -- the only evidence he left.",
        ]),
        "segment_terms": (
            '{"0": "octopus underwater", "1": "aquarium tank glass", '
            '"2": "octopus underwater", "3": "drain pipe water", '
            '"4": "octopus underwater", "5": "ocean waves at night", '
            '"6": "empty aquarium tank", "7": "ocean horizon"}'
        ),
        "footage_status": (
            "NOT PROBED. 'octopus underwater' is a known-good term (playbook section 6 documents "
            "that bare 'octopus' returns octopus carpaccio -- always qualify it with 'underwater'). "
            "Probe drain pipe / aquarium / night-ocean terms before rendering; these are the risky ones."
        ),
        "sources": (
            "Widely reported April 2016: New York Times, BBC, The Guardian; "
            "National Aquarium of New Zealand statements. Verify independently before render per playbook section 7a."
        ),
        "notes": (
            "FIRST story episode on this channel. Deliberately an ANIMAL story so only the FORMAT is new, "
            "not the subject. Story flow rules: do NOT use refine_hook, and lock the script with "
            "--from-dry-run before rendering or the fact-check is void (playbook section 7a)."
        ),
    },
    # ---------------------------------------------------------------- ep 15
    {
        "week": "2", "day": "Mon", "episode": "15",
        "series": "Random But True",
        "title": "Random But True Facts 15 \U0001f440",
        "format": "facts", "topic": "food (FIRST fully non-animal)",
        "status": "ALREADY BUILT -- re-title and publish",
        "hook_line_spoken": "Did you know Sweden's best-selling pizza is topped with banana and curry?",
        "outro_line_spoken": "Tell us which of these five you'd actually order -- we're guessing it's not the banana one.",
        "cta_type": "COMMENT",
        "fact_topics": "|".join([
            "ALREADY RENDERED as the standalone pizza episode -- see storage/tasks/43f86404-4b9e-46ce-b693-8ba6c1130524/",
            "Sweden: banana + curry powder + chicken pizza, a genuine staple.",
            "Brazil: Pizza Portuguesa with hard-boiled egg, green peas, ham.",
            "Japan: potato mayo pizza with corn, bacon, Kewpie mayonnaise stripes. Do NOT call it 'mentai mayo' -- that is a different pizza topped with cod roe.",
            "Finland: the Berlusconi pizza, smoked reindeer, created in 2005 after Italy's prime minister mocked Finnish food. Make clear Berlusconi led ITALY, not Finland.",
            "Philippines: sweet mango pizza with cheese and chilli sauce.",
        ]),
        "segment_terms": (
            '{"0": "pizza slice close up cheese", "1": "pizza toppings variety", '
            '"2": "pizza with egg and peas", "3": "potato pizza corn bacon", '
            '"4": "reindeer meat food", "5": "mango fruit slices", '
            '"6": "pizza slice close up cheese"}'
        ),
        "footage_status": "PROBED + RENDERED + verified frame-by-frame 2026-08-01. Known good.",
        "sources": "fontanaforniusa.com, hungryhowies.com, atlasobscura.com (reindeer pizza), plus independent checks",
        "notes": (
            "Only 5 facts, not 6 -- it was built as a standalone before the series slot existed. "
            "Either publish as-is with a 5/5 counter, or rebuild with a 6th topping for consistency. "
            "Hook already updated to question form. 8 AI hero images + Veo prompts were generated for this one."
        ),
    },
    # ---------------------------------------------------------------- ep 16
    {
        "week": "2", "day": "Wed", "episode": "16",
        "series": "Random But True",
        "title": "Random But True Facts 16 \U0001f440",
        "format": "facts", "topic": "dogs (return to animals)",
        "status": "ready to build",
        "hook_line_spoken": "Did you know there's a dog breed that physically cannot bark?",
        "outro_line_spoken": "Comment your dog's breed and we'll tell you its weirdest trait.",
        "cta_type": "COMMENT",
        "fact_topics": "|".join([
            "Basenjis do not bark. The shape of their larynx is different, so instead of barking they make a strange yodelling sound owners call a baroo.",
            "Dalmatians are born completely white. Their spots only start appearing after about two weeks, and keep developing for months.",
            "Greyhounds can hit around 45 miles an hour, making them the fastest dogs on Earth and, over short distances, faster than a racehorse.",
            "A border collie named Chaser learned the names of over a thousand individual objects and could fetch them by name, the largest tested vocabulary of any non-human animal.",
            "Chow Chows and Shar-Peis have blue-black tongues instead of pink ones. Nobody is entirely sure why, and they are the only dog breeds that have it.",
            "Newfoundlands have webbed feet and a water-resistant coat, and were bred specifically to haul drowning people out of the sea. Some are still trained as rescue dogs today.",
        ]),
        "segment_terms": (
            '{"0": "dog close up portrait", "1": "basenji dog", "2": "dalmatian dog", '
            '"3": "greyhound running fast", "4": "border collie herding", '
            '"5": "chow chow dog", "6": "newfoundland dog swimming", "7": "dog close up portrait"}'
        ),
        "footage_status": (
            "PARTIALLY PROBED 2026-08-02. dalmatian=excellent (spotted dog shaking off water). "
            "greyhound + border collie NOT yet eyeballed. "
            "basenji / chow chow / newfoundland are BREED-SPECIFIC and therefore the highest-risk terms in "
            "this episode -- Pexels rarely distinguishes breeds. Probe all three before render; "
            "fall back to generic dog footage rather than showing an obviously wrong breed."
        ),
        "sources": (
            "Basenji larynx: AKC breed standard; Chaser: Pilley & Reid 2011 Behavioural Processes; "
            "greyhound speed: AKC; Dalmatian spots: AKC; Newfoundland water rescue: AKC"
        ),
        "notes": "Returns to animals so the topic shift doesn't read as abandoning the channel's identity. Dogs = broad audience + good stock coverage.",
    },
    # ---------------------------------------------------------------- ep 17
    {
        "week": "2", "day": "Fri", "episode": "17",
        "series": "Random But True",
        "title": "Random But True: The Insult That Built Lamborghini",
        "format": "STORY (story_episode.py)", "topic": "cars / true story",
        "status": "ALREADY BUILT -- re-title and publish",
        "hook_line_spoken": "(already rendered: 'An angry tractor maker started a luxury car company just to spite Ferrari.')",
        "outro_line_spoken": "Drop a comment if you'd walk away from a giant like Ferrari just to build your own.",
        "cta_type": "COMMENT",
        "fact_topics": "|".join([
            "ALREADY RENDERED -- see storage/tasks/70c8a157-61e3-44de-b8a8-7b00e6872b09/",
            "Alfa Romeo pushed out Enzo Ferrari, who left and founded Ferrari.",
            "Ferruccio Lamborghini complained about his Ferrari's clutch; Enzo told him to stick to tractors.",
            "That snub pushed Lamborghini to build his own sports cars.",
            "Horacio Pagani was denied budget for carbon fibre at Lamborghini, left, and founded Pagani.",
            "Payoff: every one of these rivals was born from someone being dismissed.",
        ]),
        "segment_terms": (
            '{"0": "tractor field farmer", "1": "vintage convertible car driving countryside", '
            '"2": "red ferrari sports car driving", "3": "sports car engine revving close up", '
            '"4": "tractor field farmer", "5": "black lamborghini supercar", '
            '"6": "supercar factory workshop engineer", "7": "sports car driving sunset road"}'
        ),
        "footage_status": "PROBED + RENDERED + verified frame-by-frame 2026-08-01. Known good.",
        "sources": (
            "he.wikipedia.org/Alfa_Romeo; en.wikipedia.org/Ferrari; caranddriver.com (clutch story); "
            "motorvalley.it (Pagani interview). Clutch anecdote is framed as the story Lamborghini itself tells, not as verified transcript."
        ),
        "notes": (
            "Second story, and the first NON-animal story -- by now both the story format (ep 14) and "
            "non-animal topics (ep 15) have each been introduced separately. Was originally built under "
            "the series name 'Rival Origins'; re-title under Random But True per the branding decision in playbook section 5."
        ),
    },
    # ---------------------------------------------------------------- ep 18
    {
        "week": "3", "day": "Mon", "episode": "18",
        "series": "Random But True",
        "title": "Random But True Facts 18 \U0001f440",
        "format": "facts", "topic": "everyday objects",
        "status": "ready to build",
        "hook_line_spoken": "Did you know bubble wrap was invented as wallpaper?",
        "outro_line_spoken": "Comment which one of these you're going to check right now.",
        "cta_type": "COMMENT",
        "fact_topics": "|".join([
            "Bubble wrap was invented in 1957 as textured wallpaper. Nobody wanted it on their walls, so its inventors spent years looking for another use before it became packaging.",
            "That tiny extra pocket inside the front pocket of your jeans was designed to hold a pocket watch, back when Levi's made trousers for miners in the 1870s.",
            "Aluminium was once more valuable than gold. Napoleon the Third reportedly served his most honoured guests with aluminium cutlery while everyone else got gold, because refining it was so difficult.",
            "The small hole in a pen cap is a safety feature. If someone swallows the cap, that hole keeps an airway open instead of sealing the windpipe shut.",
            "Honey never spoils. Archaeologists found pots of honey in Egyptian tombs, more than three thousand years old, and it was still perfectly edible.",
            "The little arrow next to the fuel pump symbol on your dashboard points to the side of the car your fuel cap is on. Most drivers have never noticed it.",
        ]),
        "segment_terms": (
            '{"0": "bubble wrap popping", "1": "bubble wrap popping", "2": "denim jeans texture", '
            '"3": "silver metal foil texture", "4": "writing with pen close up", '
            '"5": "honey jar dripping", "6": "car dashboard driving", "7": "bubble wrap popping"}'
        ),
        "footage_status": (
            "PARTIALLY PROBED 2026-08-02. bubble wrap=excellent (hands squeezing bubble wrap). "
            "honey jar=excellent (jar + wooden dipper). "
            "REJECTED: 'blue jeans pocket close up' returns a hand holding a lit cigarette against denim -- "
            "wrong subject AND poor fit for a general-audience channel. Use 'denim jeans texture' instead and re-probe. "
            "silver foil / pen / dashboard NOT yet eyeballed."
        ),
        "sources": (
            "Bubble wrap: Sealed Air company history (Fielding & Chavannes, 1957); "
            "Levi's watch pocket: Levi Strauss & Co. archives; "
            "Napoleon III aluminium: widely documented, e.g. Royal Society of Chemistry; "
            "Egyptian tomb honey: Smithsonian Magazine; pen cap hole: BIC safety statement"
        ),
        "notes": (
            "Most footage-abstract episode of the batch -- objects are rated 'excellent' coverage in "
            "playbook section 5, but each fact needs a literal filmable object, so probe every term. "
            "Fact 6 (fuel arrow) is the strongest comment-bait in the whole batch."
        ),
    },
]


def main() -> int:
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for row in ROWS:
            writer.writerow(row)
    print(f"wrote {OUT} ({len(ROWS)} episodes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
