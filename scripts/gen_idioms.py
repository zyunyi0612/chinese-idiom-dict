#!/usr/bin/env python3
"""
Generate N new Chinese idioms and append to idioms.json.
Uses Hermes LLM via hermes_tools subprocess.

Usage: python3 gen_idioms.py [count]
"""
import json
import os
import random
import subprocess
import sys
from pathlib import Path

BASE = Path("/Users/zhangyunyi/projects/idiom-dict")
IDIOMS_FILE = BASE / "idioms" / "idioms.json"

# Pool of common, well-known chengyu to draw from (high search value)
# These are classical 4-character idioms not yet in the dataset
CANDIDATE_IDIOMS = [
    ("一帆风顺", "yī fān fēng shùn", "smooth sailing"),
    ("一举两得", "yī jǔ liǎng dé", "kill two birds with one stone"),
    ("一目了然", "yī mù liǎo rán", "clear at a glance"),
    ("一丝不苟", "yī sī bù gǒu", "meticulous"),
    ("一心一意", "yī xīn yī yì", "wholeheartedly"),
    ("不屈不挠", "bù qū bù náo", "unyielding"),
    ("不耻下问", "bù chǐ xià wèn", "not ashamed to ask below"),
    ("不速之客", "bù sù zhī kè", "uninvited guest"),
    ("不可思议", "bù kě sī yì", "inconceivable"),
    ("不负众望", "bù fù zhòng wàng", "live up to expectations"),
    ("丰富多彩", "fēng fù duō cǎi", "rich and colorful"),
    ("风和日丽", "fēng hé rì lì", "fine weather"),
    ("风雨同舟", "fēng yǔ tóng zhōu", "stand together in storm"),
    ("光明正大", "guāng míng zhèng dà", "open and upright"),
    ("海阔天空", "hǎi kuò tiān kōng", "as boundless as sea and sky"),
    ("含辛茹苦", "hán xīn rú kǔ", "endure hardships"),
    ("红颜薄命", "hóng yán bó mìng", "beautiful women suffer tragic fates"),
    ("虎头蛇尾", "hǔ tóu shé wěi", "strong start, weak finish"),
    ("花容月貌", "huā róng yuè mào", "beautiful as flowers and moon"),
    ("焕然一新", "huàn rán yī xīn", "completely new look"),
    ("恍然大悟", "huǎng rán dà wù", "suddenly see the light"),
    ("鸡犬不宁", "jī quǎn bù níng", "even chickens and dogs restless"),
    ("家喻户晓", "jiā yù hù xiǎo", "known to every household"),
    ("驾轻就熟", "jià qīng jiù shú", "do sth with ease"),
    ("坚不可摧", "jiān bù kě cuī", "indestructible"),
    ("艰苦奋斗", "jiān kǔ fèn dòu", "struggle hard"),
    ("皆大欢喜", "jiē dà huān xǐ", "everybody is happy"),
    ("竭尽全力", "jié jìn quán lì", "do one's utmost"),
    ("金枝玉叶", "jīn zhī yù yè", "noble lineage"),
    ("精益求精", "jīng yì qiú jīng", "constantly improve"),
    ("惊弓之鸟", "jīng gōng zhī niǎo", "once-bitten twice-shy"),
    ("惊天动地", "jīng tiān dòng dì", "world-shaking"),
    ("敬而远之", "jìng ér yuǎn zhī", "respect but keep distance"),
    ("举一反三", "jǔ yī fǎn sān", "draw inferences"),
    ("开门见山", "kāi mén jiàn shān", "come straight to the point"),
    ("刻骨铭心", "kè gǔ míng xīn", "engraved in heart"),
    ("空前绝后", "kōng qián jué hòu", "unprecedented and unrepeatable"),
    ("口若悬河", "kǒu ruò xuán hé", "talk glibly"),
    ("苦尽甘来", "kǔ jìn gān lái", "sweetness after bitterness"),
    ("来者不拒", "lái zhě bù jù", "refuse nobody"),
    ("老马识途", "lǎo mǎ shí tú", "an old horse knows the way"),
    ("理直气壮", "lǐ zhí qì zhuàng", "with justice on one's side"),
    ("力不从心", "lì bù cóng xīn", "ability falls short of desire"),
    ("力挽狂澜", "lì wǎn kuáng lán", "turn the tide"),
    ("良药苦口", "liáng yào kǔ kǒu", "good medicine tastes bitter"),
    ("两全其美", "liǎng quán qí měi", "satisfy both sides"),
    ("琳琅满目", "lín láng mǎn mù", "superb collection"),
    ("柳暗花明", "liǔ àn huā míng", "new sight in the dark"),
    ("落井下石", "luò jǐng xià shí", "kick someone when they're down"),
    ("毛遂自荐", "máo suí zì jiàn", "volunteer oneself"),
    ("每况愈下", "měi kuàng yù xià", "go from bad to worse"),
    ("美中不足", "měi zhōng bù zú", "a fly in the ointment"),
    ("名落孙山", "míng luò sūn shān", "fail an exam"),
    ("莫名其妙", "mò míng qí miào", "baffling"),
    ("南辕北辙", "nán yuán běi zhé", "act contrary to one's goal"),
    ("难能可贵", "nán néng kě guì", "difficult but praiseworthy"),
    ("鸟语花香", "niǎo yǔ huā xiāng", "birds singing, flowers fragrant"),
    ("庞然大物", "páng rán dà wù", "giant thing"),
    ("抛砖引玉", "pāo zhuān yǐn yù", "humble remark to spark better ideas"),
    ("披荆斩棘", "pī jīng zhǎn jí", "break through thorns"),
    ("萍水相逢", "píng shuǐ xiāng féng", "meet by chance"),
    ("七上八下", "qī shàng bā xià", "anxious and unsettled"),
    ("杞人忧天", "qǐ rén yōu tiān", "unnecessary anxiety"),
    ("千军万马", "qiān jūn wàn mǎ", "a mighty force"),
    ("千载难逢", "qiān zǎi nán féng", "rare chance in a thousand years"),
    ("潜移默化", "qián yí mò huà", "imperceptible influence"),
    ("强词夺理", "qiǎng cí duó lǐ", "use lame arguments"),
    ("锲而不舍", "qiè ér bù shě", "perseverance"),
    ("青红皂白", "qīng hóng zào bái", "right and wrong"),
    ("青云直上", "qīng yún zhí shàng", "meteoric rise"),
    ("倾国倾城", "qīng guó qīng chéng", "devastatingly beautiful"),
    ("全心全意", "quán xīn quán yì", "wholeheartedly"),
    ("人山人海", "rén shān rén hǎi", "huge crowd"),
    ("人面兽心", "rén miàn shòu xīn", "beast in human face"),
    ("忍无可忍", "rěn wú kě rěn", "at the end of one's patience"),
    ("日新月异", "rì xīn yuè yì", "change rapidly"),
    ("如出一辙", "rú chū yī zhé", "exactly the same"),
    ("如鱼得水", "rú yú dé shuǐ", "like fish in water"),
    ("入木三分", "rù mù sān fēn", "penetrating insight"),
    ("三顾茅庐", "sān gù máo lú", "earnestly seek talent"),
    ("三心二意", "sān xīn èr yì", "half-hearted"),
    ("色彩斑斓", "sè cǎi bān lán", "colorful"),
    ("杀鸡儆猴", "shā jī jǐng hóu", "punish one as a warning to others"),
    ("山穷水尽", "shān qióng shuǐ jìn", "at the end of one's rope"),
    ("赏心悦目", "shǎng xīn yuè mù", "pleasing to eye and mind"),
    ("身临其境", "shēn lín qí jìng", "feel like being there"),
    ("实事求是", "shí shì qiú shì", "seek truth from facts"),
    ("史无前例", "shǐ wú qián lì", "unprecedented"),
    ("世外桃源", "shì wài táo yuán", "earthly paradise"),
    ("手不释卷", "shǒu bù shì juàn", "never seen without a book"),
    ("熟能生巧", "shú néng shēng qiǎo", "practice makes perfect"),
    ("水落石出", "shuǐ luò shí chū", "truth comes out"),
    ("顺其自然", "shùn qí zì rán", "let nature take its course"),
    ("四海之内", "sì hǎi zhī nèi", "within the four seas"),
    ("所向披靡", "suǒ xiàng pī mǐ", "invincible"),
    ("谈笑风生", "tán xiào fēng shēng", "talk cheerfully"),
    ("忐忑不安", "tǎn tè bù ān", "uneasy"),
    ("提心吊胆", "tí xīn diào dǎn", "be on edge"),
    ("天罗地网", "tiān luó dì wǎng", "inescapable net"),
    ("天下无双", "tiān xià wú shuāng", "matchless in the world"),
    ("甜言蜜语", "tián yán mì yǔ", "sweet words"),
    ("同甘共苦", "tóng gān gòng kǔ", "share joys and sorrows"),
    ("突如其来", "tū rú qí lái", "arise suddenly"),
    ("完璧归赵", "wán bì guī zhào", "return intact to owner"),
    ("万紫千红", "wàn zǐ qiān hóng", "rich variety"),
    ("亡羊补牢", "wáng yáng bǔ láo", "better late than never"),
    ("微不足道", "wēi bù zú dào", "insignificant"),
    ("唯我独尊", "wéi wǒ dú zūn", "extremely arrogant"),
    ("无价之宝", "wú jià zhī bǎo", "priceless treasure"),
    ("无可厚非", "wú kě hòu fēi", "give no cause for criticism"),
    ("无与伦比", "wú yǔ lún bǐ", "incomparable"),
    ("五谷丰登", "wǔ gǔ fēng dēng", "abundant harvest"),
    ("喜出望外", "xǐ chū wàng wài", "overjoyed"),
    ("喜闻乐见", "xǐ wén lè jiàn", "well-loved"),
    ("细水长流", "xì shuǐ cháng liú", "small steady flow"),
    ("相得益彰", "xiāng dé yì zhāng", "bring out the best in each other"),
    ("心旷神怡", "xīn kuàng shén yí", "relaxed and happy"),
    ("心心相印", "xīn xīn xiāng yìn", "kindred spirits"),
    ("欣欣向荣", "xīn xīn xiàng róng", "thriving"),
    ("胸有成竹", "xiōng yǒu chéng zhú", "have a well-thought-out plan"),
    ("悬梁刺股", "xuán liáng cì gǔ", "study desperately hard"),
    ("鸦雀无声", "yā què wú shēng", "dead silent"),
    ("言而无信", "yán ér wú xìn", "break one's word"),
    ("言归正传", "yán guī zhèng zhuàn", "back to the topic"),
    ("掩耳盗铃", "yǎn ěr dào líng", "self-deception"),
    ("眼花缭乱", "yǎn huā liáo luàn", "dazzled"),
    ("洋洋洒洒", "yáng yáng sǎ sǎ", "copious and fluent"),
    ("一举成名", "yī jǔ chéng míng", "become famous overnight"),
    ("一诺千金", "yī nuò qiān jīn", "a promise worth a thousand gold"),
    ("一视同仁", "yī shì tóng rén", "treat equally"),
    ("一丝不挂", "yī sī bù guà", "stark naked"),
    ("一往无前", "yī wǎng wú qián", "press forward with indomitable will"),
    ("一意孤行", "yī yì gū xíng", "act arbitrarily"),
    ("衣冠楚楚", "yī guān chǔ chǔ", "immaculately dressed"),
    ("贻笑大方", "yí xiào dà fāng", "make a fool of oneself"),
    ("因地制宜", "yīn dì zhì yí", "suit measures to local conditions"),
    ("引人注目", "yǐn rén zhù mù", "attract attention"),
    ("迎刃而解", "yíng rèn ér jiě", "easily solved"),
    ("邮亭驿馆", "yóu tíng yì guǎn", "posthouse"),
    ("有备无患", "yǒu bèi wú huàn", "preparedness prevents peril"),
    ("有口皆碑", "yǒu kǒu jiē bēi", "universally praised"),
    ("有恃无恐", "yǒu shì wú kǒng", "feel secure with backing"),
    ("余音绕梁", "yú yīn rào liáng", "lingering sound"),
    ("与日俱增", "yǔ rì jù zēng", "grow with each passing day"),
    ("语重心长", "yǔ zhòng xīn cháng", "sincere and earnest"),
    ("源远流长", "yuán yuǎn liú cháng", "long-standing"),
    ("跃跃欲试", "yuè yuè yù shì", "itching to try"),
    ("在所不惜", "zài suǒ bù xī", "not hesitate"),
    ("责无旁贷", "zé wú páng dài", "duty-bound"),
    ("贼眉鼠眼", "zéi méi shǔ yǎn", "shifty-eyed"),
    ("争先恐后", "zhēng xiān kǒng hòu", "strive to be first"),
    ("知难而进", "zhī nán ér jìn", "go despite difficulties"),
    ("直截了当", "zhí jié liǎo dàng", "straightforward"),
    ("纸上谈兵", "zhǐ shàng tán bīng", "empty talk"),
    ("志同道合", "zhì tóng dào hé", "share the same ambitions"),
    ("中流砥柱", "zhōng liú dǐ zhù", "mainstay"),
    ("众矢之的", "zhòng shǐ zhī dì", "target of public criticism"),
    ("自暴自弃", "zì bào zì qì", "give up on oneself"),
    ("自强不息", "zì qiáng bù xī", "constantly strive"),
    ("走马观花", "zǒu mǎ guān huā", "give a quick glance"),
]


