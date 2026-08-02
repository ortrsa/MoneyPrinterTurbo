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
    "fact_topics", "segment_terms", "footage_status", "sources",
    "criteria_fit", "notes",
]

# 频道主给的选题三标准（2026-08-02），以及本频道能/不能满足哪一条。
# 诚实结论写在每集的 criteria_fit 列里，不要粉饰：
#   1. Universal Relatability —— 本频道天然满足（食物/动物是标准里点名的类目）。
#   2. Emotional Hook / Absurdity —— **清单式事实视频结构上做不到**。这条讲的是
#      "创作者为了一件小事投入疯狂努力"，需要镜头里有人在干活；本频道是无人出镜
#      的图库素材配旁白，没有可展示的"努力"。硬凑会变成 SKILL.md already warns
#      about 的假 before/after。故事流程能部分满足（主角是动物本身的疯狂努力）。
#   3. Completion Compulsion —— **这条是真正能修且必须修的**。六条独立事实在第
#      一条就把价值给完了，观众提前离开没有损失，这正对应 playbook §3 记录的
#      33% 留存。修法不需要改格式，只需要：钩子里预告一个"留到最后才揭晓"的
#      东西，并把最炸的一条放在**最后**而不是开头。


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
        "criteria_fit": (
            "SHIPPED BEFORE the three-criteria rule was adopted -- treat as the BASELINE to measure against. "
            "Relatability HIGH (animals). Absurdity NONE. Completion compulsion NONE: the hook gives away fact 1's "
            "payload ('1,100 times its own weight') in the first line, and the six facts are independent, so a "
            "viewer has the full value by second five. If ep 13+ retain better, the completion-compulsion "
            "restructure is the likely cause -- this is the control."
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
        "hook_line_spoken": "Did you know the strangest thing in the ocean isn't a creature?",
        "outro_line_spoken": "Comment if you had any idea the sea has its own lakes down there.",
        "cta_type": "COMMENT",
        # 顺序是刻意排的：把最"这也行？"的一条（海底盐湖）放到**最后**，钩子只
        # 抛出"最怪的东西不是生物"这个悬念而不揭晓，观众要拿到答案就必须看到第六条。
        # 这就是三标准里的 Completion Compulsion，也是本频道唯一真正能补的一条。
        "fact_topics": "|".join([
            "The deepest point in the ocean, Challenger Deep in the Mariana Trench, is about 10,900 metres down. Drop Mount Everest into it and the peak would still be roughly two kilometres underwater.",
            "Sound travels roughly four times faster underwater than through air, which is how whales can call to each other across enormous distances of open ocean.",
            "Around three quarters of all ocean animals make their own light. A 2017 survey off the California coast found roughly seventy-six percent of the animals observed were bioluminescent, making glowing the norm in the ocean, not the exception.",
            "The longest mountain range on Earth is underwater. The mid-ocean ridge winds about 65,000 kilometres around the planet, and almost nobody has ever laid eyes on it.",
            "More than eighty percent of the ocean has never been mapped, explored, or even seen by humans. We have better maps of the surface of Mars than of our own seafloor.",
            "And the strangest thing down there is not alive at all: there are lakes at the bottom of the sea. Brine pools are so dense with salt that they do not mix with the water above them, so they have their own shorelines, their own waves, and their own surface that a submarine can float on. THIS IS THE PAYOFF FACT the hook promised -- it must stay LAST, and the wording should explicitly close the loop on 'not a creature'.",
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
        "criteria_fit": (
            "Relatability HIGH -- ocean needs no prior knowledge or language. "
            "Absurdity NONE (unreachable for this format, see header note). "
            "Completion compulsion NOW BUILT IN: hook promises 'the strangest thing isn't a creature' and "
            "withholds it; the brine-pool payoff is fact 6, so leaving early means not getting the answer. "
            "FIRST episode built under the three-criteria rule -- compare its retention against ep 12, which is the control."
        ),
        "notes": (
            "The gentle bridge: still sea ANIMALS in frame, but the topic is now the ocean itself. "
            "Two things are being tested at once here (new topic AND new completion-compulsion structure), so if "
            "retention moves, do not attribute it to only one of them without ep 16 as a second data point."
        ),
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
        "criteria_fit": (
            "BEST FIT OF THE ENTIRE SLATE -- the only episode that hits all three criteria. "
            "Relatability HIGH (an animal, no language needed). "
            "Absurdity HIGH and this is the important part: the 'why would you go to all that trouble' reaction "
            "lands on INKY, not on a creator -- an octopus mounts a patient, deliberate night-time escape for the "
            "simple goal of getting back to the sea. That is the one way this faceless channel can satisfy "
            "criterion 2 at all. "
            "Completion compulsion HIGH and native to the format: 'did he make it?' is unanswerable until the end. "
            "IMPLICATION: stories satisfy 2-3 criteria natively while facts satisfy only 1, which argues for a "
            "higher story frequency than the 3:1 ratio originally proposed. Do not flip wholesale on an untested "
            "framework -- facts are the only format with real retention data on this channel (playbook section 3) -- "
            "but raise story frequency if ep 14 outperforms."
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
        "criteria_fit": (
            "Relatability HIGHEST of the whole slate -- food is the first category the criteria name, and pizza "
            "needs zero prior knowledge in any country. "
            "Absurdity NONE. "
            "Completion compulsion WEAK AS BUILT: the hook spends Sweden's banana pizza immediately and the five "
            "toppings are independent. If it is rebuilt for the 6th topping anyway, take that chance to move the "
            "strongest topping (Finland's reindeer 'Berlusconi' pizza -- it has a revenge story attached, so it is "
            "the only one with a narrative kick) to LAST and rewrite the hook to withhold it."
        ),
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
        "hook_line_spoken": "Did you know one dog understood more words than a toddler?",
        "outro_line_spoken": "Comment your dog's breed and whether it could ever pull off Chaser's thousand words.",
        "cta_type": "COMMENT",
        # 同样按 Completion Compulsion 排序：钩子只说"有只狗认识的词比幼儿还多"，
        # 不说是谁、多少，答案（Chaser，一千多个词）压到第六条。
        "fact_topics": "|".join([
            "Basenjis do not bark. The shape of their larynx is different, so instead of barking they make a strange yodelling sound owners call a baroo.",
            "Chow Chows and Shar-Peis have blue-black tongues instead of pink ones. Nobody is entirely sure why, and they are the only dog breeds that have it.",
            "Dalmatians are born completely white. Their spots only start appearing after about two weeks, and keep developing for months.",
            "Newfoundlands have webbed feet and a water-resistant coat, and were bred specifically to haul drowning people out of the sea. Some are still trained as rescue dogs today.",
            "Greyhounds can hit around 45 miles an hour, making them the fastest dogs on Earth and, over short distances, faster than a racehorse.",
            "And the dog from the opening: a border collie named Chaser learned the names of over a thousand individual objects and could fetch each one by name -- a bigger tested vocabulary than a typical toddler, and the largest ever measured in a non-human animal. THIS IS THE PAYOFF FACT the hook promised -- keep it LAST and open it by explicitly calling back to the hook.",
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
        "criteria_fit": (
            "Relatability HIGH -- dogs are in the criteria's named categories and need no explanation anywhere. "
            "Absurdity NONE. "
            "Completion compulsion BUILT IN: hook withholds which dog and how many words; Chaser is fact 6. "
            "This is the CLEAN second data point on the restructure -- unlike ep 13 it does NOT also change topic "
            "(back to animals, same as eps 1-12), so if 16 retains better than 12 the structure is the only variable that moved."
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
        "criteria_fit": (
            "Relatability MEDIUM -- cars are globally recognisable, but this leans on knowing the Ferrari and "
            "Lamborghini brands, so it is the weakest of the slate on criterion 1. "
            "Absurdity MEDIUM: 'a man was insulted about a clutch, so he built a rival supercar company' is exactly "
            "the disproportionate-effort-for-a-petty-reason shape criterion 2 describes -- again carried by the "
            "subject rather than a creator. "
            "Completion compulsion HIGH -- native to the story format, the chain keeps escalating to Pagani. "
            "AS ALREADY RENDERED its hook is a statement, not a question, and it gives away the tractor/Ferrari "
            "punchline up front. Acceptable to ship as-is (story hooks legitimately differ, see playbook section 5), but "
            "if it is ever re-rendered, withhold the Pagani link instead of front-loading it."
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
        "hook_line_spoken": "Did you know your car has been hiding a clue you've never noticed?",
        "outro_line_spoken": "Comment if you're going out to check that little arrow right now.",
        "cta_type": "COMMENT",
        # 最后一条（油箱箭头）是全批最强的一条：观众能立刻站起来去自己车上验证。
        # 钩子只说"你的车藏了个你没注意的线索"，答案压到第六条 —— 既是 Completion
        # Compulsion，也是最好的评论诱因。
        "fact_topics": "|".join([
            "Bubble wrap was invented in 1957 as textured wallpaper. Nobody wanted it on their walls, so its inventors spent years looking for another use before it became packaging.",
            "That tiny extra pocket inside the front pocket of your jeans was designed to hold a pocket watch, back when Levi's made trousers for miners in the 1870s.",
            "Aluminium was once more valuable than gold. Napoleon the Third reportedly served his most honoured guests with aluminium cutlery while everyone else got gold, because refining it was so difficult.",
            "The small hole in a pen cap is a safety feature. If someone swallows the cap, that hole keeps an airway open instead of sealing the windpipe shut.",
            "Honey never spoils. Archaeologists found pots of honey in Egyptian tombs, more than three thousand years old, and it was still perfectly edible.",
            "And the clue in your car from the opening: the little arrow next to the fuel pump symbol on your dashboard points to the side your fuel cap is on. It is in almost every modern car and most drivers have never once noticed it. THIS IS THE PAYOFF FACT the hook promised -- keep it LAST and open by calling back to the hook.",
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
        "criteria_fit": (
            "Relatability HIGH -- everyone owns jeans, pens and honey; no language or prior knowledge needed. "
            "Absurdity NONE. "
            "Completion compulsion STRONGEST OF THE FACTS EPISODES: the withheld payoff is not just surprising, it is "
            "ACTIONABLE -- the viewer can walk out to their own car and verify it, which is also why it is the best "
            "comment bait in the batch. If the restructure works anywhere, expect it to show up most clearly here."
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