def load_existing():
    """Load current idioms and return set of Chinese chars already present."""
    if not IDIOMS_FILE.exists():
        return [], set()
    with open(IDIOMS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = {item["chinese"] for item in data}
    return data, existing


def build_detail_prompt(chinese, pinyin, hint):
    """Build a prompt for the LLM to generate full idiom details."""
    return f"""Generate a complete dictionary entry for the classical Chinese idiom (成语) "{chinese}" (pinyin: {pinyin}, rough meaning: "{hint}").

Output strict JSON only (no markdown, no commentary), with exactly these fields:
{{
  "chinese": "{chinese}",
  "pinyin": "{pinyin}",
  "literal": "<English literal word-by-word translation, comma separated>",
  "meaning": "<2-3 sentence English explanation of what it means>",
  "origin": "<3-5 sentence English summary of the classical origin story, naming dynasties/figures if known>",
  "example_zh": "<one natural Chinese example sentence>",
  "example_en": "<natural English translation of that example>",
  "category": "<one of: Action, Attitude, Communication, Condition, Determination, Emotion, Knowledge, Leadership, Learning, Logic, Method, Morality, Perseverance, Philosophy, Power, Quality, Recovery, Success, Wisdom, Youth, Status, Skill, Variety, Distance, Clarity, Lifestyle>",
  "similar": ["<2-3 similar Chinese idioms, characters only>"],
  "opposite": ["<1-2 opposite Chinese idioms, characters only>"]
}}

Output the JSON only."""


def parse_llm_json(text):
    """Extract and parse JSON from LLM output (handles markdown fences)."""
    # Strip markdown fences if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    # Find first { and last }
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1:
        return None
    return json.loads(text[first:last+1])


def slugify_pinyin(pinyin):
    """Convert pinyin with tones to URL slug (lowercase, hyphen-separated, no tones)."""
    # Remove tone marks by stripping non-ascii after the letter
    import unicodedata
    normalized = unicodedata.normalize("NFKD", pinyin)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_only.lower().replace(" ", "-")


def gen_idiom(chinese, pinyin, hint):
    """Generate one idiom entry via LLM through hermes_tools."""
    prompt = build_detail_prompt(chinese, pinyin, hint)
    # Call hermes run-prompt CLI (or fall back to subprocess)
    try:
        # Use the 'hermes' CLI to invoke a one-shot prompt
        result = subprocess.run(
            ["hermes", "--yolo", "-z", prompt],
            capture_output=True, text=True, timeout=180
        )
        if result.returncode != 0:
            print(f"  hermes ask failed: {result.stderr[:200]}")
            return None
        text = result.stdout
    except Exception as e:
        print(f"  LLM call error: {e}")
        return None

    try:
        data = parse_llm_json(text)
    except Exception as e:
        print(f"  JSON parse error: {e}")
        return None

    if not data or "chinese" not in data:
        return None

    data["id"] = slugify_pinyin(data.get("pinyin", pinyin))
    return data


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    existing_data, existing_set = load_existing()
    print(f"Existing: {len(existing_data)} idioms")

    # Filter candidates not yet present
    candidates = [c for c in CANDIDATE_IDIOMS if c[0] not in existing_set]
    random.shuffle(candidates)
    print(f"Candidates available: {len(candidates)}")

    selected = candidates[:count]
    print(f"Generating {len(selected)} new idioms...\n")

    new_entries = []
    for chinese, pinyin, hint in selected:
        print(f"  → {chinese} ({pinyin})")
        entry = gen_idiom(chinese, pinyin, hint)
        if entry:
            new_entries.append(entry)
            print(f"    OK: literal='{entry.get('literal','')[:50]}...'")

    if not new_entries:
        print("\nNo new idioms generated. Exiting.")
        return 1

    # Append to existing
    combined = existing_data + new_entries
    with open(IDIOMS_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nAdded {len(new_entries)} idioms. Total: {len(combined)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())